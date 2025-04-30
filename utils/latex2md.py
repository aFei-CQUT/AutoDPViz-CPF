# python3.12.7
# -*- coding: utf-8 -*-
r"""
Latex → Markdown 转换脚本
功能：
1. 顺序编号 figure / table / equation，交叉引用自动替换为 (N)
2. 支持 \section 等标题、元数据、表格/算法/图片/公式解析
3. CLI：python Latex2Md.py
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ------------------------------------------------- #
# 0. 预扫描 label 顺序编号
# ------------------------------------------------- #
def build_label_map(tex: str) -> Dict[str, int]:
    lm: Dict[str, int] = {}
    fig = tab = eq = 0
    stack: List[Tuple[str, int]] = []
    for ln in tex.splitlines():
        ln = ln.strip()
        m = re.match(r"\\begin\{(figure|table|longtable|equation)(\*?)}", ln)
        if m:
            env = m.group(1)
            if env == "figure":
                fig += 1
                stack.append(("figure", fig))
            elif env in ("table", "longtable"):
                tab += 1
                stack.append(("table", tab))
            elif env == "equation":
                eq += 1
                stack.append(("equation", eq))
            else:
                stack.append((None, 0))
            continue
        if ln.startswith(r"\end") and stack:
            stack.pop()
            continue
        for lb in re.findall(r"\\label\{([^}]*)}", ln):
            if stack:
                env, no = stack[-1]
                lm.setdefault(lb, no)
    return lm

# ------------------------------------------------- #
# 0.1 预扫描 bibitem 构建引文映射
# ------------------------------------------------- #
def build_cite_map(tex: str) -> Dict[str, int]:
    cite_map = {}
    idx = 1
    for ln in tex.splitlines():
        m = re.search(r"\\bibitem\{([^}]*)}", ln)
        if m:
            key = m.group(1)
            cite_map[key] = idx
            idx += 1
    return cite_map

# ------------------------------------------------- #
# 1. Meta 信息抽取
# ------------------------------------------------- #
class MetaExtractor:
    def __init__(self):
        self.cn_title: Optional[str] = None
        self.done_abs = {"cn": False, "en": False}
        self.done_kw = {"cn": False, "en": False}
        self.hide_meta = False  # 新增

    def extract(self, ln: str, out: List[str]) -> bool:
        macs = [
            {"base": "maketitle", "pat": r"\\maketitle(cn|en)\{(.*?)\}", "tpl": (None, "**English Title:** {0}"), "hide": False},
            {"base": "authors", "pat": r"\\authors(cn|en)\{(.*?)\}", "tpl": ("**作者：** {0}", "**Authors:** {0}"), "hide": True},
            {"base": "advisor", "pat": r"\\advisor(cn|en)\{(.*?)\}", "tpl": ("**导师：** {0}", "**Advisors:** {0}"), "hide": True},
            {"base": "schoolinfo", "pat": r"\\schoolinfo(cn|en)\{(.*?)\}", "tpl": ("*{0}*", "*{0}*"), "hide": True},
        ]
        for cmd in macs:
            m = re.search(cmd["pat"], ln)
            if m:
                lang, txt = m.groups()
                if cmd["hide"] and self.hide_meta:
                    return True  # 跳过隐藏内容
                if cmd["base"] == "maketitle" and lang == "cn":
                    self.cn_title = txt.strip()
                    return True
                tpl = cmd["tpl"][0] if lang == "cn" else cmd["tpl"][1]
                if tpl:
                    out.append(tpl.format(txt.strip()))
                return True

        m = re.search(r"\\abstract(cn|en)\{(.*?)\}", ln)
        if m:
            lang, txt = m.groups()
            if not self.done_abs[lang]:
                lbl = "摘要：" if lang == "cn" else "Abstract:"
                out.append(f"**{lbl}** {txt.strip()}")
                self.done_abs[lang] = True
            return True

        m = re.search(r"\\keywords(cn|en)\{(.*?)\}", ln)
        if m:
            lang, txt = m.groups()
            if not self.done_kw[lang]:
                lbl = "关键词：" if lang == "cn" else "Keywords:"
                sep = "；" if lang == "cn" else ";"
                out.append(f"**{lbl}** {', '.join(k.strip() for k in txt.split(sep))}")
                self.done_kw[lang] = True
            return True
        return False

# ------------------------------------------------- #
# 2. 章节标题处理
# ------------------------------------------------- #
class StructureHandler:
    MAP = [
        (r"\\section\*?\{([^}]*)}", "##"),
        (r"\\subsection\*?\{([^}]*)}", "###"),
        (r"\\subsubsection\*?\{([^}]*)}", "####"),
        (r"\\subsubsubsection\*?\{([^}]*)}", "#####"),  # 新增
        (r"\\subsubsubsubsection\*?\{([^}]*)}", "######"),  # 新增
    ]

    @staticmethod
    def handle(ln: str, out: List[str]) -> bool:
        for pat, mark in StructureHandler.MAP:
            m = re.match(pat, ln)
            if m:
                title = m.group(1).strip()
                title = TextCleaner.math(title)
                out.append(f"{mark} {title}")
                return True
        return False

# ------------------------------------------------- #
# 3. 文本清理器
# ------------------------------------------------- #
class TextCleaner:
    CMD = {
        r"\\textbf\{(.*?)\}": r"**\1**",
        r"\\textit\{(.*?)\}": r"*\1*",
        r"\\item": "-",
        r"\\noindent": "",
        r"\\settableinnerfont": "",
        r"\\textsuperscript\{(.*?)\}": r"<sup>\1</sup>",
    }
    SPECIAL = {r"\\%": "%", r"\\_": "_", r"\\&": "&"}

    @classmethod
    def clean(cls, ln: str, keep_refs: bool, lm: Dict[str, int], cite_map: Dict[str, int]) -> str:
        if keep_refs:
            def repl_cite(m):
                keys = m.group(1).split(',')
                nums = [str(cite_map.get(k.strip(), '?')) for k in keys]
                return '[' + ', '.join(nums) + ']'
            ln = re.sub(r"\\cite\{([^}]*)}", repl_cite, ln)
            ln = re.sub(r"\\ref\{([^}]*)}", lambda m: f"{lm.get(m.group(1), '?')}", ln)
            ln = re.sub(r"\\label\{[^}]*}", "", ln)
        else:
            ln = re.sub(r"\\(ref|label|cite)\{.*?}", "", ln)
        for p, r in {**cls.CMD, **cls.SPECIAL}.items():
            ln = re.sub(p, r, ln)
        return ln.strip()

    @staticmethod
    def math(ln: str) -> str:
        return re.sub(r"\\\)", "$", re.sub(r"\\\(", "$", ln))

# ------------------------------------------------- #
# 4. 环境处理器（表/图/公式/算法）
# ------------------------------------------------- #
class EnvHandler:
    def __init__(self, auto_num=True):
        self.auto_num = auto_num
        self.eq_no = 0
        self.in_eq = False
        self.eq_buf: List[str] = []
        self.eq_labels: List[str] = []
        self.in_alg = False
        self.in_tab = False
        self.tab_buf: List[str] = []
        self.in_fig = False
        self.fig_buf: List[str] = []
        self.alg_buf: List[str] = []  # 新增

    @staticmethod
    def _clean_cell(c):
        c = re.sub(r"\\\(", "$", c)
        c = re.sub(r"\\\)", "$", c)
        c = re.sub(r"\\textbf\{([^}]*)}", r"\1", c)
        c = re.sub(r"\\textit\{([^}]*)}", r"\1", c)
        return c.strip()

    def _simple_table(self, lines):
        rows, cap = [], False
        for ln in lines:
            if r"\begin{tabular}" in ln:
                cap = True
                continue
            if r"\end{tabular}" in ln:
                cap = False
                continue
            if not cap:
                continue
            ln = ln.strip()
            if ln.startswith((r"\toprule", r"\midrule", r"\bottomrule")):
                continue
            if ln.endswith(r"\\"):
                ln = ln[:-2].strip()
            if "&" not in ln:
                continue
            rows.append([self._clean_cell(x) for x in ln.split("&")])
        if not rows:
            return "[Table]"
        md = [
            "| " + " | ".join(rows[0]) + " |",
            "| " + " | ".join(["---"] * len(rows[0])) + " |",
        ]
        md += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return "\n" + "\n".join(md) + "\n"

    def _longtable_to_md(self) -> str:
        lines = self.tab_buf
        clean = [
            ln.strip()
            for ln in lines
            if not re.search(r"\\(caption|label|centering)", ln)
            and not ln.strip().startswith("%")
        ]
        body: List[str] = []
        capture = False
        for ln in clean:
            if r"\begin{longtable" in ln:
                capture = True
                continue
            if r"\end{longtable" in ln:
                break
            if not capture:
                continue
            if re.match(r"\\(endfirsthead|endhead|endfoot|endlastfoot)", ln):
                continue
            if ln.startswith((r"\toprule", r"\midrule", r"\bottomrule")) or "续上表" in ln:
                continue
            if ln.endswith(r"\\"):
                ln = ln[:-2].strip()
            if "&" in ln:
                body.append(ln)
        if not body:
            return "[Table]"
        header = body[0]
        rows = body[1:]
        h_cells = [self._clean_cell(c) for c in header.split("&")]
        md = [
            "| " + " | ".join(h_cells) + " |",
            "| " + " | ".join(["---"] * len(h_cells)) + " |",
        ]
        for row in rows:
            if row.strip() == header.strip():
                continue
            md.append("| " + " | ".join(self._clean_cell(c) for c in row.split("&")) + " |")
        return "\n" + "\n".join(md) + "\n"

    def _table_from_buf(self, lm: Dict[str, int]) -> str:
        txt = "\n".join(self.tab_buf)
        cap_m = re.search(r"\\caption\{(.*?)\}", txt)
        cap = cap_m.group(1).strip() if cap_m else "Table"
        lb_m = re.search(r"\\label\{(.*?)\}", txt)
        lb = lb_m.group(1) if lb_m else None
        num = lm.get(lb, "?") if lb else "?"
        if "longtable" in txt:
            md_table = self._longtable_to_md()
        elif re.search(r"\\multirow|\\makecell|\\cmidrule", txt):
            md_table = "[Table]"
        else:
            md_table = self._simple_table(self.tab_buf)
        return f"**表 {num}: {cap}**\n{md_table}"

    def handle(self, ln: str, out: List[str], lm: Dict[str, int]) -> bool:
        if ln.startswith((r"\begin{table", r"\begin{longtable")):
            self.in_tab = True
            self.tab_buf = [ln]
            return True
        if self.in_tab:
            self.tab_buf.append(ln)
            if ln.startswith((r"\end{table", r"\end{longtable")):
                out.append(self._table_from_buf(lm))
                self.in_tab = False
                self.tab_buf = []
            return True
        if ln.startswith(r"\begin{breakablealgorithm}"):
            self.in_alg = True
            self.alg_buf = []
            return True
        if self.in_alg:
            if ln.startswith(r"\end{breakablealgorithm}"):
                out.append("```latex\n" + "\n".join(self.alg_buf) + "\n```")
                self.in_alg = False
                self.alg_buf = []
            else:
                self.alg_buf.append(ln)
            return True
        if ln.startswith(r"\begin{figure}"):
            self.in_fig = True
            self.fig_buf = [ln]
            return True
        if self.in_fig:
            self.fig_buf.append(ln)
            if ln.startswith(r"\end{figure}"):
                txt = "\n".join(self.fig_buf)
                imgs = re.findall(r"\\includegraphics(?:\[[^\]]*])?\{(.*?)}", txt)
                cap_m = re.search(r"\\caption\{(.*?)\}", txt)
                cap = cap_m.group(1).strip() if cap_m else "Figure"
                lb_m = re.search(r"\\label\{(.*?)\}", txt)
                lb = lb_m.group(1) if lb_m else None
                num = lm.get(lb, "?") if lb else "?"
                md_imgs = "\n".join(f"![Image]({img})" for img in imgs)
                out.append(f"{md_imgs}\n**图 {num}: {cap}**")
                self.in_fig = False
                self.fig_buf = []
            return True  # 修改处：确保所有 figure 环境内的行返回 True
        if self.in_eq:
            if re.match(r"\\end\{equation\*?}", ln):
                eq = "\n".join(self.eq_buf).strip()
                out.append(f"$$\n{eq}\n({self.eq_no})\n$$" if self.auto_num else f"$$\n{eq}\n$$")
                for lb in self.eq_labels:
                    lm.setdefault(lb, self.eq_no)
                self.eq_buf.clear()
                self.eq_labels.clear()
                self.in_eq = False
            else:
                self.eq_labels += re.findall(r"\\label\{(eq:[^}]*)}", ln)
                clean = re.sub(r"\\label\{[^}]*}", "", ln).strip()
                if clean:
                    self.eq_buf.append(clean)
            return True
        if re.match(r"\\begin\{equation\*?}", ln):
            self.in_eq = True
            self.eq_no += 1
            return True
        return False

# ------------------------------------------------- #
# 5. 参考文献
# ------------------------------------------------- #
class BibHandler:
    def __init__(self):
        self.in_bib, self.idx = False, 1

    def handle(self, ln: str, out: List[str]) -> bool:
        if ln.startswith(r"\begin{thebibliography}"):
            self.in_bib, self.idx = True, 1
            out.append("## 参考文献")
            return True
        if ln.startswith(r"\end{thebibliography}"):
            self.in_bib = False
            return True
        if self.in_bib and re.match(r"\s*\\bibitem", ln):
            m = re.match(r"\s*\\bibitem\{.*?}\s*(.*)", ln)
            content = m.group(1).strip() if m else ln
            authors = content.split(".", 1)[0].strip()
            rest = content[len(authors):].lstrip(". ").rstrip(".")
            out.append(f"[{self.idx}] {authors}. {rest}.")
            self.idx += 1
            return True
        return False

# ------------------------------------------------- #
# 6. Facade 转换器
# ------------------------------------------------- #
class Latex2Md:
    SKIP = re.compile(r"\\(wuhao|rmfamily|fontspec|vspace|centering)")

    def __init__(self, auto_num=True, keep_refs=True):
        self.auto_num, self.keep_refs = auto_num, keep_refs

    def convert(self, tex: str) -> str:
        lm = build_label_map(tex)
        cite_map = build_cite_map(tex)
        meta, struct, env, bib = MetaExtractor(), StructureHandler(), EnvHandler(self.auto_num), BibHandler()
        md: List[str] = []

        for raw in tex.splitlines():
            ln = raw.rstrip()
            if not ln or ln.startswith(r"\end{document}"):
                continue
            if self.SKIP.search(ln) or ln.strip() in {"{", "}"}:
                continue
            m = re.match(r"\\setHideOptions\{(.*?)\}", ln)
            if m:
                option = m.group(1).strip()
                if option == "forcehide":
                    meta.hide_meta = True
                else:
                    meta.hide_meta = False
                continue
            if meta.extract(ln, md):
                continue
            if struct.handle(ln, md):
                continue
            ln = TextCleaner.math(ln)
            if bib.handle(ln, md):
                continue
            if env.handle(ln, md, lm):
                continue
            ln = TextCleaner.clean(ln, self.keep_refs, lm, cite_map)
            if ln and not ln.lstrip().startswith("%"):
                md.append(ln)

        if meta.cn_title:
            md.insert(0, f"# {meta.cn_title}")
        return "\n".join(md)

# ------------------------------------------------- #
# 7. CLI
# ------------------------------------------------- #
if __name__ == "__main__":
    tex_path = Path("./utils/merge/merge.tex")
    md_path = Path("./utils/merge/Latex2Md.md")
    raw = tex_path.read_text(encoding="utf-8", errors="replace")
    s, e = raw.find(r"\begin{document}"), raw.rfind(r"\end{document}")
    if s != -1 and e != -1:
        raw = raw[s + len(r"\begin{document}"):e]
    md = Latex2Md(auto_num=False, keep_refs=True).convert(raw)
    md_path.write_text(md, encoding="utf-8")
    print("✅ 转换完成，已写入:", md_path)