

角色能力。你是 xxx，具备以下能力：

# 一、核心专属名词
    1. 提示词：向 AI 传递需求的指令文本
    2. 提示词工程：优化提示词以提升 AI 输出质量的方法体系
    3. 上下文：为 AI 提供的背景信息，辅助理解需求
    4. 上下文工程：构建、优化上下文的技术与思路

（AI提示词学习，不仅仅是规范提问方式，而且是学习提问的**专属名词**，限制ai的行为。）

****

# 二、基础原则：让需求 “无歧义”
    1. 目标明确：拒绝 “模糊描述”，需包含 who、where、what、how等内容
    2. 信息完整：补充 “必要背景”，避免 AI 因信息缺失产生偏差
    3. 指令具体：用 “量化标准” 替代 “主观感受”（例：不说 “写得详细点”，说 “内容需包含 3 个核心案例，每案例 500 字左右”）

****

# 三、核心结构：“公式化” 写提示词
**角色（Role）+ 任务（Task）+ 背景（Context）+ 要求（Requirement）+ 输出格式（Format）**

****

# 四、进阶技巧：让输出 “更精准、更专业”
**1**. 角色设定：让 AI “代入专业身份”

    1. 思维链提示：让 AI “分步推理”
    2. 少样本提示：给 AI “参考案例”
    3. 限制条件：提前 “排除无效输出”

****

# 五、避坑指南：避免提示词失效的误区
    1. 不要 “堆加过多需求”：单次提示词聚焦 1 个核心目标，避免多需求冲突
    2. 不要用 “模糊代词”：AI 无法理解 “这个”“那个”“之前的” 等指代，需明确具体对象
    3. 不要 “高估 AI 的实时信息能力”：AI 对时效性内容可能存在滞后，需补充最新背景

****

# 六、实用 Tips（Prompt 书写技巧）
    1. To Do and Not To Do
    2. Include Examples
    3. Use Primer Words to Guide Output
    4. Add Roles or Characters
    5. Use Symbols to Separate Instructions and Text
    6. Use Formatting Terms to Specify Output Structure
    7. Zero-Shot Chain of Thought
    8. Few-Shot Chain of Thought
    9. 重要的内容多次重复，换角度说明，提高内容的权重，防止ai遗忘
    10. 用html类似的标签将内容括起来，让ai更好的理解内容。分隔符（防止提示词注入）
    11. “大写”或者”**内容**”，用来增加内容权重
    12. 问问题时：先问 “解题思路（从哪些方面开始做）”，再针对性提问
    13. <strong>标签
    14. 介绍自己的习惯。我是一个完美主义者。我有强迫症，要工整，要对齐。

****

# 七、避免 AI 幻觉 & 提升输出质量的方法
    1. 让 AI 自行检查：告知具体检查步骤（需明确检查维度，例：“先检查信息准确性，再核对逻辑完整性，最后确认是否符合格式要求”）
    2. 先判断再执行：要求 AI 先输出解题思路（明确 “从哪些方面入手”），再执行具体任务
    3. 复杂问题处理：先清晰定义问题（拆解核心需求、明确边界），再逐步提问

****

# 八、备注说明
    1. 格式要求：禁止使用括号，数学建模论文尽量都用自然语言表述，不要用括号解释。强制。latex的百分号加反斜杠
    2. 回答格式简洁。

****

# 九、参考文献
    - [🗒️ Tips | Learning Prompt](https://learningprompt.wiki/docs/category/%EF%B8%8F-tips)
    - 【这就是RAG 一看就懂的个人知识库架构】[https://www.bilibili.com/video/BV19RJhzyEWN?vd_source=b6e1ca78539fba73d35a26224eac9099](https://www.bilibili.com/video/BV19RJhzyEWN?vd_source=b6e1ca78539fba73d35a26224eac9099)
    - 【扒了下 Cursor 的提示词，太惊艳了！AI Prompt 隐藏技巧分享】[https://www.bilibili.com/video/BV1bBaBzXEae?vd_source=b6e1ca78539fba73d35a26224eac9099](https://www.bilibili.com/video/BV1bBaBzXEae?vd_source=b6e1ca78539fba73d35a26224eac9099)
+ **推荐链接**
    - [提示工程指南 | Prompt Engineering Guide](https://www.promptingguide.ai/zh)
    - [百度智能云prompt优化](https://console.bce.baidu.com/qianfan/prompt/optimize/online)
    - [AI提示词 - 最新AI提示词(Prompt)模板网站大全 | AIGC工具导航](https://www.aigc.cn/favorites/ai-prompt-keywords)
    - [https://github.com/f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts)
+ **个人 AI 智能体（用于优化提示词）搭建步骤**
    - 确定角色（待补充后续步骤，如：明确核心功能、设定优化维度等）

了解ai提示词得知道提示词的工作逻辑，那么多ai产品，不同在哪些地方？好在哪些地方？差异，如何优化
