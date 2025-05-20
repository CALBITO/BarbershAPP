# Project setup script for Barbershop Platform
# Author: Carlos Peña-Acosta
# Date: 2025-05-16

# Enable error handling
$ErrorActionPreference = "Stop"

# Define colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Project structure
$projectStructure = @{
    "src" = @(
        "api",
        "database",
        "models",
        "middleware",
        "schemas",
        "services",
        "utils"
    )
    "tests" = @(
        "unit",
        "integration",
        "e2e"
    )
    "scripts" = $null
    "migrations" = $null
    "docs" = @(
        "api",
        "architecture"
    )
}

# Required Python packages
$requiredPackages = @(
    "flask",
    "flask-sqlalchemy",
    "flask-migrate",
    "psycopg2-binary",
    "python-dotenv",
    "pytest",
    "marshmallow",
    "flask-marshmallow",
    "redis",
    "celery",
    "gunicorn"
    "gunicorn",
    "flask-cors",
    "flask-talisman",
    "sentry-sdk",
    "prometheus-client",
    "flask-limiter",
    "whitenoise"
)

# Create directory structure
foreach ($dir in $projectStructure.Keys) {
    $path = Join-Path $PWD $dir
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory -Force
        Write-ColorOutput Green "✓ Created directory: $dir"
        
        if ($projectStructure[$dir]) {
            foreach ($subdir in $projectStructure[$dir]) {
                $subdirPath = Join-Path $path $subdir
                New-Item -Path $subdirPath -ItemType Directory -Force
                New-Item -Path (Join-Path $subdirPath "__init__.py") -ItemType File -Force
                Write-ColorOutput Green "  ✓ Created subdirectory: $dir/$subdir"
            }
        }
        
        # Create __init__.py for Python packages
        if ($dir -eq "src" -or $dir -eq "tests") {
            New-Item -Path (Join-Path $path "__init__.py") -ItemType File -Force
        }
    }
}

# Create or update virtual environment
if (-not (Test-Path "venv")) {
    Write-ColorOutput Yellow "Creating virtual environment..."
    python -m venv venv
    Write-ColorOutput Green "✓ Virtual environment created"
}

# Activate virtual environment and install packages
Write-ColorOutput Yellow "Activating virtual environment and installing packages..."
& .\venv\Scripts\Activate.ps1

foreach ($package in $requiredPackages) {
    Write-ColorOutput Yellow "Installing $package..."
    pip install $package
}

# Create example environment file
$envExample = @"
# Flask Configuration
FLASK_APP=src.app:create_app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DB_NAME=barbershop_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
"@

Set-Content -Path ".env.example" -Value $envExample
Write-ColorOutput Green "✓ Created .env.example file"

Write-ColorOutput Green "`n✓ Environment setup complete!"
Write-ColorOutput Yellow "`nNext steps:"
Write-ColorOutput White "1. Copy .env.example to .env and update with your values"
Write-ColorOutput White "2. Initialize database with 'flask db init'"
Write-ColorOutput White "3. Run tests with 'pytest'"
Write-ColorOutput White "4. Start development server with 'flask run'"