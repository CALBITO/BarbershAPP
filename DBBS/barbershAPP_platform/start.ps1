# Function to write formatted log messages
function Write-Log {
    param([string]$Message, [string]$Type = "INFO")
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Type] $Message"
}

# Function to handle cleanup
function Remove-Processes {
    param($Processes)
    Write-Log "Cleaning up processes..." "CLEANUP"
    foreach ($proc in $Processes) {
        if ($proc) {
            try {
                Stop-Process -Id $proc.Id -Force
                Write-Log "Stopped process: $($proc.Name)" "CLEANUP"
            }
            catch {
                Write-Log "Error stopping process: $($proc.Name)" "ERROR"
            }
        }
    }
}

try {
    # Change to backend directory
    Set-Location -Path ".\backend"
    
    # Check Redis
    Write-Log "Checking Redis service..."
    $redis = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
    if (-not $redis) {
        Write-Log "Starting Redis server..." "ACTION"
        $redis = Start-Process redis-server -PassThru
        Start-Sleep -Seconds 2
    }

    # Setup virtual environment
    if (-not (Test-Path "venv")) {
        Write-Log "Creating virtual environment..." "ACTION"
        python -m venv venv
        if (-not $?) { throw "Failed to create virtual environment" }
    }

    # Activate virtual environment
    Write-Log "Activating virtual environment..."
    . .\venv\Scripts\Activate.ps1
    if (-not $?) { throw "Failed to activate virtual environment" }

    # Install dependencies
    Write-Log "Installing requirements..."
    pip install -r ..\requirements.txt --quiet
    if (-not $?) { throw "Failed to install requirements" }

    # Set environment variables
    $env:FLASK_APP = "src\app.py"
    $env:FLASK_ENV = "development"
    $env:PYTHONPATH = "src"

    # Initialize database
    Write-Log "Initializing database..."
    flask init-db
    if (-not $?) { throw "Failed to initialize database" }

    # Start Celery worker
    Write-Log "Starting Celery worker..."
    $celery = Start-Process powershell -ArgumentList @(
        "celery",
        "-A", "src.app.celery",
        "worker",
        "--pool=solo",
        "--loglevel=info"
    ) -PassThru

    # Register cleanup on script exit
    $null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
        Remove-Processes @($celery, $redis)
    }

    # Start Flask application
    Write-Log "Starting Flask application..." "ACTION"
    Write-Log "Application ready at http://localhost:5000" "SUCCESS"
    flask run --host=0.0.0.0 --port=5000

} catch {
    Write-Log $_.Exception.Message "ERROR"
    Remove-Processes @($celery, $redis)
    exit 1
}
finally {
    # Cleanup processes on script exit
    Remove-Processes @($celery, $redis)
}