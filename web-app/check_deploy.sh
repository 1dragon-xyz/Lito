#!/bin/bash
# Vercel Pre-Deploy Check Script

echo "🔒 Scanning for Secrets..."
# Check for hardcoded secrets in source files
if grep -r -E -i "(api[_-]?key|secret|password|private[_-]?key|BEGIN (RSA|PRIVATE) KEY)" --include="*.py" --include="*.js" --include="*.html" --include="*.json" .; then
    echo "❌ ERROR: Potential secret detected in source files!"
    echo "Please use environment variables for all secrets."
    exit 1
fi

# Check for credential files
if find . -type f \( -name "*.pem" -o -name "*.key" -o -name "*-key.json" -o -name "credentials.json" \) -not -path "./node_modules/*" -not -path "./.venv/*"; then
    echo "❌ ERROR: Credential files should not be in the repository!"
    exit 1
fi

echo "✅ No secrets detected"

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

echo "✅ All Checks Passed!"
