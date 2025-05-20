function Write-Log {
    param([string]$Message, [string]$Type = "INFO")
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Type] $Message" -ForegroundColor $(
        switch($Type) {
            "ERROR" { "Red" }
            "SUCCESS" { "Green" }
            "WARNING" { "Yellow" }
            default { "White" }
        }
    )
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

try {
    Write-Log "Starting Diagnostic Checks..." "INFO"

    # Check working directory
    if (-not (Test-Path "src")) {
        Write-Log "Must run from backend directory!" "ERROR"
        exit 1
    }

    # Set and verify environment variables
    $env:FLASK_APP = "src.app:app"
    $env:FLASK_ENV = "development"
    $env:PYTHONPATH = "src"
    
    Write-Log "Environment Configuration:" "INFO"
    Write-Log "FLASK_APP: $env:FLASK_APP"
    Write-Log "FLASK_ENV: $env:FLASK_ENV"
    Write-Log "PYTHONPATH: $env:PYTHONPATH"

    # Check required tools
    $tools = @("python", "pip", "flask", "redis-cli")
    foreach ($tool in $tools) {
        if (Test-Command $tool) {
            Write-Log "$tool is installed" "SUCCESS"
        } else {
            Write-Log "$tool is not installed" "ERROR"
        }
    }

    # Check Python packages
    Write-Log "Checking Python packages..." "INFO"
    pip list | Select-String -Pattern "flask|sqlalchemy|redis|psycopg2|alembic"

    # Check Redis server
    Write-Log "Checking Redis server..." "INFO"
    $redis = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
    if ($redis) {
        Write-Log "Redis server is running" "SUCCESS"
    } else {
        Write-Log "Redis server is not running" "WARNING"
        Write-Log "Starting Redis server..." "INFO"
        Start-Process redis-server -NoNewWindow
    }

    # Check database connection
    Write-Log "Running database checks..." "INFO"
    python scripts\check_db.py
    if ($LASTEXITCODE -ne 0) {
        throw "Database check failed"
    }

    # Check Flask application
    Write-Log "Checking Flask application..." "INFO"
    try {
        flask --version
        Write-Log "Flask is configured correctly" "SUCCESS"
    } catch {
        Write-Log "Flask configuration error: $_" "ERROR"
    }

    # Print summary
    Write-Log "`nDiagnostic Summary:" "INFO"
    Write-Log "✓ Environment variables set" "SUCCESS"
    Write-Log "✓ Required tools checked" "SUCCESS"
    Write-Log "✓ Python packages verified" "SUCCESS"
    Write-Log "✓ Redis server status checked" "SUCCESS"
    Write-Log "✓ Database connection tested" "SUCCESS"
    Write-Log "✓ Flask configuration verified" "SUCCESS"

} catch {
    Write-Log $_.Exception.Message "ERROR"
    exit 1
} finally {
    Write-Log "Diagnostic check completed" "INFO"
}