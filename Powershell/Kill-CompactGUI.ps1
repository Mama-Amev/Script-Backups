# Kill-CompactGUI.ps1
# Force closes the CompactGUI process if it is running

$processName = "CompactGUI"

$process = Get-Process -Name $processName -ErrorAction SilentlyContinue

if ($process) {
    Stop-Process -Name $processName -Force
    Write-Host "CompactGUI has been force closed." -ForegroundColor Green
} else {
    Write-Host "CompactGUI is not currently running." -ForegroundColor Yellow
}
