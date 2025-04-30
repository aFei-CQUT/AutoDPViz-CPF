# Marker

Marker 能够快速准确地将文档转换为 Markdown、JSON 和 HTML 格式。

- 支持转换所有语言的 PDF、图片、PPTX、DOCX、XLSX、HTML、EPUB 文件
- 格式化表格、表单、公式、行内数学公式、链接、参考文献和代码块
- 提取并保存图片
- 去除页眉/页脚/其他冗余内容
- 可通过自定义格式和逻辑进行扩展
- 可选使用 LLM 提升准确率
- 支持 GPU、CPU 和 MPS 运行

## 性能表现

<img src="data/images/overall.png" width="800px"/>

Marker 在基准测试中优于 Llamaparse 和 Mathpix 等云服务以及其他开源工具。

以上结果为单页 PDF 串行处理结果。当使用批处理模式时，Marker 速度显著提升，在 H100 GPU 上预计吞吐量可达 122 页/秒（22 个进程并行，每页耗时 0.18 秒）。

详细的速度和准确率基准测试及运行方法请参考[下方](#基准测试)内容。

## 混合模式

要获得最高准确率，可使用 `--use_llm` 参数启用 LLM 辅助处理。该模式可实现跨页表格合并、行内数学公式处理、表格格式优化和表单值提取功能。支持任意 Gemini 或 Ollama 模型，默认使用 `gemini-2.0-flash`。[详见下文](#llm-服务)

以下是 Marker 原生、单独使用 Gemini Flash 以及 Marker 结合 LLM 的表格处理对比：

<img src="data/images/table.png" width="400px"/>

可见混合模式在准确率上具有显著优势。

## 示例

| PDF                                                          | 文件类型   | Markdown                                                     | JSON                                                         |
| ------------------------------------------------------------ | ---------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Think Python](https://greenteapress.com/thinkpython/thinkpython.pdf) | 教科书     | [查看](https://github.com/VikParuchuri/marker/blob/master/data/examples/markdown/thinkpython/thinkpython.md) | [查看](https://github.com/VikParuchuri/marker/blob/master/data/examples/json/thinkpython.json) |
| [Switch Transformers](https://arxiv.org/pdf/2101.03961.pdf)  | arXiv 论文 | [查看](https://github.com/VikParuchuri/marker/blob/master/data/examples/markdown/switch_transformers/switch_trans.md) | [查看](https://github.com/VikParuchuri/marker/blob/master/data/examples/json/switch_trans.json) |
| [Multi-column CNN](https://arxiv.org/pdf/1804.07821.pdf)     | arXiv 论文 | [查看](https://github.com/VikParuchuri/marker/blob/master/data/examples/markdown/multicolcnn/multicolcnn.md) | [查看](https://github.com/VikParuchuri/marker/blob/master/data/examples/json/multicolcnn.json) |

# 商业使用

我们鼓励研究和个人用途，商业使用需遵守以下限制：

模型权重采用 `cc-by-nc-sa-4.0` 许可，但符合以下条件的企业可申请豁免：
- 最近 12 个月总收入低于 500 万美元
- 累计融资额低于 500 万美元
- 非 [Datalab API](https://www.datalab.to/) 竞争对手

如需商业授权或双重许可，请访问[此页面](https://www.datalab.to)。

# 托管 API

我们提供托管 API 服务：
- 支持 PDF、Word 和 PPT 文件
- 价格仅为主流云服务的 1/4
- 高可用性（99.99%），250 页 PDF 转换约需 15 秒

访问地址：https://www.datalab.to

# 社区

欢迎加入 [Discord](https://discord.gg//KuZwXNGnfH) 参与开发讨论。

# 安装

要求 Python 3.10+ 和 PyTorch。非 Mac 或 GPU 设备需先安装 CPU 版 PyTorch。

基础安装：
```shell
pip install marker-pdf
```

完整功能安装：
```shell
pip install marker-pdf[full]
```

# 使用指南

## 交互式应用
```shell
pip install streamlit
marker_gui
```

## 单文件转换
```shell
marker_single 文件路径.pdf
```

常用参数：
- `--output_dir 路径`：输出目录
- `--output_format [markdown|json|html]`：输出格式
- `--use_llm`：启用 LLM 增强
- `--force_ocr`：强制 OCR 处理
- `--page_range "0,5-10,20"`：指定处理页数

## 批量转换
```shell
marker 输入文件夹路径 --workers 4
```

## 多 GPU 转换
```shell
NUM_DEVICES=4 NUM_WORKERS=15 marker_chunk_convert 输入路径 输出路径
```

## Python API
```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

converter = PdfConverter(artifact_dict=create_model_dict())
rendered = converter("文件路径.pdf")
```

# 输出格式

## Markdown
- 图片链接
- 格式化表格
- LaTeX 公式块
- 代码块
- 脚注上标

## HTML
- `<img>` 标签嵌入图片
- `<math>` 标签公式
- `<pre>` 标签代码

## JSON
树状结构组织文档元素，包含：
- 块类型（Table/Text/Equation 等）
- HTML 片段
- 坐标多边形
- 子块信息
- 图片 Base64 数据

# 高级功能

## 自定义处理流程
通过覆写 processors 和 renderers 实现个性化处理：
```python
from marker.config.parser import ConfigParser

config = {"output_format": "json"}
config_parser = ConfigParser(config)
```

## 表格提取专用
```shell
marker_single 文件.pdf --converter_cls marker.converters.table.TableConverter
```

# 故障排查

常用解决方案：
- 内存不足：减少 worker 数量或拆分文档
- 乱码问题：使用 `--force_ocr`
- 设备指定：`TORCH_DEVICE=cuda`

# 基准测试

## 综合测试
| 方法       | 平均耗时 | 启发式评分 | LLM 评分 |
| ---------- | -------- | ---------- | -------- |
| marker     | 2.84s    | 95.67      | 4.24     |
| llamaparse | 23.35s   | 84.24      | 3.98     |

## 表格测试
| 方法           | 平均得分 |
| -------------- | -------- |
| marker         | 0.816    |
| marker+LLM     | 0.907    |
| Gemini         | 0.829    |

详细测试方法参见文档[基准测试章节](#基准测试)。

# 实现原理

Marker 采用多阶段深度学习流水线：
1. 文本提取与 OCR（surya）
2. 版面分析与阅读顺序检测
3. 块级清洗与格式化（texify）
4. 可选 LLM 增强
5. 内容整合与后处理

# 限制说明

当前版本在处理以下情况时可能受限：
- 复杂嵌套表格
- 特殊表单布局

建议使用 `--use_llm` 参数提升处理效果。

# 致谢

特别感谢以下开源项目：
- Surya OCR
- Texify 公式识别
- DocLayNet 数据集
