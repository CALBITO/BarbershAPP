param(
    [switch]$Verbose,
    [switch]$Coverage
)

# Function to write formatted log messages
function Write-Log {
    param([string]$Message)
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
}

try {
    # Set environment variables
    $env:PYTHONPATH = "src"
    $env:FLASK_APP = "src.app:app"
    $env:FLASK_ENV = "testing"

    # Build pytest command
    $pytestArgs = @("tests", "-v")
    if ($Coverage) {
        $pytestArgs += @(
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html"
        )
    }
    if ($Verbose) {
        $pytestArgs += "-vv"
    }

    Write-Log "Running tests..."
    pytest $pytestArgs

    if ($LASTEXITCODE -eq 0) {
        Write-Log "All tests passed successfully!"
    } else {
        Write-Log "Tests failed with exit code: $LASTEXITCODE"
    }

} catch {
    Write-Log "Error running tests: $_"
    exit 1
}
 finally {
    # Cleanup
    Write-Log "Cleaning up..."
    $redis = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
    if ($redis) {
        Stop-Process -Id $redis.Id -Force
        Write-Log "Stopped Redis server."
    }
}