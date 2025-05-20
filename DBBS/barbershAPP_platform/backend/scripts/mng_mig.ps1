param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('init', 'create', 'upgrade', 'downgrade', 'history', 'setup')]
    [string]$Command,
    
    [Parameter()]
    [string]$Message
)

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

# Set environment variables
$env:PYTHONPATH = $PWD
$env:FLASK_APP = "src.app:create_app"
$env:FLASK_ENV = "development"

function Invoke-FlaskPython {
    param([string]$Command)
    flask shell --command $Command
}

try {
    switch ($Command) {
        'init' {
            Write-Log "Initializing database migrations..." "INFO"
            flask db init
            Write-Log "Migration directory created successfully" "SUCCESS"
        }
        'setup' {
            Write-Log "Setting up database..." "INFO"
            # Enable PostGIS
            $setupCmd = "from src.database import db; "
            $setupCmd += "from src.database.setup import setup_database; "
            $setupCmd += "setup_database()"
            Invoke-FlaskPython $setupCmd
            Write-Log "Database setup completed" "SUCCESS"
        }
        'create' {
            if (-not $Message) {
                Write-Log "Migration message is required for create command" "ERROR"
                exit 1
            }
            Write-Log "Creating new migration: $Message" "INFO"
            flask db migrate -m "$Message"
            Write-Log "Migration created successfully" "SUCCESS"
        }
        'upgrade' {
            Write-Log "Upgrading database..." "INFO"
            flask db upgrade
            Write-Log "Database upgraded successfully" "SUCCESS"
        }
        'downgrade' {
            Write-Log "Downgrading database..." "WARNING"
            flask db downgrade
            Write-Log "Database downgraded" "SUCCESS"
        }
        'history' {
            Write-Log "Migration History:" "INFO"
            flask db history
        }
    }
} catch {
    Write-Log $_.Exception.Message "ERROR"
    exit 1
}