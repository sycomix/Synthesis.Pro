$pythonExe = "D:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\runtime\python\python.exe"
$updaterScript = "D:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\rag_integration\rag_auto_updater.py"
$taskName = "SynthesisProRAGUpdater"

Write-Host "Installing RAG Auto Updater as scheduled task..."
Write-Host ""

$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$updaterScript`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
    Write-Host "[OK] RAG Auto Updater installed successfully!" -ForegroundColor Green
    Write-Host "It will start automatically when you log in to Windows."
    Write-Host ""
    Write-Host "To start it now: .\start_rag_auto_updater.bat"
    Write-Host "To remove it: .\uninstall_rag_auto_updater.bat"
} catch {
    Write-Host "[ERROR] Failed to install: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
