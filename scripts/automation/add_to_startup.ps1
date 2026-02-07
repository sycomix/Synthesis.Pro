# Add RAG Auto Updater to Windows Startup (no admin needed)

$startupFolder = [Environment]::GetFolderPath('Startup')
$pythonExe = "D:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\runtime\python\python.exe"
$updaterScript = "D:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\rag_integration\rag_auto_updater.py"

$WshShell = New-Object -ComObject WScript.Shell
$shortcutPath = "$startupFolder\SynthesisProRAGUpdater.lnk"
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonExe
$shortcut.Arguments = "`"$updaterScript`""
$shortcut.WorkingDirectory = "D:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\rag_integration"
$shortcut.WindowStyle = 7  # Minimized
$shortcut.Description = "Synthesis.Pro RAG Auto Updater"
$shortcut.Save()

Write-Host "[OK] Added to Windows Startup!" -ForegroundColor Green
Write-Host "Location: $shortcutPath"
Write-Host ""
Write-Host "The RAG updater will start automatically on next login."
Write-Host "It's already running now (PID: $(Get-Process python -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Id))"
