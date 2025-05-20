[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('start','stop','restart','status')]
    [string]$Action
)

# Get the script's directory regardless of where it's called from
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$redisPath = Join-Path $scriptPath "..\redis\redis-server.exe"
$redisLogPath = Join-Path $scriptPath "..\logs\redis.log"

# Ensure log directory exists
$logDir = Split-Path -Parent $redisLogPath
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

function Get-RedisStatus {
    $running = Get-Process redis-server -ErrorAction SilentlyContinue
    return $null -ne $running
}

function Write-RedisLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Add-Content -Path $redisLogPath
    Write-Host $Message
}

# Verify Redis executable exists
if (-not (Test-Path $redisPath)) {
    Write-RedisLog "Error: Redis executable not found at: $redisPath"
    exit 1
}

switch ($Action) {
    'start' {
        if (-not (Get-RedisStatus)) {
            try {
                Start-Process $redisPath -WindowStyle Hidden
                Write-RedisLog "Redis started successfully"
            }
            catch {
                Write-RedisLog "Error starting Redis: $_"
                exit 1
            }
        } else {
            Write-RedisLog "Redis is already running"
        }
    }
    'stop' {
        try {
            Stop-Process -Name redis-server -Force -ErrorAction Stop
            Write-RedisLog "Redis stopped successfully"
        }
        catch {
            Write-RedisLog "Error stopping Redis: $_"
            exit 1
        }
    }
    'restart' {
        & $MyInvocation.MyCommand.Path -Action stop
        Start-Sleep -Seconds 2
        & $MyInvocation.MyCommand.Path -Action start
    }
    'status' {
        if (Get-RedisStatus) {
            Write-RedisLog "Redis is running"
        } else {
            Write-RedisLog "Redis is not running"
        }
    }
}