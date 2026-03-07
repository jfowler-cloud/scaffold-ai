"""Shared pytest fixtures for agents tests."""
import os
import sys

# Add the agents directory to sys.path so `import shared.config` works
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault("DEPLOYMENT_TIER", "testing")
os.environ.setdefault("AWS_REGION", "us-east-1")
