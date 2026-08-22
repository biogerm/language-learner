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

## 2. 前端数据接口 (Abstract Datasets)

为了确保前端应用与特定的后端技术解耦，并且可以部署在任何地方（本地、云端或移动端 App），Phase 5 的输出必须是纯粹的、抽象的 JSON 数据集。**绝对不允许出现硬编码的 `.js` 变量注入。**

### 2.1 静态文章数据集 (Static Article Dataset)
必须将 Phase 2 生成的文章组装成单个 JSON 数据集，精确反映 **课程 (Course) -> 阶段 (Stage) -> 文章 (Article)** 的层级结构。

**输出规范 (`course_sfid_articles.json`):**
```json
{
  "course_id": "sfid",
  "course_title": "SFI D",
  "stages": [
    {
      "stage_id": "stage_01",
      "stage_title": "Daily Life and Health",
      "articles": [
        {
          "article_id": "art01",
          "article_title": "En dag på gymmet",
          "sentences": [
            {
              "sentence_id": "art01_s001",
              "sv": "Min granne är en riktig soffpotatis som aldrig tränar.",
              "en": "My neighbor is a real couch potato who never exercises.",
              "target_words": [
                {
                  "word_in_sentence": "soffpotatis",
                  "base_form": "soffpotatis",
                  "contextual_en": "couch potato",
                  "position_start": 25,
                  "position_end": 36
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### 2.2 静态语境词汇全集 (Static Contextual Vocabulary Dataset)
Phase 5 必须从所有文章中提取出所有的 `target_words` 和 `secondary_words`，将其与 `master_dictionary.json` 中的翻译进行合并，最终输出一个统一的、扁平化的 **Word Objects** 数组。这个数据集将作为前端学习队列预先编译好的“弹药库”。

**通用 `Word Object` 结构：**
这是贯穿整个前端生态系统的最小原子数据单元。
```json
[
  {
    "base_form": "springa",
    "word_in_sentence": "sprang",
    "en_translation": "run",
    "contextual_en": "ran",
    "stage_id": "stage_01",
    "article_id": "art01",
    "sentence_id": "art01_s001"
  }
]
```

**字段说明 (Field Descriptions)：**

| 字段 | 来源 | 说明 |
|---|---|---|
| `base_form` | 主词典 & Phase 2 | 字典里的原形（主键）。 |
| `word_in_sentence`| Phase 2 文章 | 该词在文中实际使用的确切变形形式。 |
| `en_translation` | 主词典 | 字典里的全局基础翻译。 |
| `contextual_en` | Phase 2 文章 | 该词在当前句子中的精准语境翻译。 |
| `stage_id` | Phase 5 组装器 | 级联索引 1 (例如 `stage_01`)。 |
| `article_id` | Phase 5 组装器 | 级联索引 2 (例如 `art01`)。 |
| `sentence_id` | Phase 5 组装器 | 级联索引 3 (例如 `art01_s001`)。 |

*(输出文件: `course_sfid_vocab.json`)*

## 3. Web App UI 与 FSRS 逻辑

前端 Web 应用将处理这些抽象的 JSON 数据集，以提供交互式阅读体验并与间隔重复系统 (FSRS) 进行整合。

### 3.1 学习队列与单词存储架构

为了保证高质量的间隔重复和正确的数据生命周期管理，系统实现了**两个独立的数据存储库 (Stores)**。这两个库都必须严格使用上述的 8 字段 **通用 Word Object** 结构。

#### Store A: 临时学习队列 (Temporary Learning Queue)
这是一个轻量级的数据库，用作**进行中的学习队列**。当用户开始学习某篇文章时，单词进入此队列；一旦该单词被完全掌握（通过双重阈值测试），它就会被**永久删除**。

*   **数据来源**: 当学习会话开始时，前端直接从“静态语境词汇全集”中，将属于该文章的、已经完全填充完毕的 `Word Objects` **复制 (COPY)** 进 Store A。
*   **双重阈值（移除规则）**: 当单词同时通过以下两项测试后，将从 Store A 中被剔除：
    *   ✅ **听写模式 (Dictation)**: 100% 正确
    *   ✅ **闪卡翻译模式 (Flashcard)**: 100% 正确

#### Store B: 永久自定义词汇库 (Permanent Custom Vocabulary)
这是一个永久性的数据存储库，用于存放**用户自定义的单词**——也就是那些不在课程大纲内，但用户手动高亮或添加的单词。这个库在单词被掌握后**永远不会被清空**。

*   **数据来源**: 由用户手动实例化。前端会创建一个全新的 `Word Object`。
*   **字段填充规则**:
    *   `base_form` 和 `word_in_sentence` 被设为用户点击的确切字符串（因为这里没有大模型来推断字典原形）。
    *   `en_translation` 必须由用户手动输入。
    *   `contextual_en` 设为 `null`（系统无法推断）。
    *   如果是在阅读某篇文章时添加的单词，那么 3 层 ID（`stage_id`, `article_id`, `sentence_id`）会自动根据上下文填充。否则它们将保持为空 (`null`)。

### 3.2 UI 渲染与测试逻辑 (唯一事实源)
由于 Store A、Store B 和静态词汇数据集使用的都是完全一样的 `Word Object` 结构，前端的 UI 逻辑得到了彻底的统一：
1.  **测试 (听写/闪卡)**: 评判答案是否正确的唯一标准就是匹配 `word_in_sentence` 字段。
2.  **释义显示**: UI 优先显示 `contextual_en`。如果它为空（例如在 Store B 中），则回退显示全局的 `en_translation`。
3.  **高亮与挖空**: 前端利用 `Word Object` 里的 3 层 ID (`stage_id`, `article_id`, `sentence_id`) 去动态查询 **静态文章数据集**。从而获取到 `sentenceData`，里面包含了 `sv` 原句以及用于精确高亮的 `position_start` / `position_end` 坐标。`Word Object` 本身**绝对不存储**坐标，彻底消除了数据冗余。

## 4. 可打印 HTML 生成

为了满足提供可打印纸质学习材料的需求，管线必须生成一个包含所有文章、排版为 A4 打印格式的独立 HTML 文件。

### 4.1 布局与排版要求

*   **打印目标**: A4 纸张 (`size: A4`)。
*   **分页**: 每篇文章**必须**使用 CSS `page-break-before: always;` 在新的物理页面上开始。
*   **排版**: 使用适合打印的易读字体（例如 Arial, Helvetica, sans-serif），字号至少为 12pt。
*   **视觉高亮**: 必须使用 JSON 中的 `position_start` 和 `position_end` 索引来包裹目标单词，使用 `<strong>` 或 `<mark>` 标签进行高亮。
    *   *示例*: `Min granne är en riktig <strong>soffpotatis</strong> som aldrig tränar.`
*   **翻译处理**: 英文翻译 (`en`) 应直接打印在瑞典语句子 (`sv`) 下方，使用较小、较浅的字体，或者采用左右对照的表格格式。
*   **元数据页眉**: 首页顶部应包含课程标题、级别 (SFI D / B1) 和生成日期。

### 4.2 HTML 输出路径
*   **文件路径**: `output/print/sfid_b1_articles.html`

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

1.  读取 Phase 1 的 `master_dictionary.json`。
2.  读取 Phase 2 的所有文章 JSON (`chapters/*.json`)。
3.  将具有层级结构的文章组装成 `course_sfid_articles.json` (静态文章数据集)。
4.  遍历所有句子，提取 `target_words` 和 `secondary_words`。
5.  与 `master_dictionary.json` 交叉比对，拼装出字段饱满的 `Word Objects`。
6.  将这些 Word Objects 的扁平化数组输出至 `course_sfid_vocab.json` (静态语境词汇全集)。
7.  将文章 JSON 传递给 HTML 模板引擎，输出 `output/print/sfid_b1_articles.html`。
