#!/bin/bash
# Vercel Pre-Deploy Check Script

echo "Installing Production Dependencies..."
pip install -r requirements.txt

echo "Installing Test Dependencies..."
pip install pytest pip-audit httpx

echo "Running Security Audit..."
# Check for vulnerabilities in dependencies
# --desc: show descriptions
# --ignore-vuln: (Optionally ignore known low-severity issues if needed)
pip-audit --desc

echo "Running Automated Tests..."
# Run pytest. 
# PYTHONPATH=. ensures api module is found
export PYTHONPATH=$PYTHONPATH:.
pytest

echo "Checks Passed!"
