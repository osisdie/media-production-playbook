# Voice production — 本機 ASR、TTS、聲音 clone 與評估

> 在 CPU-only 的機器（例如 WSL2 8 vCPU、23 GB RAM、沒有 NVIDIA GPU）上做語音辨識、合成旁白、聲音 clone，以及模型評估。範例預設用 Kokoro（不 clone 任何人）；clone 是選用流程，**只能用取得同意的聲音**（見 [`../consent/voice-consent-template.md`](../consent/voice-consent-template.md)）。

## Principles — 原則

- **地端優先**：慢可以（用預先合成或緩衝解決），但要自然；不行才考慮雲端。雲端 TTS 的金鑰只從環境變數讀。
- **先客觀、後主觀**：RTF、CER、聲紋相似度先刷掉明顯不行的候選；盲聽只留給機器量不出來的（自然度、口音、像不像）。
- **權重只用官方來源**，固定 revision，必要時自己轉格式；下載來的 pickle 不直接執行（用 `torch.load(weights_only=True)` 讀出來再重存）。
- **重運算一次只跑一個**：ASR、TTS、render 同時跑，RTF 直接翻倍，量到的數字也不能用。

## Engines — 引擎選擇（實測過的）

| 用途 | 引擎 | 說明 |
|---|---|---|
| 範例旁白（不 clone） | **Kokoro-82M**（Apache-2.0） | 非自回歸，結果穩定可重現；有英文與中文的男女聲；CPU 很快。本 repo 範例都用它 |
| 華語聲音 clone | **GPT-SoVITS v2ProPlus** | CPU 上 RTF 約 2.5；參考音 3–10 秒；自回歸，偶爾拖音／重複 → 一定要跑 [narration QA](narration-qa.md) |
| 台灣華語合成、clone 對照 | BreezyVoice（Apache-2.0） | 台灣腔與用字通常最準；CPU RTF 約 12–22（依硬體與句長），只適合預先合成 |
| 台語 TTS（研究預覽） | GPT-SoVITS-tw 系列 fork | 只吃 POJ／Tâi-lô；一定要 ref-free；長句會飄 → 詳見 [Taiwanese (Taigi)](taiwanese-taigi.md) |
| 台語 ASR | Breeze-ASR-26（Whisper 微調，CT2 int8） | 台語語音 → 華語漢字；一律 `language="zh"` → 詳見 [Taiwanese (Taigi)](taiwanese-taigi.md) |
| 華語＋中英夾雜 ASR | Breeze-ASR-25（Whisper 微調，CT2 int8） | 直接輸出繁體；beam 1 比 beam 5 快 1.8 倍、準確度幾乎不變 |
| 跨語言 ASR（範例 QA） | faster-whisper small | 輕量、Mac/Linux 都能跑；對中文的絕對準確度較低，適合「有沒有漏字、拖音」這類檢查 |

### Kokoro 的坑（本 repo 範例實際遇到的）
- **字典沒有的英文詞**（虛構品牌名）會退回 espeak 拼音，常念歪（「Verdalo」→「Vertilow」）。TTS 文字改用重音拼法（`Ver-dah-lo`），畫面字幕照原寫法；QA 時在該句加 `"qa_text"`，比對時用正確寫法，不用拼法。
- **中文版念外語品牌名**：直接換成中文音譯念（例如「維達洛」），字幕仍顯示原名。
- **中文聲線夾英文字**：misaki 的中文 G2P 在 Kokoro v1.0 模型上不會呼叫英文 G2P，英文字母會被當成原始音素送進模型（「Verdalo」念成一串怪音，改拼法也沒用）。`kokoro_synth.py` 遇到含英文字的中文句，會把英文段交給英文 G2P；要指定念法，在 `tts` 加 `"lexicon": {"Verdalo": "vɜɹdˈɑlO"}`（音素用 misaki 的符號）。純中文句不受影響，也不會重新合成。想要英文念法時用這招，比中文音譯更貼近原名。
- **破音字**：「乾淨」的「乾」被念成 qián、「接著」的「著」被念成 zhù → 換詞（「清爽」、「然後」），不要硬調音訊。
- ASR 輸出簡體、稿子是繁體時，比對前兩邊都轉成簡體（`textnorm.py` 已處理，需要 `opencc-python-reimplemented`）。
- Kokoro 是確定性的：同一段文字每次結果一樣，所以沒有「多抽幾個 seed」這招，只能改寫文字或調 `speed`。

### GPT-SoVITS 參數

```python
from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config
tts = TTS(TTS_Config({"custom": dict(TTS_Config.default_configs["v2ProPlus"], device="cpu", is_half=False)}))
tts.run({"text": text, "text_lang": "zh",           # zh = 華語可夾英文
         "ref_audio_path": ref, "prompt_text": ref_text, "prompt_lang": "zh",
         "aux_ref_audio_paths": [other_clean_clip],  # 只融合音色
         "text_split_method": "cut1",               # 只在句號切；cut5（逢逗號切）短片段會整段消失
         "top_k": 15, "temperature": 1.0, "batch_size": 8, "seed": 42, "parallel_infer": True})
```
- config 路徑是相對 repo 根目錄：先 `os.chdir(root)`，`sys.path` 加 `root` 和 `root/GPT_SoVITS`。
- 參考音前後保留約 0.3–0.4 秒自然靜音，否則句首被吃、參考句漏進輸出。
- 每句先抽 3 個 seed，被標出的句子再補抽 4–8 個；用 `scripts/vo/pick_takes.py` 挑。
- 句首是「短詞＋逗號／冒號」（「第四步，…」）時常整段被吞 → 改寫句首。

### BreezyVoice 的坑
- 沒有 `ttsfrd` 時，文字正規化退回 WeTextProcessing，**預設會轉成簡體**，很多字會念錯音。換掉 normalizer（`traditional_to_simple=False`），而且 FST cache 會把旗標燒進去，要用另一個 cache 目錄。
- 建置：`openai-whisper` 要 `setuptools<70`；`HyperPyYAML` 要 `ruamel.yaml<0.18`。
- 會把參考句念進輸出、句尾亂語；參考音前後留靜音後改善。

### Breeze-ASR 自己轉 int8
```bash
ct2-transformers-converter --model MediaTek-Research/Breeze-ASR-25 --revision <pinned-sha> \
  --output_dir breeze-asr-25-ct2-int8 --quantization int8 --copy_files preprocessor_config.json
```
- 轉換用的 venv 和執行用的 venv 分開。不要用網路上別人轉好的版本（來源追不到固定版本）。
- 長檔整段跑會在結尾幻覺：VAD 切細（`min_silence_duration_ms=500, max_speech_duration_s=25`）。
- 模型沒有標點：用 segments 的停頓長短在 client 端補「，」「。」「？」。

## CPU tips — CPU 機器注意事項
- 全部放在 WSL 的 ext4（`~/`）；venv 和權重放在 `/mnt/c` 會慢 5–10 倍。
- WSL 預設只給一半 RAM。各引擎峰值大約：GPT-SoVITS 6–7 GB、BreezyVoice 5–6 GB、ASR 2.5 GB → **一次只載入一個模型**。
- `torch.set_num_threads(os.cpu_count())`；有些套件 import 時會把 threads 設成 1，要在 import **之後**再設回來。
- PyAV 19 移除了 `metadata_errors`，faster-whisper 1.2.1 還在傳 → 限制 `av<19`（`scripts/setup/requirements.txt` 已設定）。
- Node `fetch` 送長音檔會撞到 300 秒逾時 → 用 `node:http` 串流。
- ffmpeg 寫的 WAV 在 data 前面有 LIST chunk，不要假設 header 固定 44 bytes。

## Evaluation — 評估方法（可直接套到新模型）

**測試材料**：10–12 句，涵蓋日常用語、數字日期、破音字、中英夾雜、一句全英文、疑問與情緒、一段 70 字長句、一句容易引發 ASR 幻覺的結尾。講者念一次全部：第 1 句當參考音，其他當測試句；講者原音切成每句一檔，當盲聽的**隱藏錨點**。錄完先用 ASR 轉寫自己的錄音，確認念的是哪一份稿，再切參考音。

| 指標 | 工具 | 解讀 |
|---|---|---|
| RTF | 牆鐘時間 ÷ 音長，載入時間分開記 | 每個模型分開跑，記下 load average |
| CER | ASR 對標準答案；先正規化（`scripts/vo/textnorm.py`） | **講者原音的 CER＝ASR 自己的誤差基準** |
| 聲紋相似度 | CAM++ embedding cosine | 講者兩段錄音之間的值＝上限 |
| 音高 | pyin／Praat F0 中位數，換成半音 | 「聲音偏高」可以量化 |
| 頻寬 | 99% spectral roll-off | 「聲音被壓扁」＝高頻不見 |
| MOS | UTMOS | 絕對值不採用，只看相對值 |
| 拖音／長度／語速 | ASR word timestamps＋各 take 長度 | 長篇旁白必跑（[narration QA](narration-qa.md)） |

**盲聽頁**：每句的各來源隨機標 A–E，答案另存；頁面離線可開。每個樣本打 1–5 分（自然、口音、像不像）；混入講者原音當隱藏錨點（MUSHRA 做法）——錨點拿 4 分時，其他引擎的 3.5 分其實很接近了。頁面不存分數，記得匯出。

## Licensing — 授權與同意
- Apache-2.0／MIT 只處理程式和權重，**不處理聲音肖像權**。用任何人的聲音都要有書面同意，不能模仿名人或公眾人物。
- clone 產出的檔名加 `-clone`，參考音只存本機，不進公開 repo（本 repo 的 `.gitignore` 已排除 `voices/`、`ref-audio/` 與所有音訊檔）。
- 公開示範（README、影片）用合成聲音或模型 repo 內附、授權明確的範例講者。
