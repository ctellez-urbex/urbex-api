# Urbex API

A modern, scalable REST API built with FastAPI, designed for serverless deployment on AWS Lambda with comprehensive authentication and email services.

## 🚀 Features

- **FastAPI Framework**: Modern, fast web framework for building APIs with Python
- **AWS Lambda Serverless**: Deploy as serverless functions with automatic scaling
- **AWS Cognito Integration**: Complete authentication and user management
- **Mailgun Email Service**: Transactional email capabilities
- **Clean Architecture**: Domain-driven design with dependency injection
- **Comprehensive Testing**: Full test coverage with pytest
- **Code Quality**: Pre-commit hooks, linting, and formatting
- **Docker Support**: Containerized development and deployment
- **API Gateway**: RESTful API with automatic documentation

## 🏗️ Architecture

```
urbex-api/
├── app/                    # Main application package
│   ├── api/               # API routes and endpoints
│   │   └── v1/           # Versioned API endpoints
│   ├── core/             # Core configuration and utilities
│   ├── models/           # Pydantic models and schemas
│   ├── services/         # External service integrations
│   └── main.py          # FastAPI application entry point
├── tests/                # Test suite
├── serverless.yml        # AWS Lambda deployment configuration
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Project configuration
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Local development setup
└── Makefile            # Development commands
```

## 🛠️ Technology Stack

- **Python 3.13+**: Latest stable Python version
- **FastAPI**: Modern web framework for APIs
- **Pydantic**: Data validation and settings management
- **AWS Lambda**: Serverless compute platform
- **AWS Cognito**: User authentication and management
- **Mailgun**: Email service integration
- **Mangum**: AWS Lambda adapter for ASGI applications
- **pytest**: Testing framework
- **Black & isort**: Code formatting
- **flake8 & mypy**: Code linting and type checking
- **pre-commit**: Git hooks for code quality

## 📋 Prerequisites

- Python 3.13 or higher
- Node.js 18+ (for Serverless Framework)
- AWS CLI configured
- Docker (optional, for containerized development)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd urbex-api
```

### 2. Setup Development Environment

```bash
# Install Python dependencies
make install-dev

# Or manually:
pip install -r requirements.txt
pip install -e .
pre-commit install
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
- `COGNITO_USER_POOL_ID`: AWS Cognito User Pool ID
- `COGNITO_CLIENT_ID`: AWS Cognito Client ID
- `MAILGUN_API_KEY`: Mailgun API key
- `MAILGUN_DOMAIN`: Mailgun domain
- `ADMIN_EMAIL`: Admin email for contact form notifications
- `SECRET_KEY`: JWT secret key

### Production Configuration

For production deployment, ensure these services are properly configured:

1. **Mailgun Setup**:
   - Create a Mailgun account at https://mailgun.com
   - Add and verify your domain
   - Get your API key from the dashboard
   - Configure environment variables:
     ```bash
     MAILGUN_API_KEY=your-mailgun-api-key
     MAILGUN_DOMAIN=your-verified-domain.com
     ADMIN_EMAIL=your-admin-email@domain.com
     ```

2. **AWS Cognito Setup**:
   - Create a User Pool in AWS Cognito
   - Create an App Client (public client recommended)
   - **Important**: Enable `USER_PASSWORD_AUTH` flow in the App Client settings
   - Configure environment variables:
     ```bash
     COGNITO_USER_POOL_ID=your-user-pool-id
     COGNITO_CLIENT_ID=your-client-id
     COGNITO_REGION=us-east-2
     ```

   **Note**: If you encounter `USER_PASSWORD_AUTH flow not enabled for this client` error,
   enable this authentication flow in your Cognito App Client settings.

3. **Custom Cognito Attributes**:
   The API supports custom Cognito attributes:
   - `custom:su`: User subscription ID (used as `su` in API responses)
   - `custom:plan`: User subscription plan (used as `plan` in API responses)

   These attributes are automatically included in login and user info responses.

### 4. Run the Application

```bash
# Run locally
make run

# Or with Docker
make run-docker

# Or manually:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/test_auth.py

# Run tests with specific markers
pytest -m "not slow"
```

## 🔧 Development

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run pre-commit hooks
make pre-commit

# Run all CI checks
make ci
```

### Available Commands

```bash
make help  # Show all available commands
```

## 🚀 Deployment

### AWS Lambda Deployment

1. **Install Serverless Framework**:
   ```bash
   npm install -g serverless
   ```

2. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```

3. **Deploy to AWS**:
   ```bash
   # Deploy to dev environment
   make deploy

   # Deploy to production
   make deploy-prod

   # Remove deployment
   make remove
   ```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t urbex-api .
docker run -p 8000:8000 urbex-api

# Or use docker-compose
docker-compose up --build
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Contact Form Endpoints

#### Submit Contact Form
```http
POST /api/v1/contact/
Content-Type: application/json

{
  "full_name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "phone": "+1234567890",
  "message": "Hola, me gustaría obtener más información sobre sus servicios."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Mensaje enviado exitosamente. Te responderemos pronto.",
  "data": {
    "full_name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

#### Login User
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+1234567890",
      "su": "user-sub-id",
      "plan": "basic",
      "name": "John Doe"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

#### Confirm Registration
```http
POST /api/v1/auth/confirm
Content-Type: application/json

{
  "username": "john_doe",
  "confirmation_code": "123456"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "User information retrieved successfully",
  "error": null,
  "data": {
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "su": "user-sub-id",
    "plan": "basic",
    "name": "John Doe"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": null,
  "error": "Invalid token",
  "data": null
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

### Admin Endpoints

#### List Users
```http
POST /api/v1/admin/users
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "filter": "john",
  "pagination": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": {
    "users": [
      {
        "username": "john@example.com",
        "email": "john@example.com",
        "emailVerified": true,
        "status": "ENABLED",
        "createdAt": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

#### Get User Details
```http
GET /api/v1/admin/users/{user_id}
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "user_id": "user-123",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "plan": "mensual",
  "su": "1",
  "status": "ENABLED",
  "email_verified": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Update User
```http
PUT /api/v1/admin/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "first_name": "John Updated",
  "last_name": "Doe Updated",
  "phone_number": "+1234567890",
  "plan": "anual",
  "su": "1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "user_id": "user-123",
    "updated_attributes": ["given_name", "family_name", "phone_number", "custom:plan", "custom:su"]
  }
}
```

#### Update User Status
```http
PATCH /api/v1/admin/users/{user_id}/status
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "status": "DISABLED"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User status updated to DISABLED",
  "data": {
    "user_id": "user-123",
    "status": "DISABLED"
  }
}
```

#### Delete User
```http
DELETE /api/v1/admin/users/{user_id}
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully",
  "data": {
    "user_id": "user-123"
  }
}
```

### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "Urbex API",
  "version": "0.1.0"
}
```

## 🔐 Authentication



### JWT Authentication Flow

1. **User Registration**: User registers with email and password
2. **Email Verification**: User receives confirmation code via email
3. **Account Confirmation**: User confirms account with verification code
4. **Login**: User logs in and receives access/refresh tokens
5. **API Access**: User uses access token for authenticated requests
6. **Token Refresh**: User refreshes access token when needed

## 📧 Email Services

The API integrates with Mailgun for sending:
- Welcome emails
- Password reset emails
- Email verification codes
- Contact form notifications (to admin and confirmation to user)
- Custom transactional emails

## 🏗️ AWS Infrastructure

The Serverless Framework creates:
- **Lambda Function**: API runtime
- **API Gateway**: REST API endpoints
- **Cognito User Pool**: User authentication
- **CloudWatch Logs**: Application logging
- **IAM Roles**: Security permissions

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `false` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `COGNITO_USER_POOL_ID` | Cognito User Pool ID | Required |
| `COGNITO_CLIENT_ID` | Cognito Client ID | Required |
| `MAILGUN_API_KEY` | Mailgun API key | Required |
| `MAILGUN_DOMAIN` | Mailgun domain | Required |
| `ADMIN_EMAIL` | Admin email for contact notifications | Required |
| `SECRET_KEY` | JWT secret key | Required |

### AWS Configuration

1. **Create Cognito User Pool**:
   - Go to AWS Cognito Console
   - Create User Pool with email verification
   - Create App Client
   - Note User Pool ID and Client ID

2. **Configure Mailgun**:
   - Create Mailgun account
   - Add domain
   - Get API key

3. **Set Environment Variables**:
   - Update `.env` file with your credentials
   - For production, use AWS Systems Manager Parameter Store

## 🚨 Security Considerations

- Use strong, unique secret keys in production
- Enable HTTPS in production
- Implement rate limiting
- Use AWS IAM roles with minimal permissions
- Regularly rotate API keys and secrets
- Enable CloudWatch monitoring and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Development Workflow

```bash
# Setup development environment
make setup

# Make changes and test
make test

# Format and lint code
make ci

# Commit changes (pre-commit hooks will run automatically)
git add .
git commit -m "feat: add new feature"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🔄 Version History

- **v0.1.0**: Initial release with authentication and email services
