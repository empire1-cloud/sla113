#!/bin/bash
# ============================================
# Empire1 Quick Start Helper
# ============================================
# Run this script to get started quickly

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Empire1 Ecosystem - Quick Start${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${YELLOW}Please run this script from the sla113 repository root${NC}"
    exit 1
fi

echo -e "${BLUE}What would you like to do?${NC}"
echo ""
echo "1) Set up for LOCAL DEVELOPMENT"
echo "2) Set up for PRODUCTION DEPLOYMENT"
echo "3) View unified login information"
echo "4) Check if configuration is complete"
echo "5) View documentation links"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Setting up for local development...${NC}"
        echo ""
        
        # Backend
        if [ ! -f "backend/.env" ]; then
            echo -e "${YELLOW}Creating backend/.env from template...${NC}"
            cp backend/.env.example backend/.env
            echo -e "${GREEN}✓${NC} Created backend/.env"
            echo -e "${YELLOW}→ Edit backend/.env and add your MongoDB URL and API keys${NC}"
        else
            echo -e "${GREEN}✓${NC} backend/.env already exists"
        fi
        
        # Frontend
        if [ ! -f "frontend/.env" ]; then
            echo -e "${YELLOW}Creating frontend/.env from template...${NC}"
            cp frontend/.env.example frontend/.env
            echo -e "${GREEN}✓${NC} Created frontend/.env"
            echo "REACT_APP_BACKEND_URL=http://localhost:8001" > frontend/.env
        else
            echo -e "${GREEN}✓${NC} frontend/.env already exists"
        fi
        
        # Check emergentintegrations symlink
        if [ ! -L "backend/emergentintegrations" ] && [ -d "backend/emergentintegrations_local_backup" ]; then
            echo -e "${YELLOW}Creating emergentintegrations symlink...${NC}"
            cd backend && ln -s emergentintegrations_local_backup emergentintegrations && cd ..
            echo -e "${GREEN}✓${NC} Created symlink"
        fi
        
        echo ""
        echo -e "${GREEN}Next steps:${NC}"
        echo "1. Edit backend/.env with your values (minimum: MONGO_URL, DB_NAME)"
        echo "2. Start MongoDB: sudo mongod --dbpath /data/db --fork --logpath /var/log/mongod.log"
        echo "   Or use MongoDB Atlas: https://www.mongodb.com/cloud/atlas"
        echo "3. Start backend: cd backend && uvicorn server:app --reload --port 8001"
        echo "4. Start frontend (new terminal): cd frontend && yarn start"
        echo "5. Open http://localhost:3000 and create your account"
        echo ""
        echo -e "${BLUE}Full guide: LOCAL_SETUP.md${NC}"
        ;;
        
    2)
        echo ""
        echo -e "${GREEN}Setting up for production deployment...${NC}"
        echo ""
        
        SECRETS_FILE="$HOME/empire1-secrets.sh"
        
        if [ -f "$SECRETS_FILE" ]; then
            echo -e "${GREEN}✓${NC} Secrets file already exists at $SECRETS_FILE"
        else
            echo -e "${YELLOW}Creating secrets file template...${NC}"
            cat > "$SECRETS_FILE" << 'EOF'
#!/bin/bash
# Empire1 Secrets - Keep this file safe!

export PROJECT_ID="your-gcp-project-id"
export MONGO_URL="mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority"
export DB_NAME="hybrid_intelligence"
export GEMINI_API_KEY="your-gemini-api-key"
export EMERGENT_LLM_KEY="your-emergent-key"  # Optional
export STRIPE_SECRET_KEY="sk_live_..."  # Optional
EOF
            chmod +x "$SECRETS_FILE"
            echo -e "${GREEN}✓${NC} Created $SECRETS_FILE"
        fi
        
        echo ""
        echo -e "${GREEN}Next steps:${NC}"
        echo "1. Edit $SECRETS_FILE with your actual values:"
        echo "   nano $SECRETS_FILE"
        echo ""
        echo "2. Get your API keys:"
        echo "   - GCP Project: https://console.cloud.google.com"
        echo "   - MongoDB: https://www.mongodb.com/cloud/atlas"
        echo "   - Gemini: https://ai.google.dev/"
        echo ""
        echo "3. Deploy with one command:"
        echo "   source $SECRETS_FILE && bash deployment/deploy.sh"
        echo ""
        echo -e "${BLUE}Full guide: deployment/QUICK_DEPLOY.md${NC}"
        ;;
        
    3)
        echo ""
        echo -e "${GREEN}Unified Login System${NC}"
        echo ""
        echo -e "${YELLOW}Important:${NC} The Empire1 ecosystem uses ONE login for ALL universes"
        echo ""
        echo "✅ Empire1 (empire1.cloud) - Main creator dashboard"
        echo "✅ SLA113 (sla113.southernlifestyle.org) - Game studio"
        echo "✅ Lyrica3 (lyrica3.com) - Music universe"
        echo "✅ Arcade (arcade.southernlifestyle.org) - Game portal"
        echo ""
        echo "Same email/password works everywhere!"
        echo ""
        echo -e "${BLUE}Test credentials (development):${NC}"
        echo "Email: newuser@example.com"
        echo "Password: NewPass123!"
        echo ""
        echo -e "${BLUE}Full details: memory/test_credentials.md${NC}"
        ;;
        
    4)
        echo ""
        echo -e "${GREEN}Checking configuration...${NC}"
        echo ""
        
        MISSING=0
        
        # Check backend env
        if [ -f "backend/.env" ]; then
            echo -e "${GREEN}✓${NC} backend/.env exists"
            if grep -q "MONGO_URL=" backend/.env && ! grep -q "MONGO_URL=mongodb://localhost:27017" backend/.env; then
                echo -e "${GREEN}✓${NC} MongoDB URL configured"
            else
                echo -e "${YELLOW}⚠${NC} MongoDB URL not configured in backend/.env"
                MISSING=$((MISSING + 1))
            fi
            if grep -q "GEMINI_API_KEY=" backend/.env && ! grep -q "your-gemini-api-key" backend/.env; then
                echo -e "${GREEN}✓${NC} Gemini API key configured"
            else
                echo -e "${YELLOW}⚠${NC} Gemini API key not configured (optional but recommended)"
            fi
        else
            echo -e "${YELLOW}⚠${NC} backend/.env not found - run option 1 to create it"
            MISSING=$((MISSING + 1))
        fi
        
        # Check frontend env
        if [ -f "frontend/.env" ]; then
            echo -e "${GREEN}✓${NC} frontend/.env exists"
        else
            echo -e "${YELLOW}⚠${NC} frontend/.env not found - run option 1 to create it"
            MISSING=$((MISSING + 1))
        fi
        
        echo ""
        if [ $MISSING -eq 0 ]; then
            echo -e "${GREEN}✅ Configuration looks good!${NC}"
        else
            echo -e "${YELLOW}⚠ Some configuration missing - run option 1 to set up${NC}"
        fi
        ;;
        
    5)
        echo ""
        echo -e "${GREEN}Documentation Links${NC}"
        echo ""
        echo -e "${BLUE}Setup Guides:${NC}"
        echo "  • LOCAL_SETUP.md - Local development setup"
        echo "  • deployment/QUICK_DEPLOY.md - One-command deployment"
        echo "  • deployment/DEPLOYMENT_GUIDE.md - Detailed Cloud Run guide"
        echo ""
        echo -e "${BLUE}Configuration:${NC}"
        echo "  • backend/.env.example - Backend config template"
        echo "  • frontend/.env.example - Frontend config template"
        echo "  • memory/test_credentials.md - Login information"
        echo ""
        echo -e "${BLUE}Reference:${NC}"
        echo "  • README.md - Main overview"
        echo "  • AGENTS.md - Full architecture"
        echo "  • deployment/SUMMARY.md - Complete change summary"
        echo "  • TASK_COMPLETE.md - Quick reference"
        echo ""
        ;;
        
    *)
        echo -e "${YELLOW}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
