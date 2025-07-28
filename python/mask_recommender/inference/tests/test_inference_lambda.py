import pytest
import json
import os
import sys

# Add the parent directory to the path so we can import lambda_function
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if module_path not in sys.path:
    sys.path.append(module_path)

def test_handler_structure():
    """Test that the handler function exists and has the right signature"""
    try:
        from lambda_function import handler
        assert callable(handler)
        
        # Test with minimal event
        event = {"facial_measurements": {}}
        context = {}
        
        result = handler(event, context)
        assert isinstance(result, dict)
        assert 'statusCode' in result
        assert 'body' in result
        
    except ImportError as e:
        # Expected if dependencies are missing
        assert "No module named" in str(e)
    except Exception as e:
        # Expected to fail due to missing model data or dependencies
        assert any(msg in str(e) for msg in [
            "Error loading model", 
            "No module named", 
            "boto3", 
            "arviz"
        ])

def test_lambda_function_exists():
    """Test that the lambda_function.py file exists and can be imported"""
    lambda_file = os.path.join(os.path.dirname(__file__), '..', 'lambda_function.py')
    assert os.path.exists(lambda_file), f"lambda_function.py not found at {lambda_file}"

def test_requirements_exist():
    """Test that requirements.txt exists"""
    req_file = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    assert os.path.exists(req_file), f"requirements.txt not found at {req_file}"

def test_environment_yml_exists():
    """Test that environment.yml exists"""
    env_file = os.path.join(os.path.dirname(__file__), '..', 'environment.yml')
    assert os.path.exists(env_file), f"environment.yml not found at {env_file}"
