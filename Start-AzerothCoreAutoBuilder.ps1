#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    AzerothCore Windows AutoBuilder - Enhanced Version 2.0

.DESCRIPTION
    Comprehensive PowerShell script to automate the entire AzerothCore server build process
    with modern dependency management, security, logging, and error handling.

.PARAMETER ConfigPath
    Path to the configuration file. Defaults to ".\AzerothCore-Config.json"

.PARAMETER SkipDependencies
    Skip dependency installation and checking

.PARAMETER DryRun
    Show what would be done without actually performing operations

.PARAMETER LogLevel
    Set the logging level (Debug, Info, Warning, Error)

.EXAMPLE
    .\Start-AzerothCoreAutoBuilder.ps1
    Run the script with default configuration

.EXAMPLE
    .\Start-AzerothCoreAutoBuilder.ps1 -ConfigPath "C:\MyConfig.json" -LogLevel Debug
    Run with custom configuration and debug logging

.NOTES
    Author: AzerothCore AutoBuilder Team
    Version: 2.0.0
    Minimum Requirements:
    - Windows 10 or later
    - PowerShell 5.1 or later
    - Administrator privileges for dependency installation
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$ConfigPath = ".\AzerothCore-Config.json",
    
    [Parameter()]
    [switch]$SkipDependencies,
    
    [Parameter()]
    [switch]$DryRun,
    
    [Parameter()]
    [ValidateSet("Debug", "Info", "Warning", "Error")]
    [string]$LogLevel = "Info"
)

# Script metadata
$ScriptInfo = @{
    Name = "AzerothCore Windows AutoBuilder"
    Version = "2.0.0"
    Author = "AzerothCore AutoBuilder Team"
    Description = "Enhanced automation script for AzerothCore server setup"
}

# Global variables
$Global:Config = $null
$Global:DependencyManager = $null
$Global:RestartRequired = $false

# Import required modules
$ModulePath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$ModulePath\Modules\Logging.psm1" -Force
Import-Module "$ModulePath\Modules\Security.psm1" -Force
Import-Module "$ModulePath\Modules\Configuration.psm1" -Force
Import-Module "$ModulePath\Modules\DependencyManager.psm1" -Force

function Initialize-Script {
    [CmdletBinding()]
    param()

    try {
        # Check Windows version
        $osVersion = [System.Environment]::OSVersion.Version
        if ($osVersion.Major -lt 10) {
            throw "This script requires Windows 10 or later. Current version: $($osVersion.Major).$($osVersion.Minor)"
        }

        # Check PowerShell version
        if ($PSVersionTable.PSVersion.Major -lt 5) {
            throw "This script requires PowerShell 5.1 or later. Current version: $($PSVersionTable.PSVersion)"
        }

        # Check for administrator privileges
        if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
            throw "This script must be run as Administrator for dependency installation"
        }

        Write-Host "`n=== $($ScriptInfo.Name) v$($ScriptInfo.Version) ===" -ForegroundColor Cyan
        Write-Host "Enhanced AzerothCore server automation script" -ForegroundColor Green
        Write-Host "Minimum Requirements:" -ForegroundColor Yellow
        Write-Host "  - Windows ≥ 10" -ForegroundColor White
        Write-Host "  - Boost ≥ 1.78" -ForegroundColor White
        Write-Host "  - MySQL ≥ 8.0 (Recommended 8.4)" -ForegroundColor White
        Write-Host "  - OpenSSL ≥ 3.x.x" -ForegroundColor White
        Write-Host "  - CMake ≥ 3.27" -ForegroundColor White
        Write-Host "  - MS Visual Studio (Community) ≥ 17 (2022)" -ForegroundColor White
        Write-Host ""

        return $true
    }
    catch {
        Write-Error "Initialization failed: $($_.Exception.Message)"
        return $false
    }
}

function Load-Configuration {
    [CmdletBinding()]
    param()

    try {
        Write-LogInfo "Loading configuration..."
        
        if (Test-Path $ConfigPath) {
            $Global:Config = Get-Configuration -ConfigPath $ConfigPath
        } else {
            Write-LogWarning "Configuration file not found. Creating new configuration..."
            $Global:Config = New-Configuration -ConfigPath $ConfigPath
        }

        if (-not $Global:Config) {
            throw "Failed to load or create configuration"
        }

        # Override log level if specified
        if ($LogLevel) {
            $Global:Config.Logging.Level = $LogLevel
        }

        # Initialize logger
        Initialize-Logger -LogFile $Global:Config.Logging.LogFile -MinLevel $Global:Config.Logging.Level -MaxLogSize $Global:Config.Logging.MaxLogSize

        Write-LogInfo "Configuration loaded successfully"
        Write-LogInfo "Log file: $($Global:Config.Logging.LogFile)"
        Write-LogInfo "Build configuration: $($Global:Config.Build.Configuration)"

        return $true
    }
    catch {
        Write-Error "Failed to load configuration: $($_.Exception.Message)"
        return $false
    }
}

function Initialize-Dependencies {
    [CmdletBinding()]
    param()

    try {
        if ($SkipDependencies) {
            Write-LogInfo "Skipping dependency management as requested"
            return $true
        }

        Write-LogInfo "Initializing dependency manager..."
        $Global:DependencyManager = Initialize-DependencyManager -DownloadFolder $Global:Config.Paths.DownloadFolder -Logger $Global:Logger

        # Ensure download folder exists
        if (-not (Test-Path $Global:Config.Paths.DownloadFolder)) {
            New-Item -Path $Global:Config.Paths.DownloadFolder -ItemType Directory -Force | Out-Null
            Write-LogInfo "Created download folder: $($Global:Config.Paths.DownloadFolder)"
        }

        return $true
    }
    catch {
        Write-LogError "Failed to initialize dependencies: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Show-MainMenu {
    [CmdletBinding()]
    param()

    Clear-Host
    Write-Host "`n`n`n============= AzerothCore Windows AutoBuilder v2.0 =============" -ForegroundColor Cyan
    Write-Host "Enhanced automation script with modern features" -ForegroundColor Green
    Write-Host ""
    Write-Host "Main Menu:" -ForegroundColor Yellow
    Write-Host "1: Install/Update Dependencies (CMake, Git, MySQL, etc)" -ForegroundColor White
    Write-Host "2: Clone/Clean/Update AzerothCore Git Repository" -ForegroundColor White
    Write-Host "3: Download and Test Pull Request" -ForegroundColor White
    Write-Host "4: Manage Custom Modules" -ForegroundColor White
    Write-Host "5: Build Server and Database" -ForegroundColor White
    Write-Host "6: Start Test Server" -ForegroundColor White
    Write-Host "7: Create Personal Server/Repack" -ForegroundColor White
    Write-Host "8: Configuration Management" -ForegroundColor White
    Write-Host "9: System Information and Diagnostics" -ForegroundColor White
    Write-Host "Q: Quit" -ForegroundColor Red
    Write-Host ""
    Write-Host "Current Configuration:" -ForegroundColor Yellow
    Write-Host "  Build Type: $($Global:Config.Build.Configuration)" -ForegroundColor White
    Write-Host "  Log Level: $($Global:Config.Logging.Level)" -ForegroundColor White
    Write-Host "  Download Folder: $($Global:Config.Paths.DownloadFolder)" -ForegroundColor White
    Write-Host ""
}

function Install-Dependencies {
    [CmdletBinding()]
    param()

    try {
        Write-LogInfo "Starting dependency installation process..."
        
        if ($DryRun) {
            Write-LogInfo "DRY RUN: Would check and install dependencies"
            return $true
        }

        # Check all dependencies
        $Global:DependencyManager.CheckAllDependencies()

        # Get missing and outdated dependencies
        $missingDeps = $Global:DependencyManager.GetMissingDependencies()
        $outdatedDeps = $Global:DependencyManager.GetOutdatedDependencies()

        if ($missingDeps.Count -eq 0 -and $outdatedDeps.Count -eq 0) {
            Write-LogInfo "All dependencies are installed and up to date"
            return $true
        }

        # Install missing dependencies
        foreach ($dep in $missingDeps) {
            Write-LogInfo "Installing missing dependency: $($dep.Name)"
            $success = $Global:DependencyManager.InstallDependency($dep.Name)
            if (-not $success) {
                Write-LogError "Failed to install $($dep.Name)"
                return $false
            }
            $Global:RestartRequired = $true
        }

        # Update outdated dependencies
        foreach ($dep in $outdatedDeps) {
            Write-LogWarning "Dependency $($dep.Name) is outdated (Current: $($dep.CurrentVersion), Required: $($dep.MinVersion))"
            $update = Read-Host "Update $($dep.Name)? (y/n)"
            if ($update -eq "y") {
                $success = $Global:DependencyManager.InstallDependency($dep.Name)
                if (-not $success) {
                    Write-LogError "Failed to update $($dep.Name)"
                    return $false
                }
                $Global:RestartRequired = $true
            }
        }

        if ($Global:RestartRequired) {
            Write-LogWarning "One or more applications have been installed and PATH variables modified."
            Write-LogWarning "You MUST close and reopen PowerShell to continue."
            Write-LogWarning "Please restart the script after closing this session."
            return $false
        }

        Write-LogInfo "Dependency installation completed successfully"
        return $true
    }
    catch {
        Write-LogError "Dependency installation failed: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Manage-Repository {
    [CmdletBinding()]
    param()

    try {
        Write-LogInfo "Managing AzerothCore repository..."
        
        $repoUrl = "https://github.com/azerothcore/azerothcore-wotlk.git"
        
        # Ensure base location exists
        if (-not (Test-Path $Global:Config.Paths.BaseLocation)) {
            Write-LogInfo "Creating base location directory: $($Global:Config.Paths.BaseLocation)"
            New-Item -Path $Global:Config.Paths.BaseLocation -ItemType Directory -Force | Out-Null
        }

        $gitHeadPath = Join-Path $Global:Config.Paths.BaseLocation ".git\HEAD"
        
        if (-not (Test-Path $gitHeadPath)) {
            Write-LogInfo "Cloning AzerothCore repository..."
            if ($DryRun) {
                Write-LogInfo "DRY RUN: Would clone repository to $($Global:Config.Paths.BaseLocation)"
                return $true
            }
            
            Set-Location $Global:Config.Paths.BaseLocation
            git clone $repoUrl . --branch master
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to clone repository"
            }
            Write-LogInfo "Repository cloned successfully"
        } else {
            Write-LogInfo "Repository exists. Cleaning and updating..."
            if ($DryRun) {
                Write-LogInfo "DRY RUN: Would clean and update repository"
                return $true
            }
            
            # Clean modules and updates
            if (Test-Path (Join-Path $Global:Config.Paths.BaseLocation "modules")) {
                Remove-Item (Join-Path $Global:Config.Paths.BaseLocation "modules") -Recurse -Force
            }
            if (Test-Path (Join-Path $Global:Config.Paths.BaseLocation "data\sql\updates")) {
                Remove-Item (Join-Path $Global:Config.Paths.BaseLocation "data\sql\updates") -Recurse -Force
            }

            Set-Location $Global:Config.Paths.BaseLocation
            
            # Reset and update
            git reset --hard
            git checkout master
            git clean -fd
            git pull
            
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to update repository"
            }
            
            Write-LogInfo "Repository updated successfully"
        }

        return $true
    }
    catch {
        Write-LogError "Repository management failed: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Test-PullRequest {
    [CmdletBinding()]
    param()

    try {
        Write-LogInfo "Pull Request testing functionality..."
        
        do {
            $prNumber = Read-Host "`nEnter 4-digit PR number to test"
            
            if (-not ($prNumber -match '^\d{4}$')) {
                Write-LogWarning "Please enter a valid 4-digit PR number"
                continue
            }

            $prUrl = "https://github.com/azerothcore/azerothcore-wotlk/pull/$prNumber"
            
            try {
                $prResult = Invoke-WebRequest -Uri $prUrl -Method Get
                $prTitle = $prResult.ParsedHtml.title
                
                Write-Host "`nPR Title: $prTitle" -ForegroundColor Yellow
                $confirm = Read-Host "Is this the correct PR? (y/n)"
                
                if ($confirm -eq "y") {
                    if ($DryRun) {
                        Write-LogInfo "DRY RUN: Would checkout PR #$prNumber"
                        return $true
                    }
                    
                    Set-Location $Global:Config.Paths.BaseLocation
                    git checkout -b "pr-$prNumber"
                    git pull origin "pull/$prNumber/head"
                    
                    if ($LASTEXITCODE -ne 0) {
                        throw "Failed to pull PR #$prNumber"
                    }
                    
                    Write-LogInfo "PR #$prNumber has been pulled successfully"
                    return $true
                }
            }
            catch {
                Write-LogError "Invalid PR number or network error: $($_.Exception.Message)"
            }
        } while ($true)
    }
    catch {
        Write-LogError "Pull request testing failed: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Manage-Modules {
    [CmdletBinding()]
    param()

    try {
        Write-LogInfo "Module management functionality..."
        
        # Create a modern GUI for module selection
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing

        $form = New-Object System.Windows.Forms.Form
        $form.Text = "AzerothCore Module Manager"
        $form.Size = New-Object System.Drawing.Size(800, 600)
        $form.StartPosition = 'CenterScreen'
        $form.FormBorderStyle = 'FixedDialog'
        $form.MaximizeBox = $false

        # Create module list
        $moduleList = New-Object System.Windows.Forms.CheckedListBox
        $moduleList.Location = New-Object System.Drawing.Point(20, 20)
        $moduleList.Size = New-Object System.Drawing.Size(740, 450)
        $moduleList.CheckOnClick = $true

        # Get available modules from GitHub API
        Write-LogInfo "Fetching available modules..."
        $modules = @()
        
        for ($page = 1; $page -le 2; $page++) {
            $apiUrl = "https://api.github.com/orgs/azerothcore/repos?q=mod&sort=name&per_page=100&page=$page"
            $response = Invoke-RestMethod -Uri $apiUrl
            $modules += $response | Where-Object { $_.name -like "mod*" }
        }

        # Populate module list
        foreach ($module in $modules) {
            $moduleName = $module.name -replace '^mod-', ''
            $moduleList.Items.Add($moduleName) | Out-Null
        }

        # Add buttons
        $okButton = New-Object System.Windows.Forms.Button
        $okButton.Text = "OK"
        $okButton.Location = New-Object System.Drawing.Point(600, 500)
        $okButton.Size = New-Object System.Drawing.Size(75, 30)
        $okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK

        $cancelButton = New-Object System.Windows.Forms.Button
        $cancelButton.Text = "Cancel"
        $cancelButton.Location = New-Object System.Drawing.Point(685, 500)
        $cancelButton.Size = New-Object System.Drawing.Size(75, 30)
        $cancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel

        $form.Controls.Add($moduleList)
        $form.Controls.Add($okButton)
        $form.Controls.Add($cancelButton)
        $form.AcceptButton = $okButton
        $form.CancelButton = $cancelButton

        # Show form
        $result = $form.ShowDialog()

        if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
            $selectedModules = $moduleList.CheckedItems
            Write-LogInfo "Selected modules: $($selectedModules -join ', ')"
            
            if ($DryRun) {
                Write-LogInfo "DRY RUN: Would install selected modules"
                return $true
            }
            
            # Install selected modules
            foreach ($moduleName in $selectedModules) {
                $module = $modules | Where-Object { $_.name -like "*$moduleName" }
                if ($module) {
                    $modulePath = Join-Path $Global:Config.Paths.BaseLocation "modules\$($module.name)"
                    Write-LogInfo "Installing module: $($module.name)"
                    
                    if (Test-Path "$modulePath\.git\HEAD") {
                        Set-Location $modulePath
                        git pull
                    } else {
                        git clone $module.clone_url $modulePath
                    }
                }
            }
            
            Write-LogInfo "Module installation completed"
        }

        return $true
    }
    catch {
        Write-LogError "Module management failed: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Build-Server {
    [CmdletBinding()]
    param()

    try {
        Write-LogInfo "Starting server build process..."
        
        if ($DryRun) {
            Write-LogInfo "DRY RUN: Would build server with configuration: $($Global:Config.Build.Configuration)"
            return $true
        }

        # Ensure build folder exists
        if (-not (Test-Path $Global:Config.Paths.BuildFolder)) {
            New-Item -Path $Global:Config.Paths.BuildFolder -ItemType Directory -Force | Out-Null
        }

        # Clean build folder if needed
        $cleanChoice = Read-Host "`nChoose build option:`n1: Build (preserve data folder)`n2: Clean build (delete all)`nEnter choice (1/2)"
        
        if ($cleanChoice -eq "2") {
            if (Test-Path $Global:Config.Paths.BuildFolder) {
                Remove-Item -Path $Global:Config.Paths.BuildFolder -Recurse -Force
                New-Item -Path $Global:Config.Paths.BuildFolder -ItemType Directory -Force | Out-Null
            }
        }

        # Configure with CMake
        Write-LogInfo "Configuring build with CMake..."
        Set-Location "C:\Program Files\CMake\bin"
        
        $cmakeArgs = @(
            "-G", "Visual Studio 17 2022",
            "-A", "x64",
            "-DTOOLS=1",
            "-S", $Global:Config.Paths.BaseLocation,
            "-B", $Global:Config.Paths.BuildFolder
        )
        
        Start-Process -FilePath "cmake.exe" -ArgumentList $cmakeArgs -Wait -NoNewWindow
        
        if ($LASTEXITCODE -ne 0) {
            throw "CMake configuration failed"
        }

        # Build with CMake
        Write-LogInfo "Building server (this may take a while)..."
        $buildArgs = @(
            "--build", $Global:Config.Paths.BuildFolder,
            "--config", $Global:Config.Build.Configuration,
            "--parallel", $Global:Config.Build.ParallelJobs
        )
        
        Start-Process -FilePath "cmake.exe" -ArgumentList $buildArgs -Wait -NoNewWindow
        
        if ($LASTEXITCODE -ne 0) {
            throw "Build failed"
        }

        # Verify build
        $authServerPath = Join-Path $Global:Config.Paths.BuildFolder "bin\$($Global:Config.Build.Configuration)\authserver.exe"
        $worldServerPath = Join-Path $Global:Config.Paths.BuildFolder "bin\$($Global:Config.Build.Configuration)\worldserver.exe"
        
        if (-not ((Test-Path $authServerPath) -and (Test-Path $worldServerPath))) {
            throw "Build verification failed - required executables not found"
        }

        Write-LogInfo "Server build completed successfully"
        return $true
    }
    catch {
        Write-LogError "Server build failed: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Start-TestServer {
    [CmdletBinding()]
    param()

    try {
        Write-LogInfo "Starting test server..."
        
        Write-LogWarning "Remember: This is for testing only!"
        Write-LogWarning "Do not use for personal gameplay - files will be deleted on rebuild"
        Write-LogWarning "Use option 7 to create a permanent personal server"
        
        Start-Sleep -Seconds 3
        
        $serverPath = Join-Path $Global:Config.Paths.BuildFolder "bin\$($Global:Config.Build.Configuration)"
        
        if (-not (Test-Path $serverPath)) {
            throw "Server build not found. Please run option 5 first."
        }

        Set-Location $serverPath
        
        # Start MySQL
        if (Test-Path "1_start_mysql.bat") {
            Start-Process -FilePath "1_start_mysql.bat" -WindowStyle Normal
            Start-Sleep -Seconds 3
        }

        # Start Auth Server
        if (Test-Path "2_start_authserver.bat") {
            Start-Process -FilePath "2_start_authserver.bat" -WindowStyle Normal
            Start-Sleep -Seconds 3
        }

        # Start World Server
        if (Test-Path "3_start_worldserver.bat") {
            Start-Process -FilePath "3_start_worldserver.bat" -WindowStyle Normal
        }

        Write-LogInfo "Test server started. Use CTRL+C in each window to stop servers."
        return $true
    }
    catch {
        Write-LogError "Failed to start test server: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Create-PersonalServer {
    [CmdletBinding()]
    param()

    try {
        Write-LogInfo "Creating personal server/repack..."
        
        $serverPath = Join-Path $Global:Config.Paths.BuildFolder "bin\$($Global:Config.Build.Configuration)"
        
        if (-not (Test-Path $serverPath)) {
            throw "Server build not found. Please run option 5 first."
        }

        # Check if personal server already exists
        if (Test-Path (Join-Path $Global:Config.Paths.PersonalServerFolder "Server\worldserver.exe")) {
            Write-Host "`nExisting personal server found at: $($Global:Config.Paths.PersonalServerFolder)" -ForegroundColor Yellow
            $choice = Read-Host "`nWhat would you like to do?`n1: Update existing server`n2: Create new server`nQ: Back`nEnter choice"
            
            switch ($choice) {
                "1" {
                    Write-LogInfo "Updating existing personal server..."
                    # Update logic here
                }
                "2" {
                    Write-LogInfo "Removing existing personal server..."
                    Remove-Item -Path $Global:Config.Paths.PersonalServerFolder -Recurse -Force
                }
                "Q" { return $true }
                default {
                    Write-LogWarning "Invalid choice"
                    return $false
                }
            }
        }

        # Create personal server directory
        if (-not (Test-Path $Global:Config.Paths.PersonalServerFolder)) {
            New-Item -Path $Global:Config.Paths.PersonalServerFolder -ItemType Directory -Force | Out-Null
        }

        # Copy server files
        Write-LogInfo "Copying server files..."
        Copy-Item -Path $serverPath -Destination $Global:Config.Paths.PersonalServerFolder -Recurse -Force
        Rename-Item -Path (Join-Path $Global:Config.Paths.PersonalServerFolder $Global:Config.Build.Configuration) -NewName "Server"

        # Create startup script
        $startupScript = Join-Path $Global:Config.Paths.PersonalServerFolder "Start_WoW_Server.bat"
        $startupContent = @"
@echo off
title AzerothCore Server
echo.
echo Starting AzerothCore Server...
echo.
cd .\Server
start 1_start_mysql.bat
timeout /T 3
start 2_start_authserver.bat
timeout /T 3
3_start_worldserver.bat
"@
        Set-Content -Path $startupScript -Value $startupContent

        Write-LogInfo "Personal server created successfully at: $($Global:Config.Paths.PersonalServerFolder)"
        Write-LogInfo "Start your server by running: Start_WoW_Server.bat"
        
        return $true
    }
    catch {
        Write-LogError "Failed to create personal server: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Show-SystemInfo {
    [CmdletBinding()]
    param()

    try {
        Write-Host "`n=== System Information ===" -ForegroundColor Cyan
        
        # OS Information
        $os = Get-WmiObject -Class Win32_OperatingSystem
        Write-Host "`nOperating System:" -ForegroundColor Yellow
        Write-Host "  Name: $($os.Caption)" -ForegroundColor White
        Write-Host "  Version: $($os.Version)" -ForegroundColor White
        Write-Host "  Architecture: $($os.OSArchitecture)" -ForegroundColor White

        # PowerShell Information
        Write-Host "`nPowerShell:" -ForegroundColor Yellow
        Write-Host "  Version: $($PSVersionTable.PSVersion)" -ForegroundColor White
        Write-Host "  Edition: $($PSVersionTable.PSEdition)" -ForegroundColor White

        # Memory Information
        $memory = Get-WmiObject -Class Win32_ComputerSystem
        Write-Host "`nMemory:" -ForegroundColor Yellow
        Write-Host "  Total: $([math]::Round($memory.TotalPhysicalMemory / 1GB, 2)) GB" -ForegroundColor White

        # Disk Information
        $disks = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
        Write-Host "`nDisk Space:" -ForegroundColor Yellow
        foreach ($disk in $disks) {
            $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
            $totalGB = [math]::Round($disk.Size / 1GB, 2)
            Write-Host "  $($disk.DeviceID) Free: $freeGB GB / $totalGB GB" -ForegroundColor White
        }

        # Dependency Status
        if ($Global:DependencyManager) {
            Write-Host "`nDependency Status:" -ForegroundColor Yellow
            $Global:DependencyManager.CheckAllDependencies()
            foreach ($dep in $Global:DependencyManager.Dependencies.Values) {
                $status = if ($dep.IsInstalled) { 
                    if ($dep.IsUpToDate) { "✓ Up to date" } else { "⚠ Outdated" }
                } else { "✗ Not installed" }
                Write-Host "  $($dep.Name): $status ($($dep.CurrentVersion))" -ForegroundColor White
            }
        }

        Write-Host ""
        Read-Host "Press Enter to continue"
        return $true
    }
    catch {
        Write-LogError "Failed to show system information: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Show-ConfigurationMenu {
    [CmdletBinding()]
    param()

    try {
        do {
            Clear-Host
            Write-Host "`n=== Configuration Management ===" -ForegroundColor Cyan
            Write-Host "1: View Current Configuration" -ForegroundColor White
            Write-Host "2: Edit Configuration" -ForegroundColor White
            Write-Host "3: Reset to Defaults" -ForegroundColor White
            Write-Host "4: Validate Configuration" -ForegroundColor White
            Write-Host "Q: Back to Main Menu" -ForegroundColor Red
            
            $choice = Read-Host "`nEnter choice"
            
            switch ($choice) {
                "1" {
                    Write-Host "`n=== Current Configuration ===" -ForegroundColor Yellow
                    $Global:Config | ConvertTo-Json -Depth 3 | Write-Host
                    Read-Host "Press Enter to continue"
                }
                "2" {
                    $Global:Config = Edit-Configuration -ConfigPath $ConfigPath
                }
                "3" {
                    $confirm = Read-Host "Reset configuration to defaults? (y/n)"
                    if ($confirm -eq "y") {
                        $Global:Config = [Configuration]::new()
                        Save-Configuration -Configuration $Global:Config -ConfigPath $ConfigPath
                        Write-Host "Configuration reset to defaults" -ForegroundColor Green
                    }
                }
                "4" {
                    Test-Configuration -Configuration $Global:Config
                    Read-Host "Press Enter to continue"
                }
                "Q" { break }
                default {
                    Write-Host "Invalid choice" -ForegroundColor Red
                }
            }
        } while ($true)
        
        return $true
    }
    catch {
        Write-LogError "Configuration menu failed: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

# Main script execution
function Main {
    try {
        # Initialize script
        if (-not (Initialize-Script)) {
            return
        }

        # Load configuration
        if (-not (Load-Configuration)) {
            return
        }

        # Initialize dependencies
        if (-not (Initialize-Dependencies)) {
            return
        }

        # Main menu loop
        do {
            Show-MainMenu
            $selection = Read-Host "`nEnter choice"
            
            switch ($selection) {
                "1" { Install-Dependencies }
                "2" { Manage-Repository }
                "3" { Test-PullRequest }
                "4" { Manage-Modules }
                "5" { Build-Server }
                "6" { Start-TestServer }
                "7" { Create-PersonalServer }
                "8" { Show-ConfigurationMenu }
                "9" { Show-SystemInfo }
                "Q" { 
                    Write-LogInfo "Script terminated by user"
                    break 
                }
                default {
                    Write-Host "Invalid choice. Please try again." -ForegroundColor Red
                    Start-Sleep -Seconds 2
                }
            }
            
            if ($selection -ne "Q") {
                Read-Host "`nPress Enter to continue"
            }
        } while ($selection -ne "Q")

        Write-LogInfo "Script execution completed"
    }
    catch {
        Write-LogError "Script execution failed: $($_.Exception.Message)" -Exception $_
    }
    finally {
        if ($Global:Logger) {
            $Global:Logger.Info("Script session ended")
        }
    }
}

# Execute main function
Main