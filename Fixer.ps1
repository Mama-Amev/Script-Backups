# Sole purpose is to restart file explorer and run
# sfc /scannow due to my own machine having occasional hiccups
# with file explorer.

# Self-elevate if not running as Administrator
$IsAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    Start-Process powershell.exe `
        -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" `
        -Verb RunAs
    exit
}

Write-Host "Running with administrative privileges."

Write-Host "Restarting Windows Explorer..."

# Stop Explorer the same way Task Manager does (no shutdown prompt)
Get-Process explorer -ErrorAction SilentlyContinue | Stop-Process -Force

Start-Sleep -Seconds 2

# Relaunch Explorer
Start-Process explorer.exe

Write-Host "Explorer restarted."
Start-Sleep -Seconds 5

Write-Host "Running System File Checker (sfc /scannow)..."
Start-Process -FilePath "sfc.exe" -ArgumentList "/scannow" -Wait -NoNewWindow

Write-Host "SFC scan completed."
