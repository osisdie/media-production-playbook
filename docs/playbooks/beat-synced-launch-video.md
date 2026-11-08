# Beat-synced 3D launch video — 有節奏感的 3D 產品發表短片

> 16:9、30–60 秒的產品發表片：Blender 程序產生的 3D 鏡頭＋Remotion 合成＋本機生成的節奏型配樂，所有切點都踩在拍上。在 CPU-only 的 WSL2 筆電上實際做過一支，下面是流程、數字和踩過的坑。工具見 [blender-in-pipeline](blender-in-pipeline.md)、[narration-qa](narration-qa.md)、[voice-production](voice-production.md)。

## Principle — 節奏感來自「對齊」

音樂、剪接點、畫面動作共用**同一條節拍格線**，觀眾就會覺得有節奏；再好聽的配樂，切點沒踩在拍上也會顯得鬆散。

- 先定 BPM：產品發表常用 **120–128 BPM**（house／electro-pop）。128 BPM＝每拍 0.469 秒（≈ 14.1 幀 @30fps）、每小節 1.875 秒。
- 寫腳本時就把每句旁白分配到小節上：例如第 0–4 小節 build-up、第 4 小節第一拍 **drop＝品牌揭示**、中段一個 break、第二個 drop 接重點功能、最後一個 outro hit＝CTA 彈出。
- 產出一份 `beats.json`（BPM、第一個強拍的偏移、drop／hit 時間），音樂、剪輯、3D 動畫都讀它。

## Shot timing — 切點規則

- 每顆鏡頭從**該句旁白所在的小節線**開始；如果前一句還沒講完，就退到它講完之後最早的一拍（不切斷旁白）。
- drop 那一句：音樂**晚一拍**才 duck，讓 drop 先全音量打出來，旁白再壓上去。
- 沒有旁白時音樂增益約 0.6；有旁白時約 0.14–0.2，也就是**相對**壓低約 10–12 dB（[promo-video](promo-video.md) 的 0.14 是偏保守的一端；音樂本身很密集時取低值）。attack 0.15 秒、release 0.3 秒。
- 3D 鏡頭內的小推進（camera punch）放在每小節第一拍：快升、慢退，像 kick 的包絡。

## 3D shots — Blender 鏡頭

- **全部程序產生**（bpy）：產品本體、手機、卡片、格狀面板、轉台、立體字標。唯一的外部素材是官方字標（取顏色與字形）。卡片上的文字先畫成貼圖（HTML/Remotion stills）再貼到 3D 卡片。
- **人物用風格化人偶（木頭人偶、低多邊形）或剪影**：程序產生寫實人物很難好看（恐怖谷），也避開肖像權。
- **字標照官方檔案**：取樣官方圖檔的顏色，不要照 brief 的文字描述（顏色、字重、字距、哪個部件用哪個顏色，都很容易被記錯）。
- **亮場不要「白配白」**：小角度 key light 做出接觸陰影、窄角 spot 做輪廓光（大面積 area light 會把整個無縫背景染色）、背景自然漸暗、淺景深；品牌色只當重點光。
- **審查流程**：半解析試渲（每顆 2–3 幀）→ 拼成一張 contact sheet 給人看（`scripts/video/contact_sheet.py`） → 每 10 幀一張的草稿 → 正式版。每一輪都看 contact sheet 再往下。

### Animation in code, rendered frame by frame
- 動畫用 Python 逐幀計算（`apply(frame)` 設定位置、材質、可見性），再逐幀 render still，不用關鍵影格：緩動公式精確、拍點同步容易，在自己的渲染腳本加上 `--step`（每 N 幀一張）和 `--only`（指定幀）參數，草稿和抽幀就不用另外寫程式（本 repo 的 `render_scene.py` 尚未實作這兩個參數）。
- 同一份剪輯表（JSON，幀號由小節／拍的時間四捨五入）同時給 Blender 和 Remotion 讀。
- 鏡頭內的同步範例：物件每拍彈出一個、格狀面板依 16 分音符依序翻轉、材質或顏色在第 2/4/6 拍切換、轉台每 2 拍轉 90°、每小節第一拍攝影機小推進、CTA 在 outro hit 彈出。
- 字幕帶要在 3D 構圖階段就考慮：在測試幀上疊半透明的字幕框，確認主體沒被壓到再調鏡頭。
- 體積光在低取樣、半解析度時會出現塊狀雜訊 → 改用假光錐（cone 網格＋朝向衰減的 emission），更乾淨也更快。

### Blender 5.x API pitfalls
- 合成器改成 `scene.compositing_node_group`，輸出改用 Group Output。
- Glare 的類型變成 menu socket，要填顯示名稱（例如 `"Bloom"`），Size 是 0–1；舊寫法會靜靜退回 Streaks（十字星芒）。EEVEE 沒有內建 bloom。
- WSL 呼叫 Windows Blender 的迴圈要加 `< /dev/null`，否則 `cmd.exe` 會吃掉 `while read` 的 stdin，只跑第一次。中斷 WSL 端的 shell 不會停掉 Windows 端的 Blender——用「停掉迴圈、讓目前這顆跑完」的方式暫停。

### Render cost on a CPU laptop（EEVEE，AMD 內顯，實測）
| 設定 | 每幀 |
|---|---|
| 960×540、12 samples（草稿） | 約 0.75 秒 |
| 1920×1080、16 samples（正式） | 約 2–7 秒（依場景） |

**估算時要扣掉啟動開銷**：只 render 2–3 幀的試渲，每次都含 Blender 啟動與 shader 編譯，算出來的「每幀秒數」會被灌高好幾倍。用連續 10 幀以上的穩態速度估總時間。

### PNG → H.264 for Remotion
轉檔時指定 `out_color_matrix=bt709` 並標記 bt709（primaries／trc／colorspace）；ffmpeg 預設用 BT.601 會偏色。實測來回色差 ≤ 2/255。

### Pre-rendering with handles — 預先 render 再裁切
旁白還沒定案時，可以先 render 比較長的鏡頭（例如 4 小節上限），之後依新 timing 只裁尾巴。**前提是鏡頭內的關鍵動作用「從鏡頭開頭算的絕對時間（或第幾拍）」錨定**；如果動作是照鏡頭總長度的比例排的（例如 45% 處開始組合），長度一變節奏就跑掉，只能重 render。只讓收尾的攝影機運動吃掉多餘的長度。

## Music — 本機生成節奏型配樂

1. **生成素材**：ACE-Step 1.5（MIT，model card 允許生成音樂商用）——器樂、指定 BPM 與拍號、`inference_steps=8`、多個 seed。描述詞寫風格與節奏元素（four-on-the-floor kick、crisp hi-hats、sidechained bass、bright plucks）。
2. **模型不會照「第幾秒做什麼」走**：把它當素材庫。用 Demucs 分軌，在**小節線上**重新編排出 build-up → drop → groove → break → drop → outro，接點加短交叉淡化，**不要 time-stretch**。
3. **補強節奏**：程序產生每拍的 kick、hi-hat、noise riser、crash、sub boom。**只加沒有音高的元素**——生成音樂的調性不確定，有音高的內容全部取自生成音樂本身。
4. **drop 要有落差**：每個 hit 前留半拍空拍。用 RMS 量「hit 前一拍 vs hit 第一拍」：riser 一路衝上去時兩者幾乎一樣，留空拍後落差可以到 20 dB 以上。
5. **對齊格線**：用 **drum 分軌的低頻起音**擬合格線（整首混音的 beat tracker 常鎖在反拍），kick 和格線誤差可以壓到 1 ms 以內。
6. **母帶**：highpass 40 Hz、收中低頻、2-pass loudnorm −14 LUFS。
   - ffmpeg `alimiter` 只壓 **sample peak**；噪音類的 crash＋高頻提升可能讓 **true peak** 比 sample peak 高約 1.7 dB → 用 4× 超取樣的 true-peak limiter，loudnorm 的 LRA 設大（例如 20）維持 linear 模式。
   - **mp3 編碼會讓 true peak 再升 0.5–1.2 dB**：混音用 WAV；mp3 解碼後再量 TP，必要時降一點重編。

### ACE-Step on CPU
- **bf16 先確認 CPU 支援**（AVX512-BF16／AMX）。不支援時 bf16 是軟體模擬，比 fp32 慢很多（實測 > 600 秒／seed vs fp32 約 310 秒／seed，峰值 RAM 約 15 GB）。記憶體夠就用 fp32；記憶體不夠（約 16 GB 以下）才需要 bf16。
- `uv pip install -e` 會照 pyproject 的 CUDA 釘選抓 CUDA 版 torch：CPU 機器用 `--override` 換成 `+cpu` wheel。

## Narration for a launch video — 旁白

（通用規則見 [narration-qa](narration-qa.md)；這裡是這類短片額外的經驗）
- **先驗證參考音**，不要相信檔名或 brief：
  - 語言：**確認參考音是什麼語言時**，先跑 Whisper 的語言偵測（強制指定語言時，Whisper 可能把英文直接「翻譯」成中文，看起來像中文旁白）；確定語言之後，轉寫時再指定 language（台語一律 `zh`，見 [taiwanese-taigi](taiwanese-taigi.md)）。
  - 是不是同一個人：CAM++ 聲紋比對，同一段音檔切兩段互比的值就是上限（通常約 0.7–0.8）；跨來源只有 0.3 左右就是不同人，**不要把兩段混用**（不論當主參考或 aux），否則音色會融在一起。
  - 是不是原始錄音：22.05 kHz float32 是 CosyVoice 系列（含 BreezyVoice）的輸出格式，可能是先前合成的成品——要問來源，公開用途請本人補錄 5–10 秒原音。
- **台灣華語**：BreezyVoice（台灣華語訓練）在用字和腔調上通常比 GPT-SoVITS 準，代價是 CPU 上 RTF 偏高（約 12–22，依硬體與句長而定）、長度變動較大。用你在意的「腔調來源」決定主參考音：口音主要來自主參考音，GPT-SoVITS 的 aux 只影響音色（同一個 seed 加不加 aux，長度與 ASR 結果完全相同）。
- **英文品牌名**：GPT-SoVITS 前端會刪掉「英文，中文」之間的逗號，英文詞黏到後面的中文而念壞；BreezyVoice 則常吞掉句首的「英文詞＋句號」。先用 3 個 seed 比較幾種寫法（大小寫、逗號 vs 句號、放句首或句尾）再定稿，字幕保持正確寫法。
- **同音字 vs 念錯**：所有 seed 都被 ASR 聽成同一個同音詞時，問題在 ASR，不在 TTS——寫進試聽清單，不必一直補 seed。
- 最難的句子 10 個 seed 可能只有 1 個乾淨：改寫台詞前先補到約 10 個。
- `pick_takes.py` 平手時取長度最接近中位數的 take，**不看語速和起伏**：挑完再看 verify 的語速標記，必要時手動換。
- 韻律放大（PSOLA）只在**全部句子都偏平**時才做；只有個別句子偏平時，自然度損失（UTMOS −0.25～−0.4）通常不划算，把放大版留給人耳比較就好。

## Team orchestration — 多個 agent／工作並行時

- **重工作共用一把鎖**（`flock heavy.lock <cmd>`）：TTS、ASR、音樂生成、render 一次只跑一個。
- **flock 不保證先來先用**：長 render 會一顆接一顆搶到鎖，關鍵路徑上的短工作（ASR 挑 take）被卡在後面。做法：
  - 關鍵路徑優先：長工作每顆跑完先檢查有沒有人在排隊，有就讓。
  - 更穩的是「預約」：下一個要跑的工作先寫一個預約標記，其他人看到就等。
- **`pgrep -f`／`pkill -f` 會比對到自己 shell 的命令列**：inline 寫 `pgrep -f "flock.*heavy.lock"` 永遠會找到自己而一直等；`pkill -f` 甚至會殺掉自己。改用完成標記檔，或放進腳本檔再比對更精確的字串。
- **Microsoft Store 版 Blender 跑在 Windows 那一側**：WSL 的 `ps` 看不到它，用 `tasklist.exe` 查。
- **agent 卡在權限確認時，從外面看就像當掉**：沒有程序在跑、log 不動、訊息也讀不到（它要做完當下的工具呼叫才會讀收件匣）。派工前先把會用到的安全指令（暫存資料夾裡的 `sed -i`、`ffmpeg`、自己的腳本）加進 allowlist；超過 20 分鐘沒進展就去看它的對話紀錄最後一筆。
- **訊息可能晚到**：改稿這類關鍵變更，除了發訊息，也要改共用的 brief 檔，並在對方交付時核對（例如逐字比對 timing.json 和 brief）。
- 每個 agent 在共用的 `PROGRESS.log` 每個階段寫一行，lead 才能回報進度、及早發現卡住。

## Final loudness — 成片響度
- 混音整體偏小（例如 −19 LUFS）時，loudnorm 要拉 +5 dB 以上，會從 linear 改走 dynamic 模式，加上 AAC 編碼過衝，true peak 可能超標（實測 −0.5 dBTP）。
- **loudnorm 的 TP 目標設得比交付上限低 1.5–2.5 dB**（例如交付 −1.5 就設 −3 到 −4），或先把混音電平拉到接近目標再做 loudnorm。最後一定在**編碼後的 mp4** 上量。

## Checklist — 交付前
- [ ] `beats.json`、剪輯表、混音的 drop／hit 幀數一致
- [ ] 每個切點在拍上、沒有切斷旁白（旁白結束到切點至少幾幀）
- [ ] 字標顏色、字形與官方檔案一致；畫面沒有價格、網址、placeholder
- [ ] 字幕在安全區、行尾標點去掉、不被 3D 物件蓋住
- [ ] ffprobe 規格、ebur128 −14 LUFS／TP ≤ −1.5（WAV 和最終 mp4 都量）
- [ ] 旁白 QA 清單＋「哪些還沒有人耳聽過」（腔調、像不像本人、音樂好不好聽、接縫、混音清晰度）
