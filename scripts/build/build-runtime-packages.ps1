# Build Runtime Packages for Asset Store Download-on-Demand
# Creates: python-embedded.zip, node-embedded.zip, models.zip

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host "`n=== Synthesis.Pro Runtime Package Builder ===" -ForegroundColor Cyan
Write-Host "Building packages for GitHub Pages hosting`n" -ForegroundColor Gray

# Create temp build directory
$buildDir = ".\temp-runtime-build"
if (Test-Path $buildDir) {
    Remove-Item $buildDir -Recurse -Force
}
New-Item -ItemType Directory -Path $buildDir | Out-Null

# Output directory
$outputDir = ".\runtime-packages"
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

Write-Host "[1/3] Building python-embedded.zip..." -ForegroundColor Yellow

# Download Python embedded if needed
$pythonZip = "$buildDir\python-3.11.0-embed-amd64.zip"
if (!(Test-Path $pythonZip)) {
    Write-Host "  Downloading Python 3.11.0 embedded..." -ForegroundColor Gray
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.0/python-3.11.0-embed-amd64.zip" `
        -OutFile $pythonZip
}

# Extract Python
$pythonTemp = "$buildDir\python"
Expand-Archive -Path $pythonZip -DestinationPath $pythonTemp -Force
Write-Host "  Extracted Python base runtime" -ForegroundColor Gray

# Copy site-packages from existing installation
$existingPython = ".\Assets\Synthesis.Pro\KnowledgeBase\python"
if (Test-Path "$existingPython\Lib\site-packages") {
    Write-Host "  Copying site-packages from existing installation..." -ForegroundColor Gray

    # Create Lib directory in temp
    $libDir = "$pythonTemp\Lib"
    if (!(Test-Path $libDir)) {
        New-Item -ItemType Directory -Path $libDir | Out-Null
    }

    # Copy site-packages
    Copy-Item -Path "$existingPython\Lib\site-packages" `
        -Destination $libDir `
        -Recurse -Force

    Write-Host "  Copied site-packages" -ForegroundColor Gray
}

# Create python-embedded.zip
$pythonOutput = "$outputDir\python-embedded.zip"
if (Test-Path $pythonOutput) {
    Remove-Item $pythonOutput -Force
}

Write-Host "  Creating python-embedded.zip..." -ForegroundColor Gray
Compress-Archive -Path "$pythonTemp\*" -DestinationPath $pythonOutput -CompressionLevel Optimal

$pythonSize = [math]::Round((Get-Item $pythonOutput).Length / 1MB, 2)
Write-Host "  ✓ python-embedded.zip created ($pythonSize MB)`n" -ForegroundColor Green

# ===== NODE.JS =====
Write-Host "[2/3] Building node-embedded.zip..." -ForegroundColor Yellow

# Download Node.js if needed
$nodeZip = "$buildDir\node-v18.19.0-win-x64.zip"
if (!(Test-Path $nodeZip)) {
    Write-Host "  Downloading Node.js 18.19.0..." -ForegroundColor Gray
    Invoke-WebRequest -Uri "https://nodejs.org/dist/v18.19.0/node-v18.19.0-win-x64.zip" `
        -OutFile $nodeZip
}

# Extract Node.js
$nodeTemp = "$buildDir\node-extract"
Expand-Archive -Path $nodeZip -DestinationPath $nodeTemp -Force

# Node.js extracts to node-v18.19.0-win-x64 folder, we just need node.exe
$nodeFinal = "$buildDir\node"
New-Item -ItemType Directory -Path $nodeFinal | Out-Null
Copy-Item -Path "$nodeTemp\node-v18.19.0-win-x64\node.exe" -Destination $nodeFinal

Write-Host "  Extracted node.exe" -ForegroundColor Gray

# Create node-embedded.zip
$nodeOutput = "$outputDir\node-embedded.zip"
if (Test-Path $nodeOutput) {
    Remove-Item $nodeOutput -Force
}

Compress-Archive -Path "$nodeFinal\node.exe" -DestinationPath $nodeOutput -CompressionLevel Optimal

$nodeSize = [math]::Round((Get-Item $nodeOutput).Length / 1MB, 2)
Write-Host "  ✓ node-embedded.zip created ($nodeSize MB)`n" -ForegroundColor Green

# ===== MODELS =====
Write-Host "[3/3] Building models.zip..." -ForegroundColor Yellow

$modelsSource = ".\Synthesis.Pro\Server\models"
if (Test-Path $modelsSource) {
    $modelsOutput = "$outputDir\models.zip"
    if (Test-Path $modelsOutput) {
        Remove-Item $modelsOutput -Force
    }

    Write-Host "  Compressing AI models..." -ForegroundColor Gray
    Compress-Archive -Path "$modelsSource\*" -DestinationPath $modelsOutput -CompressionLevel Optimal

    $modelsSize = [math]::Round((Get-Item $modelsOutput).Length / 1MB, 2)
    Write-Host "  ✓ models.zip created ($modelsSize MB)`n" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Models directory not found: $modelsSource" -ForegroundColor Yellow
    Write-Host "  Skipping models.zip creation`n" -ForegroundColor Yellow
}

# Cleanup
Write-Host "Cleaning up temporary files..." -ForegroundColor Gray
Remove-Item $buildDir -Recurse -Force

# Summary
Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "Runtime packages created in: $outputDir`n" -ForegroundColor Gray
Get-ChildItem $outputDir -Filter *.zip | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  $($_.Name) - $size MB" -ForegroundColor White
}

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Upload these files to GitHub Pages (see GITHUB_PAGES_SETUP.md)" -ForegroundColor Gray
Write-Host "2. Test FirstTimeSetup in Unity" -ForegroundColor Gray
Write-Host "3. Ship to beta testers!`n" -ForegroundColor Gray
