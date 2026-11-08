# Taiwanese (Taigi) TTS & ASR — 台語語音合成與辨識

> 在 CPU-only 機器上做台語（臺灣閩南語）的語音合成與辨識：引擎選擇、實測數據、踩過的坑、評估方法。台語開源資源少、坑多，這一節把實際試過的路整理出來，換到別的專案可以直接沿用。

## Summary — 一句話結論

- **台語 TTS**：目前地端可用的是 **GPT-SoVITS-tw 系列 fork**（例如 KaedeTai 的台語 GPT-SoVITS，MIT）。只吃 POJ／Tâi-lô 拼音，要用 ref-free 模式，屬於研究預覽等級。
- **台語 ASR**：**Breeze-ASR-26**（聯發科，Whisper 微調）——聽台語、輸出**華語漢字**。
- **最大的難題不在合成，而在文字**：使用者給的通常是華語。華語 → 台語漢字 → Tâi-lô，兩步的錯誤會疊加。實務上先做「固定句、事先合成」。

## TTS candidates — 實測比較（8 句日常台語，CPU，ref-free／預設講者）

| 引擎 | 設定 | 載入 | RTF | 峰值 RAM | CER（Breeze-ASR-26） | 結論 |
|---|---|---|---|---|---|---|
| **GPT-SoVITS-tw（KaedeTai）** | 訓練語者、ref-free | 約 11 s | **約 2.0–2.2** | 約 4.7 GB | **約 0.13** | 選定（原型） |
| MERaLiON OmniVoice Hokkien | 預設語者、32 步 | 約 11 s | 約 45 | 約 7 GB | 約 0.37 | 太慢、腔調偏新加坡 |
| MERaLiON（8 步） | 預設語者 | 約 9 s | 約 9 | 約 6.3 GB | 約 0.27 | 快一點但更不準 |

數字是 CPU 被其他程式佔用約 2 核時量的，只看相對關係。clone 特定講者的音色（需要該講者同意）時，KaedeTai 的 CER 幾乎不變，但**只換音色、不帶講者自己的語調**——節奏仍是訓練語者的。

**淘汰的選項與原因**
- `facebook/mms-tts-nan`：**CC-BY-NC**（不能商用）、聖經朗讀的單一聲音、不能 clone。
- coqui VITS 台語模型：G2P 執行時要下載 Go 執行檔或連遠端服務。
- CosyVoice3「閩南話」指令、Qwen3-TTS：第三方評測裡分別只有約 18/25、7/25 的句子聽起來像閩南語。
- 語音轉語音的大模型（數十 GB）：CPU 機器跑不動。

## GPT-SoVITS-tw pitfalls — 要注意的地方

- **只吃 POJ／Tâi-lô，不吃漢字。** 台語句先套 fork 內附的變調前處理（`apply_sandhi`，NFC 正規化前後各做一次），再走它的 `tw` G2P。
- **文件寫的 CLI 在 repo 裡可能不存在**：改用 `GPT_SoVITS/inference_webui.get_tts_wav`。它的語言切段器會把 Tâi-lô 當成英文，要把 `get_phones_and_bert` 包一層，讓 `tw` 直接走 `clean_text_inf(text, "tw", <version>)`。
- `inference_webui` 會把 `sys.argv[-1]` 當 UI 語言：import 前先 `sys.argv = sys.argv[:1]`。
- **一定要 ref-free**：有參考文字時，S1 會吃掉句首（「今天下午三點開會，請大家準時參加」只剩後半句）。ref-free 時音色只靠 S2，節奏和訓練語者相同。
- **下載的權重可能是「訓練 checkpoint」**：用 `torch.load(weights_only=True)` 讀出，再轉成推論格式（去掉 `enc_q`、轉 fp16、補版本 header）重存。**下載檔裡的 pickle 永遠不要直接執行。**
- 環境變數：`gpt_path`、`sovits_path`、`is_half=False`、`version`；載入後確認模型版本是台語版。
- 取樣參數用 WebUI 預設（`top_k=15, top_p=1, temperature=1`）、固定 seed、不切句。
- 研究預覽的限制：長句（> 約 60 音節）會飄；同一句不能台華混用。
- 可以和華語 GPT-SoVITS 共用底模（symlink），省幾 GB 空間。

## Taigi ASR — 台語辨識（Breeze-ASR-26）

- 它是「**台語語音 → 華語漢字**」的模型，不是台語漢字或拼音轉寫；拿來量 TTS 的 CER 時，標準答案要用**華語意思**那一欄。
- **一律指定 `language="zh"`**：讓 Whisper 自動偵測語言會判錯。
- 不能當華語 ASR 用（華語請用 Breeze-ASR-25）。
- 官方 repo 沒附 faster-whisper 需要的 `tokenizer.json`：從 repo 的 tokenizer 檔自己產生：
  ```bash
  python -c "from transformers import WhisperTokenizerFast as T; T.from_pretrained('MediaTek-Research/Breeze-ASR-26', revision='<pinned-sha>').save_pretrained('breeze-asr-26-ct2-int8')"
  ```
  轉 CT2 int8 的方法同 Breeze-ASR-25（見 [voice-production](voice-production.md)）。

## The real problem: text — 最大的問題在文字

使用端送出的通常是華語漢字。要念台語得先「華語 → 台語漢字」翻譯，再「台語漢字 → Tâi-lô」標音，**兩步的錯誤會疊上去**，而且兩步都缺少成熟的開源工具。

建議做法：
1. **先做固定句**：事先寫好 Tâi-lô（請母語者校對），預先合成存成音檔，產品端直接播放（提示音、問候語、固定說明）。
2. 任意華語即時轉台語，另外當成研究題目評估，不要一開始就承諾。
3. 稿子同時保留三欄：台語漢字、Tâi-lô、華語意思——合成用 Tâi-lô、ASR 驗收比對華語意思、字幕看需求選漢字或華語。

## Evaluation — 評估方法

- **測試句**：8 句左右的日常台語（問候、時間、數字、請託、疑問），每句三欄（台語漢字＋Tâi-lô＋華語意思，存成 TSV），另外加 2 句**華語原文**——看引擎會不會把華語硬念成台語。
- **客觀**：RTF（載入分開記）、峰值 RAM、Breeze-ASR-26 CER（對華語意思）。每個引擎分開跑，記下 load average。
- **盲聽**：沿用 [voice-production](voice-production.md) 的盲聽頁（隨機 A–E、離線、匯出分數），台語另外加一欄「聽起來是：台語／華語／聽不出來」。有母語者錄音時放進去當隱藏錨點。
- 合格門檻建議：「聽起來是台語」≥ 80%、自然度 ≥ 3.5／5、固定句 CER 不高於母語者錄音太多。

## Licensing — 授權
- KaedeTai 台語 GPT-SoVITS（code + weights）：MIT。MERaLiON：見其 model card。mms-tts-nan：CC-BY-NC，不能商用。
- clone 任何人的聲音（包括台語）都要取得同意，見 [`../consent/voice-consent-template.md`](../consent/voice-consent-template.md)。
