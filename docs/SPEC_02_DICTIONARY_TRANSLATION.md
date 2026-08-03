# Phase 2: Dictionary & Complete Translation Generation (词典清洗与完整翻译生成)

## 1. 概述 (Overview)

本阶段 (Phase 2) 旨在确保从教科书 (Rivstart B1+B2) 提取的每个瑞典语词汇都有正确、完整的英文翻译。
原始从 PDF 提取的词汇文件 (JSON) 中存在因格式问题导致的脏数据（如软连字符截断、语法信息覆盖翻译、短语动词分裂等）。本阶段的数据管道将接收这些原始 JSON 文件，通过自动化清洗规则和 AI 修复与补全，最终生成一个干净、经过验证的 Master Dictionary，并输出供前端应用使用的 JavaScript 数据字典。

> [!NOTE]
> 词典数据的完整性对该语言学习应用至关重要。目前前端使用一个扁平的 JavaScript 对象 `globalDictionary` (`{ "word": "translation" }`)。应用内设的“提取词汇”模式 (Extract Vocab mode) 允许用户在文章中选取单词，系统将自动通过 `globalDictionary[word.toLowerCase()]` 查找并保存至个人生词本。

## 2. 输入规范 (Input Specification)

本阶段的数据源主要由从 PDF 导出的原始 JSON 文件组成。

*   **Primary Input (主要输入)**:
    *   `b1_ordlista.json`: B1 级别词汇列表（共 3,433 条目，约 30 个缺陷条目）
    *   `b2_ordlista.json`: B2 级别词汇列表（共 2,303 条目，约 36 个缺陷条目）
    *   `ok_b1_ordlista.json`: B1 级别补充词汇（46 个干净条目）
    *   `ok_b2_ordlista.json`: B2 级别补充词汇（32 个干净条目）
    *   `b1_extra.json`: B1 额外词汇（233 条目，原文和译文形式相同）
    *   `b2_extra.json`: B2 额外词汇（128 条目，原文和译文形式相同）

*   **Parameters (控制参数)**:
    *   `source_level` (String): 目标处理等级，可选项 `"B1"` 或 `"B2"`。
    *   `native_language` (String): 目标翻译语言。默认值: `"english"`。
    *   `include_extras` (Boolean): 是否包含 `extra.json` 系列文件中的单词。默认值: `false`。

## 3. 数据清洗规则 (Data Cleaning Rules)

必须按照以下特定规则对输入 JSON 文件进行遍历和缺陷修复。修复过程需保持日志记录，以便审计 (Audit Trail)。

### 3.1 软连字符截断修复 (Soft-Hyphen Truncation Fix)
*   **检测条件**: JSON 的 value 字符串中包含软连字符 `\u00ad`。
*   **处理逻辑**: 提取出被截断的 value，调用 AI 进行补全，并移除软连字符。
*   **示例**:
    *   输入: `"människa": "human being, per\u00ad"`
    *   修复输出: `"människa": "human being, person"`

### 3.2 语法信息替代修复 (Grammar Info Replacement Fix)
*   **检测条件**: JSON 的 value 字符串以 `(-` 或 `(+` 开头（这些是瑞典语的变位模式，而不是英文翻译）。
*   **处理逻辑**: 清除该错误的 value，将该 key 发送给 AI 重新获取准确的英文翻译。
*   **示例**:
    *   输入: `"sammanfatta": "(-r, -de, -t)"`
    *   修复输出: `"sammanfatta": "summarize"`

### 3.3 短语动词分裂修复 (Phrasal Verb Split Fix)
*   **检测条件**: JSON 的 value 仅为一个瑞典语的小品词 (Particle) 或介词（如 `på`, `av`, `ut`, `upp` 等）。
*   **处理逻辑**: 将原本的 key 和该 value 合并为一个完整的短语动词 (Phrasal Verb) 作为新的 key，并删除原有词条。然后使用 AI 为合并后的新短语动词生成对应的英文翻译。
*   **示例**:
    *   输入: `"stöta": "på"`
    *   修复输出: `"stöta på": "run into, encounter"`

### 3.4 换行孤儿条目清除 (Line-Wrap Orphan Cleanup)
*   **检测条件**: JSON 的 key 仅包含英文字符（无瑞典语特殊字符如 `å, ä, ö`）**且** 长度非常短（通常 `< 5` 个字符）。这类条目通常是 PDF 跨行识别导致的碎片。
*   **处理逻辑**: 将此类匹配的条目完全删除。
*   **示例**:
    *   检测到: `"ne": "well known in the arts"`, `"ty": "flower"`, `"me": "my jacket?"`
    *   处理: 从数据集中永久移除。

## 4. 翻译补全规则 (Translation Completion)

在执行完所有清洗规则后，必须遍历词典执行全面检查，确保每个有效单词都有合法的英文翻译。
*   **处理逻辑**:
    1.  收集所有 value 为空字符串 (`""`)、`null`、或经上一步判断为无效需要重翻的单词。
    2.  利用 AI 进行**批量翻译 (Batch Translation)**。为防止达到 API 上限，按每批 50 个瑞典语单词 (Batch of 50) 将词汇发给 AI。
    3.  强制 AI 以 JSON 格式返回结果：`{ "word": "translation" }`。
    4.  验证返回数据，确保所有请求的词均获得了非空翻译。

## 5. 输出规范 (Output Specification)

清洗和补全完成后，系统应输出两个核心文件：

### 5.1 Master Dictionary JSON (`master_dictionary.json`)
此文件是持久化的基础数据，包含结构化的元数据与词汇详情，供后端处理。

```json
{
  "metadata": {
    "level": "B1",
    "source": "rivstart_b1_b2",
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
> 这里的 `word_class` 和 `gender` 在本阶段如无法完全通过 AI 或规则确定，可设为 `null` 并在后续阶段完善，但 `en` (翻译) 字段必须包含非空字符串。

### 5.2 Frontend `globalDictionary` JS (`globalDictionary.js`)
此文件将直接加载到前端，必须严格匹配现有的数据结构。

```javascript
const globalDictionary = {
  "soffpotatis": "couch potato",
  "träna": "exercise, work out",
  // ... more entries ...
};
```

## 6. 校验规则 (Validation Rules)

在输出最终文件之前，执行数据校验。如有任何违规，脚本需抛出异常并中止执行，防止脏数据流入。

*   **Key 规则**: 必须包含至少一个字母（支持瑞典语特有字母 `å, ä, ö`）。对于多词短语 (Multi-word phrase)，允许包含空格，但不允许出现未解析的 PDF 碎片。
*   **Value 规则**:
    *   必须是非空字符串。
    *   **不得**包含软连字符 `\u00ad`。
    *   **不得**以 `(-` 或 `(+` 开头。
*   **唯一性**: 词典中不得存在重复的 Key（重复项必须合并或去重）。
*   **编码格式**: 所有文件必须以 **UTF-8** 格式保存。

## 7. 与其他阶段的接口 (Interfaces with Other Phases)

本阶段生成的输出 (Master Dictionary) 是整个应用数据管道的核心枢纽，它将喂给以下后续阶段：

*   **SPEC_01 (Article Generation)**: 向文章生成模块提供可用的瑞典语目标词汇表。
*   **SPEC_03 (Audio TTS)**: 为单词提供用于生成 Edge TTS 发音音频的精确词列表。
*   **SPEC_04 (Frontend Integration)**: 提供 `globalDictionary.js`，支撑用户界面的文本翻译提取功能。

## 8. Prompt 模板 (Prompt Templates)

使用以下 Prompt 模板驱动大语言模型执行修复与翻译任务。

### 8.1 缺陷修复 Prompt (AI Defect Repair Prompt)
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

### 8.2 批量翻译 Prompt (AI Batch Translation Prompt)
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

*   **AI 重试机制**: 如果 AI 批量翻译或缺陷修复的接口返回了非结构化格式（非 JSON）、发生网络超时、或有 key 对应的翻译依然为空白（如 `""` 或 `null`），系统应在报错前**最多重试 3 次** (Retry up to 3 times)。
*   **日志记录 (Audit Trail)**:
    *   创建一个 `dictionary_cleaning.log` 文件。
    *   所有被 `3.1` ~ `3.4` 清洗规则命中并修改的条目，必须将原数据与修改后的数据追加写入日志中。
    *   任何在 3 次重试后依旧无法翻译的单词必须在日志中标记为 `[ERROR_UNTRANSLATED]` 供人工干预。
