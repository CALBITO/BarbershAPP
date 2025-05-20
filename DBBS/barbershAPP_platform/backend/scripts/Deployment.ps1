# Deployment script for Barbershop Platform
$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "🚀 Starting deployment process..." -ForegroundColor Cyan

try {
    # 1. Backend preparation
    Write-Host "📦 Preparing backend..." -ForegroundColor Yellow
    Set-Location $BackendDir
    
    # Check virtual environment
    if (-not (Test-Path "venv")) {
        python -m venv venv
        .\venv\Scripts\activate
        pip install -r requirements.txt
    }

    # 2. Database migrations
    Write-Host "🗃️ Running database migrations..." -ForegroundColor Yellow
    $env:FLASK_APP = "src.app:create_app"
    flask db upgrade

    # 3. Frontend build
    Write-Host "🏗️ Building frontend..." -ForegroundColor Yellow
    Set-Location $FrontendDir
    npm install
    npm run build

    # 4. Prepare for Render deployment
    Write-Host "📤 Preparing for Render deployment..." -ForegroundColor Yellow
    Set-Location $ProjectRoot

    # Check if render.yaml exists
    if (-not (Test-Path "render.yaml")) {
        Write-Error "render.yaml not found!"
        exit 1
    }

    # 5. Git operations
    git add .
    git commit -m "Deployment update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git push origin main

    Write-Host "✅ Deployment preparation complete!" -ForegroundColor Green
    Write-Host "🌐 Visit Render dashboard to complete deployment" -ForegroundColor Cyan
    Write-Host "   https://dashboard.render.com" -ForegroundColor Cyan

} catch {
    Write-Error "❌ Deployment failed: $_"
    exit 1
} finally {
    # Reset location
    Set-Location $ProjectRoot
}