#!/bin/bash

echo "🔐 AWS Cognito Setup for Urbex API"
echo "=================================="

echo ""
echo "📋 Follow these steps to configure AWS Cognito:"
echo ""
echo "1. Go to AWS Console → Cognito"
echo "2. Create a User Pool"
echo "3. Create an App Client (public client recommended)"
echo "4. Note the User Pool ID and Client ID"
echo ""

read -p "Do you have your Cognito User Pool ID and Client ID? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔑 Enter your Cognito configuration:"
    echo ""

    read -p "Cognito User Pool ID: " cognito_user_pool_id
    read -p "Cognito Client ID: " cognito_client_id
    read -p "AWS Region (default: us-east-2): " cognito_region

    # Set default region if empty
    if [ -z "$cognito_region" ]; then
        cognito_region="us-east-2"
    fi

    echo ""
    echo "📝 Updating .env file..."

    # Update .env file
    if [ -f .env ]; then
        # Backup original
        cp .env .env.backup
        echo "✅ Backup created: .env.backup"
    fi

    # Read existing .env and update Cognito settings
    if [ -f .env ]; then
        # Update existing .env file
        sed -i.bak "s/COGNITO_USER_POOL_ID=.*/COGNITO_USER_POOL_ID=${cognito_user_pool_id}/" .env
        sed -i.bak "s/COGNITO_CLIENT_ID=.*/COGNITO_CLIENT_ID=${cognito_client_id}/" .env
        sed -i.bak "s/COGNITO_REGION=.*/COGNITO_REGION=${cognito_region}/" .env
        rm -f .env.bak
    else
        echo "❌ .env file not found. Run setup-mailgun.sh first."
        exit 1
    fi

    echo "✅ .env file updated with Cognito configuration"
    echo ""
    echo "🔍 Current Cognito settings:"
    echo "   User Pool ID: $cognito_user_pool_id"
    echo "   Client ID: $cognito_client_id"
    echo "   Region: $cognito_region"
    echo ""
    echo "🎉 Configuration complete! Run 'make check-env' to verify."

else
    echo ""
    echo "❌ Please configure AWS Cognito first and run this script again."
    echo ""
    echo "🔗 AWS Cognito Console: https://console.aws.amazon.com/cognito/"
    echo ""
    echo "📚 Quick setup guide:"
    echo "1. Create User Pool:"
    echo "   - Name: urbex-user-pool"
    echo "   - Email verification: Required"
    echo "   - Password policy: Default"
    echo ""
    echo "2. Create App Client:"
    echo "   - Name: urbex-client"
    echo "   - Generate client secret: No (public client)"
    echo "   - Auth flows: ALLOW_USER_PASSWORD_AUTH, ALLOW_REFRESH_TOKEN_AUTH"
fi
