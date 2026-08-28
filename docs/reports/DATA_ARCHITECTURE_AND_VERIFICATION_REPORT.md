# Language Learner 数据架构与验证报告

## 📝 文档背景 (Context)

**生成时间**：2026年8月22日
**目的**：此文档生成于项目云端同步 (Cloud Sync) 架构确立并实施后。为了确保从 Python 数据流水线（Pipeline）到云端数据库（Supabase），再到本地离线存储（IndexedDB）的全链路数据 100% 准确流转，开发者运行了一系列真实数据验证脚本（Read-only 探伤探测）。
**读者受众**：未来的项目维护者、新加入的开发人员，或需要了解“数据是如何在系统中产生、存储、同步和消耗”的任何人。
**前置背景**：项目采用了“Local-First”架构，浏览器内的 Dexie IndexedDB 是应用唯一的事实来源（Single Source of Truth），通过 Supabase 实现跨设备的增量后台同步，所有多媒体资源托管在 Cloudflare R2。

---

## 一、 数据现状澄清

系统中的数据**绝大部分已经真实产生，并且真正在系统中流转**。

*   **Pipeline 输出文件（Layer 1）**：`course_sfid_articles.json` 和 `course_sfid_vocab.json` 真实存在于 `course/sfid/phase5/output/` 及其对应的前端 `dist` / `public` 文件夹中。同时，本地实际生成了 1751 个句子音频和 5953 个单词音频。
*   **Supabase 云端数据（Layer 2）**：表已经建好，且**存在真实的测试用户数据**。通过后台 Service Key 绕过 RLS 权限墙，查到了 32 条真实的 `fsrs_progress` 进度记录和 2 条 `custom_dictionary` 用户自定义生词记录。

---

## 二、 详尽的数据验证统计报告 (基于真实脚本运行结果)

通过自动化脚本对全系统数据进行了探伤扫描，结果非常乐观。

### 1. Layer 1 (Pipeline 产出的静态 JSON 数据) 验证报告

脚本遍历了字典中的每一个单词，去它关联的句子原文中根据 `position_start` / `position_end` 坐标“扣”出对应字符串，进行绝对相等的交叉查验。

*   **总校验词汇量**：6,365 个
*   **孤立词汇错误**（找不到所属句子）：**0** 个
*   **匹配落空错误**（句子里没这个词）：**0** 个
*   **坐标切分不匹配错误**：**28** 个
*   **最终数据准确率**：**(6365 - 28) / 6365 = 99.56%** ✅ (已达到 99% 的工程健康度标准)

**🚨 问题原因分析（The 28 Errors）**
这 28 个报错**全部都是大小写不匹配导致的**。
*举例*：在句子 `art_52_s008` 中，切分出来的字符串是大写的 `"Farbror"`，但是在 JSON 的 `word_in_sentence` 字段中存的却是小写的 `"farbror"`。
*根本原因*：Python 数据流水线（Phase 2 或 Phase 5）在处理句首单词时，强行将其 `.lower()` 转成了小写，导致坐标截取出的原文无法与 JSON 中的属性 100% 绝对等于（===）。

### 2. Layer 2 (Supabase 云端数据) 验证报告

拉取了目前数据库里的所有进度记录，并进行了约束查错。

*   **`fsrs_progress` 表**：共扫描 32 条记录。
    *   状态越界 (`state` 不属于 0,1,2,3)？ -> **0** 条
    *   逻辑异常 (复习次数 `reps` / `lapses` 为负数)？ -> **0** 条
    *   穿越未来 (上次复习时间晚于当前时间)？ -> **0** 条
*   **`custom_dictionary` 表**：共扫描 2 条记录。
    *   空指针或脏数据？ -> **0** 条
*   **最终云端数据健康度**：**100%** ✅

---

## 三、 全链路数据变换与业务代码承接情况（Data Flow Trace）

数据从 JSON 进入浏览器后的关键变化，代码承接高度符合设计预期，并且包含了极佳的容错设计。

### 1. 28 个大小写错误会搞崩 UI 吗？
**结论：完全不会。**
`pages/Narration.tsx` 中使用的 `localParseSentence` 解析逻辑非常鲁棒：当它尝试根据 `position_start` / `position_end` 去高亮单词，如果发生了不匹配（比如大小写问题），它不会报错崩溃，而是**自动降级 (Fallback) 到正则模糊匹配（Regex Match）**。它会按单词长度从长到短排序，逐个在原文中进行正则替换。这不仅兜底了那 28 个大小写错误，还完美保证了业务预期的呈现效果。

### 2. 数据是如何变成“队列”的？(临时学习队列的生命周期)
数据流向：`course_sfid_vocab.json` -> Dexie `course_data` (缓存) -> **Dexie `learning_queue` (学习队列)**。
这里业务逻辑执行得非常严密。每当用户点击某篇文章，系统会调用 `syncStoreA`：
*   如果单词已经通过了今天的“听写”和“闪卡”双重门 -> 剔除。
*   如果单词存在于 Custom Dictionary（自定义生词本）中 -> 剔除（防竞态条件）。
剩下的才会塞进队列供今天学习。用户在 UI 上的操作，真实精准地反映在了这几个数据集的此消彼长中。

### 3. FSRS 双重门 (Dual-Gate) 逻辑是否到位？
**结论：精准到位。**
在 `submitGatePass` 函数中，必须 `todayDictationPassed == true` 且 `todayFlashcardPassed == true` 才会真正调用 `fsrs.repeat()` 计算新的间隔，并将其推送到 Supabase。否则只会在本地保留单次打卡记录。

### 4. Custom Dictionary (自定义生词本) 到底同步了吗？
`DataContext.tsx` 中的 `addToStoreB` 函数**确实包含了向 Supabase `custom_dictionary` 表写入的逻辑**。
逻辑是：乐观 UI 先更新 Dexie（此时打上 `synced: false` 标记），然后在后台静默发起 Supabase `.insert()` 操作。成功后刷新同步标记。这与后来在 Supabase 中查到的真实数据完全吻合。

---

## 四、 全系统数据结构详表

以下是系统使用的真实数据结构（包含静态文件、云端、本地）：

### 1. 静态分发文件 (Cloudflare R2 JSON)

| 文件名 / 路径 | 核心字段结构 | 说明 |
|---|---|---|
| `course_sfid_articles.json` | `stages[]` -> `articles[]` -> `sentences[]` <br> `sentence` = `{ id, sv, en, target_words[], secondary_words[] }` | 4层树状结构，供 Narration 页面渲染。词汇对象内仅含 `position_start` / `position_end`。 |
| `course_sfid_vocab.json` | 扁平对象数组: `{ base_form, word_in_sentence, en_translation, contextual_en, stage_id, article_id, sentence_id }` | **Universal Word Object**，包含所有翻译和溯源坐标，是学习队列的母体。 |

### 2. 云端关系型数据库 (Supabase PostgreSQL)

| 表名 | 列结构 (Columns) | RLS 安全策略 | 用途 |
|---|---|---|---|
| `courses` | `id` (PK), `title`, `description`, `r2_base_url`, `r2_json_url`, `r2_vocab_url`, `created_at` | 全员只读 | 课程元信息注册中心 |
| `fsrs_progress` | `id` (PK), `user_id` (FK), `course_id` (FK), `word_id`, `state`, `due`, `stability`, `difficulty`, `elapsed_days`, `scheduled_days`, `reps`, `lapses`, `last_review`, `updated_at` | 仅用户自身可增删改查 | FSRS 算法进度，用于跨设备同步 |
| `custom_dictionary` | `id` (PK), `user_id` (FK), `base_form`, `word_in_sentence`, `en_translation`, `contextual_en`, `stage_id`, `article_id`, `sentence_id`, `created_at`, `updated_at` | 仅用户自身可增删改查 | 云端自定义生词本 |

### 3. 本地缓存数据库 (浏览器 IndexedDB / Dexie)

| 表名 (Dexie Table) | 索引 / 主键 | 核心字段扩展 (相对于云端/JSON) | 生命周期与用途 |
|---|---|---|---|
| `course_data` | `courseId` | `{ courseId, dictionary, articles }` | **本地缓存**：只在首次拉取 R2 时写入，永不过期 |
| `fsrs_progress` | `word_id` | 额外带有本地专属字段：`synced`, `sync_error`, `todayDictationPassed`, `todayFlashcardPassed`, `max_wrongs`, `max_time`, `gave_up`, `reveal_count`, `lastGatePassDate` | **本地核心**：包含打卡过程中的暂存状态（Dual-Gate） |
| `learning_queue` | `++id`, `article_id`, `base_form` | 与 Universal Word Object 完全一致 | **临时队列**：用户进入文章时按需生成，过关即销毁 |
| `custom_dictionary`| `++id`, `base_form` | 与 Universal Word Object 一致，额外增加 `synced` 标记 | **持久存储**：本地优先写入，后台静默同步给 Supabase |
| `courses` | `id, title` | `{ id, title, content }` | 本地轻量化课程列表缓存 |

---

## 五、 后续改进实施记录

本报告生成后，立即执行了以下两次重构，以追求 100% 的工程卓越：

**Phase A：修复 Python Pipeline 大小写抹除问题**
- 修复了 Python 生成脚本，确保 `word_in_sentence` 字段**原封不动**地保留它在句子中出现的原本大小写状态（避免句首单词被意外 `.lower()`）。

**Phase B：统一数据命名规范与加固云端同步**
- **统一命名**：将本地 `store_b_items` 重命名为 `custom_dictionary`；将 `store_a_queue` 重命名为 `learning_queue`。
- **重试机制**：为 Custom Dictionary 添加了离线转在线时的重试钩子。
- **合并冲突**：拉取云端 Custom Dictionary 时，改为了基于 `base_form` 的 Upsert 逻辑，避免覆盖离线写入的数据。
