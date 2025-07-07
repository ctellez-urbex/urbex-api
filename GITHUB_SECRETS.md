# GitHub Secrets Configuration

This document explains how to configure GitHub Secrets for automatic deployment.

## 🔐 Required GitHub Secrets

Add these secrets in your GitHub repository:

### AWS Credentials
- `AWS_ACCESS_KEY_ID` - Your AWS Access Key ID
- `AWS_SECRET_ACCESS_KEY` - Your AWS Secret Access Key

### Mailgun Configuration
- `MAILGUN_API_KEY` - Your Mailgun API key
- `MAILGUN_DOMAIN` - Your verified Mailgun domain
- `ADMIN_EMAIL` - Admin email for contact form notifications

### AWS Cognito Configuration
- `COGNITO_USER_POOL_ID` - Your Cognito User Pool ID
- `COGNITO_CLIENT_ID` - Your Cognito Client ID
- `COGNITO_REGION` - AWS region (e.g., us-east-2)

## 📋 How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. Click on **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with its corresponding value

## 🚀 Automatic Deployment

Once secrets are configured, deployment will happen automatically when you push to the `developer` branch.

## 🔧 Manual Deployment

For manual deployment with local environment variables:

```bash
# Setup environment variables
./setup-mailgun.sh
./setup-cognito.sh

# Deploy to production
make deploy-prod
```

## 📝 Example Values

### Mailgun
- `MAILGUN_API_KEY`: `key-1234567890abcdef1234567890abcdef`
- `MAILGUN_DOMAIN`: `your-domain.com`
- `ADMIN_EMAIL`: `admin@your-domain.com`

### AWS Cognito
- `COGNITO_USER_POOL_ID`: `us-east-2_123456789`
- `COGNITO_CLIENT_ID`: `1234567890abcdef1234567890abcdef`
- `COGNITO_REGION`: `us-east-2`

## 🔍 Verification

After deployment, verify your configuration:

```bash
# Check environment variables
./check-env.sh

# Test AWS credentials
aws sts get-caller-identity
```
