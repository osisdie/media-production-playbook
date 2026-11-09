# Windows + WSL2

The pipeline runs inside WSL2 (Ubuntu 22.04/24.04). Windows-only tools (e.g. a Windows Blender install) are called from WSL.

## Setup
```bash
sudo apt update && sudo apt install -y ffmpeg git   # espeak-ng ships with misaki; no system package needed
bash scripts/setup/setup-linux-wsl.sh                          # repo-local .venv + Remotion deps + fonts
python3 scripts/setup/check_env.py                             # what's installed / missing
```

## Tips
- **Keep the repo, venvs and models on the WSL filesystem** (`~/...`), not under `/mnt/c`. File I/O across the boundary is 5–10× slower.
- WSL gets half of the host RAM by default. To change it, create `%USERPROFILE%\.wslconfig`:
  ```ini
  [wsl2]
  memory=20GB
  processors=8
  ```
  then `wsl --shutdown` from PowerShell.
- Open outputs from Windows: `explorer.exe "$(wslpath -w examples/course-demo/out)"`.
- Call a Windows program from WSL with a Windows-style path: `"/mnt/c/.../blender.exe" -b -P "$(wslpath -w script.py)"`. Run it from a `/mnt/c` working directory to avoid UNC-path warnings.
- Microsoft Store apps (e.g. Blender from the Store) live under `C:\Program Files\WindowsApps` and their `.exe` cannot be executed directly from WSL. Blender's Store alias `blender-launcher.exe` does work headless, but it detaches from the console — `scripts/blender/run_blender.sh` waits for a `.done`/`.failed` marker file instead of the exit code. The official portable zip is the alternative (see [blender-in-pipeline](../playbooks/blender-in-pipeline.md)).
- **Google Drive for desktop (a virtual drive such as `G:`) is not mounted in WSL** — `/mnt/g` doesn't exist and `wslpath -u 'G:\...'` can't help. Copy from Windows instead, with the WSL folder as the source. `robocopy` is re-runnable (no extra nesting on a second run) and prints file and byte totals; exit codes 0–7 mean success:
  ```bash
  SRC=$(wslpath -w ~/path/to/delivery-folder)
  (cd /mnt/c && cmd.exe /c robocopy "$SRC" "G:\My Drive\some\folder\delivery-folder" /E)
  ```
  The subshell keeps your current directory. Then compare both sides:
  - Windows: `Get-ChildItem -LiteralPath 'G:\My Drive\some\folder\delivery-folder' -Recurse -File | Measure-Object -Property Length -Sum` (Count and Sum)
  - WSL: `find ~/path/to/delivery-folder -type f -printf '%s\n' | awk '{n++; s+=$1} END {print n, s}'` (file count and bytes — `du` would also count directory entries)

  (With PowerShell `Copy-Item -Recurse`, the result depends on whether the destination already exists — a second run nests one level deeper. Paths containing a single quote also break PowerShell single-quoted strings.) Mounting the drive with `sudo mkdir -p /mnt/g && sudo mount -t drvfs G: /mnt/g` works too, but needs sudo and is gone after a WSL restart unless added to `/etc/fstab`.
- No NVIDIA GPU? Everything here works CPU-only; see [low-resource](low-resource.md).
