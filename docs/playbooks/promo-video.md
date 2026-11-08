# Promo video — 9:16 宣傳短片（Remotion）

> 1080×1920、30 fps 的 App／產品宣傳短片：模擬 App UI、多版本素材分流、本地 AI 配音與音樂、ducking、響度正規化、審查清單。範例：[`examples/promo-demo`](../../examples/promo-demo)。

> **範例實作了哪些**：`examples/promo-demo` 示範了旁白驅動的鏡頭、模擬 App 畫面、字幕安全區、多語言版本、Blender 3D 開場與 2D 退回、響度後製。下面的**音樂與 ducking、`showSafe` 疊層、素材 manifest／prep 腳本、overlay 轉場、CBR 規格**是實務上的一般做法，範例沒有實作（歡迎 PR）。

**原則：Remotion 原始碼（鏡頭表＋旁白 timing）是時間的唯一依據。** 前製文件（script／storyboard）常常落後於實作；交付前要列出文件和實作的差異。

## Spec — 成片規格

| 項目 | 值 |
|---|---|
| 畫面 | 1080×1920（9:16），30 fps 恆定 |
| 視訊 | H.264 High、yuv420p、bt709、tv range、`+faststart`；平台要求時用 CBR（例如 12 Mbps），範例 `post.sh` 用 CRF 18 |
| 音訊 | AAC 48 kHz 立體聲（範例 192k；有音樂時建議 256k 以上） |
| 響度 | Integrated **−14 LUFS**、True Peak **≤ −1.5 dBTP**（2-pass loudnorm，`linear=true`） |
| 節奏 | 例如 120 BPM＝每拍 15 幀；主要切點盡量落在拍點，再為了配旁白微調 |

## Remotion structure — 專案結構

- **鏡頭表**：`{ id, from, to, exit?: 'cut'|'left'|'up'|'zoom', node }`，時間用絕對秒數。下一顆鏡頭提早約 6 幀疊進來，而且它自己的時鐘比前一顆超前幾幀，轉場時畫面不會空白。
- **Overlay 層**：白閃、圓形擴散、漏光、色塊掃過——用來接品牌鏡頭或高潮。
- **`showSafe` prop**：打開時疊紅色禁區＋綠色安全框，抽幀時 debug 用。
- **素材元件**：從 `public/shots/<id>.png|mp4` 依序找；找不到就畫明顯的 PLACEHOLDER，而不是空白。
- **prep 腳本**：掃描素材、音樂、旁白，產生 manifest；**換素材、音樂、旁白後一定要重跑**，否則成片會出現 PLACEHOLDER 或沒有音樂。

## Mock UI — 模擬 App 畫面

- 不放真實螢幕錄影：App 畫面直接用 React 畫。這樣不會出現價格、真人資料，而且每幀都可控。
- 手機框放大時用 `transformOrigin: center top`，否則水平中心會偏離畫面中軸。內容要填滿手機框，留白太多在手機上看不清楚。
- 字幕 pill 放在手機上方，字級 ≥ 48 px，每行用陣列寫死，不自動換行。
- 點擊動畫（手指圓點下壓＋外擴圓環）的目標**避開最右欄**，那裡會被短影音平台的右側按鈕蓋住。
- 文案和畫面不能暗示產品做不到的事。

## Safe area — 安全區

- 以 x=540 為中軸；資訊性元素（字幕、CTA、結果卡）放在平台 UI 不會蓋到的範圍（例如 y 288–1480，左右各留 90）。
- 每個平台的 UI 不同：換專案時重新決定，並用帶 safe 疊層的抽幀實際檢查。
- 全幅背景圖可以滿版出血。

## Variants — 多版本素材分流

- 例如不同語言或受眾版本：每支 composition 傳一個 variant 參數，**所有會顯示人物或文案的元件都要接這個參數**。漏接就會沿用預設版本的內容，是最常見的 review bug。
- 素材 id 依版本分開命名，**不要讓某版本 fallback 到另一版本的圖**。
- 版本專屬的文字集中在一個表裡（`COPY[variant]`），不要散落在元件中。
- 調整某版本的對位參數時，其他版本的路徑不能動；改完抽幀確認其他版本沒被影響。
- 旁白和音樂可以跨版本共用。

## AI assets — AI 素材

- 人物一律是 AI 生成的虛構臉孔，同一支片保持同一個角色。prompt 結尾加 `No text, no logos, no brand names, no watermark`。
- 原圖留在 `ai-source/`，處理後放 `public/shots/`；換掉前先備份舊版。

## Narration — 旁白

1. 逐句合成（模型只載入一次），自回歸引擎每句多抽幾個 take。
2. ASR 驗字＋拖音＋長度檢查（[narration QA](narration-qa.md)）。
3. 組裝：去頭尾靜音 → 每句 −20 LUFS → 塞進鏡頭 slot（可提早一點開始、最多加速到約 1.12×）→ 輸出每句 wav＋timing.json。
4. **塞不進 slot 時改台詞，不要硬加速**；在 timing 的 note 寫明，並同步改畫面字幕。

## Music & ducking — 音樂與 ducking

- 本地音樂生成（例如 ACE-Step，MIT）：器樂、固定 BPM 與調性、每支抽數個 seed；caption 不要太長；生成長度比成片多幾秒。
- 選 seed 的客觀指標：tempo 準確、拍點相位接近 0、第一個 drop 早、中段沒有空洞、響度變異低——並註明「還沒有人實際聽過」。
- 後製：highpass 40 Hz → 低頻減一點 → 高頻加一點 → 精準裁長 → 淡入淡出 → 2-pass loudnorm −14 LUFS。
- Ducking：沒有旁白時音樂增益約 0.6；有旁白時約 0.14（壓低約 12–13 dB）；每句旁白前 0.15 秒 attack、後 0.3 秒 release，多句重疊取最小值；片尾最後幾幀淡出。
- 授權另外記錄：選用的模型、被排除的模型（例如 CC-BY-NC 的不能商用）。

## Render & post — 渲染與後製

- 一次 render 一支，`concurrency: 1`；重新渲染前把舊成片存到 `out/prev-roundN/`。
- 後製用 `scripts/video/post.sh`（2-pass loudnorm、H.264 High、bt709、AAC 48k、faststart）。
- 驗證：`ffprobe`（解析度、30/1、yuv420p、h264 High、aac 48k、長度精準）＋`ebur128`（I≈−14、TP≤−1.5）。
- 每輪在 `NOTES.md` 記錄：哪裡錯 → 怎麼修 → 實測數字 → 產物路徑 → 哪些版本沒變。

## Delivery gotchas — 交付
- 用 API 上傳到雲端儲存時，確認 MP4 的 MIME type 是 `video/mp4`；被存成其他類型時，網頁預覽可能無法播放。
- GitHub README 不會內嵌 repo 裡的 MP4：要在網頁的留言框或編輯器上傳，拿到 `user-attachments` 網址單獨一行貼上，才會變成播放器。GIF 留給不能播影片的地方。
- 不擅自分享、刪除或覆蓋雲端上的檔案。

## Review checklist — 每輪交付前

> 技術清單之外，宣傳片一定要過**行銷審查**（吸引力、質感、文案與畫面一致、品牌色實測）：見 [marketing-review](marketing-review.md)。

抽幀：結尾卡（CTA 剛出現、靜止、最後一幀）、結果卡、各版本的人物鏡頭；有改共用元件時另外抽沒改的版本證明沒有回歸。用像素量尺寸（例如卡片寬度、中心 x）。

1. **版本參數一路傳下去**：搜尋寫死的預設版本字串有沒有出現在其他版本的路徑。
2. **素材 fallback**：成片不能出現 PLACEHOLDER。
3. **尺寸一致**：同一種元件在各版本規格相同；標題 ≥ 48 px、小字 ≥ 28 px。
4. **安全區**：字幕、CTA、結果卡在安全框內；點擊目標避開右側按鈕列。
5. **字幕和旁白一致**：旁白改字，字幕跟著改。
6. **時間**：總幀數＝最後一顆鏡頭的結束 × fps；音樂不短於片長。
7. **音訊**：ducking 後旁白清楚、沒有 clipping；響度符合規格。
8. **規格與檔名**。
9. **文件差異**：script／storyboard 和實作不同的地方列出來。
10. **宣稱**：不顯示價格；不暗示產品做不到的功能；CTA 文字正確。

審查結果分 HIGH／MEDIUM／LOW；修正後在 NOTES 記錄「What was wrong / Fix / Measured / Artifacts」。
