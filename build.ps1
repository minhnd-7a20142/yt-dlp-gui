$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = (Get-Command python -ErrorAction Stop).Source

& $pythonExe -m PyInstaller --version *> $null
if ($LASTEXITCODE -ne 0) {
    & $pythonExe -m pip install --user --upgrade pyinstaller
}

& $pythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "YT-DLP-GUI" `
    --distpath (Join-Path $projectDir "dist") `
    --workpath (Join-Path $projectDir "build") `
    --specpath $projectDir `
    (Join-Path $projectDir "app.py")

$isccCommand = Get-Command iscc.exe -ErrorAction SilentlyContinue
$isccPath = if ($isccCommand) { $isccCommand.Source } else { $null }
if (-not $isccPath) {
    $candidate = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (Test-Path -LiteralPath $candidate) {
        $isccPath = $candidate
    }
}
if (-not $isccPath) {
    $candidate = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    if (Test-Path -LiteralPath $candidate) {
        $isccPath = $candidate
    }
}

if (-not $isccPath) {
    throw "Không tìm thấy Inno Setup 6. Cài bằng: winget install --id JRSoftware.InnoSetup --exact"
}

Push-Location $projectDir
try {
    & $isccPath (Join-Path $projectDir "installer.iss")
}
finally {
    Pop-Location
}

Write-Host "Hoàn tất: $projectDir\release\YT-DLP-GUI-Setup-1.0.0.exe"
