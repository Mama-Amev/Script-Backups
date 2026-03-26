$WatcherJson = "$env:LOCALAPPDATA\IridiumIO\CompactGUI\watcher.json"
$Algorithm   = "XPRESS8K"
$KillGUI     = $false

if (-not (Test-Path $WatcherJson)) {
    Write-Host "ERROR: watcher.json not found at: $WatcherJson" -ForegroundColor Red
    pause; exit 1
}

$watcherData = Get-Content $WatcherJson -Raw | ConvertFrom-Json

$folders = if ($watcherData -is [array]) { $watcherData }
           elseif ($watcherData.Folders)  { $watcherData.Folders }
           elseif ($watcherData.folders)  { $watcherData.folders }
           else { @($watcherData) }

if ($folders.Count -eq 0) { Write-Host "No watched folders found."; pause; exit 0 }

$success = 0; $failed = 0; $startTime = Get-Date

foreach ($entry in $folders) {
    $folderPath = if ($entry.Folder)          { $entry.Folder }
                  elseif ($entry.FolderPath)  { $entry.FolderPath }
                  elseif ($entry -is [string]) { $entry }
                  else { $null }

    if (-not $folderPath -or -not (Test-Path $folderPath)) {
        Write-Host "[SKIP] $folderPath" -ForegroundColor Yellow
        $failed++; continue
    }

    Write-Host "[COMPRESSING] $folderPath"
    & compact.exe /C /S /A /I /EXE:$Algorithm "$folderPath\*" 2>&1 | Out-Null
    Write-Host "[DONE]" -ForegroundColor Green
    $success++
}

$elapsed = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
Write-Host "`nDone — $success compressed, $failed skipped ($elapsed min)"

Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon    = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.ShowBalloonTip(5000, "CompactGUI Refresh Complete", "$success folder(s) in $elapsed min", [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 2
$notify.Dispose()

if ($KillGUI) { Get-Process -Name "CompactGUI" -ErrorAction SilentlyContinue | Stop-Process -Force }

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
