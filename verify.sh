#!/bin/bash

# Installation Verification Script
# This script checks if all prerequisites are installed correctly

echo "🔍 Checking System Prerequisites..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check counters
PASSED=0
FAILED=0

# Function to check command
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed: $(which $1)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to check version
check_version() {
    echo -e "${BLUE}  Version:${NC} $($1)"
}

echo "=== Core Requirements ==="
echo ""

# Check Python
if check_command python3; then
    check_version "python3 --version"
else
    echo -e "${YELLOW}  Install: brew install python3 (macOS) or apt-get install python3 (Linux)${NC}"
fi
echo ""

# Check pip
if check_command pip3; then
    check_version "pip3 --version"
else
    echo -e "${YELLOW}  Install: python3 -m ensurepip${NC}"
fi
echo ""

# Check Node.js
if check_command node; then
    check_version "node --version"
else
    echo -e "${YELLOW}  Install: brew install node (macOS) or visit nodejs.org${NC}"
fi
echo ""

# Check npm
if check_command npm; then
    check_version "npm --version"
else
    echo -e "${YELLOW}  Install: Comes with Node.js${NC}"
fi
echo ""

# Check MongoDB
echo "=== Database ==="
echo ""
if check_command mongod; then
    check_version "mongod --version | head -n 1"
    
    # Check if MongoDB is running
    if pgrep -x mongod > /dev/null; then
        echo -e "${GREEN}  ✓ MongoDB is running${NC}"
    else
        echo -e "${YELLOW}  ⚠ MongoDB is installed but not running${NC}"
        echo -e "${YELLOW}    Start with: brew services start mongodb-community (macOS)${NC}"
        echo -e "${YELLOW}    Or: sudo systemctl start mongod (Linux)${NC}"
    fi
else
    echo -e "${YELLOW}  Install:${NC}"
    echo -e "${YELLOW}    macOS: brew tap mongodb/brew && brew install mongodb-community${NC}"
    echo -e "${YELLOW}    Linux: Follow https://docs.mongodb.com/manual/administration/install-on-linux/${NC}"
fi
echo ""

# Check Docker (optional)
echo "=== Optional Tools ==="
echo ""
if check_command docker; then
    check_version "docker --version"
    
    # Check if Docker is running
    if docker info &> /dev/null; then
        echo -e "${GREEN}  ✓ Docker is running${NC}"
    else
        echo -e "${YELLOW}  ⚠ Docker is installed but not running${NC}"
        echo -e "${YELLOW}    Start Docker Desktop${NC}"
    fi
else
    echo -e "${YELLOW}  Install: https://docs.docker.com/get-docker/${NC}"
fi
echo ""

if check_command docker-compose; then
    check_version "docker-compose --version"
else
    echo -e "${YELLOW}  Install: Comes with Docker Desktop${NC}"
fi
echo ""

# Check Git
if check_command git; then
    check_version "git --version"
else
    echo -e "${YELLOW}  Install: brew install git (macOS) or apt-get install git (Linux)${NC}"
fi
echo ""

# Check project directories
echo "=== Project Structure ==="
echo ""

if [ -d "backend" ]; then
    echo -e "${GREEN}✓${NC} backend/ directory exists"
    PASSED=$((PASSED + 1))
    
    if [ -f "backend/app.py" ]; then
        echo -e "${GREEN}  ✓${NC} backend/app.py exists"
    else
        echo -e "${RED}  ✗${NC} backend/app.py missing"
        FAILED=$((FAILED + 1))
    fi
    
    if [ -f "backend/requirements.txt" ]; then
        echo -e "${GREEN}  ✓${NC} backend/requirements.txt exists"
    else
        echo -e "${RED}  ✗${NC} backend/requirements.txt missing"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}✗${NC} backend/ directory missing"
    FAILED=$((FAILED + 1))
fi
echo ""

if [ -d "frontend" ]; then
    echo -e "${GREEN}✓${NC} frontend/ directory exists"
    PASSED=$((PASSED + 1))
    
    if [ -f "frontend/package.json" ]; then
        echo -e "${GREEN}  ✓${NC} frontend/package.json exists"
    else
        echo -e "${RED}  ✗${NC} frontend/package.json missing"
        FAILED=$((FAILED + 1))
    fi
    
    if [ -f "frontend/src/App.jsx" ]; then
        echo -e "${GREEN}  ✓${NC} frontend/src/App.jsx exists"
    else
        echo -e "${RED}  ✗${NC} frontend/src/App.jsx missing"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}✗${NC} frontend/ directory missing"
    FAILED=$((FAILED + 1))
fi
echo ""

# Check for .env file
echo "=== Configuration ==="
echo ""

if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓${NC} backend/.env exists"
    
    # Check if OPENAI_API_KEY is set
    if grep -q "OPENAI_API_KEY=sk-" backend/.env; then
        echo -e "${GREEN}  ✓${NC} OPENAI_API_KEY is configured"
    elif grep -q "OPENAI_API_KEY=your_" backend/.env; then
        echo -e "${YELLOW}  ⚠${NC} OPENAI_API_KEY needs to be updated"
        echo -e "${YELLOW}    Edit backend/.env and add your OpenAI API key${NC}"
    else
        echo -e "${YELLOW}  ⚠${NC} OPENAI_API_KEY may not be configured"
    fi
else
    echo -e "${YELLOW}⚠${NC} backend/.env not found"
    echo -e "${YELLOW}  Run: cd backend && cp .env.example .env${NC}"
    echo -e "${YELLOW}  Then edit .env with your OpenAI API key${NC}"
fi
echo ""

# Check Python packages (if venv exists)
if [ -d "backend/venv" ]; then
    echo "=== Python Environment ==="
    echo ""
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    
    # Check if it's activated
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}  ✓${NC} Virtual environment is activated"
    else
        echo -e "${YELLOW}  ⚠${NC} Virtual environment is not activated"
        echo -e "${YELLOW}    Run: source backend/venv/bin/activate${NC}"
    fi
    echo ""
fi

# Check if node_modules exists
if [ -d "frontend/node_modules" ]; then
    echo "=== Frontend Dependencies ==="
    echo ""
    echo -e "${GREEN}✓${NC} node_modules installed"
    echo ""
fi

# Network checks
echo "=== Network Checks ==="
echo ""

# Check if ports are available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠${NC} Port $1 is already in use"
        echo -e "${YELLOW}    Process: $(lsof -Pi :$1 -sTCP:LISTEN | tail -n 1 | awk '{print $1}')${NC}"
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 is available"
        return 0
    fi
}

check_port 8000
check_port 3000
check_port 27017
echo ""

# Summary
echo "=========================================="
echo "         VERIFICATION SUMMARY"
echo "=========================================="
echo ""
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! You're ready to run the application.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Make sure MongoDB is running"
    echo "  2. Configure backend/.env with your OpenAI API key"
    echo "  3. Run ./setup.sh to install dependencies"
    echo "  4. Start the backend: cd backend && python app.py"
    echo "  5. Start the frontend: cd frontend && npm run dev"
    echo "  6. Open http://localhost:3000"
else
    echo -e "${YELLOW}⚠ Some checks failed. Please install missing prerequisites.${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  • Python: brew install python3"
    echo "  • Node: brew install node"
    echo "  • MongoDB: brew tap mongodb/brew && brew install mongodb-community"
    echo "  • Docker: https://docs.docker.com/get-docker/"
    echo ""
    echo "After installing, run this script again to verify."
fi

echo ""

