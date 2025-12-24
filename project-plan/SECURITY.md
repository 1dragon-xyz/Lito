# Security Checklist

## Secrets Management ✅

### What's Protected
- [x] `lito-key.json` in `.gitignore`
- [x] Google Cloud credentials stored as Vercel environment variable
- [x] No hardcoded API keys in source code
- [x] Pre-commit hook template created (`.agent/hooks/pre-commit`)
- [x] Pre-deploy secret scanning in `check_deploy.sh`

### Installation: Pre-Commit Hook

To install the secret scanning hook locally:

```bash
# Copy the hook
cp .agent/hooks/pre-commit .git/hooks/pre-commit

# Make it executable (Linux/Mac)
chmod +x .git/hooks/pre-commit

# On Windows (Git Bash)
git update-index --chmod=+x .git/hooks/pre-commit
```

The hook will automatically scan for:
- API keys, secrets, passwords
- Private keys (PEM, RSA)
- Credential files (*.key, *-key.json)
- The specific `lito-key.json` file

## Pre-Deploy Checks ✅

The `web-app/check_deploy.sh` script runs automatically on Vercel deployment and checks for:

1. **Secret Scanning**: Scans all source files for hardcoded secrets
2. **Credential Files**: Checks for accidentally committed key files
3. **Dependency Audit**: Scans for known vulnerabilities (`pip-audit`)
4. **Automated Tests**: Runs pytest suite

## Files That Should NEVER Be Committed

- `lito-key.json` - Google Cloud service account key
- `*.pem` - Private keys
- `*.key` - Any key files
- `credentials.json` - Any credential files
- `.env` files with secrets

## Environment Variables (Vercel)

| Variable | Purpose | Status |
|----------|---------|--------|
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Google Cloud TTS auth | ✅ Set |

## Regular Security Tasks

- [ ] **Monthly**: Review Google Cloud usage and costs
- [ ] **Quarterly**: Rotate Google Cloud service account keys
- [ ] **On dependency updates**: Run `pip-audit` to check for vulnerabilities

## Emergency: If Secrets Are Exposed

1. **Immediately revoke** the exposed credentials in Google Cloud Console
2. **Generate new** service account key
3. **Update** Vercel environment variable
4. **Redeploy** the application
5. **Review** git history and consider using `git-filter-repo` to remove from history

## Audit Commands

```bash
# Check for secrets in staged files
git diff --cached | grep -E -i "(api[_-]?key|secret|password)"

# Check for credential files
find . -name "*.pem" -o -name "*.key" -o -name "*-key.json"

# Run dependency audit
cd web-app && pip-audit

# Verify .gitignore is working
git status --ignored
```

## Security Best Practices Followed

- ✅ Secrets in environment variables, not code
- ✅ Pre-commit hooks to prevent accidents
- ✅ Automated security scanning in CI/CD
- ✅ Dependency vulnerability scanning
- ✅ Minimal permissions (service account has only TTS API access)
- ✅ Budget alerts to prevent unexpected costs
