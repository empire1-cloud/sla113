#!/bin/bash
# ============================================
# Empire1 Configuration Verification
# ============================================
# Checks that all documentation and config files are present

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Empire1 Configuration Verification${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $description: $file (MISSING)"
        ((CHECKS_FAILED++))
    fi
}

check_content() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $description (NOT FOUND)"
        ((CHECKS_FAILED++))
    fi
}

echo -e "${YELLOW}Checking configuration templates...${NC}"
check_file "backend/.env.example" "Backend env template"
check_file "frontend/.env.example" "Frontend env template"
echo ""

echo -e "${YELLOW}Checking documentation...${NC}"
check_file "README.md" "Main README"
check_file "LOCAL_SETUP.md" "Local setup guide"
check_file "memory/test_credentials.md" "Login credentials guide"
check_file "deployment/README.md" "Deployment hub"
check_file "deployment/QUICK_DEPLOY.md" "Quick deploy guide"
check_file "deployment/DEPLOYMENT_GUIDE.md" "Detailed deployment guide"
check_file "deployment/LAUNCH_CHECKLIST.md" "Launch checklist"
check_file "deployment/deploy.sh" "Deploy script"
echo ""

echo -e "${YELLOW}Checking environment templates...${NC}"
check_content "backend/.env.example" "GEMINI_API_KEY" "Gemini API key in backend template"
check_content "backend/.env.example" "MONGO_URL" "MongoDB URL in backend template"
check_content "frontend/.env.example" "REACT_APP_BACKEND_URL" "Backend URL in frontend template"
echo ""

echo -e "${YELLOW}Checking unified login documentation...${NC}"
check_content "memory/test_credentials.md" "unified authentication" "Unified auth documented"
check_content "memory/test_credentials.md" "Lyrica" "Lyrica login info"
check_content "memory/test_credentials.md" "newuser@example.com" "Test credentials"
echo ""

echo -e "${YELLOW}Checking deployment configuration...${NC}"
check_content "deployment/deploy.sh" "GEMINI_API_KEY" "Gemini API key in deploy script"
check_content "deployment/QUICK_DEPLOY.md" "one-hand" "Accessibility features"
check_content "deployment/QUICK_DEPLOY.md" "empire1-secrets.sh" "Secrets file template"
echo ""

echo -e "${YELLOW}Checking backend router configuration...${NC}"
check_content "backend/routers/sla113.py" "lyrica3" "Lyrica3 universe registered"
check_content "backend/routers/sla113.py" "lyrica3.com" "Lyrica3 domain configured"
echo ""

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Summary${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
    echo ""
    echo -e "${RED}Some checks failed. Please review the missing items above.${NC}"
    exit 1
else
    echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
    echo ""
    echo -e "${GREEN}✅ All configuration checks passed!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Copy backend/.env.example to backend/.env and configure"
    echo "  2. Copy frontend/.env.example to frontend/.env and configure"
    echo "  3. Get your Gemini API key from https://ai.google.dev/"
    echo "  4. For local dev: See LOCAL_SETUP.md"
    echo "  5. For deployment: See deployment/QUICK_DEPLOY.md"
    echo ""
    echo -e "${GREEN}🎯 Unified Login System:${NC}"
    echo "  - One account works across ALL universes"
    echo "  - Empire1, SLA113, Lyrica3, Arcade - same credentials"
    echo "  - See memory/test_credentials.md for details"
    echo ""
fi
