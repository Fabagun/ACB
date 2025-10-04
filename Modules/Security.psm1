#Requires -Version 5.1

<#
.SYNOPSIS
    Security module for AzerothCore AutoBuilder

.DESCRIPTION
    Provides secure credential management, input validation, and security utilities.

.NOTES
    Author: AzerothCore AutoBuilder
    Version: 2.0.0
#>

function Get-SecurePassword {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Prompt,
        
        [Parameter()]
        [string]$ConfirmPrompt = "Confirm password",
        
        [Parameter()]
        [int]$MinLength = 8,
        
        [Parameter()]
        [switch]$RequireConfirmation
    )

    do {
        $securePassword = Read-Host -AsSecureString -Prompt $Prompt
        $password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
        
        if ($password.Length -lt $MinLength) {
            Write-Warning "Password must be at least $MinLength characters long."
            continue
        }

        if ($RequireConfirmation) {
            $confirmSecurePassword = Read-Host -AsSecureString -Prompt $ConfirmPrompt
            $confirmPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($confirmSecurePassword))
            
            if ($password -ne $confirmPassword) {
                Write-Warning "Passwords do not match. Please try again."
                continue
            }
        }

        return $securePassword
    } while ($true)
}

function Get-SecureCredential {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Username,
        
        [Parameter()]
        [string]$Message = "Enter password for $Username"
    )

    $securePassword = Get-SecurePassword -Prompt $Message
    return New-Object System.Management.Automation.PSCredential($Username, $securePassword)
}

function Test-PasswordStrength {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Password
    )

    $score = 0
    $feedback = @()

    # Length check
    if ($Password.Length -ge 8) { $score += 1 } else { $feedback += "Password should be at least 8 characters long" }
    if ($Password.Length -ge 12) { $score += 1 }

    # Character variety checks
    if ($Password -match '[a-z]') { $score += 1 } else { $feedback += "Password should contain lowercase letters" }
    if ($Password -match '[A-Z]') { $score += 1 } else { $feedback += "Password should contain uppercase letters" }
    if ($Password -match '\d') { $score += 1 } else { $feedback += "Password should contain numbers" }
    if ($Password -match '[^a-zA-Z\d]') { $score += 1 } else { $feedback += "Password should contain special characters" }

    # Common patterns check
    if ($Password -match '(.)\1{2,}') { $score -= 1; $feedback += "Password should not contain repeated characters" }
    if ($Password -match '(123|abc|qwe|asd)') { $score -= 1; $feedback += "Password should not contain common sequences" }

    $strength = switch ($score) {
        { $_ -le 2 } { "Weak" }
        { $_ -le 4 } { "Medium" }
        { $_ -le 6 } { "Strong" }
        default { "Very Strong" }
    }

    return @{
        Score = $score
        Strength = $strength
        Feedback = $feedback
    }
}

function Test-InputValidation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Input,
        
        [Parameter(Mandatory = $true)]
        [ValidateSet("Path", "URL", "Email", "Alphanumeric", "Numeric", "Version")]
        [string]$Type
    )

    $patterns = @{
        Path = '^[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$'
        URL = '^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        Email = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        Alphanumeric = '^[a-zA-Z0-9]+$'
        Numeric = '^\d+$'
        Version = '^\d+\.\d+(\.\d+)?(\.\d+)?$'
    }

    if ($patterns.ContainsKey($Type)) {
        return $Input -match $patterns[$Type]
    }

    return $false
}

function Get-FileChecksum {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        
        [Parameter()]
        [ValidateSet("MD5", "SHA1", "SHA256", "SHA512")]
        [string]$Algorithm = "SHA256"
    )

    if (-not (Test-Path $FilePath)) {
        throw "File not found: $FilePath"
    }

    $hash = Get-FileHash -Path $FilePath -Algorithm $Algorithm
    return $hash.Hash
}

function Test-FileIntegrity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        
        [Parameter(Mandatory = $true)]
        [string]$ExpectedChecksum,
        
        [Parameter()]
        [ValidateSet("MD5", "SHA1", "SHA256", "SHA512")]
        [string]$Algorithm = "SHA256"
    )

    try {
        $actualChecksum = Get-FileChecksum -FilePath $FilePath -Algorithm $Algorithm
        return $actualChecksum -eq $ExpectedChecksum
    }
    catch {
        Write-LogError "Failed to verify file integrity: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Invoke-SecureDownload {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,
        
        [Parameter(Mandatory = $true)]
        [string]$Destination,
        
        [Parameter()]
        [string]$ExpectedChecksum,
        
        [Parameter()]
        [ValidateSet("MD5", "SHA1", "SHA256", "SHA512")]
        [string]$ChecksumAlgorithm = "SHA256",
        
        [Parameter()]
        [switch]$Resume
    )

    try {
        Write-LogInfo "Starting secure download from: $Url"
        Write-LogInfo "Destination: $Destination"

        # Create destination directory if it doesn't exist
        $destDir = Split-Path -Parent $Destination
        if (-not (Test-Path $destDir)) {
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }

        # Use BITS for better reliability and resume capability
        if ($Resume -and (Test-Path $Destination)) {
            Write-LogInfo "Resuming download..."
            Resume-BitsTransfer -BitsJob (Get-BitsTransfer | Where-Object { $_.DisplayName -eq $Url })
        } else {
            Start-BitsTransfer -Source $Url -Destination $Destination -DisplayName $Url
        }

        # Verify file integrity if checksum provided
        if ($ExpectedChecksum) {
            Write-LogInfo "Verifying file integrity..."
            if (Test-FileIntegrity -FilePath $Destination -ExpectedChecksum $ExpectedChecksum -Algorithm $ChecksumAlgorithm) {
                Write-LogInfo "File integrity verified successfully"
            } else {
                throw "File integrity check failed. Expected: $ExpectedChecksum"
            }
        }

        Write-LogInfo "Download completed successfully"
        return $true
    }
    catch {
        Write-LogError "Download failed: $($_.Exception.Message)" -Exception $_
        return $false
    }
}

function Remove-SecureFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath
    )

    try {
        if (Test-Path $FilePath) {
            # Overwrite file with random data before deletion (basic secure deletion)
            $fileSize = (Get-Item $FilePath).Length
            $randomData = New-Object byte[] $fileSize
            (New-Object Random).NextBytes($randomData)
            [System.IO.File]::WriteAllBytes($FilePath, $randomData)
            
            Remove-Item -Path $FilePath -Force
            Write-LogInfo "File securely deleted: $FilePath"
        }
    }
    catch {
        Write-LogError "Failed to securely delete file: $($_.Exception.Message)" -Exception $_
    }
}

Export-ModuleMember -Function Get-SecurePassword, Get-SecureCredential, Test-PasswordStrength, Test-InputValidation, Get-FileChecksum, Test-FileIntegrity, Invoke-SecureDownload, Remove-SecureFile