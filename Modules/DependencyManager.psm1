#Requires -Version 5.1

<#
.SYNOPSIS
    Dependency management module for AzerothCore AutoBuilder

.DESCRIPTION
    Manages software dependencies with version checking, installation, and validation.

.NOTES
    Author: AzerothCore AutoBuilder
    Version: 2.0.0
#>

class Dependency {
    [string]$Name
    [string]$MinVersion
    [string]$CurrentVersion
    [string]$InstallPath
    [string]$DownloadUrl
    [string]$Checksum
    [string]$ChecksumAlgorithm
    [bool]$IsInstalled
    [bool]$IsUpToDate

    Dependency([string]$Name, [string]$MinVersion, [string]$DownloadUrl, [string]$Checksum = "", [string]$ChecksumAlgorithm = "SHA256") {
        $this.Name = $Name
        $this.MinVersion = $MinVersion
        $this.DownloadUrl = $DownloadUrl
        $this.Checksum = $Checksum
        $this.ChecksumAlgorithm = $ChecksumAlgorithm
        $this.IsInstalled = $false
        $this.IsUpToDate = $false
    }
}

class DependencyManager {
    [hashtable]$Dependencies
    [string]$DownloadFolder
    [Logger]$Logger

    DependencyManager([string]$DownloadFolder, [Logger]$Logger) {
        $this.DownloadFolder = $DownloadFolder
        $this.Logger = $Logger
        $this.Dependencies = @{}
        $this.InitializeDependencies()
    }

    [void] InitializeDependencies() {
        # Git
        $this.Dependencies["Git"] = [Dependency]::new(
            "Git",
            "2.45.0",
            "https://api.github.com/repos/git-for-windows/git/releases/latest"
        )

        # CMake
        $this.Dependencies["CMake"] = [Dependency]::new(
            "CMake",
            "3.27.0",
            "https://github.com/Kitware/CMake/releases/download/v3.27.9/cmake-3.27.9-windows-x86_64.msi",
            "sha256:abc123...",
            "SHA256"
        )

        # Visual Studio
        $this.Dependencies["VisualStudio"] = [Dependency]::new(
            "Visual Studio",
            "17.0.0",
            "https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&rel=17"
        )

        # OpenSSL
        $this.Dependencies["OpenSSL"] = [Dependency]::new(
            "OpenSSL",
            "3.0.0",
            "https://slproweb.com/download/Win64OpenSSL-3_3_1.exe",
            "sha256:def456...",
            "SHA256"
        )

        # MySQL
        $this.Dependencies["MySQL"] = [Dependency]::new(
            "MySQL",
            "8.0.0",
            "https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-8.4.0-winx64.zip",
            "sha256:ghi789...",
            "SHA256"
        )

        # Boost
        $this.Dependencies["Boost"] = [Dependency]::new(
            "Boost",
            "1.78.0",
            "https://sourceforge.net/projects/boost/files/boost-binaries/1.84.0/boost_1_84_0-msvc-14.3-64.exe/download",
            "sha256:jkl012...",
            "SHA256"
        )
    }

    [void] CheckAllDependencies() {
        $this.Logger.Info("Checking all dependencies...")
        
        foreach ($dep in $this.Dependencies.Values) {
            $this.CheckDependency($dep)
        }
    }

    [void] CheckDependency([Dependency]$Dependency) {
        $this.Logger.Debug("Checking dependency: $($Dependency.Name)")
        
        switch ($Dependency.Name) {
            "Git" { $this.CheckGit($Dependency) }
            "CMake" { $this.CheckCMake($Dependency) }
            "VisualStudio" { $this.CheckVisualStudio($Dependency) }
            "OpenSSL" { $this.CheckOpenSSL($Dependency) }
            "MySQL" { $this.CheckMySQL($Dependency) }
            "Boost" { $this.CheckBoost($Dependency) }
        }
    }

    [void] CheckGit([Dependency]$Dependency) {
        try {
            $gitPath = "C:\Program Files\Git\git-cmd.exe"
            if (Test-Path $gitPath) {
                $version = & git --version 2>$null
                if ($version) {
                    $versionNumber = ($version -split ' ')[2]
                    $Dependency.CurrentVersion = $versionNumber
                    $Dependency.InstallPath = $gitPath
                    $Dependency.IsInstalled = $true
                    $Dependency.IsUpToDate = $this.CompareVersions($versionNumber, $Dependency.MinVersion) -ge 0
                    $this.Logger.Info("Git found: $versionNumber")
                }
            }
        }
        catch {
            $this.Logger.Debug("Git not found or error checking version: $($_.Exception.Message)")
        }
    }

    [void] CheckCMake([Dependency]$Dependency) {
        try {
            $cmakePath = "C:\Program Files\CMake\bin\cmake.exe"
            if (Test-Path $cmakePath) {
                $version = & cmake --version 2>$null
                if ($version) {
                    $versionNumber = ($version -split '\n')[0] -replace 'cmake version ', ''
                    $Dependency.CurrentVersion = $versionNumber
                    $Dependency.InstallPath = $cmakePath
                    $Dependency.IsInstalled = $true
                    $Dependency.IsUpToDate = $this.CompareVersions($versionNumber, $Dependency.MinVersion) -ge 0
                    $this.Logger.Info("CMake found: $versionNumber")
                }
            }
        }
        catch {
            $this.Logger.Debug("CMake not found or error checking version: $($_.Exception.Message)")
        }
    }

    [void] CheckVisualStudio([Dependency]$Dependency) {
        try {
            $vsPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
            if (Test-Path $vsPath) {
                $Dependency.CurrentVersion = "17.0.0"
                $Dependency.InstallPath = $vsPath
                $Dependency.IsInstalled = $true
                $Dependency.IsUpToDate = $true
                $this.Logger.Info("Visual Studio 2022 Community found")
            }
        }
        catch {
            $this.Logger.Debug("Visual Studio not found: $($_.Exception.Message)")
        }
    }

    [void] CheckOpenSSL([Dependency]$Dependency) {
        try {
            $opensslPath = "C:\Program Files\OpenSSL-Win64\bin\openssl.exe"
            if (Test-Path $opensslPath) {
                $version = & openssl version 2>$null
                if ($version) {
                    $versionNumber = ($version -split ' ')[1]
                    $Dependency.CurrentVersion = $versionNumber
                    $Dependency.InstallPath = $opensslPath
                    $Dependency.IsInstalled = $true
                    $Dependency.IsUpToDate = $this.CompareVersions($versionNumber, $Dependency.MinVersion) -ge 0
                    $this.Logger.Info("OpenSSL found: $versionNumber")
                }
            }
        }
        catch {
            $this.Logger.Debug("OpenSSL not found or error checking version: $($_.Exception.Message)")
        }
    }

    [void] CheckMySQL([Dependency]$Dependency) {
        try {
            $mysqlPath = "C:\MySQL\bin\mysqld.exe"
            if (Test-Path $mysqlPath) {
                $version = & mysqld --version 2>$null
                if ($version) {
                    $versionNumber = ($version -split ' ')[2] -replace ',', ''
                    $Dependency.CurrentVersion = $versionNumber
                    $Dependency.InstallPath = $mysqlPath
                    $Dependency.IsInstalled = $true
                    $Dependency.IsUpToDate = $this.CompareVersions($versionNumber, $Dependency.MinVersion) -ge 0
                    $this.Logger.Info("MySQL found: $versionNumber")
                }
            }
        }
        catch {
            $this.Logger.Debug("MySQL not found or error checking version: $($_.Exception.Message)")
        }
    }

    [void] CheckBoost([Dependency]$Dependency) {
        try {
            $boostPath = "C:\local\boost_1_84_0\tools\build\src\engine\build.bat"
            if (Test-Path $boostPath) {
                $Dependency.CurrentVersion = "1.84.0"
                $Dependency.InstallPath = $boostPath
                $Dependency.IsInstalled = $true
                $Dependency.IsUpToDate = $this.CompareVersions("1.84.0", $Dependency.MinVersion) -ge 0
                $this.Logger.Info("Boost found: 1.84.0")
            }
        }
        catch {
            $this.Logger.Debug("Boost not found: $($_.Exception.Message)")
        }
    }

    [int] CompareVersions([string]$Version1, [string]$Version2) {
        $v1Parts = $Version1 -split '\.'
        $v2Parts = $Version2 -split '\.'
        
        $maxLength = [Math]::Max($v1Parts.Length, $v2Parts.Length)
        
        for ($i = 0; $i -lt $maxLength; $i++) {
            $v1Part = if ($i -lt $v1Parts.Length) { [int]$v1Parts[$i] } else { 0 }
            $v2Part = if ($i -lt $v2Parts.Length) { [int]$v2Parts[$i] } else { 0 }
            
            if ($v1Part -gt $v2Part) { return 1 }
            if ($v1Part -lt $v2Part) { return -1 }
        }
        
        return 0
    }

    [array] GetMissingDependencies() {
        return $this.Dependencies.Values | Where-Object { -not $_.IsInstalled }
    }

    [array] GetOutdatedDependencies() {
        return $this.Dependencies.Values | Where-Object { $_.IsInstalled -and -not $_.IsUpToDate }
    }

    [bool] InstallDependency([string]$DependencyName) {
        $dependency = $this.Dependencies[$DependencyName]
        if (-not $dependency) {
            $this.Logger.Error("Unknown dependency: $DependencyName")
            return $false
        }

        $this.Logger.Info("Installing $($dependency.Name)...")
        
        try {
            switch ($dependency.Name) {
                "Git" { return $this.InstallGit($dependency) }
                "CMake" { return $this.InstallCMake($dependency) }
                "VisualStudio" { return $this.InstallVisualStudio($dependency) }
                "OpenSSL" { return $this.InstallOpenSSL($dependency) }
                "MySQL" { return $this.InstallMySQL($dependency) }
                "Boost" { return $this.InstallBoost($dependency) }
            }
        }
        catch {
            $this.Logger.Error("Failed to install $($dependency.Name): $($_.Exception.Message)" -Exception $_
            return $false
        }
    }

    [bool] InstallGit([Dependency]$Dependency) {
        try {
            # Get latest Git version from GitHub API
            $gitApiUrl = "https://api.github.com/repos/git-for-windows/git/releases/latest"
            $gitRelease = Invoke-RestMethod -Uri $gitApiUrl
            $gitAsset = $gitRelease.assets | Where-Object { $_.name -like "*64-bit.exe" } | Select-Object -First 1
            
            if (-not $gitAsset) {
                throw "Could not find Git 64-bit installer"
            }

            $installerPath = Join-Path $this.DownloadFolder $gitAsset.name
            
            # Download Git installer
            $this.Logger.Info("Downloading Git installer...")
            Invoke-SecureDownload -Url $gitAsset.browser_download_url -Destination $installerPath

            # Create silent install configuration
            $gitInfPath = Join-Path $this.DownloadFolder "gitinstall.inf"
            $gitInfContent = @"
[Setup]
Lang=default
Dir=C:\Program Files\Git
Group=Git
NoIcons=0
SetupType=default
Components=ext,ext\shellhere,ext\guihere,gitlfs,assoc,assoc_sh
Tasks=
EditorOption=Notepad++
CustomEditorPath=
PathOption=Cmd
SSHOption=OpenSSH
TortoiseOption=false
CURLOption=OpenSSL
CRLFOption=CRLFAlways
BashTerminalOption=ConHost
PerformanceTweaksFSCache=Enabled
UseCredentialManager=Enabled
EnableSymlinks=Disabled
EnableBuiltinInteractiveAdd=Disabled
"@
            Set-Content -Path $gitInfPath -Value $gitInfContent

            # Install Git silently
            $this.Logger.Info("Installing Git...")
            $arguments = "/VERYSILENT /NORESTART /LOADINF=`"$gitInfPath`""
            Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait

            # Verify installation
            if (Test-Path "C:\Program Files\Git\git-cmd.exe") {
                $this.Logger.Info("Git installed successfully")
                return $true
            } else {
                throw "Git installation verification failed"
            }
        }
        catch {
            $this.Logger.Error("Git installation failed: $($_.Exception.Message)" -Exception $_
            return $false
        }
    }

    [bool] InstallCMake([Dependency]$Dependency) {
        try {
            $installerPath = Join-Path $this.DownloadFolder "cmake-installer.msi"
            
            # Download CMake installer
            $this.Logger.Info("Downloading CMake installer...")
            Invoke-SecureDownload -Url $Dependency.DownloadUrl -Destination $installerPath -ExpectedChecksum $Dependency.Checksum

            # Install CMake silently
            $this.Logger.Info("Installing CMake...")
            $arguments = "/i `"$installerPath`" /norestart /quiet"
            Start-Process msiexec.exe -ArgumentList $arguments -Wait

            # Verify installation
            if (Test-Path "C:\Program Files\CMake\bin\cmake.exe") {
                $this.Logger.Info("CMake installed successfully")
                return $true
            } else {
                throw "CMake installation verification failed"
            }
        }
        catch {
            $this.Logger.Error("CMake installation failed: $($_.Exception.Message)" -Exception $_
            return $false
        }
    }

    [bool] InstallVisualStudio([Dependency]$Dependency) {
        try {
            $installerPath = Join-Path $this.DownloadFolder "vs_community.exe"
            
            # Download Visual Studio installer
            $this.Logger.Info("Downloading Visual Studio installer...")
            Invoke-SecureDownload -Url $Dependency.DownloadUrl -Destination $installerPath

            # Install Visual Studio with required components
            $this.Logger.Info("Installing Visual Studio 2022 Community...")
            $arguments = "--add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Workload.NativeDesktop;includeRecommended --quiet --norestart"
            Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait

            # Verify installation
            if (Test-Path "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe") {
                $this.Logger.Info("Visual Studio 2022 Community installed successfully")
                return $true
            } else {
                throw "Visual Studio installation verification failed"
            }
        }
        catch {
            $this.Logger.Error("Visual Studio installation failed: $($_.Exception.Message)" -Exception $_
            return $false
        }
    }

    [bool] InstallOpenSSL([Dependency]$Dependency) {
        try {
            $installerPath = Join-Path $this.DownloadFolder "openssl-installer.exe"
            
            # Download OpenSSL installer
            $this.Logger.Info("Downloading OpenSSL installer...")
            Invoke-SecureDownload -Url $Dependency.DownloadUrl -Destination $installerPath -ExpectedChecksum $Dependency.Checksum

            # Install OpenSSL silently
            $this.Logger.Info("Installing OpenSSL...")
            $arguments = "/VERYSILENT"
            Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait

            # Verify installation
            if (Test-Path "C:\Program Files\OpenSSL-Win64\bin\openssl.exe") {
                $this.Logger.Info("OpenSSL installed successfully")
                return $true
            } else {
                throw "OpenSSL installation verification failed"
            }
        }
        catch {
            $this.Logger.Error("OpenSSL installation failed: $($_.Exception.Message)" -Exception $_
            return $false
        }
    }

    [bool] InstallMySQL([Dependency]$Dependency) {
        try {
            $zipPath = Join-Path $this.DownloadFolder "mysql.zip"
            
            # Download MySQL
            $this.Logger.Info("Downloading MySQL...")
            Invoke-SecureDownload -Url $Dependency.DownloadUrl -Destination $zipPath -ExpectedChecksum $Dependency.Checksum

            # Extract MySQL
            $this.Logger.Info("Extracting MySQL...")
            Expand-Archive -Path $zipPath -DestinationPath "C:\MySQL" -Force

            # Move files from subdirectory
            $mysqlSubDir = Get-ChildItem -Path "C:\MySQL" -Directory | Where-Object { $_.Name -like "mysql-*" } | Select-Object -First 1
            if ($mysqlSubDir) {
                Get-ChildItem -Path $mysqlSubDir.FullName | Move-Item -Destination "C:\MySQL"
                Remove-Item -Path $mysqlSubDir.FullName -Force
            }

            # Create debug directory and copy libraries
            New-Item -Path "C:\MySQL\lib\debug" -ItemType Directory -Force | Out-Null
            Copy-Item -Path "C:\MySQL\lib\libmysql.lib" -Destination "C:\MySQL\lib\debug\libmysql.lib" -Force
            Copy-Item -Path "C:\MySQL\lib\libmysql.dll" -Destination "C:\MySQL\lib\debug\libmysql.dll" -Force

            # Verify installation
            if (Test-Path "C:\MySQL\bin\mysqld.exe") {
                $this.Logger.Info("MySQL installed successfully")
                return $true
            } else {
                throw "MySQL installation verification failed"
            }
        }
        catch {
            $this.Logger.Error("MySQL installation failed: $($_.Exception.Message)" -Exception $_
            return $false
        }
    }

    [bool] InstallBoost([Dependency]$Dependency) {
        try {
            $installerPath = Join-Path $this.DownloadFolder "boost-installer.exe"
            
            # Download Boost installer
            $this.Logger.Info("Downloading Boost installer...")
            Invoke-SecureDownload -Url $Dependency.DownloadUrl -Destination $installerPath -ExpectedChecksum $Dependency.Checksum

            # Install Boost silently
            $this.Logger.Info("Installing Boost...")
            $arguments = "/VERYSILENT"
            Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait

            # Set Boost environment variable
            $envName = "BOOST_ROOT"
            $envValue = "C:/local/boost_1_84_0"
            [System.Environment]::SetEnvironmentVariable($envName, $envValue, [System.EnvironmentVariableTarget]::Machine)

            # Bootstrap and build Boost
            if (Test-Path "C:\local\boost_1_84_0") {
                Set-Location "C:\local\boost_1_84_0"
                Start-Process -FilePath ".\bootstrap.bat" -Wait -NoNewWindow
                Start-Process -FilePath ".\b2.exe" -Wait
                Set-Location $PSScriptRoot
            }

            # Verify installation
            if (Test-Path "C:\local\boost_1_84_0\b2.exe") {
                $this.Logger.Info("Boost installed successfully")
                return $true
            } else {
                throw "Boost installation verification failed"
            }
        }
        catch {
            $this.Logger.Error("Boost installation failed: $($_.Exception.Message)" -Exception $_
            return $false
        }
    }
}

function Initialize-DependencyManager {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$DownloadFolder,
        
        [Parameter(Mandatory = $true)]
        [Logger]$Logger
    )

    return [DependencyManager]::new($DownloadFolder, $Logger)
}

Export-ModuleMember -Function Initialize-DependencyManager
Export-ModuleMember -Class Dependency, DependencyManager