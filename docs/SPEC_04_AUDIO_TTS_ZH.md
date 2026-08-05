# Phase 4: 音频 TTS 生成与校验

## 1. 概述
Phase 4 的核心目标是为所有生成的句子和独立单词生成 MP3 发音音频，并对其质量进行严格校验。

为了满足 SFI 学习者的需求，音频使用 Microsoft Edge TTS API 生成，语速降低 20% 以适应学习节奏。
此外，本阶段引入了基于 OpenAI Whisper 的自动语音识别 (ASR) 闭环校验机制。这确保了发音的准确性，并防止因网络超时或静音生成 Bug 导致流水线输出损坏的文件。

## 2. 输入规范

- **来自 Phase 2 的输入**: 包含所有句子的文章 JSON 文件。每个句子必须具有 `id` 和 `sv` (瑞典语文本) 字段。
- **来自 Phase 1 的输入**: 包含所有独立单词的 `master_dict.json` (使用 `base_form` 键)。
- **参数**:
  - `voices`: TTS 语音池 (默认: `["sv-SE-SofieNeural", "sv-SE-MattiasNeural"]`，即一女一男)
  - `rate`: 语速调整 (默认: `-20%`)
  - `output_format`: 音频格式 (默认: `mp3`)
  - `max_concurrent`: 最大并发请求数 (默认: 10)
  - `retry_count`: 失败请求的重试次数 (默认: 5)
  - `min_file_size_bytes`: 最小有效 MP3 文件大小 (默认: 1024 字节)
  - `whisper_model`: 用于校验的 Whisper 模型 (默认: `base`)
  - `verification_threshold`: TTS 校验的最低相似度分数 (默认: 0.85)

## 3. TTS 生成管线

### 3.1 任务拆分
- **句子音频任务**: 从 Phase 2 的 JSON 文件中提取所有唯一的句子。
- **单词音频任务**: 从 Phase 1 词典中提取所有唯一的 `base_form` 条目。
- **去重**: 在不同章节中多次出现的单词和句子只生成一次并共享。
- **男女声交替 (Voice Alternation)**: 生成句子或单词音频时，必须在提供的语音池（男声和女声）中进行交替轮换。例如：句子 1 使用女声，句子 2 使用男声，句子 3 使用女声...；单词生成同理（词 1 女，词 2 男）。这对于防止学习者产生听觉疲劳、适应不同性别口音至关重要。

### 3.2 并发
- 使用 Python 的 `asyncio` 和 `edge-tts` 库实现高并发生成。
- 将并发数限制在 `max_concurrent` 以防止触发 Edge API 的速率限制。
- 每个子任务的流程: 调用 Edge TTS API -> 保存为 MP3 文件。

### 3.3 文件命名规范
- 句子音频: `sentences_audio/{sentence_id}.mp3` (例如, `sentences_audio/art01_s001.mp3`)
- 单词音频: `words_audio/{base_form}.mp3` (例如, `words_audio/soffpotatis.mp3`)
- 所有文件名必须**小写**，空格替换为下划线 `_`。
- 瑞典语特殊字符 (å, ä, ö) 必须保留在文件名中；不要降级为 ASCII。

### 3.4 质量检查
每次生成后执行基本检查:
1. **文件存在性**: 确认文件已保存到正确路径。
2. **文件大小**: 检查文件大小是否 `>= min_file_size_bytes` (1KB)，以防空文件或损坏文件。
3. **音频时长 (可选)**: 拒绝短于 0.3 秒的音频文件。
- 未通过这些检查的文件自动触发重试 (最高 `retry_count` 次)。
- 如果重试次数用尽，记录错误并跳至下一个任务。

## 4. 语音识别 (ASR) 校验
引入 ASR 机制对生成的音频进行闭环验证，确保 TTS 引擎确实正确发音了预期文本。

### 4.1 校验流程
1. 加载生成的 MP3 文件。
2. 将其输入 Whisper (或 Azure Speech-to-Text) 提取文本记录。
3. **标准化**: 将原始文本和生成的文本记录全部转为小写，并去除所有标点符号和多余空格。
4. 计算 **Levenshtein 距离 (字符级)** 或 **词错率 (WER)**。
5. 计算相似度分数: `similarity score = 1 - (edit_distance / max_length)`。

### 4.2 决策规则
- **通过 (PASS)**: 如果 `similarity >= verification_threshold` (默认 0.85)。
- **失败 (FAIL)**: 如果 `similarity < verification_threshold`，标记为失败并触发重新生成。
- **标记 (FLAG)**: 如果 3 次重新生成循环后相似度仍低于阈值，将音频标记为人工审查。

### 4.3 特殊处理
- **单字音频**: 对于独立单词，在标准化后强制要求**精确匹配**，而不是使用编辑距离。
- **数字**: 如果句子中包含数字，在比较之前将数字标准化为其拼写出的文本形式。
- **专有名词**: 如果已知 Whisper 经常误认某些专有名词，将其从比较文本中排除。

## 5. 输出规范

### 5.1 音频文件
- **目录**: `sentences_audio/` 和 `words_audio/`。
- **格式**: MP3, 单声道 (Mono), 24kHz 采样率。

### 5.2 音频清单 JSON (Audio Manifest)
在运行结束时，必须生成一个 `audio_manifest.json` 供前端和后端状态追踪。
```json
{
  "metadata": {
    "generated_at": "2025-01-01T00:00:00Z",
    "voices": ["sv-SE-SofieNeural", "sv-SE-MattiasNeural"],
    "rate": "-20%",
    "total_sentence_files": 500,
    "total_word_files": 3433
  },
  "sentences": {
    "art01_s001": {
      "file": "sentences_audio/art01_s001.mp3",
      "duration_ms": 3200,
      "verification_score": 0.95,
      "status": "verified"
    }
  },
  "words": {
    "soffpotatis": {
      "file": "words_audio/soffpotatis.mp3",
      "duration_ms": 1100,
      "verification_score": 1.0,
      "status": "verified"
    }
  }
}
```

## 6. 校验规则
1. Phase 2 JSONs 中引用的每个 `sentence` 必须在 `sentences_audio/` 中有对应的 MP3。
2. Master Dictionary 中引用的每个 `base_form` 必须在 `words_audio/` 中有对应的 MP3。
3. 所有音频文件必须通过 `min_file_size_bytes` 检查。
4. 至少 **95%** 的音频文件必须通过 ASR 校验。
5. 剩余 <= 5% 未经验证的文件必须在清单中明确记录为 "flagged" 状态，以供人工检查。

## 7. 脚本与片段

> [!NOTE]
> 这一阶段完全由 API/脚本驱动。不需要 LLM 推理提示词 (Prompt)。

**Edge TTS CLI 参考:**
```bash
# Word Audio
edge-tts --text "soffpotatis" --voice "sv-SE-MattiasNeural" --rate="-20%" --write-media "words_audio/soffpotatis.mp3"

# Sentence Audio
edge-tts --text "Det är en fin dag idag." --voice "sv-SE-SofieNeural" --rate="-20%" --write-media "sentences_audio/art01_s001.mp3"
```

**Whisper 校验片段 (Python):**
```python
import whisper
import Levenshtein

def verify_audio(file_path, original_text, threshold=0.85):
    model = whisper.load_model("base")
    # 强制指定瑞典语
    result = model.transcribe(file_path, language="sv")
    
    transcript = result["text"].lower().strip()
    target_text = original_text.lower().strip()
    
    # 简单清理
    transcript = "".join([c for c in transcript if c.isalnum() or c.isspace()])
    target_text = "".join([c for c in target_text if c.isalnum() or c.isspace()])
    
    distance = Levenshtein.distance(target_text, transcript)
    max_len = max(len(target_text), len(transcript))
    
    if max_len == 0:
        return 0.0
        
    similarity = 1 - (distance / max_len)
    return similarity
```

## 8. 错误处理

- **网络超时**: Edge TTS API 可能停止响应。使用指数退避 (exponential backoff) 策略进行重试。
- **速率限制 (Rate limiting)**: 如果发生 429 错误，暂停执行 (冷却) 几秒钟，并在恢复前减少并发池。
- **损坏的音频**: 如果文件太小或无法被音频库读取，立即将其删除并重试生成。
- **Whisper 不可用**: 如果本地 Whisper 模型加载失败或内存溢出 (OOM)，记录 Warning，跳过 ASR 校验阶段，但继续保存生成的 MP3，以确保流水线不会彻底崩溃。
