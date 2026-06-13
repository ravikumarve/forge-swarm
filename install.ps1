# Forge Swarm Installation Script for Windows
# Requirements: Python 3.10+, Ollama

# Error action preference
$ErrorActionPreference = "Stop"

# Color functions
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Header {
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  ⚡ Forge Swarm Installation" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
}

# Check Python version
function Test-PythonVersion {
    Write-Info "Checking Python version..."

    try {
        $pythonVersion = python --version 2>&1
        Write-Info "Found: $pythonVersion"

        # Extract version number
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]

            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
                Write-Error "Python 3.10+ is required (found: $pythonVersion)"
                Write-Info "Please install Python 3.10 or higher from https://python.org"
                exit 1
            }

            Write-Success "Python $major.$minor detected"
        } else {
            Write-Error "Could not parse Python version"
            exit 1
        }
    } catch {
        Write-Error "Python is not installed"
        Write-Info "Please install Python 3.10 or higher from https://python.org"
        exit 1
    }
}

# Check and install Ollama
function Test-OllamaInstallation {
    Write-Info "Checking Ollama installation..."

    try {
        $ollamaVersion = ollama --version 2>&1
        Write-Success "Ollama is already installed ($ollamaVersion)"
    } catch {
        Write-Warning "Ollama is not installed"
        Write-Info "Please install Ollama from https://ollama.ai/download"
        Write-Info "After installation, restart PowerShell and run this script again"
        exit 1
    }
}

# Start Ollama server
function Start-OllamaServer {
    Write-Info "Starting Ollama server..."

    # Check if Ollama is already running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2
        Write-Success "Ollama server is already running"
        return
    } catch {
        # Ollama not running, start it
    }

    # Start Ollama in background
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

    # Wait for Ollama to start
    Write-Info "Waiting for Ollama server to start..."
    for ($i = 1; $i -le 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2
            Write-Success "Ollama server started"
            return
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    Write-Error "Failed to start Ollama server"
    exit 1
}

# Pull required models
function Install-Models {
    Write-Info "Pulling required models..."

    $modelsToPull = @("llama3.1:8b", "nomic-embed-text")
    $modelsNeeded = @()

    # Check which models are already pulled
    $existingModels = ollama list 2>&1

    foreach ($model in $modelsToPull) {
        if ($existingModels -match $model) {
            Write-Success "Model $model already exists"
        } else {
            $modelsNeeded += $model
        }
    }

    # Pull missing models
    foreach ($model in $modelsNeeded) {
        Write-Info "Pulling $model..."
        try {
            ollama pull $model
            Write-Success "Model $model pulled successfully"
        } catch {
            Write-Error "Failed to pull model $model"
            exit 1
        }
    }
}

# Create virtual environment
function New-VirtualEnvironment {
    Write-Info "Creating virtual environment..."

    if (Test-Path "venv") {
        Write-Warning "Virtual environment already exists"
        $response = Read-Host "Do you want to recreate it? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Remove-Item -Recurse -Force venv
            python -m venv venv
            Write-Success "Virtual environment recreated"
        } else {
            Write-Success "Using existing virtual environment"
        }
    } else {
        python -m venv venv
        Write-Success "Virtual environment created"
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Info "Installing Python dependencies..."

    # Activate virtual environment
    & .\venv\Scripts\Activate.ps1

    # Upgrade pip
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip

    # Install requirements
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        Write-Success "Dependencies installed"
    } else {
        Write-Error "requirements.txt not found"
        exit 1
    }
}

# Run installation tests
function Test-Installation {
    Write-Info "Running installation tests..."

    if (Test-Path "test_installation.py") {
        & .\venv\Scripts\python.exe test_installation.py
        if ($LASTEXITCODE -eq 0) {
            Write-Success "All installation tests passed"
        } else {
            Write-Error "Installation tests failed"
            exit 1
        }
    } else {
        Write-Warning "test_installation.py not found, skipping tests"
    }
}

# Launch Forge Swarm
function Start-ForgeSwarm {
    Write-Success "Installation complete!"
    Write-Host ""
    Write-Info "Launching Forge Swarm..."
    Write-Host ""

    # Activate virtual environment
    & .\venv\Scripts\Activate.ps1

    # Launch Streamlit
    streamlit run Home.py
}

# Main installation flow
function Main {
    Write-Header

    # Check Python
    Test-PythonVersion

    # Check and install Ollama
    Test-OllamaInstallation

    # Start Ollama server
    Start-OllamaServer

    # Pull models
    Install-Models

    # Create virtual environment
    New-VirtualEnvironment

    # Install dependencies
    Install-Dependencies

    # Run tests
    Test-Installation

    # Launch
    Start-ForgeSwarm
}

# Run main function
Main
