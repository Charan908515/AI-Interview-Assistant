# -------------------------------------------
# Set-Audio-Devices.ps1
# Robust VB-CABLE setup for Windows 11
# Logs steps and pauses so you see messages
# -------------------------------------------

Add-Type -AssemblyName System.Windows.Forms

try {
    Write-Host "=== VB-CABLE Audio Configuration ===" -ForegroundColor Cyan

    # Start log file
    $LogFile = "$env:TEMP\VBConfigLog.txt"
    if (Test-Path $LogFile) { Remove-Item $LogFile -Force }
    Start-Transcript -Path $LogFile -Append

    # Load AudioDeviceCmdlets
    Write-Host "Checking for AudioDeviceCmdlets..."
    if (-not (Get-Module -ListAvailable -Name AudioDeviceCmdlets)) {
        Write-Host "Installing AudioDeviceCmdlets..."
        Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force | Out-Null
        Install-Module -Name AudioDeviceCmdlets -Force | Out-Null
    }
    Import-Module AudioDeviceCmdlets -ErrorAction Stop

    # Get all audio devices
    $devices = Get-AudioDevice -List

    # Find VB-CABLE playback and recording
    $vbPlayback = $devices | Where-Object { $_.Type -eq 'Playback' -and $_.Name -match 'CABLE' }
    $vbRecording = $devices | Where-Object { $_.Type -eq 'Capture' -and $_.Name -match 'CABLE' }
    $defaultPlayback = Get-AudioDevice -Playback

    if (-not $vbPlayback) { throw "VB-CABLE playback device not found." }
    if (-not $vbRecording) { throw "VB-CABLE recording device not found." }
    if (-not $defaultPlayback) { throw "Could not detect default playback device." }

    Write-Host "Found playback: $($vbPlayback.Name)"
    Write-Host "Found recording: $($vbRecording.Name)"
    Write-Host "Current output: $($defaultPlayback.Name)"

    # Set as default for all roles
    Set-AudioDevice $vbPlayback.ID -DefaultOnly
    Set-AudioDevice $vbPlayback.ID -CommunicationOnly
    Set-AudioDevice $vbRecording.ID -DefaultOnly
    Set-AudioDevice $vbRecording.ID -CommunicationOnly

    # Use SoundVolumeView to enable Listen To This Device
    $nirsoftDir = "$env:TEMP\SVV"
    $svvExe = Join-Path $nirsoftDir "SoundVolumeView.exe"

    if (!(Test-Path $svvExe)) {
        Write-Host "Downloading SoundVolumeView..."
        Invoke-WebRequest -Uri "https://www.nirsoft.net/utils/soundvolumeview.zip" -OutFile "$nirsoftDir\svv.zip" -UseBasicParsing
        Expand-Archive -Path "$nirsoftDir\svv.zip" -DestinationPath $nirsoftDir -Force
    }

    if (!(Test-Path $svvExe)) { throw "SoundVolumeView.exe not found." }

    Write-Host "Enabling Listen To This Device..."
    & $svvExe /SetListenToThisDevice "$($vbRecording.Name)" 1
    & $svvExe /SetPlaybackThroughDevice "$($vbRecording.Name)" "$($defaultPlayback.Name)"

    Write-Host "VB-CABLE setup completed successfully!"
    Stop-Transcript
    Write-Host "Press Enter to close this window..."
    Read-Host
    exit 0
}
catch {
    Stop-Transcript
    $msg = "Automatic setup failed.`n`nError: $($_.Exception.Message)`n`nOpen Sound Settings manually?"
    $result = [System.Windows.Forms.MessageBox]::Show($msg, "VB-CABLE Setup Error",
                [System.Windows.Forms.MessageBoxButtons]::YesNo,
                [System.Windows.Forms.MessageBoxIcon]::Error)
    if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
        Start-Process "ms-settings:sound"
    }
    exit 1
}
