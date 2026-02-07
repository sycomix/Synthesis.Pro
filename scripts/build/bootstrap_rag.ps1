# Synthesis.Pro RAG Bootstrap Script
# Automates Python setup and RAG database initialization

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Synthesis.Pro RAG Bootstrap" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Step 1: Check for Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow

$pythonCommand = $null
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "C:\Python39\python.exe"
)

foreach ($path in $pythonPaths) {
    try {
        $version = & $path --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $version -match "Python 3\.(9|1[0-9])") {
            $pythonCommand = $path
            Write-Host "  ✓ Found Python: $version at $path" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCommand) {
    Write-Host "  ✗ Python 3.9+ not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python 3.9+ is required. Please install from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installation tips:" -ForegroundColor Yellow
    Write-Host "  1. Download Python 3.11 (recommended)" -ForegroundColor White
    Write-Host "  2. Check 'Add Python to PATH' during installation" -ForegroundColor White
    Write-Host "  3. Restart terminal after installation" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Verify pip
Write-Host ""
Write-Host "[2/5] Verifying pip..." -ForegroundColor Yellow

try {
    & $pythonCommand -m pip --version | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ pip is available" -ForegroundColor Green
    } else {
        throw "pip check failed"
    }
} catch {
    Write-Host "  ✗ pip not available" -ForegroundColor Red
    Write-Host "  Installing pip..." -ForegroundColor Yellow
    & $pythonCommand -m ensurepip --default-pip
}

# Step 3: Install Python dependencies
Write-Host ""
Write-Host "[3/5] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes on first run..." -ForegroundColor Gray

$serverReq = "Assets\Synthesis.Pro\Server\requirements.txt"
$ragReq = "Assets\Synthesis.Pro\RAG\requirements.txt"

if (Test-Path $serverReq) {
    Write-Host "  Installing Server requirements..." -ForegroundColor Cyan
    & $pythonCommand -m pip install -r $serverReq --quiet --upgrade
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Server dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Some server dependencies may have failed" -ForegroundColor Yellow
    }
}

if (Test-Path $ragReq) {
    Write-Host "  Installing RAG requirements..." -ForegroundColor Cyan
    & $pythonCommand -m pip install -r $ragReq --quiet --upgrade
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ RAG dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Some RAG dependencies may have failed" -ForegroundColor Yellow
    }
}

# Step 4: Initialize databases
Write-Host ""
Write-Host "[4/5] Initializing RAG databases..." -ForegroundColor Yellow

$initScript = "Assets\Synthesis.Pro\RAG\init_databases.py"

if (Test-Path $initScript) {
    & $pythonCommand $initScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Databases initialized successfully" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Database initialization had warnings" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ Init script not found: $initScript" -ForegroundColor Red
}

# Step 5: Verify installation
Write-Host ""
Write-Host "[5/5] Verifying installation..." -ForegroundColor Yellow

$publicDb = "Assets\Synthesis.Pro\Server\synthesis_public.db"
$privateDb = "Assets\Synthesis.Pro\Server\synthesis_private.db"

$allGood = $true

if (Test-Path $publicDb) {
    $size = (Get-Item $publicDb).Length
    Write-Host "  ✓ Public database exists ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Public database not found" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path $privateDb) {
    $size = (Get-Item $privateDb).Length
    Write-Host "  ✓ Private database exists ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Private database not found" -ForegroundColor Red
    $allGood = $false
}

# Summary
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan

if ($allGood) {
    Write-Host "Bootstrap Complete! 🚀" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Open Unity Editor" -ForegroundColor White
    Write-Host "  2. Menu: Tools → Synthesis → Synthesis Pro" -ForegroundColor White
    Write-Host "  3. Start chatting with your AI partner!" -ForegroundColor White
    Write-Host ""
    Write-Host "The RAG system is ready for partnership mode! 🤝" -ForegroundColor Cyan
} else {
    Write-Host "Bootstrap completed with warnings ⚠" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please review the output above for any errors." -ForegroundColor White
    Write-Host "You may need to manually resolve some issues." -ForegroundColor White
}

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
