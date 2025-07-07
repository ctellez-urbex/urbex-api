"""
Lambda authorizer for API Gateway.

This module provides authorization functionality for API Gateway
to validate x-api-key headers before allowing access to protected endpoints.
"""

import json
import os
from typing import Dict, Any


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda authorizer handler for API Gateway.
    
    Args:
        event: API Gateway authorizer event
        context: Lambda context
        
    Returns:
        IAM policy document for API Gateway
    """
    try:
        # Get API key from the event
        api_key = event.get('headers', {}).get('x-api-key')
        
        if not api_key:
            return generate_policy('user', 'Deny', event['methodArn'])
        
        # Get valid API keys from environment
        api_keys_str = os.environ.get('API_KEYS', '[]')
        valid_api_keys = json.loads(api_keys_str)
        
        # Validate API key
        if api_key in valid_api_keys:
            return generate_policy('user', 'Allow', event['methodArn'])
        else:
            return generate_policy('user', 'Deny', event['methodArn'])
            
    except Exception as e:
        print(f"Authorization error: {str(e)}")
        return generate_policy('user', 'Deny', event['methodArn'])


def generate_policy(principal_id: str, effect: str, resource: str) -> Dict[str, Any]:
    """
    Generate IAM policy document for API Gateway.
    
    Args:
        principal_id: Principal identifier
        effect: Allow or Deny
        resource: API Gateway resource ARN
        
    Returns:
        IAM policy document
    """
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    } 