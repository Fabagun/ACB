#Requires -Version 5.1

<#
.SYNOPSIS
    Configuration management module for AzerothCore AutoBuilder

.DESCRIPTION
    Handles loading, validation, and management of configuration files.

.NOTES
    Author: AzerothCore AutoBuilder
    Version: 2.0.0
#>

class Configuration {
    [string]$Version
    [hashtable]$Paths
    [hashtable]$Database
    [hashtable]$Downloads
    [hashtable]$Dependencies
    [hashtable]$Build
    [hashtable]$Logging

    Configuration() {
        $this.Version = "2.0.0"
        $this.Paths = @{
            DownloadFolder = "C:\WowServer\ACdownloads\"
            BaseLocation = "C:\WowServer\SourceGit\"
            BuildFolder = "C:\WowServer\Compile\"
            PersonalServerFolder = "C:\WowServer\Server\"
        }
        $this.Database = @{
            RootPassword = ""
            Port = 3306
        }
        $this.Downloads = @{
            DownloadData = $true
            DataUrl = "https://github.com/wowgaming/client-data/releases/download/v12/data.zip"
        }
        $this.Dependencies = @{}
        $this.Build = @{
            Configuration = "Release"
            ParallelJobs = 4
        }
        $this.Logging = @{
            Level = "Info"
            LogFile = "C:\WowServer\Logs\AzerothCore-Builder.log"
            MaxLogSize = 10
        }
    }
}

function Get-Configuration {
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$ConfigPath = ".\AzerothCore-Config.json"
    )

    try {
        if (Test-Path $ConfigPath) {
            Write-LogInfo "Loading configuration from: $ConfigPath"
            $configJson = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
            $config = [Configuration]::new()
            
            # Map JSON properties to configuration object
            if ($configJson.PSObject.Properties.Name -contains "paths") {
                $config.Paths = $configJson.paths
            }
            if ($configJson.PSObject.Properties.Name -contains "database") {
                $config.Database = $configJson.database
            }
            if ($configJson.PSObject.Properties.Name -contains "downloads") {
                $config.Downloads = $configJson.downloads
            }
            if ($configJson.PSObject.Properties.Name -contains "dependencies") {
                $config.Dependencies = $configJson.dependencies
            }
            if ($configJson.PSObject.Properties.Name -contains "build") {
                $config.Build = $configJson.build
            }
            if ($configJson.PSObject.Properties.Name -contains "logging") {
                $config.Logging = $configJson.logging
            }
            
            Write-LogInfo "Configuration loaded successfully"
            return $config
        } else {
            Write-LogWarning "Configuration file not found at: $ConfigPath. Using defaults."
            return [Configuration]::new()
        }
    }
    catch {
        Write-LogError "Failed to load configuration: $($_.Exception.Message)" -Exception $_
        Write-LogInfo "Using default configuration"
        return [Configuration]::new()
    }
}

function Save-Configuration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [Configuration]$Configuration,
        
        [Parameter()]
        [string]$ConfigPath = ".\AzerothCore-Config.json"
    )

    try {
        $configObject = @{
            version = $Configuration.Version
            paths = $Configuration.Paths
            database = $Configuration.Database
            downloads = $Configuration.Downloads
            dependencies = $Configuration.Dependencies
            build = $Configuration.Build
            logging = $Configuration.Logging
        }

        $configJson = $configObject | ConvertTo-Json -Depth 10
        Set-Content -Path $ConfigPath -Value $configJson -Encoding UTF8
        Write-LogInfo "Configuration saved to: $ConfigPath"
        return $true
    }
    catch {
        Write-LogError "Failed to save configuration: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Test-Configuration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [Configuration]$Configuration
    )

    $errors = @()
    $warnings = @()

    # Validate paths
    foreach ($pathKey in $Configuration.Paths.Keys) {
        $path = $Configuration.Paths[$pathKey]
        if (-not (Test-InputValidation -Input $path -Type "Path")) {
            $errors += "Invalid path for $pathKey : $path"
        }
    }

    # Validate database configuration
    if ($Configuration.Database.Port -lt 1024 -or $Configuration.Database.Port -gt 65535) {
        $errors += "Database port must be between 1024 and 65535"
    }

    if ($Configuration.Database.RootPassword -and $Configuration.Database.RootPassword.Length -lt 8) {
        $warnings += "Database root password should be at least 8 characters long"
    }

    # Validate build configuration
    if ($Configuration.Build.Configuration -notin @("Debug", "Release")) {
        $errors += "Build configuration must be either 'Debug' or 'Release'"
    }

    if ($Configuration.Build.ParallelJobs -lt 1 -or $Configuration.Build.ParallelJobs -gt 16) {
        $warnings += "Parallel jobs should be between 1 and 16"
    }

    # Validate logging configuration
    if ($Configuration.Logging.Level -notin @("Debug", "Info", "Warning", "Error")) {
        $errors += "Logging level must be one of: Debug, Info, Warning, Error"
    }

    if ($Configuration.Logging.MaxLogSize -lt 1) {
        $warnings += "Max log size should be at least 1 MB"
    }

    # Validate download URL
    if ($Configuration.Downloads.DataUrl -and -not (Test-InputValidation -Input $Configuration.Downloads.DataUrl -Type "URL")) {
        $errors += "Invalid data download URL"
    }

    # Report results
    if ($errors.Count -gt 0) {
        Write-LogError "Configuration validation failed with $($errors.Count) errors:"
        foreach ($error in $errors) {
            Write-LogError "  - $error"
        }
        return $false
    }

    if ($warnings.Count -gt 0) {
        Write-LogWarning "Configuration validation completed with $($warnings.Count) warnings:"
        foreach ($warning in $warnings) {
            Write-LogWarning "  - $warning"
        }
    } else {
        Write-LogInfo "Configuration validation passed"
    }

    return $true
}

function New-Configuration {
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$ConfigPath = ".\AzerothCore-Config.json"
    )

    try {
        $config = [Configuration]::new()
        
        # Prompt for user preferences
        Write-Host "`n=== AzerothCore AutoBuilder Configuration ===" -ForegroundColor Cyan
        Write-Host "Setting up your configuration. Press Enter to use defaults.`n" -ForegroundColor Yellow

        # Paths
        Write-Host "Directory Paths:" -ForegroundColor Green
        $downloadFolder = Read-Host "Download folder [$($config.Paths.DownloadFolder)]"
        if ($downloadFolder) { $config.Paths.DownloadFolder = $downloadFolder }

        $baseLocation = Read-Host "Source Git folder [$($config.Paths.BaseLocation)]"
        if ($baseLocation) { $config.Paths.BaseLocation = $baseLocation }

        $buildFolder = Read-Host "Build folder [$($config.Paths.BuildFolder)]"
        if ($buildFolder) { $config.Paths.BuildFolder = $buildFolder }

        $serverFolder = Read-Host "Personal server folder [$($config.Paths.PersonalServerFolder)]"
        if ($serverFolder) { $config.Paths.PersonalServerFolder = $serverFolder }

        # Database
        Write-Host "`nDatabase Configuration:" -ForegroundColor Green
        $dbPort = Read-Host "MySQL port [$($config.Database.Port)]"
        if ($dbPort) { $config.Database.Port = [int]$dbPort }

        $downloadData = Read-Host "Download maps data? (y/n) [y]"
        if ($downloadData -eq "n") { $config.Downloads.DownloadData = $false }

        # Build
        Write-Host "`nBuild Configuration:" -ForegroundColor Green
        $buildConfig = Read-Host "Build configuration (Debug/Release) [$($config.Build.Configuration)]"
        if ($buildConfig) { $config.Build.Configuration = $buildConfig }

        $parallelJobs = Read-Host "Parallel build jobs [$($config.Build.ParallelJobs)]"
        if ($parallelJobs) { $config.Build.ParallelJobs = [int]$parallelJobs }

        # Logging
        Write-Host "`nLogging Configuration:" -ForegroundColor Green
        $logLevel = Read-Host "Log level (Debug/Info/Warning/Error) [$($config.Logging.Level)]"
        if ($logLevel) { $config.Logging.Level = $logLevel }

        $logFile = Read-Host "Log file path [$($config.Logging.LogFile)]"
        if ($logFile) { $config.Logging.LogFile = $logFile }

        # Validate configuration
        if (Test-Configuration -Configuration $config) {
            Save-Configuration -Configuration $config -ConfigPath $ConfigPath
            Write-Host "`nConfiguration created successfully!" -ForegroundColor Green
            return $config
        } else {
            Write-Host "`nConfiguration validation failed. Please fix the errors and try again." -ForegroundColor Red
            return $null
        }
    }
    catch {
        Write-LogError "Failed to create configuration: $($_.Exception.Message)" -Exception $_
        return $null
    }
}

function Edit-Configuration {
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$ConfigPath = ".\AzerothCore-Config.json"
    )

    try {
        $config = Get-Configuration -ConfigPath $ConfigPath
        if (-not $config) {
            Write-LogError "Failed to load configuration for editing"
            return $null
        }

        Write-Host "`n=== Edit Configuration ===" -ForegroundColor Cyan
        Write-Host "Current configuration loaded. Press Enter to keep current values.`n" -ForegroundColor Yellow

        # Allow editing of key settings
        $newDownloadFolder = Read-Host "Download folder [$($config.Paths.DownloadFolder)]"
        if ($newDownloadFolder) { $config.Paths.DownloadFolder = $newDownloadFolder }

        $newBuildConfig = Read-Host "Build configuration (Debug/Release) [$($config.Build.Configuration)]"
        if ($newBuildConfig) { $config.Build.Configuration = $newBuildConfig }

        $newLogLevel = Read-Host "Log level (Debug/Info/Warning/Error) [$($config.Logging.Level)]"
        if ($newLogLevel) { $config.Logging.Level = $newLogLevel }

        # Validate and save
        if (Test-Configuration -Configuration $config) {
            Save-Configuration -Configuration $config -ConfigPath $ConfigPath
            Write-Host "`nConfiguration updated successfully!" -ForegroundColor Green
            return $config
        } else {
            Write-Host "`nConfiguration validation failed. Changes not saved." -ForegroundColor Red
            return $config
        }
    }
    catch {
        Write-LogError "Failed to edit configuration: $($_.Exception.Message)" -Exception $_
        return $null
    }
}

Export-ModuleMember -Function Get-Configuration, Save-Configuration, Test-Configuration, New-Configuration, Edit-Configuration
Export-ModuleMember -Class Configuration