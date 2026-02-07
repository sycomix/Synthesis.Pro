# Build Python with RAG deps
$ErrorActionPreference = "Stop"
Write-Host "Building Python RAG package..."

$buildDir = ".\temp-python-build"
if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
New-Item -ItemType Directory -Path $buildDir | Out-Null

Write-Host "Downloading Python..."
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.0/python-3.11.0-embed-amd64.zip" -OutFile "$buildDir\python.zip"

Write-Host "Extracting..."
Expand-Archive -Path "$buildDir\python.zip" -DestinationPath "$buildDir\python" -Force

Write-Host "Enabling site-packages..."
$pth = "$buildDir\python\python311._pth"
(Get-Content $pth) -replace '#import site', 'import site' | Set-Content $pth

Write-Host "Installing pip..."
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$buildDir\get-pip.py"
& "$buildDir\python\python.exe" "$buildDir\get-pip.py" --no-warn-script-location | Out-Null

Write-Host "Installing packages..."
& "$buildDir\python\python.exe" -m pip install numpy scipy bm25s sentence-transformers scikit-learn --quiet

Write-Host "Testing..."
"import numpy, scipy, bm25s, sentence_transformers; print('OK')" | & "$buildDir\python\python.exe"

Write-Host "Packaging..."
$outDir = ".\runtime-packages"
if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
Compress-Archive -Path "$buildDir\python\*" -DestinationPath "$outDir\python-embedded-rag.zip" -Force

Write-Host "Done! Check runtime-packages folder"
Remove-Item $buildDir -Recurse -Force
