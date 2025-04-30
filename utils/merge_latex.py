import re
import os

def remove_extra_blank_lines(content):
    """Remove multiple consecutive blank lines, leaving only one blank line."""
    return re.sub(r"(\n\s*){3,}", "\n\n", content)

def merge_tex_files(main_tex_path, output_path):
    with open(main_tex_path, "r", encoding="utf-8") as f:
        content = f.read()

    base_dir = os.path.dirname(main_tex_path)
    processed_files = set()

    def replace_input(match):
        file_rel_path = match.group(1).strip()
        normalized_path = file_rel_path.replace("\\", "/").replace(".tex", "")
        full_path = os.path.join(base_dir, normalized_path)

        # Automatically append .tex if needed
        if not os.path.exists(full_path):
            full_path += ".tex"

        if not os.path.exists(full_path):
            print(f"警告：文件 {normalized_path} 不存在")
            return match.group(0)

        if full_path in processed_files:
            return ""  # Prevent circular references

        processed_files.add(full_path)

        with open(full_path, "r", encoding="utf-8") as f:
            sub_content = f.read()

        # Recursively process \input commands in the subfile
        sub_content = re.sub(r"\\input{([^}]+)}", replace_input, sub_content)
        return sub_content

    # Process \input commands in the main content
    new_content = re.sub(r"\\input{([^}]+)}", replace_input, content, flags=re.DOTALL)

    # Remove any remaining unprocessed \input commands
    new_content = re.sub(r"\\input{.*", "", new_content)

    # Remove multiple consecutive blank lines, keeping only one blank line
    new_content = remove_extra_blank_lines(new_content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"合并完成！输出文件：{output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_tex_path = os.path.join(base_dir, "main.tex")
    merge_tex_files(main_tex_path, "./utils/merge/merge.tex")