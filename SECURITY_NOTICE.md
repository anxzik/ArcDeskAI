# Security Notice

## Sensitive Files Protection

This project contains sensitive information that must NEVER be committed to version control.

### Protected Files

The following files contain sensitive information and are protected by `.gitignore`:

#### Environment Variables
- `.env.dev` - Development environment variables with API keys and database credentials
- `.env` - Any environment file
- `*.env` - All environment file variants

#### API Keys & Credentials
- All files matching `*secret*`, `*credential*`, `*_key`, `*_keys`
- Certificate files: `*.pem`, `*.key`, `*.crt`, `*.cer`, `*.p12`, `*.pfx`
- Service account files: `service-account*.json`

#### Database Files
- Database backups in `backups/` directory
- Database dumps: `*.dump`, `*.sql`, `*.sql.gz`
- SQLite files: `*.db`, `*.sqlite`, `*.sqlite3`
- PostgreSQL password files: `*.pgpass`, `.pgpass`

### Verify Protection

Before committing, always verify sensitive files are not being tracked:

```bash
# Check what will be committed
git status

# Verify .env files are ignored
git check-ignore .env.dev agentdesk/.env.dev

# List all tracked files (should not include .env or backups)
git ls-files | grep -E '\.env|secret|credential|\.pem|\.key|backup'
```

### If You Accidentally Commit Sensitive Data

If you accidentally commit sensitive information:

1. **DO NOT** just remove it in a new commit - it remains in git history
2. **IMMEDIATELY** rotate all exposed credentials (API keys, passwords, tokens)
3. Remove from git history:

```bash
# Remove a specific file from all git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: rewrites history)
git push origin --force --all
```

4. Verify the file is gone:
```bash
git log --all --full-history -- path/to/sensitive/file
```

5. **Rotate ALL credentials** that were in the file

### Using .env.example

Instead of `.env.dev`, we provide `.env.example` as a template:

```bash
# Copy the example file
cp agentdesk/.env.example agentdesk/.env.dev

# Edit with your actual credentials
nano agentdesk/.env.dev
```

The `.env.example` file is safe to commit as it contains no real credentials.

### Current Exposed Credentials (If Any)

⚠️ **IMPORTANT**: If this repository was previously public or the `.env.dev` was committed, you MUST rotate:

- Anthropic API Key
- OpenAI API Key  
- Google Gemini API Key
- Database password
- JWT secret keys
- Any other credentials that were in `.env.dev`

### Best Practices

1. **Never hardcode secrets** in source code
2. **Always use environment variables** for configuration
3. **Use different credentials** for dev/staging/production
4. **Rotate credentials regularly**
5. **Use secret management tools** in production (AWS Secrets Manager, HashiCorp Vault, etc.)
6. **Enable 2FA** on all accounts with API access
7. **Review git status** before every commit

### Checking for Exposed Secrets

Use tools to scan for accidentally committed secrets:

```bash
# Install gitleaks
brew install gitleaks  # macOS
# or download from https://github.com/gitleaks/gitleaks

# Scan the repository
gitleaks detect --source . --verbose

# Scan before committing
gitleaks protect --staged
```

### Additional Security Measures

For production deployments:

1. Use environment-specific credentials
2. Enable database encryption at rest
3. Use SSL/TLS for all database connections
4. Implement IP whitelisting for database access
5. Enable audit logging for all database operations
6. Use managed secret services (not .env files)
7. Implement proper RBAC (Role-Based Access Control)
8. Regular security audits and dependency updates

### Questions?

If you're unsure whether something should be committed:
- **When in doubt, DON'T commit it**
- Ask a team member
- Check if it's in `.gitignore`
- Use `git check-ignore <file>` to verify

### Emergency Contact

If you discover a security breach or exposed credentials:
1. Immediately notify the security team
2. Rotate all potentially compromised credentials
3. Review access logs for unauthorized access
4. Document the incident for future reference

---

**Remember**: Security is everyone's responsibility. Always verify before you commit!
