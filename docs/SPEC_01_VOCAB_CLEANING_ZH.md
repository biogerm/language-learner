# Phase 1: 词汇提取、清洗与词典生成

## 1. 概述 (Overview)

本阶段 (Phase 1) 是数据流水线的基础步骤。其目标是确保为课程提取的每个瑞典语词汇都有正确、完整的英文翻译。

因为后续阶段（例如文章生成）严重依赖词典的准确性来生成包含上下文的句子，**此阶段必须严格在 Phase 2 之前执行**。

从 PDF 提取的原始词汇文件（JSON 格式）通常包含由于格式问题导致的脏数据（如软连字符截断、语法信息覆盖了翻译、短语动词分裂等）。本流水线将接收原始输入，应用自动化清洗规则和 AI 辅助修复，最终输出一个干净、经过验证的主词典 (Master Dictionary)。

> [!NOTE]
> 词典数据的完整性至关重要。前端使用一个扁平的 JavaScript 对象 `globalDictionary` (`{ "word": "translation" }`)。应用内的“提取词汇”模式允许用户在文章中选择单词，系统会自动通过 `globalDictionary[word.toLowerCase()]` 查找并保存至用户的个人生词本。

## 2. 输入规范 (Input Specification)

### 2.1 输入灵活性 (Input Flexibility)
流水线在输入源方面设计得非常灵活。输入可以是：
1. **带翻译的 JSON**：将瑞典语单词映射到英语翻译的字典（如从教科书 PDF 中提取的）。
2. **原始生词表**：没有翻译的纯瑞典语单词文本列表。
3. **原始文章文本**：一段瑞典语文本，流水线必须首先从中提取核心词汇。

> [!TIP]
> **对于当前项目**，输入特指**带翻译的 JSON** 格式，来源于教科书的词汇表。

### 2.2 主要输入 (Current Project)
*   `b1_ordlista.json`: B1 级别词汇列表（约 3,433 条目，包含约 30 个缺陷条目）
*   `ok_b1_ordlista.json`: B1 级别补充词汇（46 个干净条目）
*   `b1_extra.json`: B1 额外词汇（233 条目，原文和译文形式相同）

### 2.3 参数继承 (Parameters)
这些参数在 Phase 1 中定义，并且**必须被所有后续阶段继承**（Phase 2 至 5）：
*   `source_level` (String): 目标处理等级。**默认值: `"B1"`**。（注：对于本项目，等级严格定为 B1，对应 SFI D 标准）。
*   `native_language` (String): 目标翻译语言。**默认值: `"english"`**。
*   `include_extras` (Boolean): 是否包含 `extra.json` 文件中的单词。**默认值: `false`**。

## 3. 数据清洗规则 (Data Cleaning Rules)

必须按照以下特定规则对输入 JSON 进行遍历和修复。修复过程必须保持日志记录 (Audit Trail)。

### 3.1 软连字符截断修复
*   **条件**: JSON 的 value 字符串中包含软连字符 `\u00ad`。
*   **逻辑**: 提取出被截断的 value，调用 AI 进行补全，并移除软连字符。
*   **示例**:
    *   输入: `"människa": "human being, per\u00ad"`
    *   输出: `"människa": "human being, person"`

### 3.2 语法信息替代修复
*   **条件**: JSON 的 value 字符串以 `(-` 或 `(+` 开头（这些是瑞典语的变位模式，不是英文翻译）。
*   **逻辑**: 清除该错误的 value，将该 key 发送给 AI 重新获取准确的英文翻译。
*   **示例**:
    *   输入: `"sammanfatta": "(-r, -de, -t)"`
    *   输出: `"sammanfatta": "summarize"`

### 3.3 短语动词分裂修复
*   **条件**: JSON 的 value 仅为一个瑞典语的小品词或介词（如 `på`, `av`, `ut`, `upp` 等）。
*   **逻辑**: 将原本的 key 和该 value 合并为一个完整的短语动词作为新的 key，并删除原有词条。然后使用 AI 为合并后的新短语动词生成对应的英文翻译。
*   **示例**:
    *   输入: `"stöta": "på"`
    *   输出: `"stöta på": "run into, encounter"`

### 3.4 换行孤儿条目清除
*   **条件**: JSON 的 key 仅包含英文字符（无瑞典语特殊字符如 `å, ä, ö`）**且** 长度非常短（通常 `< 5` 个字符）。这类条目通常是 PDF 跨行识别导致的碎片。
*   **逻辑**: 永久删除这些条目。
*   **示例**:
    *   检测到: `"ne": "well known in the arts"`, `"ty": "flower"`, `"me": "my jacket?"`
    *   处理: 从数据集中移除。

## 4. 翻译补全规则 (Translation Completion)

在执行完所有清洗规则后，必须进行全面检查，确保每个有效单词都有合法的英文翻译。
*   **逻辑**:
    1.  收集所有 value 为空字符串 (`""`)、`null`、或经上一步判断为无效需要重翻的单词。
    2.  利用 AI 进行**批量翻译**。为防止达到 API Token 上限，按每批 50 个瑞典语单词将词汇发给 AI。
    3.  强制 AI 以 JSON 格式返回结果：`{ "word": "translation" }`。
    4.  验证返回数据，确保所有请求的词均获得了非空翻译。

## 5. 输出规范 (Output Specification)

完成后，系统必须输出主词典 JSON (`master_dictionary.json`)。此文件是包含结构化元数据和词汇详情的持久化基础数据源。

```json
{
  "metadata": {
    "level": "B1",
    "source": "rivstart_b1",
    "total_words": 3433,
    "generated_at": "2025-01-01T00:00:00Z"
  },
  "words": {
    "soffpotatis": {
      "en": "couch potato",
      "word_class": "noun",
      "gender": "en"
    },
    "träna": {
      "en": "exercise, work out",
      "word_class": "verb",
      "gender": null
    }
  }
}
```
> [!TIP]
> 如果 `word_class` 和 `gender` 在本阶段无法通过规则或 AI 完全确定，可设为 `null` 并在后续阶段完善。但是 `en` (翻译) 字段必须包含非空字符串。

## 6. 校验规则 (Validation Rules)

在输出最终文件之前执行数据校验。如有任何违规，脚本必须抛出异常并中止。

*   **Key 规则**: 必须包含至少一个字母（支持 `å, ä, ö`）。对于多词短语，允许包含空格，但不允许出现未解析的 PDF 碎片。
*   **Value 规则**:
    *   必须是非空字符串。
    *   **不得**包含软连字符 `\u00ad`。
    *   **不得**以 `(-` 或 `(+` 开头。
*   **唯一性**: 词典中不得存在重复的 Key（重复项必须合并或去重）。
*   **编码**: 所有文件必须以 **UTF-8** 格式保存。

## 7. 与其他阶段的接口 (Interfaces)

此处生成的输出 (`master_dictionary.json`) 是整个应用数据管道的枢纽。它将直接输送给：

*   **Phase 2 (文章生成)**: 向 AI 提供生成阅读材料必须使用的经验证的目标词汇表。
*   **Phase 3 (数据库导出)**: 为 SQLite 插入提供词根和翻译。
*   **Phase 4 (音频 TTS)**: 为生成 Edge TTS 音频提供精确的词列表。
*   **Phase 5 (前端组装)**: 转换为 `global_dict.js` 以支持 UI 的文本翻译提取功能。

## 8. Prompt 模板 (Prompt Templates)

使用以下 Prompt 模板驱动 LLM 执行修复与翻译任务。

### 8.1 缺陷修复 Prompt
```text
You are an expert Swedish to English translator. I have some corrupted entries from a Swedish vocabulary dictionary extracted from a PDF. Please repair them based on the context.

For truncated translations (indicated by '\u00ad' or similar), guess the full English translation. 
For grammatical info entries (e.g. "(-r, -de, -t)"), provide the actual English translation of the Swedish word.

Input JSON:
{
  "människa": "human being, per\u00ad",
  "sammanfatta": "(-r, -de, -t)"
}

Provide ONLY the repaired JSON as your response:
{
  "människa": "human being, person",
  "sammanfatta": "summarize"
}
```

### 8.2 批量翻译 Prompt
```text
You are an expert Swedish to English translator. Please translate the following list of Swedish vocabulary words into English. Provide concise translations suitable for a language learner's dictionary.

If a word has multiple common meanings, provide a short comma-separated list.
Input (List of Swedish words):
["soffpotatis", "träna", "att", "tro"]

Respond ONLY with a valid JSON object where the key is the Swedish word and the value is the English translation:
{
  "soffpotatis": "couch potato",
  "träna": "exercise, work out",
  "att": "to",
  "tro": "believe, think"
}
```

## 9. 错误处理 (Error Handling)

*   **AI 重试机制**: 如果 AI 返回非结构化格式（非 JSON）、超时、或翻译为空白（如 `""` 或 `null`），系统在报错前必须**最多重试 3 次**。
*   **日志记录 (Audit Trail)**:
    *   创建一个 `dictionary_cleaning.log` 文件。
    *   所有被规则 `3.1` 至 `3.4` 修改的条目必须将原始数据和修改后的数据追加写入日志。
    *   任何在 3 次重试后依旧无法翻译的单词必须在日志中标记为 `[ERROR_UNTRANSLATED]` 供人工干预。
