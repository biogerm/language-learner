# Phase 5: 前端数据组装与 HTML 打印

## 1. 概述

这最后一个阶段负责整理生成的数据，以供最终面向用户的系统使用：Web 应用程序和物理打印资料。

数据流水线提取 Phase 1 (主词典) 和 Phase 2 (文章 JSON) 的输出，生成静态 JavaScript 数据文件，供前端应用程序加载。同时，它还会获取生成的文章，并将其编译为一个专为 A4 纸张格式化设计的、可直接打印的 HTML 文件。

```mermaid
graph TD
    A[Phase 1: master_dict.json] --> C[前端组装器]
    B[Phase 2: Structured Articles] --> C
    C --> D[data.js (文章数据)]
    C --> E[global_dict.js (词汇数据)]
    B --> F[HTML 打印生成器]
    F --> G[sfid_b1_articles.html]
```

## 2. 前端数据接口

前端应用程序要求数据作为全局 JavaScript 变量注入。这允许静态前端在没有后端服务器的情况下运行。

### 2.1 词典接口 (`global_dict.js`)

`master_dict.json` 必须被扁平化为一个简单的键值对 (Key-Value) 存储。这为前端的“提取词汇 (Extract Vocab)”功能提供支持（特别是 `app.js` 的 200-464 行），该功能会查找用户高亮的单词并显示其翻译。

**输出规范 (`global_dict.js`):**
```javascript
// Auto-generated from master_dict.json. DO NOT EDIT.
window.globalDictionary = {
    "soffpotatis": "couch potato",
    "träna": "exercise, work out",
    "granne": "neighbor"
};
```

### 2.2 文章数据接口 (`data.js`)

Phase 2 生成的文章必须被组装成一个映射了 **Course -> Stage -> Article** 层级结构的单一 JavaScript 对象。

**输出规范 (`data.js`):**
```javascript
// Auto-generated. DO NOT EDIT.
window.APP_DATA = {
  "course_id": "sfid",
  "course_title": "SFI D",
  "stages": [
    {
      "stage_id": "stage_01",
      "stage_title": "Daily Life and Health",
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
          ]
        }
      ]
    }
  ]
};
```

### 2.3 听写题库接口 (`dictation_data.js`)

Phase 5 需要从 Phase 2 输出的所有文章中提取出带语境的 `target_words`，并生成供前端“听写模式”和“闪卡模式”使用的数据集。
为了在前端显示时既能展示语境释义，又能展示标准字典释义，该接口在生成时**必须**跨表联查主词典：

**组装逻辑:**
1. 遍历所有文章中的句子，提取所有的 `target_words`。
2. 提取其瑞典语原形 (`base_form`) 和语境翻译 (`contextual_en` 映射为 `en`)。
3. 拿着 `base_form` 去 `master_dict.json` 中查询标准的全局解释。
4. 将查到的全局解释作为新字段 `dictionary_en` 一并注入。
5. 前端 App 在显示时，应将 `dictionary_en` 用括号包裹显示在原本释义的旁边。

**输出规范 (`dictation_data.js`):**
```javascript
// Auto-generated from articles and master_dict.json. DO NOT EDIT.
window.DICTATION_WORDS = [
  {
    "sv": "gå",
    "en": "went",
    "dictionary_en": "go, walk",
    "context_sv": "Han gick hem.",
    "stage": "Daily Life and Health",
    "article": "En dag på gymmet",
    "course_id": "sfid"
  }
];
```

## 3. Web App UI 与 FSRS 逻辑

前端应用程序不仅需要加载 `data.js` 展示静态内容，还需要提供高度交互的阅读体验并集成 FSRS 间隔重复记忆算法。

### 3.1 学习队列与单词存储架构

为了确保间隔重复复习的质量以及数据生命周期的正确管理，系统必须实现**两个独立的数据存储**，并遵循严格的准入协议。

#### 存储 A：暂存学习队列（临时）
一个轻量级的数据存储，用作**进行中的学习队列**。单词在进入"初始学习队列"时被放入此处，在通过双重考核（双重准入门槛）后从此处删除。此存储处理 **Target Words（考点词）** 和 **Secondary Words（副词汇）** —— 这些词均已在主词典中有索引记录。

*   **Target Words（考点词）**：随文章加载自动进入存储 A，无需任何用户操作。
*   **Secondary Words（副词汇）/ 查词保存**：在阅读中，用户通过 📖 按钮查词并选中某个词点击"保存"后，该词才会进入存储 A。此时，系统必须通过以下方式组装词条记录：
    *   `contextual_en`（来自当前句子的 JSON）—— 语境精准翻译
    *   来自 `global_dict.js` 的全局字典翻译 —— 词语基础含义
    *   组合格式：`[语境精准翻译] ([主词典全局翻译])`（例如：`couch potato (someone who lies on the sofa, inactive)`）

**存储 A 的记录结构**（必须与主词典的数据结构保持一致，以便复习时能通过索引取得包括例句在内的所有信息）：

| 字段 | 来源 | 说明 |
|---|---|---|
| `base_form` | 句子 JSON | 主键 / 查找索引 |
| `word_type` | `word_metadata.json` | 动词、名词、形容词等 |
| `en_translation` | 组合（语境 + 全局） | 按上述格式组装 |
| `sv_context` | 句子 JSON（`sv` 字段） | 完整的瑞典语例句 |
| `sentence_audio_filename` | 句子 JSON | 仅文件名，不含路径 |
| `contextual_en` | 句子 JSON | 该词在本句中的精确翻译 |
| `source` | 文章元数据 | 该词来自哪篇文章 |

**双重准入门槛（删除规则）**：当一个词通过以下两项后，从存储 A 中删除：
- ✅ **听写模式**：100% 正确
- ✅ **翻译模式**：100% 正确

因为 Target Words 和 Secondary Words 在主词典中已有完整记录，通过双重考核后**不需要持久保存**——从存储 A 删除即可。

---

#### 存储 B：永久自定义词汇库（持久化）
一个永久性的长期数据存储，用于保存**用户自定义词汇** —— 即不在文章数据中出现、但用户仍希望学习的单词。此存储在通过双重准入后**永不清除**，相当于用户的个人词汇库（类似于 FSRS 记忆库）。

*   **触发条件**：用户可在任何时候手动添加单词（例如来自课外书、物理教材或日常对话）。
*   **需要用户输入**：由于系统无法从文章数据中推断释义，用户必须手动输入英文翻译。
*   **系统自动补全**：系统应尽量自动填充其余字段（例如，若该词存在于 SQLite 数据库中，则自动查询并填入 `word_type`、变形信息等）。无法自动解析的字段（如 `sv_context`、`sentence_audio_filename`）留空。

**存储 B 的记录结构**：

| 字段 | 来源 | 说明 |
|---|---|---|
| `base_form` | 用户输入 | 主键 |
| `en_translation` | 用户输入（必填） | 用户手动输入 |
| `word_type` | 自动从数据库查询 | 如在 SQLite 中存在则填充，否则留空 |
| `sv_context` | 自动从数据库查询 | 如在 SQLite 中存在则填充，否则留空 |
| `sentence_audio_filename` | 自动从数据库查询 | 如在 SQLite 中存在则填充，否则留空 |
| `notes` | 用户输入（选填） | 用户的自由文本笔记 |

**双重准入门槛（保留规则）**：即使存储 B 中的单词通过了双重考核验证，也必须**永久保留**。用户的自定义词汇库是个人资产，绝对不能被删除。

### 3.2 双端双语高亮渲染 (Bilingual Highlighting)
在阅读模式的 UI 层（例如 `renderSentences` 中），必须实现严丝合缝的中瑞双语对齐高亮：
*   **Target Words (考点词)**：
    *   **瑞典语侧 (sv)**：匹配 `word_in_sentence` 字段，进行醒目渲染（例如：**加粗+金色**）。
    *   **英语侧 (en)**：匹配大模型提取的 `contextual_en` 字符串，进行完全对应的同款渲染（**加粗+金色**）。
*   **Secondary Words (副词汇)**：
    *   **瑞典语侧 (sv)**：匹配 `word_in_sentence` 字段，进行次级渲染（例如：蓝色虚线下划线）。
    *   **英语侧 (en)**：匹配 `contextual_en` 字符串，进行对应的次级渲染（蓝色虚线下划线）。

这样学生在阅读时，视线在上下两行扫过，立刻就能将语境严丝合缝地对齐，极大提升双语对照学习的效率。

## 4. 可打印 HTML 生成

为了满足提供物理学习资料的打印需求，流水线必须生成一个独立的 HTML 文件，包含所有格式化为适合 A4 打印的文章。

### 4.1 布局与排版要求

*   **打印目标**: A4 纸张 (`size: A4`)。
*   **分页**: 每篇文章**必须**使用 CSS `page-break-before: always;` 在新的物理页面上开始。
*   **排版**: 使用适合打印的易读字体（例如 Arial, Helvetica, sans-serif），字号至少为 12pt。
*   **视觉高亮**: 必须使用 JSON 中的 `position_start` 和 `position_end` 索引来包裹目标单词，使用 `<strong>` 或 `<mark>` 标签进行高亮。
    *   *示例*: `Min granne är en riktig <strong>soffpotatis</strong> som aldrig tränar.`
*   **翻译处理**: 英文翻译 (`en`) 应直接打印在瑞典语句子 (`sv`) 下方，使用较小、较浅的字体，或者采用左右对照的表格格式。
*   **元数据页眉**: 首页顶部应包含课程标题、级别 (SFI D / B1) 和生成日期。

### 4.2 HTML 输出路径
*   **文件路径**: `print/sfid_b1_articles.html`

### 4.3 CSS 打印样式示例
生成器脚本必须将以下 CSS 块注入生成的 HTML 中：
```html
<style>
    @media print {
        @page { size: A4; margin: 20mm; }
        body { font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.5; }
        .article { page-break-before: always; }
        .article:first-child { page-break-before: avoid; }
        .sentence-sv { font-weight: normal; margin-bottom: 2px; }
        .target-word { font-weight: bold; text-decoration: underline; }
        .sentence-en { font-size: 10pt; color: #555; margin-bottom: 15px; font-style: italic; }
    }
</style>
```

## 5. 执行步骤

1.  读取 `master_dict.json`。
2.  格式化为 Key-Value 键值对，并包裹在 `window.globalDictionary = ...` 中。
3.  写入到外部应用目录 `<web_app_dir>/js/global_dict.js`。
4.  读取 `chapters/` 目录下的所有文章 JSON。
5.  将它们合并为嵌套的 `Course -> Stage -> Article` 结构。
6.  包裹在 `window.APP_DATA = ...` 中。
7.  写入到外部应用目录 `<web_app_dir>/js/data.js`。
8.  提取文章中的 `target_words` 并结合 `master_dict.json` 生成带 `dictionary_en` 字段的词汇数组。
9.  包裹在 `window.DICTATION_WORDS = ...` 中，并写入到 `<web_app_dir>/js/dictation_data.js`。
10. 将文章 JSON 传递给 HTML 模板引擎（如 Jinja2 或自定义字符串插值），并写入 `print/sfid_b1_articles.html`。
