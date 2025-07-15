# API Endpoints Documentation

This document describes all available API endpoints for the Urbex API.

## 🔗 Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: `https://your-api-gateway-url.amazonaws.com`

## 📋 Available Endpoints

### Health & Documentation

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check endpoint | No |
| GET | `/docs` | Swagger UI documentation | No |
| GET | `/redoc` | ReDoc documentation | No |
| GET | `/openapi.json` | OpenAPI specification | No |

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/confirm` | Confirm user registration | No |
| POST | `/api/v1/auth/login` | User login | No |
| POST | `/api/v1/auth/refresh` | Refresh access token | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |
| POST | `/api/v1/auth/logout` | User logout | Yes |

### Contact Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/contact` | Submit contact form | No |

### Admin Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/admin/users` | List users with pagination and filters | Yes (Admin) |
| GET | `/api/v1/admin/users/{user_id}` | Get user details | Yes (Admin) |
| PUT | `/api/v1/admin/users/{user_id}` | Update user information | Yes (Admin) |
| PATCH | `/api/v1/admin/users/{user_id}/status` | Enable/disable user | Yes (Admin) |
| DELETE | `/api/v1/admin/users/{user_id}` | Delete user account | Yes (Admin) |

## 🔐 Authentication

### Public Endpoints
These endpoints don't require authentication:
- Health check
- Documentation
- User registration
- User confirmation
- User login
- Contact form

### Protected Endpoints
These endpoints require a valid Bearer token:
- `/api/v1/auth/me` - Get user info
- `/api/v1/auth/logout` - User logout

### Admin Endpoints
These endpoints require admin privileges (Bearer token with admin role):
- `/api/v1/admin/users` - List all users
- `/api/v1/admin/users/{user_id}` - Get specific user details
- `/api/v1/admin/users/{user_id}` - Update user information
- `/api/v1/admin/users/{user_id}/status` - Change user status
- `/api/v1/admin/users/{user_id}` - Delete user account

## 📝 Request Examples

### User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### User Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### Get Current User
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Contact Form
```bash
curl -X POST "http://localhost:8000/api/v1/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "message": "I would like to know more about your services."
  }'
```

### Admin Endpoints

#### List Users
```bash
curl -X POST "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": "john",
    "pagination": 1
  }'
```

#### Get User Details
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users/user-123" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### Update User
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/users/user-123" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John Updated",
    "last_name": "Doe Updated",
    "phone_number": "+1234567890",
    "plan": "Anual",
    "su": "1"
  }'
```

#### Update User Status
```bash
curl -X PATCH "http://localhost:8000/api/v1/admin/users/user-123/status" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "DISABLED"
  }'
```

#### Delete User
```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/users/user-123" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## 🚀 Testing

### Local Testing
```bash
# Test all endpoints
make test-apis

# Or run manually
./test-apis.sh
```

### Production Testing
```bash
# Deploy to production
make deploy-prod

# Test with production URL
curl -X GET "https://your-api-gateway-url.amazonaws.com/health"
```

## 🔧 Configuration

### Environment Variables
- `COGNITO_USER_POOL_ID` - AWS Cognito User Pool ID
- `COGNITO_CLIENT_ID` - AWS Cognito Client ID
- `MAILGUN_API_KEY` - Mailgun API key
- `MAILGUN_DOMAIN` - Mailgun domain
- `ADMIN_EMAIL` - Admin email for contact notifications

### API Gateway
All endpoints are configured with:
- CORS enabled
- API key protection (in production)
- Proper HTTP methods
- Error handling

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "detail": "Error description"
}
```

### Token Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here"
}
```
