# VoiceKey bootstrap для Windows.
# Запуск одной командой в PowerShell:
#   irm https://raw.githubusercontent.com/serenkiy-commits/voicekey/main/bootstrap.ps1 | iex
$ErrorActionPreference = "Stop"
$repoGit = "https://github.com/serenkiy-commits/voicekey.git"
$repoZip = "https://github.com/serenkiy-commits/voicekey/archive/refs/heads/main.zip"
$dir = Join-Path $env:USERPROFILE "voicekey"

function Have($name) { [bool](Get-Command $name -ErrorAction SilentlyContinue) }
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host "=== VoiceKey bootstrap ===" -ForegroundColor Cyan

# 1. Python
if (-not (Have "python")) {
    if (Have "winget") {
        Write-Host "Python не найден, ставлю через winget..." -ForegroundColor Yellow
        winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        Refresh-Path
    }
}
if (-not (Have "python")) {
    Write-Host "Не удалось поставить Python автоматически. Установи вручную:" -ForegroundColor Red
    Write-Host "  https://www.python.org/downloads/  (отметь 'Add python.exe to PATH')" -ForegroundColor Red
    Write-Host "затем запусти эту команду снова." -ForegroundColor Red
    return
}
Write-Host ("Python: " + (python --version)) -ForegroundColor Green

# 2. Получить проект
if (Test-Path (Join-Path $dir ".git")) {
    Write-Host "Папка voicekey уже есть, обновляю (git pull)..." -ForegroundColor Yellow
    git -C $dir pull --ff-only
} elseif (Test-Path $dir) {
    Write-Host "Папка $dir уже существует, использую её." -ForegroundColor Yellow
} elseif (Have "git") {
    git clone $repoGit $dir
} else {
    Write-Host "Скачиваю архив проекта..." -ForegroundColor Yellow
    $zip = Join-Path $env:TEMP "voicekey.zip"
    $extract = Join-Path $env:TEMP "voicekey-extract"
    Invoke-WebRequest -Uri $repoZip -OutFile $zip
    if (Test-Path $extract) { Remove-Item -Recurse -Force $extract }
    Expand-Archive -Path $zip -DestinationPath $extract -Force
    Move-Item (Join-Path $extract "voicekey-main") $dir
    Remove-Item -Force $zip
    Remove-Item -Recurse -Force $extract
}

# 3. Установка (venv + зависимости + модель)
Write-Host "Запускаю install.bat..." -ForegroundColor Cyan
& (Join-Path $dir "install.bat")

# 4. Ярлык на рабочем столе
try {
    $ws = New-Object -ComObject WScript.Shell
    $lnk = $ws.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Desktop")) "VoiceKey.lnk"))
    $lnk.TargetPath = Join-Path $dir "start.bat"
    $lnk.WorkingDirectory = $dir
    $lnk.Save()
    Write-Host "Ярлык 'VoiceKey' создан на рабочем столе." -ForegroundColor Green
} catch {
    Write-Host "Ярлык создать не удалось (не критично)." -ForegroundColor Yellow
}

Write-Host "Готово. Запуск: ярлык VoiceKey на рабочем столе или start.bat в $dir" -ForegroundColor Green
