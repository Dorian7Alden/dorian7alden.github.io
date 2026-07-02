# Daily English Dictation

Daily English Dictation（每日英语听写）是 [Coach Shane](https://www.youtube.com/@DailyEnglishDictation) 的英语听写练习系列。每篇练习包含一段真实语境下的英语句子（来自新闻、美剧、电影、访谈等），要求先听写，再对照答案，学习其中的发音现象、词汇和语法。

## 目录结构

练习按 10 篇一组分目录存放：

```
Daily English Dictation/
├── README.md          ← 本文件
├── 001-010/           ← 第 001-010 篇
├── 011-020/           ← 第 011-020 篇
├── 021-030/
├── 031-040/
├── 041-050/
├── 051-060/
├── 061-070/
├── 071-080/
└── 081-090/
```

## 文件命名规范

每篇练习文件命名为 `NNN-level.md`：

- **NNN**：三位数字编号，如 `001`、`045`、`083`
- **level**：难度级别，见下方难度分级表

示例：`001-intermedia.md`、`045-expert.md`

## 难度分级

从 045 开始引入难度分级，001-044 已手动补充分级。分级从以下维度主观评估：

- **词汇难度**：是否包含低频、专业词汇
- **句子复杂度**：从句数量、句子长度、语序是否特殊
- **口语连读现象**：省音、连读、弱读的数量和难度

| 级别 | 文件名标签 | 说明 | 典型特征 |
|------|-----------|------|---------|
| **beginner** | `beginner` | 初级 | 短句、日常词汇、无明显连读难点 |
| **intermedia** | `intermedia` | 中级 | 中等长度、一定词汇量、常见连读现象 |
| **advanced** | `advanced` | 高级 | 长复合句、专业词汇、多重连读 |
| **expert** | `expert` | 专家 | 诗歌、古语、极不规则发音 |

> **注意**：分级是主观的，不作为严格标准，仅用于粗略区分练习难度。

## 文档元数据

每个练习文件使用 YAML frontmatter 记录元数据：

```yaml
---
create-time: 2026-04-14
update-time: 2026-07-02
tags: intermedia|daily-english-dictation
background: 新闻
---
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `create-time` | `YYYY-MM-DD` | 创建日期，标注实际听写日期（部分为推算） |
| `update-time` | `YYYY-MM-DD` | 最后更新日期 |
| `tags` | 英文，`\|` 分隔 | 难度标签 + `daily-english-dictation` |
| `background` | 中文 | 句子来源背景类型 |

### Background 背景标签

| 标签 | 说明 |
|------|------|
| `新闻` | AP News 等新闻媒体 |
| `美剧` | 情景喜剧、电视剧（如 Seinfeld、Peanuts） |
| `电影` | 电影台词（如 The Pursuit of Happiness） |
| `体育` | 体育赛事报道 |
| `访谈` | 人物访谈、个人叙述 |
| `日常对话` | 日常口语交流 |
| `诗歌` | 诗歌、韵文 |
| `名言` | 格言、引语 |

### Tags 标签

固定格式：`{难度级别}|daily-english-dictation`

- 难度级别：`beginner` / `intermedia` / `advanced` / `expert`
- 固定标签：`daily-english-dictation`

## 文档内容结构

早期格式（001-043）和后期格式（044+）略有不同，后期统一为以下结构：

```markdown
## Daily English Dictation NNN - YYYY/MM/DD - level

### 🎧 Listening Practice
- **My listening**: 用户听写内容
- **Answer**: 正确答案
- **Pronunciation**: 发音标注

### 📖 Accumulation
- 词汇、短语、语法积累
```

## 相关资料

- Coach Shane YouTube 频道：https://www.youtube.com/@DailyEnglishDictation
- 发音规则参考：7 H's 规则、S/N/L 强音取消 D/T/TH 弱音规则
