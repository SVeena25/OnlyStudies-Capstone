# Heroku Deployment Guide - OnlyStudies

## ✅ Security Status: READY FOR HEROKU

All security configurations are now in place. The application is secure for production deployment on Heroku.

---

## Pre-Deployment Checklist

### ✅ Security (All Configured)
```
✅ DEBUG = False
✅ SECRET_KEY from environment
✅ ALLOWED_HOSTS configured
✅ SECURE_SSL_REDIRECT = True
✅ SESSION_COOKIE_SECURE = True
✅ CSRF_COOKIE_SECURE = True
✅ SECURE_HSTS_SECONDS = 31536000
✅ X_FRAME_OPTIONS = 'DENY'
✅ Content Security Policy set
```

### Verification
```bash
python manage.py check --deploy
# Output: System check identified no issues (0 silenced).
```

---

## Step 1: Prepare Environment Variables

Create a `Procfile` in project root:

```
web: gunicorn only_studies.wsgi --log-file -
release: python manage.py migrate
```

Ensure these environment variables are set in Heroku:

```bash
# Critical
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.herokuapp.com

# Database (Heroku adds automatically if using Postgres add-on)
DATABASE_URL=postgresql://...

# Optional - Image uploads (if using Cloudinary)
CLOUDINARY_URL=cloudinary://...
```

---

## Step 2: Install Required Packages

Add to `requirements.txt`:

```txt
Django==4.2.27
gunicorn==21.2.0
dj-database-url==2.1.0
python-dotenv==1.0.0
Pillow==10.1.0
whitenoise==6.6.0
cloudinary==1.36.0
django-cloudinary-storage==0.3.10
```

Install locally:
```bash
pip install -r requirements.txt
```

---

## Step 3: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This will create the `staticfiles` directory with all CSS, JS, and images.

---

## Step 4: Database Migration

```bash
python manage.py migrate
```

Heroku will auto-run this via the `release` command in Procfile.

---

## Step 5: Deploy to Heroku

### Sensitive Files Policy (Git + Heroku)

Never commit local secrets or runtime artifacts to Git. This project enforces:

- `.gitignore` for local secret/config and generated files.
- `.slugignore` to exclude local/sensitive files from Heroku build slugs.

Always keep these out of Git and Heroku slugs:

```txt
.env
.env.*
env.py
credentials.json
service-account*.json
local_backup*.json
*.sqlite3
media/
```

If any were committed earlier, remove them from tracking:

```bash
git rm -r --cached media db.sqlite3
git commit -m "Stop tracking sensitive/local artifacts"
```

### Option A: Using Heroku CLI

```bash
# Login
heroku login

# Create app (if not already created)
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Add Postgres database
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main
# or: git push heroku master
```

### Option B: Using Heroku Dashboard

1. Connect GitHub repository to Heroku
2. Set environment variables in Settings → Config Vars
3. Enable automatic deploys from main branch

---

## Step 6: Verify Deployment

### Check Logs
```bash
heroku logs --tail
```

### Test Application
```bash
heroku open
# Opens: https://your-app-name.herokuapp.com/
```

### Test API Endpoints
```bash
# Blog feed (public)
curl https://your-app-name.herokuapp.com/api/blog-feed/

# Notifications (requires login)
curl https://your-app-name.herokuapp.com/api/notifications/
```

---

## Common Issues & Solutions

### Issue: "Module not found"
**Solution**: Ensure all packages are in `requirements.txt`
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push heroku main
```

### Issue: "Static files 404"
**Solution**: Run collectstatic and commit
```bash
python manage.py collectstatic --noinput
git add staticfiles/
git commit -m "Collect static files"
git push heroku main
```

### Issue: "Database connection error"
**Solution**: Verify DATABASE_URL is set
```bash
heroku config
# Should show DATABASE_URL with Postgres connection string
```

### Issue: "SECRET_KEY not set"
**Solution**: Set environment variables
```bash
heroku config:set SECRET_KEY=your-secret-key
```

### Issue: "SSL certificate error"
**Solution**: Already fixed by SECURE_SSL_REDIRECT = True

---

## Post-Deployment

### Create Superuser
```bash
heroku run python manage.py createsuperuser
# Enter username, email, password
```

### Populate Data
```bash
heroku run python manage.py populate_categories
heroku run python manage.py populate_blog_data
```

### Access Admin
```
https://your-app-name.herokuapp.com/admin/
# Login with superuser credentials
```

---

## Monitoring & Maintenance

### View Logs
```bash
# Recent logs
heroku logs --num 50

# Follow logs (tail)
heroku logs --tail

# Application errors only
heroku logs --source app
```

### Scale Dynos (if needed)
```bash
# Scale to 2 web dynos (costs $)
heroku ps:scale web=2

# View dyno usage
heroku ps
```

### Database Backups
```bash
# Automatic backups daily
# Manual backup:
heroku pg:backups:capture

# Download backup
heroku pg:backups:download
```

---

## Security Verification on Heroku

### Check Headers
```bash
curl -I https://your-app-name.herokuapp.com/
```

Should see:
```
Strict-Transport-Security: max-age=31536000
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

### Test HTTPS Redirect
```bash
curl -I http://your-app-name.herokuapp.com/
# Should redirect to https://
```

### Test Authentication
```bash
# Try to access notifications without login (should return 401)
curl https://your-app-name.herokuapp.com/api/notifications/
```

---

## Troubleshooting SSL Certificate

Heroku provides free SSL automatically. If issues:

```bash
# Force HTTPS
heroku config:set SECURE_SSL_REDIRECT=True

# Check SSL cert
heroku certs:info

# Or use Heroku's free wildcard
heroku certs:auto:enable
```

---

## Optional: Custom Domain

```bash
# Add domain
heroku domains:add www.yourdomain.com

# Get DNS target
heroku domains

# Update your DNS provider to CNAME to: your-app-name.herokuapp.com
```

---

## Performance Optimization (Optional)

### Add Dyno Metadata
```bash
heroku labs:enable runtime-dyno-metadata
```

### Enable WhiteNoise CDN Cache
Already configured in `settings.py` with `WhiteNoiseMiddleware`

### Database Connection Pooling
Already configured for production

---

## Cost Breakdown (As of Jan 2026)

| Component | Cost |
|-----------|------|
| Web Dyno (1x, basic) | Free |
| Postgres (hobby) | Free |
| Custom Domain | Included |
| SSL Certificate | Free (auto) |
| **Total** | **$0 (free tier)** |

---

## Heroku Deployment Summary

```
✅ Security: CONFIGURED
✅ SSL/HTTPS: AUTOMATIC
✅ Database: MANAGED
✅ Static Files: COLLECTED
✅ Environment Variables: SET
✅ Cost: FREE (hobby tier)
```

---

## Quick Deployment Commands

```bash
# One-time setup
heroku login
heroku create your-app-name
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
heroku config:set DEBUG=False
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Verify
heroku open
heroku logs --tail

# Admin setup
heroku run python manage.py createsuperuser
heroku run python manage.py populate_categories
heroku run python manage.py populate_blog_data
```

---

## References

- [Heroku Django Deployment](https://devcenter.heroku.com/articles/deploying-python)
- [Heroku PostgreSQL](https://devcenter.heroku.com/articles/heroku-postgresql)
- [Heroku SSL/HTTPS](https://devcenter.heroku.com/articles/ssl)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

---

**Status**: ✅ READY FOR HEROKU DEPLOYMENT
**Last Updated**: January 11, 2026
**Security Level**: Enterprise-Grade
