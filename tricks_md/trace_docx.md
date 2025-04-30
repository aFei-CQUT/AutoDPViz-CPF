# **git 镜像追踪 word**

## **1. 准备工作**
- **安装工具**  
  - [Git for Windows](https://git-scm.com/downloads)（含 Git Bash）  
  - [GitHub Desktop](https://desktop.github.com/)（管理仓库）  
  - [Pandoc](https://pandoc.org/installing.html)（转换 Word 到 Markdown）

- **配置仓库**  
  - 在 GitHub 创建私有仓库（如 `word-tracker`）  
  - 用 GitHub Desktop 克隆仓库到本地（如 `E:\word-tracker`）

## **2. 核心配置**
1. **创建钩子脚本**  
   
   - 打开 **Git Bash**，进入仓库的 `.git/hooks` 目录：
     ```bash
     cd /e/word-tracker/.git/hooks
     ```
   - 新建并编辑 `pre-commit` 文件（无后缀）：
     ```bash
     touch pre-commit
     code pre-commit  # 用 VS Code 或其他编辑器打开
     ```

2. **编写钩子脚本**  
   粘贴以下内容（注意调整 Pandoc 路径）：
   
   ```bash
   #!/bin/sh
   echo "Starting pre-commit hook..."
   
   # 遍历所有暂存的 .docx 文件
   for file in $(git diff --cached --name-only | grep '.docx$'); do
       echo "Converting $file to Markdown..."
       "D:/Pandoc/pandoc.exe" "$file" --extract-media=. -t markdown -o "${file%.docx}.md"
       git add "${file%.docx}.md"
       echo "Generated ${file%.docx}.md"
   done
   
   echo "Pre-commit hook completed."
   ```
   
3. **赋予执行权限**  
   ```bash
   chmod +x pre-commit
   ```

## **3.关键检查点**
| 问题                | 解决方法                                                     |
| ------------------- | ------------------------------------------------------------ |
| **钩子未触发**      | 使用 `git commit` 命令行提交（GitHub Desktop 可能绕过钩子）  |
| **Pandoc 路径错误** | 检查路径是否含空格，用 `"D:/Pandoc/pandoc.exe"` 格式 |
| **.md 文件未生成**  | 在脚本中添加调试日志（`echo`）确认转换过程                   |
| **权限不足**        | 运行 `chmod +x .git/hooks/pre-commit`                        |