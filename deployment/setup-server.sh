#!/bin/bash
# ============================================
# Hybrid Intelligence Core - Server Setup Script
# ============================================
# Run this script on a fresh Ubuntu 22.04 VPS
# Usage: sudo bash setup-server.sh
#
# This script will:
# 1. Update system packages
# 2. Install Python 3.11, Node.js 20, NGINX, Certbot
# 3. Create application directories
# 4. Set up Python virtual environment
# 5. Configure firewall
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Hybrid Intelligence Core - Server Setup${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo bash setup-server.sh)${NC}"
    exit 1
fi

# ==================== SYSTEM UPDATE ====================
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
apt update && apt upgrade -y

# ==================== INSTALL DEPENDENCIES ====================
echo -e "${YELLOW}[2/8] Installing system dependencies...${NC}"
apt install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban \
    htop \
    unzip

# ==================== INSTALL PYTHON 3.11 ====================
echo -e "${YELLOW}[3/8] Installing Python 3.11...${NC}"
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Set Python 3.11 as default
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# ==================== INSTALL NODE.JS 20 ====================
echo -e "${YELLOW}[4/8] Installing Node.js 20 LTS...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install Yarn
npm install -g yarn

# ==================== INSTALL NGINX ====================
echo -e "${YELLOW}[5/8] Installing NGINX...${NC}"
apt install -y nginx

# ==================== INSTALL CERTBOT ====================
echo -e "${YELLOW}[6/8] Installing Certbot...${NC}"
apt install -y certbot python3-certbot-nginx

# ==================== CREATE DIRECTORIES ====================
echo -e "${YELLOW}[7/8] Creating application directories...${NC}"

# Main application directory
mkdir -p /var/www/hybrid-intelligence
mkdir -p /var/www/hybrid-intelligence/backend
mkdir -p /var/www/hybrid-intelligence/frontend
mkdir -p /var/log/hybrid-intelligence
mkdir -p /var/www/certbot

# Set ownership
chown -R www-data:www-data /var/www/hybrid-intelligence
chown -R www-data:www-data /var/log/hybrid-intelligence

# ==================== SETUP PYTHON VENV ====================
echo -e "${YELLOW}[8/8] Setting up Python virtual environment...${NC}"
cd /var/www/hybrid-intelligence
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install gunicorn uvicorn[standard]

# ==================== CONFIGURE FIREWALL ====================
echo -e "${YELLOW}Configuring firewall...${NC}"
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# ==================== CONFIGURE FAIL2BAN ====================
echo -e "${YELLOW}Configuring Fail2Ban...${NC}"
systemctl enable fail2ban
systemctl start fail2ban

# ==================== SUMMARY ====================
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Server Setup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Installed versions:"
echo "  - Python: $(python3 --version)"
echo "  - Node.js: $(node --version)"
echo "  - NPM: $(npm --version)"
echo "  - Yarn: $(yarn --version)"
echo "  - NGINX: $(nginx -v 2>&1)"
echo ""
echo "Directories created:"
echo "  - /var/www/hybrid-intelligence/backend"
echo "  - /var/www/hybrid-intelligence/frontend"
echo "  - /var/log/hybrid-intelligence"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Clone your repository to /var/www/hybrid-intelligence"
echo "  2. Run the deploy script: bash deploy.sh"
echo "  3. Configure SSL: sudo certbot --nginx -d yourdomain.com"
echo ""
