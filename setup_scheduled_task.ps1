# ============================================
# Setup Windows Task Scheduler for Live Trading
# Run this script as Administrator to create the scheduled task
# ============================================

$TaskName = "RSI_Live_Trading_510050"
$Description = "Run RSI Live Trading on 510050.SH at 9:25 AM"

# Path to the batch file
$BatchPath = "C:\Users\Rui Ma\Desktop\real quant\schedule_live_trading.bat"
$WorkingDir = "C:\Users\Rui Ma\Desktop\real quant"

# Schedule for tomorrow at 9:25 AM
$TriggerTime = "09:25"

Write-Host "Creating Scheduled Task: $TaskName" -ForegroundColor Cyan
Write-Host "Trigger Time: $TriggerTime" -ForegroundColor Cyan

# Create the action
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatchPath`"" -WorkingDirectory $WorkingDir

# Create trigger for daily at 9:25 AM (you can modify to run once)
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime

# Settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
try {
    # Remove existing task if exists
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed existing task." -ForegroundColor Yellow
    }
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description $Description
    
    Write-Host ""
    Write-Host "SUCCESS! Task created: $TaskName" -ForegroundColor Green
    Write-Host "The script will run daily at $TriggerTime" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT REMINDERS:" -ForegroundColor Yellow
    Write-Host "1. Make sure Mini-QMT is running and logged in before 9:25 AM" -ForegroundColor Yellow
    Write-Host "2. Keep your computer on and not in sleep mode" -ForegroundColor Yellow
    Write-Host "3. Check log file: live_trading_510050_YYYYMMDD.log for results" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To run once (tomorrow only), delete the task after it runs:" -ForegroundColor Cyan
    Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Cyan
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Try running this script as Administrator" -ForegroundColor Red
}
