# Environment Variables & Secrets

This folder contains all sensitive credentials and environment-specific configuration.

## Files

- `lito-key.json` - Google Cloud service account key for Text-to-Speech API
- `.env.local` - Local development environment variables (if needed)
- `.env.production` - Production environment variables (if needed)

## Security

⚠️ **NEVER commit files in this folder to Git!**

All files in this directory are automatically ignored by `.gitignore`.

## Usage

### Local Development

```bash
# Set environment variable to point to the key
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/env/lito-key.json"

# Or on Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS = "d:\my-code\lito\env\lito-key.json"
```

### Production (Vercel)

Credentials are stored as environment variables in Vercel dashboard, not in files.

## Adding New Secrets

1. Add the file to this `env/` folder
2. Verify it's ignored: `git status --ignored`
3. Never reference absolute paths in code - use environment variables
