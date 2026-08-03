# Phase 2: 结构化文章生成

> [!NOTE]
> 本文档定义了第二阶段（Phase 2）：**结构化文章生成 (Structured Article Generation)** 的技术规范。任何负责实现该阶段的 AI 代理或开发人员都必须严格遵循本文档中的数据结构、写作标准和校验流程。

## 1. 概述

本阶段的核心任务是接收 `master_dict.json`（在 Phase 1 中生成），并将其词汇转化为结构化的、上下文连贯的文章数据（JSON 格式）。

生成的文章必须严格按照 **CEFR B1 (SFI D 级别)** 的瑞典语标准编写，并提供英语作为桥梁语言的完整翻译。每一篇文章都应该是一个连贯的故事或短文，将目标词汇自然地融入其中。

```mermaid
graph TD
    A[输入: master_dict.json] --> B[预处理: 单词分组与聚类]
    B --> C[AI 文章生成引擎]
    C --> D[结构化的 3 层 JSON]
    D --> E{校验规则}
    E -- 失败 (遗漏单词/格式错误) --> F[错误处理与重试]
    F --> C
    E -- 成功 --> G[最终 JSON 归档]
```

## 2. 输入规范

### 2.1 核心输入
*   **`master_dict.json`**: 在 Phase 1 中生成的干净、翻译完整的词典。

### 2.2 继承参数
*   **`source_level`**: 继承自 Phase 1。对于本项目，严格限定为 **"B1"**。该参数决定了 AI 生成引擎使用的语法和词汇难度。
*   **`native_language`**: 继承自 Phase 1（默认："English"）。

### 2.3 配置参数
*   `words_per_article` (Integer): 每篇文章包含的**目标词**数量（默认值：20-30）。
*   `article_length_words` (Integer): 目标文章的总词数长度（默认值：300-500）。
*   `course_id` (String): 课程标识符，用于数据命名空间（默认值："sfid"）。
*   `allow_word_overlap` (Boolean): 相同的单词是否可以作为目标词出现在多篇文章中（默认值：false）。
*   `natural_reuse_target` (Integer): 每个单词在其“主出场”文章之外，还应该自然出现在多少篇文章中（默认值：2）。

## 3. 单词分组策略

> [!IMPORTANT]
> 单词在分配到具体文章前，必须先进行语义相关性分组。相关的单词在同一篇文章中出现，能创造更连贯的上下文，极大降低学习者的理解难度。

支持的分组方法按优先级递减如下：
1.  **语义主题聚类 (Semantic Theme Clustering)**: 按语义主题将单词聚合（例如：食物、工作、家庭、自然、社会）。这直接映射到我们数据架构中的 "Step" 层。
2.  **教材章节分组**: 如果有特定的章节元数据，按章节分组。
3.  **AI 自动聚类**: 当缺乏明确的主题时，AI 引擎必须根据语义相似度动态聚类单词。

## 4. 单词重合策略

为实现 FSRS 间隔重复机制的最大效用，我们采用受控的单词复现策略：

*   **主出场 (Primary Appearance)**: 每个单词在整个课程中拥有且仅有**一次**主出场机会。在该文章中，它被视为高亮的“核心目标词”。
*   **自然复现 (Secondary Appearance)**: 相同的单词**可以且应该**在其他文章中自然出现（但不作为高亮目标词）。
*   **复现指标**: 目标是每个单词总共出现在 2-3 篇文章中（1次主出场 + 1至2次自然复现）。
*   **状态追踪**: 生成脚本必须在全局维护一个状态表，精确追踪哪些单词已被分配为“主出场”，哪些单词还需要“自然复现”，以确保输入词典的 100% 覆盖率。

## 5. CEFR B1 (SFI D) 写作标准

由于输入的 `source_level` 为 B1，所有 AI 生成的文章必须严格遵循 CEFR B1 (SFI Level D) 标准：

*   **语言难度**: 使用 B1 级别的瑞典语词汇和语法。频繁使用从句（如 `att`, `eftersom`, `om`），但要**避免** C1 及以上的生僻词汇或过于复杂的修辞（如高级被动语态或古语）。
*   **文章结构**: 必须具有清晰的叙事弧（引言、正文、结语）。不能是毫无逻辑的句子堆砌。
*   **句子长度**: 平均每句 10-15 个单词。长短句结合，保证阅读节奏。
*   **目标词密度**: 目标词汇应占文章总词数的 5-8%。
*   **上下文线索**: 目标词必须置于“可通过上下文猜测词义”的语境中。例如，不要仅仅说 "Han är en soffpotatis" (他是个沙发土豆)，而应该说 "Han är en soffpotatis som sitter framför TV:n hela dagen och aldrig tränar" (他是个整天坐在电视前从不锻炼的沙发土豆)。
*   **自然性**: 文本必须读起来像原生的瑞典语文章，坚决避免填鸭式的“生词表式”生硬造句。

## 6. 输出规范 (三层架构)

AI 生成的结果必须被序列化为严格遵循三层嵌套架构的 JSON 数据：**Course -> Step -> Article**。

> [!WARNING]
> `sv` 字段必须是纯文本。**不允许**包含任何 HTML 标签（如 `<strong>`）或 Markdown（如 `**`）。高亮是通过精确的字符索引 `position_start` 和 `position_end` 实现的。

### JSON Schema & Example

```json
{
  "course_id": "sfid",
  "steps": [
    {
      "step_id": "step_01",
      "step_title": "Step 1: Daily Life and Health",
      "articles": [
        {
          "article_id": "art_01",
          "article_title": "En dag på gymmet",
          "target_word_count": 25,
          "sentences": [
            {
              "sentence_id": "art01_s001",
              "sv": "Min granne är en riktig soffpotatis som aldrig tränar.",
              "en": "My neighbor is a real couch potato who never exercises.",
              "target_words": [
                {
                  "word_in_sentence": "soffpotatis",
                  "base_form": "soffpotatis",
                  "position_start": 25,
                  "position_end": 36
                },
                {
                  "word_in_sentence": "tränar",
                  "base_form": "träna",
                  "position_start": 48,
                  "position_end": 54
                }
              ]
            }
          ],
          "primary_words_used": ["soffpotatis", "träna", "granne"],
          "secondary_words_used": ["riktig", "aldrig"]
        }
      ]
    }
  ]
}
```

### 字段说明
*   `step_title`: Step 的有意义的主题标题（例如 "Step 1: 日常生活"）。
*   `article_title`: 具体阅读文章的有意义的标题。
*   `sv`: 完整的瑞典语原句文本。
*   `en`: 该句子的完整英语翻译。
*   `target_words`: 该句子中出现的目标词汇数组。
    *   `word_in_sentence`: 单词在句子中的实际形态（可能发生了变位）。
    *   `base_form`: 字典基本形态（必须与 `master_dict.json` 中的 key 完全匹配）。
    *   `position_start` / `position_end`: 基于 `sv` 字符串的 0 索引字符边界 `[start, end)`，用于 UI 精确高亮。
*   `primary_words_used`: 在本篇文章中完成“主出场”的词汇。
*   `secondary_words_used`: 在本篇文章中作为自然复现上下文的词汇。

## 7. 校验规则 (回环)

> [!CAUTION]
> 生成后必须运行自动校验脚本。任何违反以下规则的输出都将导致流水线构建失败。

1.  **100% 覆盖率**: `master_dict.json` 中的每个词必须作为 `primary_words_used` 出现在且仅出现在一篇文章中。
2.  **无生造词 (No Hallucinations)**: `base_form` 不能包含输入词典中没有的编造词。
3.  **索引准确性**: 对于每个 target_word，提取 `sv.substring(position_start, position_end)` 必须完全等于 `word_in_sentence`。
4.  **ID 唯一性**: `sentence_id` 和 `article_id` 必须在全局唯一。
5.  **翻译完整性**: `sentences` 数组中的 `sv` 和 `en` 字段不能为空字符串。

## 8. AI Prompt 模板

调用 LLM 时，应使用具备函数调用/结构化输出功能的模型。更新 Prompt 模板以严格强制执行 B1 级别和三层架构：

```text
You are an expert Swedish language teacher specializing in CEFR Level B1 (SFI Level D). 
Your task is to write a highly coherent, natural-sounding article in Swedish that seamlessly incorporates a specific list of target vocabulary words.

# WRITING STANDARDS:
1. Target Level: STRICTLY CEFR B1. Use grammatical structures appropriate for this level (e.g., subordinate clauses with 'att', 'eftersom', 'om'). Avoid overly academic C1/C2 phrasing.
2. Context Clues: When using a target word, provide enough context so a learner can guess its meaning. Do not just make a list of disconnected sentences.
3. Length & Flow: Write between 300-500 words. The article must have a clear beginning, middle, and end. 
4. Sentence Length: Average 10-15 words per sentence. Mix short and long sentences naturally.
5. Topic: Create an engaging story or essay about: {THEMATIC_STEP_TITLE}. Give the article a meaningful title.

# TARGET VOCABULARY (MUST USE 100%):
{TARGET_WORDS_JSON}

# CONSTRAINTS & OUTPUT FORMAT:
You must output strictly in JSON format matching the requested 3-layer schema (Course -> Step -> Article).
- "sv": The Swedish sentence string MUST be plain text. DO NOT use markdown, HTML, or **bold** tags.
- "target_words": For each target word used in the sentence, identify its exact inflected form ("word_in_sentence"), its original base form ("base_form"), and its precise 0-indexed character positions ("position_start" and "position_end") in the "sv" string.
- You are strictly FORBIDDEN from skipping any word from the target vocabulary list. All words must have their primary appearance.
```

## 9. 错误处理

*   **JSON 验证失败**: 如果 AI 返回无效的 JSON 或未通过 Schema 验证，将精确的解析器错误消息返回给 AI 并要求重试。
*   **覆盖率校验失败**: 如果遗漏了单词，提取遗漏的词汇并通过“纠正 Prompt”注入（例如："You missed the following words: ['word1']. Please rewrite the article to include ALL provided target words."）。
*   **重试上限**: 每篇文章生成的最大重试次数为 **3 次**。连续 3 次失败后，抛出异常并暂停等待人工干预。
