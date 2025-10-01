#Requires -Version 5.1

<#
.SYNOPSIS
    Comprehensive logging module for AzerothCore AutoBuilder

.DESCRIPTION
    Provides structured logging with multiple levels, file rotation, and console output.

.NOTES
    Author: AzerothCore AutoBuilder
    Version: 2.0.0
#>

enum LogLevel {
    Debug = 0
    Info = 1
    Warning = 2
    Error = 3
}

class Logger {
    [string]$LogFile
    [LogLevel]$MinLevel
    [int]$MaxLogSizeMB
    [string]$ScriptName

    Logger([string]$LogFile, [LogLevel]$MinLevel = [LogLevel]::Info, [int]$MaxLogSizeMB = 10) {
        $this.LogFile = $LogFile
        $this.MinLevel = $MinLevel
        $this.MaxLogSizeMB = $MaxLogSizeMB
        $this.ScriptName = $MyInvocation.ScriptName

        # Ensure log directory exists
        $logDir = Split-Path -Parent $LogFile
        if (-not (Test-Path $logDir)) {
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        }

        # Rotate log if it's too large
        $this.RotateLogIfNeeded()
    }

    [void] RotateLogIfNeeded() {
        if (Test-Path $this.LogFile) {
            $logSize = (Get-Item $this.LogFile).Length / 1MB
            if ($logSize -gt $this.MaxLogSizeMB) {
                $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
                $rotatedFile = $this.LogFile -replace '\.log$', "_$timestamp.log"
                Move-Item -Path $this.LogFile -Destination $rotatedFile
                $this.WriteLog([LogLevel]::Info, "Log rotated to $rotatedFile")
            }
        }
    }

    [void] WriteLog([LogLevel]$Level, [string]$Message, [Exception]$Exception = $null) {
        if ($Level -lt $this.MinLevel) {
            return
        }

        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        $levelStr = $Level.ToString().PadRight(7)
        $caller = $this.GetCallerInfo()
        
        $logEntry = "[$timestamp] [$levelStr] [$caller] $Message"
        
        if ($Exception) {
            $logEntry += "`nException: $($Exception.Message)"
            $logEntry += "`nStack Trace: $($Exception.StackTrace)"
        }

        # Write to console with colors
        $this.WriteToConsole($Level, $logEntry)

        # Write to file
        try {
            Add-Content -Path $this.LogFile -Value $logEntry -Encoding UTF8
        }
        catch {
            Write-Warning "Failed to write to log file: $($_.Exception.Message)"
        }
    }

    [void] WriteToConsole([LogLevel]$Level, [string]$Message) {
        $color = switch ($Level) {
            ([LogLevel]::Debug) { "Gray" }
            ([LogLevel]::Info) { "White" }
            ([LogLevel]::Warning) { "Yellow" }
            ([LogLevel]::Error) { "Red" }
        }

        Write-Host $Message -ForegroundColor $color
    }

    [string] GetCallerInfo() {
        $callStack = Get-PSCallStack
        if ($callStack.Count -gt 2) {
            $caller = $callStack[2]
            return "$($caller.FunctionName):$($caller.ScriptLineNumber)"
        }
        return "Main"
    }

    [void] Debug([string]$Message) {
        $this.WriteLog([LogLevel]::Debug, $Message)
    }

    [void] Info([string]$Message) {
        $this.WriteLog([LogLevel]::Info, $Message)
    }

    [void] Warning([string]$Message) {
        $this.WriteLog([LogLevel]::Warning, $Message)
    }

    [void] Error([string]$Message, [Exception]$Exception = $null) {
        $this.WriteLog([LogLevel]::Error, $Message, $Exception)
    }

    [void] LogProgress([string]$Activity, [string]$Status, [int]$PercentComplete = -1) {
        $message = "PROGRESS: $Activity - $Status"
        if ($PercentComplete -ge 0) {
            $message += " ($PercentComplete%)"
        }
        $this.Info($message)
        
        if ($PercentComplete -ge 0) {
            Write-Progress -Activity $Activity -Status $Status -PercentComplete $PercentComplete
        }
    }

    [void] LogProgressComplete([string]$Activity) {
        Write-Progress -Activity $Activity -Completed
        $this.Info("PROGRESS: $Activity - Completed")
    }
}

# Global logger instance
$Global:Logger = $null

function Initialize-Logger {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$LogFile,
        
        [Parameter()]
        [LogLevel]$MinLevel = [LogLevel]::Info,
        
        [Parameter()]
        [int]$MaxLogSizeMB = 10
    )

    $Global:Logger = [Logger]::new($LogFile, $MinLevel, $MaxLogSizeMB)
    $Global:Logger.Info("Logger initialized. Log file: $LogFile")
}

function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [LogLevel]$Level,
        
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter()]
        [Exception]$Exception
    )

    if ($Global:Logger) {
        $Global:Logger.WriteLog($Level, $Message, $Exception)
    } else {
        Write-Host "[$Level] $Message" -ForegroundColor Yellow
    }
}

function Write-LogDebug { param([string]$Message) Write-Log -Level Debug -Message $Message }
function Write-LogInfo { param([string]$Message) Write-Log -Level Info -Message $Message }
function Write-LogWarning { param([string]$Message) Write-Log -Level Warning -Message $Message }
function Write-LogError { param([string]$Message, [Exception]$Exception) Write-Log -Level Error -Message $Message -Exception $Exception }

Export-ModuleMember -Function Initialize-Logger, Write-Log, Write-LogDebug, Write-LogInfo, Write-LogWarning, Write-LogError
Export-ModuleMember -Variable Logger