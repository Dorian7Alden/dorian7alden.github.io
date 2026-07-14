# probHTML2MD

HTML 赛题内容 → Markdown。从 Web 复制 HTML 元素，解析为 Markdown 题目文档。题目内容更新时，重新复制 HTML 即可重新产出。

## 结构摘要

| 条目 | 用途 |
|------|------|
| `html2md.py` | 主转换脚本：HTML 解析 → Block IR → Markdown 渲染 |
| `requirements.txt` | Python 依赖（beautifulsoup4） |
| `raw-html/` | 原始 HTML 输入文件（从 Web 复制），文件名与输出一一对应 |

## 使用

```bash
# 单个文件：输出到 stdout
python3 html2md.py raw-html/task-01-storage.html

# 指定输出文件
python3 html2md.py raw-html/task-01-storage.html -o output/task-01-storage.md

# 批量转换所有 raw-html
mkdir -p output
for f in raw-html/*.html; do
    python3 html2md.py "$f" -o "output/$(basename "$f" .html).md"
done
```

## 本层规则

**`raw-html/` 纳入版本控制，产出文件忽略。**
> **保留 raw-html 的原因**：避免每次都要手动从 Web 逐个复制 HTML，纳入仓库可直接复用。
> **忽略产出的原因**：产物可随时通过原始 HTML 重建，无需版本控制。
