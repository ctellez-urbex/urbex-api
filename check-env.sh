#!/bin/bash

echo "🔍 Environment Variables Check for Urbex API"
echo "============================================"

echo ""
echo "📋 Checking required environment variables:"
echo ""

# Required variables
variables=(
    "MAILGUN_API_KEY"
    "MAILGUN_DOMAIN"
    "ADMIN_EMAIL"
    "COGNITO_USER_POOL_ID"
    "COGNITO_CLIENT_ID"
    "COGNITO_REGION"
)

all_good=true

for var in "${variables[@]}"; do
    if [ -n "${!var}" ]; then
        if [[ "${!var}" == *"your-"* ]]; then
            echo "⚠️  $var: ${!var} (placeholder value)"
            all_good=false
        else
            echo "✅ $var: ${!var}"
        fi
    else
        echo "❌ $var: Not set"
        all_good=false
    fi
done

echo ""
if [ "$all_good" = true ]; then
    echo "🎉 All environment variables are properly configured!"
    echo ""
    echo "🚀 Ready to deploy with: serverless deploy --stage prod"
else
    echo "⚠️  Some variables need to be configured with real values."
    echo ""
    echo "📝 Update your .env file with real values:"
    echo "   - MAILGUN_API_KEY: Get from Mailgun dashboard"
    echo "   - MAILGUN_DOMAIN: Your verified domain"
    echo "   - COGNITO_USER_POOL_ID: From AWS Cognito"
    echo "   - COGNITO_CLIENT_ID: From AWS Cognito"
    echo ""
    echo "🔗 Helpful links:"
    echo "   - Mailgun: https://mailgun.com"
    echo "   - AWS Cognito: https://console.aws.amazon.com/cognito/"
fi
