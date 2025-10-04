#Requires -Version 5.1

<#
.SYNOPSIS
    Setup script for AzerothCore Windows AutoBuilder v2.0

.DESCRIPTION
    This script helps set up the AzerothCore AutoBuilder environment,
    including directory creation, permission setup, and initial configuration.

.PARAMETER InstallPath
    Base installation path for AzerothCore Builder

.PARAMETER SkipExecutionPolicy
    Skip setting the PowerShell execution policy

.EXAMPLE
    .\Setup-AzerothCoreBuilder.ps1
    Run with default settings

.EXAMPLE
    .\Setup-AzerothCoreBuilder.ps1 -InstallPath "D:\AzerothCore"
    Install to custom path
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$InstallPath = "C:\WowServer",
    
    [Parameter()]
    [switch]$SkipExecutionPolicy
)

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Set-ExecutionPolicyIfNeeded {
    if ($SkipExecutionPolicy) {
        Write-Host "Skipping execution policy setup as requested" -ForegroundColor Yellow
        return
    }

    try {
        $currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
        if ($currentPolicy -eq "Restricted") {
            Write-Host "Setting PowerShell execution policy..." -ForegroundColor Yellow
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Write-Host "Execution policy set to RemoteSigned for CurrentUser" -ForegroundColor Green
        } else {
            Write-Host "Execution policy is already set to: $currentPolicy" -ForegroundColor Green
        }
    }
    catch {
        Write-Warning "Failed to set execution policy: $($_.Exception.Message)"
        Write-Host "You may need to run this script as Administrator" -ForegroundColor Yellow
    }
}

function New-DirectoryStructure {
    param([string]$BasePath)

    $directories = @(
        "$BasePath\ACdownloads",
        "$BasePath\SourceGit",
        "$BasePath\Compile",
        "$BasePath\Server",
        "$BasePath\Logs"
    )

    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            try {
                New-Item -Path $dir -ItemType Directory -Force | Out-Null
                Write-Host "Created directory: $dir" -ForegroundColor Green
            }
            catch {
                Write-Warning "Failed to create directory $dir : $($_.Exception.Message)"
            }
        } else {
            Write-Host "Directory already exists: $dir" -ForegroundColor Yellow
        }
    }
}

function Test-SystemRequirements {
    Write-Host "`n=== System Requirements Check ===" -ForegroundColor Cyan

    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    if ($osVersion.Major -ge 10) {
        Write-Host "✓ Windows version: $($osVersion.Major).$($osVersion.Minor)" -ForegroundColor Green
    } else {
        Write-Host "✗ Windows version: $($osVersion.Major).$($osVersion.Minor) (requires 10+)" -ForegroundColor Red
        return $false
    }

    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -ge 5) {
        Write-Host "✓ PowerShell version: $psVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ PowerShell version: $psVersion (requires 5.1+)" -ForegroundColor Red
        return $false
    }

    # Check available disk space
    $drive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "C:" }
    $freeSpaceGB = [math]::Round($drive.FreeSpace / 1GB, 2)
    if ($freeSpaceGB -ge 20) {
        Write-Host "✓ Available disk space: $freeSpaceGB GB" -ForegroundColor Green
    } else {
        Write-Host "⚠ Available disk space: $freeSpaceGB GB (recommend 20+ GB)" -ForegroundColor Yellow
    }

    # Check RAM
    $memory = Get-WmiObject -Class Win32_ComputerSystem
    $ramGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
    if ($ramGB -ge 8) {
        Write-Host "✓ Total RAM: $ramGB GB" -ForegroundColor Green
    } else {
        Write-Host "⚠ Total RAM: $ramGB GB (recommend 8+ GB)" -ForegroundColor Yellow
    }

    return $true
}

function Show-InstallationSummary {
    param([string]$BasePath)

    Write-Host "`n=== Installation Summary ===" -ForegroundColor Cyan
    Write-Host "Installation Path: $BasePath" -ForegroundColor White
    Write-Host "Directories Created:" -ForegroundColor White
    Write-Host "  - $BasePath\ACdownloads (downloads)" -ForegroundColor Gray
    Write-Host "  - $BasePath\SourceGit (source code)" -ForegroundColor Gray
    Write-Host "  - $BasePath\Compile (build output)" -ForegroundColor Gray
    Write-Host "  - $BasePath\Server (personal server)" -ForegroundColor Gray
    Write-Host "  - $BasePath\Logs (log files)" -ForegroundColor Gray
    
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "1. Run the main script: .\Start-AzerothCoreAutoBuilder.ps1" -ForegroundColor White
    Write-Host "2. Choose option 1 to install dependencies" -ForegroundColor White
    Write-Host "3. Follow the on-screen instructions" -ForegroundColor White
    
    Write-Host "`nImportant Notes:" -ForegroundColor Yellow
    Write-Host "- Run PowerShell as Administrator for dependency installation" -ForegroundColor White
    Write-Host "- Ensure stable internet connection for downloads" -ForegroundColor White
    Write-Host "- The build process requires significant disk space" -ForegroundColor White
}

function Main {
    Write-Host "=== AzerothCore Windows AutoBuilder v2.0 Setup ===" -ForegroundColor Cyan
    Write-Host "This script will set up the environment for AzerothCore AutoBuilder" -ForegroundColor Green
    Write-Host ""

    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-Warning "This script is not running as Administrator."
        Write-Host "Some operations may require elevated privileges." -ForegroundColor Yellow
        Write-Host "Consider running as Administrator for full functionality." -ForegroundColor Yellow
        Write-Host ""
    }

    # Test system requirements
    if (-not (Test-SystemRequirements)) {
        Write-Host "`nSystem requirements check failed. Please address the issues above." -ForegroundColor Red
        return
    }

    # Set execution policy
    Set-ExecutionPolicyIfNeeded

    # Create directory structure
    Write-Host "`n=== Creating Directory Structure ===" -ForegroundColor Cyan
    New-DirectoryStructure -BasePath $InstallPath

    # Create initial configuration
    Write-Host "`n=== Creating Initial Configuration ===" -ForegroundColor Cyan
    $configPath = ".\AzerothCore-Config.json"
    if (-not (Test-Path $configPath)) {
        if (Test-Path ".\AzerothCore-Config-Example.json") {
            Copy-Item ".\AzerothCore-Config-Example.json" $configPath
            Write-Host "Created configuration file: $configPath" -ForegroundColor Green
        } else {
            Write-Host "Configuration template not found. You'll need to create one manually." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Configuration file already exists: $configPath" -ForegroundColor Yellow
    }

    # Show summary
    Show-InstallationSummary -BasePath $InstallPath

    Write-Host "`nSetup completed successfully!" -ForegroundColor Green
    Write-Host "You can now run the main script to begin using AzerothCore AutoBuilder." -ForegroundColor Green
}

# Run main function
Main