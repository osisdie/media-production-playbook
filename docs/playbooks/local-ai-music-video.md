# Local AI lyric music video — 只用本機開源模型做擬真歌詞 MV（6 GB 筆電 GPU）

> 雲端流程通常是「Midjourney 生圖 → Runway／Kling 圖生影片 → Suno 作曲含人聲 → AE／剪映動態歌詞」。這份是把每一步換成**本機開源模型**的實測：一台 6 GB VRAM 的筆電 GPU（Blackwell）、WSL2 4 vCPU、31 GB RAM，ComfyUI headless 驅動。實測用的是一首 8 行、介紹虛構產品功能的中文歌。下面是流程、量到的數字、授權注意事項，以及踩過的坑。配樂與節拍格線見 [beat-synced-launch-video](beat-synced-launch-video.md)，人聲品管見 [narration-qa](narration-qa.md)，成片審查見 [marketing-review](marketing-review.md)。

## TL;DR

| 問題 | 結論 |
|---|---|
| 本機能做擬真關鍵畫面嗎？ | **可以。** SDXL 寫實微調（RealVisXL）1344×768 約 47 秒／張，質感接近商業攝影 |
| 跨鏡頭同一個角色？ | **部分可以。** IP-Adapter plus-face 臉很像、可商用；正式片再加一個角色 LoRA |
| 本機圖生影片？ | **FramePack 能保住人臉，但 5 秒鏡頭要約 26 分鐘、只有 480p、動作輕微。** LTX-2B 快約 40 倍，但臉 1 秒內就變形，不能拍人 |
| 本機作曲含中文人聲？ | **可以，GPU 上幾乎免費**（50 秒一首約 15–35 秒）。瓶頸是人耳試聽，不是算力 |
| 只用 CPU？ | 生圖約 34 分鐘／張、作曲 11–18 分鐘／30 秒，只能當備案；**影片不可行** |
| 建議分工 | 關鍵畫面、作曲、動態歌詞在本機；**有人物動作的鏡頭**交給雲端 i2v（用本機關鍵畫面當輸入），本機 FramePack 留給慢速空景、B-roll |

## Pipeline — 流程

```
歌詞（只寫產品真的有的功能）
  ├─► 作曲：ACE-Step 多 seed → ASR 預篩咬字 → Demucs 分軌＋響度 → 人耳試聽 → limiter／loudnorm
  │        └─► beats.json（BPM、強拍偏移、段落）
  └─► 分鏡 → 關鍵畫面：SDXL（負面提示）→ 局部重繪去 logo
             → 角色一致：角色設定圖＋IP-Adapter plus-face（＋角色 LoRA）
             → 圖生影片：FramePack（人物）／LTX（無人空景）→ 放大＋補幀
                  └─► Remotion：影片鏡頭＋動態歌詞＋產品介面卡片，切點踩 beats.json
```

- **AI 畫面裡的中文字一定是亂碼**：螢幕、白板、招牌上的產品介面一律在 Remotion 疊上去（見 [promo-video](promo-video.md) 的 Mock UI），提示詞裡要求「blank screen / unbranded」。
- **歌詞先做事實核對**：每一句對到產品真的有的功能，刻意避開不能承諾的說法（產品還沒有、或只在規劃中的功能就不要寫），不寫價格、不提第三方平台。
- **動態歌詞**：用 Remotion 逐字或逐詞出現，時間點取自 `beats.json`（每句從小節線開始）和人聲分軌的 ASR 字級時間。這一步沿用既有的 beat grid 做法，沒有額外的模型需求。

## Measured — 實測數字

機器：6 GB VRAM 筆電 GPU（Blackwell，約 0.5 GB 被 Windows 桌面佔用）、WSL2 4 vCPU、31 GB RAM。時間是 ComfyUI 自己的 `execution_start → execution_success`，模型已載入（warm），另註明的除外。VRAM 是 `nvidia-smi` 每秒取樣的整張卡峰值；RAM 是 ComfyUI 程序樹的 RSS（同一台機器上還有其他工作，系統總用量最高約 27 GB）。

### 畫面

| 模型 | 工作 | 解析度 | 時間 | VRAM 峰值 | RAM 峰值 | 品質（主觀） | 商用授權 |
|---|---|---|---|---|---|---|---|
| RealVisXL V5.0 fp16（SDXL），30 steps dpmpp_2m_sde | 關鍵畫面 | 1344×768 | **46–51 秒／張** | 5.4 GB | 8.5 GB | ★★★★½ 很像攝影、膚質自然；加負面提示後筆電 logo 從 4/4 降到 0/2 | CreativeML **OpenRAIL++-M**：可商用，有使用限制條款 |
| FLUX.1-schnell GGUF Q4_K_S＋t5xxl fp8，4 steps | 關鍵畫面 | 1344×768 | **35–37 秒**（冷啟動 66 秒） | 4.8 GB | 7.6–10.5 GB | ★★★½ 構圖乾淨，但皮膚塑膠感、像圖庫照片；**沒有負面提示，logo 3/4 張** | **Apache-2.0** |
| RealVisXL 遮罩 img2img（去 logo） | 局部重繪 | 1344×768（遮罩約 70 px） | 78.5 秒（整張 latent，denoise 0.75） | 5.4 GB | 8.3 GB | ★★★★★ logo 消失、看不出接縫；只裁遮罩附近重繪可降到約 15 秒 | 同 RealVisXL |
| RealVisXL 純提示詞 | 角色基準 | 1344×768 | 59–88 秒（同設定卻比第一列慢：量測時機器共用，原因沒有單獨確認） | 5.4 GB | 8–11 GB | 每個 seed 都是**不同的人** | — |
| RealVisXL＋IP-Adapter **FaceID PlusV2**（＋LoRA 0.6，weight 0.85） | 同一角色換場景 | 1344×768 | 76 秒（首次 215 秒，含 InsightFace 載入） | 5.3 GB | 13.0 GB | ★★½ 臉型、髮型相近，但像「親戚」不像同一人 | ❌ **僅限非商業研究**（InsightFace 權重） |
| RealVisXL＋IP-Adapter **plus-face** SDXL（ViT-H，weight 0.8） | 同一角色換場景 | 1344×768 | **52–63 秒** | 5.4 GB | 12.7 GB | ★★★★ 明顯是同一張臉；服裝、飾品也會一起帶過去（連戲方便，但不能每場換裝） | ✅ **Apache-2.0**；CLIP-ViT-H 為 MIT |
| LTX-Video 2B 0.9.8 distilled，8 steps | 圖生影片 5 秒（121 幀 @24fps） | 768×448 | 33.6 秒／顆 | 5.3 GB | 12.8 GB | ★★ 動作流暢、手還可以，但**臉 1 秒內就變成別人** | **LTXV Open Weights License**：年營收 **< 1,000 萬美元**的組織才免費，以上要買商用授權 |
| LTX-Video 2B 0.9.8 distilled | 圖生影片 5 秒 | 1024×576 | **37.5–38.7 秒／顆** | 5.5 GB | 12.9 GB | ★★ 同樣臉部漂移，背景建築後段變形；「static camera」提示無效 | 同上 |
| **FramePack**（HunyuanVideo I2V fp8，ComfyUI FramePackWrapper），25 steps，TeaCache 0.15 | 圖生影片 4.8 秒（145 幀 @30fps） | 832×480 | **約 26 分鐘／顆**（10.8 秒／幀） | **4.9 GB** | **18.0 GB** | ★★★★ **人臉保持是同一批人**、背景穩、小動作自然、不變形；動作偏慢，480p 要放大 | 程式 Apache-2.0；權重是 **Tencent Hunyuan Community License**（**不授權歐盟、英國、南韓**；MAU > 1 億要另談；有使用政策）；文字編碼器 llava-llama-3 適用 **Llama 3 Community License** |
| RealVisXL **只用 CPU**（`--cpu`，fp32，4 vCPU） | 關鍵畫面 | 1344×768，30 steps | 約 63 秒／step → **約 33–35 分鐘／張**（比 GPU 慢約 43 倍） | — | 17.6 GB | 未跑完，不評 | 同 RealVisXL |

PuLID、InstantID 也依賴 InsightFace，授權限制和 FaceID 相同。

### 作曲（中文人聲）

ACE-Step 透過 ComfyUI 原生節點跑。CER 用 Breeze-ASR-25（CT2 int8、CPU、beam 5）轉寫，繁簡正規化後對整段歌詞計算；另外算「無聲調拼音音節錯誤率」（SYL），不受同音字影響，比較接近「念得對不對」。

| 模型 | 裝置 | 長度 | 每首時間 | VRAM 峰值 | RAM 峰值 | 最佳 CER／SYL | 備註 | 授權 |
|---|---|---|---|---|---|---|---|---|
| ACE-Step **1.5 turbo**（DiT 2B＋Qwen3 1.7B LM＋0.6B 文字編碼器），8 steps | GPU | 30 秒 | 10–13 秒（冷啟動 21 秒） | 5.4 GB | — | 0.38／0.15 | 混音較飽滿；副歌關鍵詞常念偏（見下方陷阱） | 上游權重與程式 **MIT**；ComfyUI 重新打包版 Apache-2.0 |
| ACE-Step 1.5 turbo | GPU | 50 秒 | 14–20 秒 | 5.3 GB | — | 0.34／0.24 | 唱完整段歌詞 | 同上 |
| ACE-Step 1.5 turbo | **CPU** | 30 秒 | **約 11 分鐘** | — | **18.6 GB** | — | LM 150 個 code 約 2.7 秒／個≈7 分鐘，DiT 8 steps≈86 秒 | 同上 |
| ACE-Step **v1 3.5B**，50 steps（**拼音輸入**） | GPU | 50 秒 | 35–36 秒 | 5.3 GB | — | **0.15／0.06** | 咬字最清楚；伴奏偏薄（人聲比伴奏高約 9.5 LU） | **Apache-2.0** |
| ACE-Step v1 3.5B（直接餵漢字） | GPU | 30 秒 | 18–29 秒 | 5.4 GB | — | 0.92–1.8 | **亂唱**，有的 seed 唱成英文（見下方陷阱） | 同上 |
| ACE-Step v1 3.5B | **CPU** | 30 秒 | **約 18 分鐘**（約 20 秒／step） | — | 13.4 GB | — | 同 seed、同設定，CER 和 GPU 版接近 | 同上 |

- 30 秒對 8 行歌詞太短：v1 只唱到副歌第一句，要 50 秒才唱完。
- **所有品質數字都來自 ASR、分軌和響度計**，好不好聽、腔調（兩個模型都偏中國大陸腔，沒有台灣腔控制）、金屬感，一定要有人耳試聽。
- 共用 GPU 時 RAM 欄量到的是共用 ComfyUI 程序（含其他工作快取的模型），所以 GPU 列不填。

## Trading time for quality — 一晚（約 10 小時）的預算

一次只跑一個 GPU 工作。

| 工作 | 每單位 | 一晚數量 | 備註 |
|---|---|---|---|
| SDXL 關鍵畫面 1344×768 | 約 48 秒 | **約 700 張** | 約 1/4 可用 → 約 175 張 |
| FLUX-schnell 關鍵畫面 | 約 36 秒 | 約 1000 張 | 去 logo 的次數比較多 |
| SDXL＋plus-face 角色鏡頭 | 約 58 秒 | 約 600 張 | |
| FramePack 5 秒鏡頭 832×480 | 約 26 分鐘 | **約 22 顆≈110 秒素材** | 約一半能用 → 一晚約 11 顆；3 分鐘、40 顆鏡頭的 MV 要約 4 晚 |
| LTX-2B 5 秒鏡頭 1024×576 | 約 38 秒 | 約 900 顆 | 只用在沒有人臉的鏡頭（天際線、筆電特寫、抽象動態） |
| ACE-Step 1.5 turbo，90 秒歌（GPU，推估） | 約 25–40 秒 | 數百首 | 先用 ASR 篩，再人耳試聽 |
| ACE-Step v1，90 秒歌（GPU，推估） | 約 65–80 秒 | 約 450 首 | |
| ACE-Step 1.5 turbo（CPU，推估） | 約 25–30 分鐘 | 約 20 首 | 90 秒可能把 WSL 推到 swap |
| SDXL（CPU） | 約 34 分鐘 | 約 17 張 | |
| **建議組合** | — | 60 張關鍵畫面（約 50 分鐘）＋20 顆 FramePack（約 8.7 小時）；同時另一台或白天跑作曲 | |

- 未實測但交付需要：1080p 放大（例如 2× ESRGAN 逐幀）每幀約 1–3 秒；FramePack 調 TeaCache／步數也許能省 20–30%。
- 「用時間換品質」最划算的是：**多 seed 再挑**（畫面、歌都一樣），而不是加步數。歌曲先用 ASR 的 CER／SYL 自動刷掉咬字差的，再把前幾名交給人耳。

## Local vs cloud — 和雲端比差在哪

- **影片解析度與動作**：雲端 i2v 幾分鐘出 1080p、5–10 秒、有運鏡和大動作；本機 FramePack 26 分鐘出 480p 輕微動作。
- **每次決策的回饋速度**：雲端約 1 分鐘回 4 個版本；本機一顆 FramePack 佔 GPU 26 分鐘，改動作提示詞只能整晚批次跑。
- **角色一致**：雲端的角色參考比較好用；本機要 plus-face＋角色 LoRA（LoRA 訓練時間未實測）。
- **作曲**：雲端作曲服務直接吃漢字、混音接近可上架、2–4 分鐘完整段落結構；本機 v1 要拼音、伴奏薄，1.5 混音飽滿但會削波、壓縮很重（LRA 約 2），關鍵詞咬字會漂。長歌（90 秒以上）的段落結構未實測。
- **本機的優點**：靜態畫面品質不輸雲端、邊際成本為零、品牌素材不用上傳、可以完整控制（局部重繪、固定 seed）。

## License flags — 授權（商用前逐一到 model card 確認）

| 元件 | 授權 | 注意 |
|---|---|---|
| RealVisXL V5.0 | CreativeML OpenRAIL++-M | 可商用，附使用限制 |
| FLUX.1-schnell | Apache-2.0 | 官方 repo 是 gated（要登入同意），見下方下載陷阱 |
| IP-Adapter plus-face（h94/IP-Adapter）、CLIP-ViT-H | Apache-2.0、MIT | 可商用 |
| IP-Adapter FaceID、PuLID、InstantID | **InsightFace 權重：非商業研究** | 商用片不要用 |
| LTX-Video 2B | LTXV Open Weights License | **年營收 ≥ 1,000 萬美元要付費授權**，用之前先確認 |
| FramePack／HunyuanVideo | Tencent Hunyuan Community License | **不授權歐盟、英國、南韓**；大規模用戶另談；文字編碼器另適用 Llama 3 Community License |
| ACE-Step v1／1.5 | Apache-2.0／MIT | 輸出可商用；上游建議揭露 AI 生成並做原創性檢查 |
| Remotion | Remotion License | 公司超過門檻要買授權（見 [README](../../README.zh-TW.md#授權)） |

## Traps — 踩過的坑

### 作曲
- **ComfyUI 的 ACE-Step v1 會把每個漢字變成 UNK**：v1 的歌詞 tokenizer 原本靠 pypinyin 先轉拼音，ComfyUI 的移植拿掉了這一步。直接餵漢字，模型會亂唱（CER≈1，有的 seed 唱成英文）。
  - 修法：歌詞先用 pypinyin 轉 **tone3 拼音**（例如「看懂光線」→ `kan4 dong3 guang1 xian4`），破音字手動修（例如結構助詞「得」改 `de5`）。
  - 每一行加 `[zh]` 前綴，否則會被當英文；英文詞放在獨立的 `[en]` 行。
  - ACE-Step 1.5 用 Qwen tokenizer，可以直接吃漢字。
- **ACE-Step 1.5 的副歌關鍵詞會漂**：同一個品牌短語在 7 個 take 裡有 4 個子音或聲調被唱偏，其他雙音節詞也常被唱成同音不同調的詞。關鍵詞要用 SYL 指標逐 take 檢查，必要時改用 v1（拼音）或換一個比較好唱的詞。
- **英文品牌名**：v1 只有放在獨立 `[en]` 行時才會唱，ASR 聽起來像被拆成兩個字；1.5 會跳過或在那裡打轉。退路：歌只唱中文短語，品牌英文名用畫面字卡呈現。
- **ACE-Step 1.5 會削波**：成品 true peak 0 到 +0.7 dBTP、整體 −10 到 −12 LUFS。使用前一律過 true-peak limiter 到 −1 dBTP 以下，再 loudnorm（網路 −14 LUFS，或配合 MV 混音），做法見 [beat-synced-launch-video](beat-synced-launch-video.md#music--本機生成節奏型配樂)。
- **唱歌的 ASR 很吵**：會陷入重複迴圈（「A-A-A…」）、分不出同音字；CER 異常高的 take 標記成「人耳確認」，不要直接丟掉。Demucs 2-stem 分出人聲再跑 ASR 會準一點，也可以順便確認伴奏沒有人聲殘留。
- **seed 不能跨裝置重現**：同一個 seed 在 CPU 和 GPU 上是不同的歌，比較 CPU／GPU 品質時不要拿同 seed 當同一首。

### 畫面
- **FLUX-schnell 沒有負面提示**（cfg 1）：提示詞寫「unbranded laptops」也沒用，筆電上照樣出現真實品牌 logo。要嘛用 SDXL＋負面提示（`logo, brand, text, watermark`），要嘛用遮罩局部重繪把 logo 蓋掉。
- **SDXL 會多畫人**：指定兩人的畫面，有的 seed 會畫成三人或背景多一個路人 → 多抽 seed，挑圖時數人數。
- **plus-face 會連衣服一起複製**：連戲方便，但想讓角色換裝時要降低 weight 或改用角色 LoRA。
- **LTX-2B 不能拍人臉**：再多的「faces stay the same」提示都救不回來；只拿來做沒有人的鏡頭。

### 下載與模型檔
- **HF CDN 的 ETag 不是檔案的 sha256**：`resolve` 網址會 302 到 CDN，跟著轉址後拿到的 ETag 是另一種 hash，拿來比對就會一直報「sha mismatch」。正確做法：
  - HEAD 請求**不要跟隨轉址**，從 Hub 的回應讀 `x-linked-etag`／`x-linked-size`；或用 `paths-info` API 取 LFS 的 `oid`（就是 sha256）來驗證。
  - 帶 token 的請求轉址到 CDN 時，**不要把 Authorization header 一起帶過去**。token 只從環境變數讀，不印進 log。
- **huggingface_hub 的 xet 後端被 kill 之後不會續傳**：每次重啟都從 0 開始一個新的 `.incomplete`。大檔（數 GB）下載中**不要 kill worker**；真的要續傳，用支援 HTTP Range 的下載器分段抓（可沿用舊的 `.incomplete` 當前段），完成後驗 sha256。
- **`curl -C -` 續傳也可能壞檔**：實測多寫了 51 MB；兩個程序同時寫同一個檔案更一定壞。續傳後一律核對檔案大小和 sha256，safetensors 再讀一次 header。
- **gated repo 和無 gate 的重新打包版**：有些官方 repo 要登入並同意條款（例如 FLUX.1-schnell 的 VAE 會回 401／GatedRepoError）。ComfyUI 社群常有同一份檔案的重新打包版（例如 Comfy-Org 的 `*_repackaged`），不用 gate；用之前確認 sha256 和上游一致（或至少檔案大小與結構一致），**授權仍以上游為準**。
- 模型放在 HF cache 或 repo 外的資料夾，用 symlink 接進 `ComfyUI/models/`，不要複製第二份（見 [`models/README.md`](../../models/README.md)）。

### 記憶體與 GPU
- **WSL 的 RAM 會被 ComfyUI 的模型快取吃滿**：FramePack 程序約 18 GB，加上其他工作，31 GB 的 WSL 很快就接近上限。換大模型之前、或把 GPU 讓給別的工作之前，先呼叫 ComfyUI 的 `POST /free`（`{"unload_models": true, "free_memory": true}`）釋放 VRAM 和 RAM。WSL 的記憶體上限在 `.wslconfig` 調（見 [windows-wsl](../platform/windows-wsl.md)），要 `wsl --shutdown` 才生效。
- **多個工作共用一張 GPU**：
  - 最簡單：所有 GPU 工作都排進**同一個 ComfyUI server 的佇列**（`POST /prompt`，再輪詢 `/history/<id>`）。ComfyUI 一次只跑一個 prompt，GPU 不會被重複佔用。
  - 一定要另起 GPU 程序時，用鎖檔：開始前建立 `gpu.<owner>.lock`、結束後刪除，其他人每個重工作前檢查有沒有別人的鎖。
  - CPU 對照組另起一個 `main.py --cpu --port <另一個 port>` 的 ComfyUI，跑完就關。
- **量測時記錄「機器很忙」**：共用機器時量到的時間是上限，另外記下當時的 load average；真正的基準用 ComfyUI 自己的執行時間戳，不用 wall clock。

### 多 agent 協作
- **agent 之間的訊息可能送不到**：改用共用的狀態檔（例如 `STATUS.md`／`GPU_SHARING.md`，每人每階段寫一行），寫清楚誰擁有哪個資源（ComfyUI server、下載、GPU）。
- **orchestrator 重啟後，之前派出去的 helper 可能還活著**：它們變成孤兒，繼續跑同一份工作，造成重複下載、互相 kill 對方的 worker、兩個程序寫同一個檔。重新派工**之前**先查程序列表（`ps`、tmux pane、各自的 log 最後更新時間），確認舊的 helper 已停止，或把工作交接給它，不要直接再開一個。
- 接手的 agent 寫一段「交接」：哪些已完成、哪些檔案可能被兩個程序寫過要重驗、從哪一步接著做（通用做法見 [beat-synced-launch-video](beat-synced-launch-video.md#team-orchestration--多個-agent工作並行時)）。

## Checklist — 交付前
- [ ] 每顆鏡頭用到的模型授權都適用於這次用途（營收門檻、地區排除、非商業權重）
- [ ] 畫面沒有真實品牌 logo、亂碼文字、多出來的人、變形的手和臉（[marketing-review](marketing-review.md)）
- [ ] 同一角色在所有鏡頭長得一樣（並排抽幀比對臉部）
- [ ] 歌曲 take 經過 ASR 預篩**和**人耳試聽（咬字、腔調、關鍵詞、金屬感）；試聽清單寫明哪些還沒人聽過
- [ ] 歌曲 true peak ≤ −1 dBTP、響度符合交付規格（WAV 和最終 mp4 都量）
- [ ] 動態歌詞與人聲對齊、切點在拍上；螢幕內容都是 Remotion 疊上去的
- [ ] 每個數字都有 log（執行時間、`nvidia-smi` VRAM、RSS），模型檔核對過 sha256
