#!/bin/bash

# Forge Swarm Installation Script
# Supports: Linux, macOS
# Requirements: Python 3.10+, Ollama

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  ⚡ Forge Swarm Installation${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    print_info "Checking Python version..."

    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        print_info "Please install Python 3.10 or higher from https://python.org"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_error "Python 3.10+ is required (found: $PYTHON_VERSION)"
        exit 1
    fi

    print_success "Python $PYTHON_VERSION detected"
}

# Check and install Ollama
check_ollama() {
    print_info "Checking Ollama installation..."

    if ! command_exists ollama; then
        print_warning "Ollama is not installed"
        print_info "Installing Ollama..."

        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL https://ollama.ai/install.sh | sh
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            if command_exists brew; then
                brew install ollama
            else
                print_error "Homebrew not found. Please install Ollama manually from https://ollama.ai/download"
                exit 1
            fi
        else
            print_error "Unsupported OS. Please install Ollama manually from https://ollama.ai/download"
            exit 1
        fi

        print_success "Ollama installed"
    else
        print_success "Ollama is already installed"
    fi
}

# Start Ollama server
start_ollama() {
    print_info "Starting Ollama server..."

    # Check if Ollama is already running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama server is already running"
        return
    fi

    # Start Ollama in background
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!

    # Wait for Ollama to start
    print_info "Waiting for Ollama server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama server started (PID: $OLLAMA_PID)"
            return
        fi
        sleep 1
    done

    print_error "Failed to start Ollama server"
    exit 1
}

# Pull required models
pull_models() {
    print_info "Pulling required models..."

    # Check if models are already pulled
    MODELS_TO_PULL=("llama3.1:8b" "nomic-embed-text")
    MODELS_NEEDED=()

    for model in "${MODELS_TO_PULL[@]}"; do
        if ollama list | grep -q "$model"; then
            print_success "Model $model already exists"
        else
            MODELS_NEEDED+=("$model")
        fi
    done

    # Pull missing models
    for model in "${MODELS_NEEDED[@]}"; do
        print_info "Pulling $model..."
        if ollama pull "$model"; then
            print_success "Model $model pulled successfully"
        else
            print_error "Failed to pull model $model"
            exit 1
        fi
    done
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."

    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            print_success "Virtual environment recreated"
        else
            print_success "Using existing virtual environment"
        fi
    else
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."

    # Activate virtual environment
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        source venv/bin/activate
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        source venv/bin/activate
    fi

    # Upgrade pip
    pip install --upgrade pip

    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Run installation tests
run_tests() {
    print_info "Running installation tests..."

    if [ -f "test_installation.py" ]; then
        if python test_installation.py; then
            print_success "All installation tests passed"
        else
            print_error "Installation tests failed"
            exit 1
        fi
    else
        print_warning "test_installation.py not found, skipping tests"
    fi
}

# Launch Forge Swarm
launch_forge_swarm() {
    print_success "Installation complete!"
    echo ""
    print_info "Launching Forge Swarm..."
    echo ""

    # Activate virtual environment
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        source venv/bin/activate
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        source venv/bin/activate
    fi

    # Launch Streamlit
    streamlit run Home.py
}

# Main installation flow
main() {
    print_header

    # Check Python
    check_python

    # Check and install Ollama
    check_ollama

    # Start Ollama server
    start_ollama

    # Pull models
    pull_models

    # Create virtual environment
    create_venv

    # Install dependencies
    install_dependencies

    # Run tests
    run_tests

    # Launch
    launch_forge_swarm
}

# Run main function
main
