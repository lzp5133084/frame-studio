# 下载内置 FFmpeg（essentials 构建）到 tools/ffmpeg
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $root "tools"
$zip = Join-Path $tools "ffmpeg.zip"
$dest = Join-Path $tools "ffmpeg"

if (Test-Path (Join-Path $dest "bin\ffmpeg.exe")) {
    Write-Host "FFmpeg 已存在：$dest" -ForegroundColor Green
    exit 0
}
New-Item -ItemType Directory -Force -Path $tools | Out-Null
Write-Host "正在下载 FFmpeg ..." -ForegroundColor Cyan
curl.exe -L -o $zip "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" --progress-bar
Expand-Archive -Path $zip -DestinationPath $tools -Force
$dir = Get-ChildItem $tools -Directory | Where-Object Name -like "ffmpeg-*" | Select-Object -First 1
Rename-Item -Path $dir.FullName -NewName "ffmpeg" -Force
Remove-Item $zip
Write-Host "完成：" (Join-Path $dest "bin\ffmpeg.exe") -ForegroundColor Green
