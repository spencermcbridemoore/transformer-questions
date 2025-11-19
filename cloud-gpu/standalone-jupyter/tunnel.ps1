# PowerShell script to create SSH tunnel for Jupyter
# Usage: .\tunnel.ps1 -Host your-remote-host -Port 8888

param(
    [Parameter(Mandatory=$true)]
    [string]$Host,
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8888,
    
    [Parameter(Mandatory=$false)]
    [string]$RemotePort = "8888",
    
    [Parameter(Mandatory=$false)]
    [string]$User = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$IdentityFile = $null
)

Write-Host "Creating SSH tunnel for Jupyter..." -ForegroundColor Cyan
Write-Host "Host: $Host" -ForegroundColor Yellow
Write-Host "Local Port: $Port -> Remote Port: $RemotePort" -ForegroundColor Yellow
Write-Host ""
Write-Host "Once connected, access Jupyter at: http://localhost:$Port" -ForegroundColor Green
Write-Host "Press Ctrl+C to close the tunnel" -ForegroundColor Yellow
Write-Host ""

# Build SSH command
$sshArgs = @("-L", "${Port}:localhost:${RemotePort}")

if ($User) {
    $sshTarget = "${User}@${Host}"
} else {
    $sshTarget = $Host
}

if ($IdentityFile) {
    $sshArgs += @("-i", $IdentityFile)
}

$sshArgs += @("-N", $sshTarget)

try {
    ssh @sshArgs
} catch {
    Write-Host "Error creating tunnel: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure SSH is installed and accessible." -ForegroundColor Yellow
    exit 1
}

