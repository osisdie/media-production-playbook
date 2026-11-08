# Blender in the pipeline — 用 Blender 補 3D 鏡頭

> Blender（GPL）只當外部工具呼叫：用 Python（`bpy`）腳本以無頭模式渲染，輸出透明背景的影格，再交給 Remotion 合成。範例：[`examples/blender-demo`](../../examples/blender-demo)，腳本在 [`scripts/blender/`](../../scripts/blender)。

## When 3D is worth it — 什麼時候值得用 3D
- **產品轉台（turntable）**：還沒有實體照片或想要乾淨的棚拍感。
- **立體標題、Logo reveal**：開場 3–6 秒最有效。
- **資料視覺化**：3D 長條、地圖擠出。
- 不值得的情況：整支片都 3D（CPU 機器渲染太久）、需要寫實人物。

## Headless render — 無頭渲染

```bash
scripts/blender/find_blender.sh                          # 印出找到的 Blender 執行檔
"$(scripts/blender/find_blender.sh)" -b -P scripts/blender/render_scene.py -- --help
```
- `-b`：背景模式（不開 UI）；`-P script.py`：執行腳本；`--` 之後的參數交給腳本自己解析。
- 全部程序產生（幾何、材質、燈光都在腳本裡建），不依賴 `.blend` 或外部素材，沒有授權問題，也方便版控。

## Finding Blender on each OS — 各 OS 的執行檔

`find_blender.sh` 依序找：`$BLENDER` 環境變數 → macOS `/Applications/Blender.app/Contents/MacOS/Blender` → PATH 上的 `blender` → WSL 上的 Windows 安裝。

**WSL ＋ Microsoft Store 版的坑**：Store 版的 `blender.exe` 在 `C:\Program Files\WindowsApps\…`，從 WSL 直接執行會 Permission denied。它的 `blender-launcher.exe`（`%LOCALAPPDATA%\Microsoft\WindowsApps\`）可以用 `-b -P` 無頭執行，但會自己脫離終端機，看不到輸出也拿不到結束碼 → `scripts/blender/run_blender.sh` 讓 bpy 腳本在結束時寫 `.done`／`.failed` 標記檔，外面輪詢標記檔判斷成功與否。另一個做法是解壓官方 portable zip 到使用者資料夾（不需要系統管理員權限），路徑用 `wslpath -w` 轉換。

實測：EEVEE 16 samples、1080×1920、180 幀，在 AMD 內顯的筆電上約 95 秒。

## Compositing in Remotion — 交給 Remotion 合成
- 輸出 RGBA PNG 序列 → 轉成帶 alpha 的影片（ProRes 4444 `.mov` 或 VP9 alpha `.webm`）→ 在 Remotion 用 `<OffthreadVideo transparent>` 疊在背景上。
- 先實際 render 一幀確認 alpha 有保留，再做整段。
- 讓 Remotion 端在找不到 3D 素材時退回 2D 畫面，沒裝 Blender 的人也能 render 範例。

## Low-resource settings — 低資源設定
- 先用 EEVEE、低取樣、解析度減半出草稿，確認構圖和動作後再出最終版。
- CPU 機器上 Cycles 很慢；有 GPU（AMD HIP、Apple Metal、NVIDIA）時才考慮 Cycles。
- 6 秒 × 30 fps＝180 幀：先 render 每 10 幀一張檢查，再 render 全部。
- 和 TTS、ASR、Remotion render 一樣，一次只跑一個重工作。
