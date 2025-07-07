#!/bin/bash

echo "📧 Mailgun Setup for Urbex API"
echo "=============================="

echo ""
echo "📋 Follow these steps to configure Mailgun:"
echo ""
echo "1. Go to https://mailgun.com and create an account"
echo "2. Add and verify your domain (or use sandbox domain)"
echo "3. Get your API key from the dashboard"
echo "4. Note your domain name"
echo ""

read -p "Do you have your Mailgun API key and domain? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔑 Enter your Mailgun configuration:"
    echo ""

    read -p "Mailgun API Key: " mailgun_api_key
    read -p "Mailgun Domain: " mailgun_domain
    read -p "Admin Email (for contact form): " admin_email

    echo ""
    echo "📝 Updating .env file..."

    # Update .env file
    if [ -f .env ]; then
        # Backup original
        cp .env .env.backup
        echo "✅ Backup created: .env.backup"
    fi

    # Create or update .env
    cat > .env << EOF
# Application Settings
APP_NAME=Urbex API
APP_VERSION=0.1.0
DEBUG=false

# Server Settings
HOST=0.0.0.0
PORT=8000

# AWS Settings
AWS_REGION=us-east-2

# Cognito Settings
COGNITO_USER_POOL_ID=your-cognito-user-pool-id
COGNITO_CLIENT_ID=your-cognito-client-id
COGNITO_REGION=us-east-2

# Mailgun Settings
MAILGUN_API_KEY=${mailgun_api_key}
MAILGUN_DOMAIN=${mailgun_domain}
MAILGUN_BASE_URL=https://api.mailgun.net/v3
ADMIN_EMAIL=${admin_email}

# Security Settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_ORIGINS=["*"]
ALLOWED_METHODS=["*"]
ALLOWED_HEADERS=["*"]
EOF

    echo "✅ .env file updated with Mailgun configuration"
    echo ""
    echo "🔍 Current Mailgun settings:"
    echo "   API Key: ${mailgun_api_key:0:10}..."
    echo "   Domain: $mailgun_domain"
    echo "   Admin Email: $admin_email"
    echo ""
    echo "📝 Next step: Configure AWS Cognito"

else
    echo ""
    echo "❌ Please configure Mailgun first and run this script again."
    echo ""
    echo "🔗 Mailgun Setup: https://mailgun.com"
fi
