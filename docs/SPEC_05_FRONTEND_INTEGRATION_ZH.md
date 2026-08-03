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

Phase 2 生成的文章必须被组装成一个映射了 **Course -> Step -> Article** 层级结构的单一 JavaScript 对象。

**输出规范 (`data.js`):**
```javascript
// Auto-generated. DO NOT EDIT.
window.APP_DATA = {
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
          ]
        }
      ]
    }
  ]
};
```

## 3. 可打印 HTML 生成

为了满足提供物理学习资料的打印需求，流水线必须生成一个独立的 HTML 文件，包含所有格式化为适合 A4 打印的文章。

### 3.1 布局与排版要求

*   **打印目标**: A4 纸张 (`size: A4`)。
*   **分页**: 每篇文章**必须**使用 CSS `page-break-before: always;` 在新的物理页面上开始。
*   **排版**: 使用适合打印的易读字体（例如 Arial, Helvetica, sans-serif），字号至少为 12pt。
*   **视觉高亮**: 必须使用 JSON 中的 `position_start` 和 `position_end` 索引来包裹目标单词，使用 `<strong>` 或 `<mark>` 标签进行高亮。
    *   *示例*: `Min granne är en riktig <strong>soffpotatis</strong> som aldrig tränar.`
*   **翻译处理**: 英文翻译 (`en`) 应直接打印在瑞典语句子 (`sv`) 下方，使用较小、较浅的字体，或者采用左右对照的表格格式。
*   **元数据页眉**: 首页顶部应包含课程标题、级别 (SFI D / B1) 和生成日期。

### 3.2 HTML 输出路径
*   **文件路径**: `print/sfid_b1_articles.html`

### 3.3 CSS 打印样式示例
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

## 4. 执行步骤

1.  读取 `master_dict.json`。
2.  格式化为 Key-Value 键值对，并包裹在 `window.globalDictionary = ...` 中。
3.  写入到 `frontend/js/global_dict.js`。
4.  读取 `chapters/` 目录下的所有文章 JSON。
5.  将它们合并为嵌套的 `Course -> Step -> Article` 结构。
6.  包裹在 `window.APP_DATA = ...` 中。
7.  写入到 `frontend/js/data.js`。
8.  将文章 JSON 传递给 HTML 模板引擎（如 Jinja2 或自定义字符串插值），并写入 `print/sfid_b1_articles.html`。
