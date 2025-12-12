# 🚀 Deploying to Replit

This guide shows you how to deploy the Letter Banner Generator to Replit while keeping your API keys secure.

## 🔒 Security First: Never Expose API Keys!

Your `.gitignore` is already configured to exclude `.env` files, but here's how to properly use secrets on Replit:

## Option 1: Replit Secrets (Recommended) ⭐

Replit has a built-in encrypted secrets manager that's perfect for API keys.

### Steps:

1. **Fork/Import your repository to Replit:**
   - Go to [Replit](https://replit.com)
   - Click "Create Repl" → "Import from GitHub"
   - Paste your repository URL
   - Click "Import from GitHub"

2. **Add Your API Keys as Secrets:**
   - In your Repl, click the 🔒 **Secrets** icon in the left sidebar
   - Or go to **Tools** → **Secrets**
   - Add your secrets:
     ```
     Key: OPENAI_API_KEY
     Value: sk-proj-your-actual-openai-key-here
     
     Key: GEMINI_API_KEY  
     Value: your-actual-gemini-key-here
     ```
   - Click "Add new secret" for each one

3. **Secrets are Automatically Loaded:**
   - Replit automatically injects secrets as environment variables
   - Your code already uses `os.getenv()` to read them
   - No code changes needed!

4. **Run Your App:**
   - Click the "Run" button
   - Replit will execute `main.py` automatically
   - Your app will be accessible at the provided URL

### ✅ Benefits of Replit Secrets:

- ✅ Never stored in code or Git
- ✅ Encrypted at rest
- ✅ Only accessible to your Repl
- ✅ Can be updated without code changes
- ✅ Shared across all your Repl runs

## Option 2: Environment Variables in .replit File

You can also use the `.replit` configuration file with environment variables (but Secrets are more secure):

```toml
# .replit file
[env]
ENVIRONMENT = "production"
# Do NOT put actual API keys here - use Secrets instead!
```

## 🚫 What NOT to Do

### ❌ Never Do This:

```python
# DON'T hardcode keys in your code!
api_key = "sk-proj-abc123..."  # ❌ WRONG!

# DON'T commit .env files
git add .env  # ❌ WRONG!

# DON'T put keys in .replit file
[env]
OPENAI_API_KEY = "sk-proj..."  # ❌ WRONG!
```

### ✅ Always Do This:

```python
# ✅ Use environment variables
import os
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Use Replit Secrets
# (automatically available as environment variables)

# ✅ Keep .env in .gitignore
# (already configured in this project)
```

## 📋 Pre-Deployment Checklist

Before pushing to GitHub or Replit:

- [ ] `.env` file is in `.gitignore` ✅ (already configured)
- [ ] No API keys hardcoded in any files
- [ ] `.env.example` exists (template without real keys)
- [ ] README explains how to set up secrets
- [ ] Test locally first with `.env` file

## 🔍 Verify Your .env is Ignored

Run this command to make sure `.env` isn't tracked by Git:

```bash
git status
# Should NOT show .env file

git check-ignore .env
# Should output: .env

cat .gitignore | grep .env
# Should show: .env
```

## 🌐 Accessing Your Deployed App

Once deployed on Replit:

1. Your app will be available at: `https://your-repl-name.your-username.repl.co`
2. The URL is public (anyone can access it)
3. But your API keys remain secure in Secrets
4. Only you can see/edit the Secrets

## 🔄 Updating API Keys

To change API keys on Replit:

1. Click 🔒 **Secrets** in sidebar
2. Find the key you want to update
3. Click the pencil icon to edit
4. Update the value
5. Click "Save"
6. Restart your Repl (it will pick up new values)

## 💰 Cost Considerations

Your Replit deployment will use your API keys:

- **Gemini 3 Pro**: ~$0.03 per letter (~$0.20 for 6-letter name)
- **OpenAI GPT-Image-1**: ~$0.17 per letter (~$1.02 for 6-letter name)

Default is Gemini for **80% cost savings**! 💵

## 🛡️ Additional Security Tips

1. **Rate Limiting:** Consider adding rate limiting to prevent abuse
2. **Authentication:** Add user authentication if making it public
3. **API Key Rotation:** Periodically rotate your API keys
4. **Monitor Usage:** Check OpenAI/Google Cloud console for unexpected usage
5. **Set Spending Limits:** Configure spending limits in OpenAI/Google Cloud

## 🆘 Troubleshooting

### "API key not found" Error:

1. Check Secrets are named exactly: `OPENAI_API_KEY` and `GEMINI_API_KEY`
2. Restart your Repl after adding secrets
3. Check the console output for "API keys loaded successfully"

### Secrets Not Loading:

1. Make sure you're using the 🔒 Secrets feature, not environment variables in `.replit`
2. Secrets may take a moment to propagate - restart the Repl
3. Check your code uses `os.getenv("KEY_NAME")`

## 📚 Additional Resources

- [Replit Secrets Documentation](https://docs.replit.com/programming-ide/storing-sensitive-information-environment-variables)
- [OpenAI API Best Practices](https://platform.openai.com/docs/guides/production-best-practices)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)

---

**Remember:** Your `.env` file is only for local development. On Replit, always use Secrets! 🔒

