# SDSCC Church Management System - Fly.io Deployment Guide

## Prerequisites
- Windows PowerShell
- Git installed
- Internet connection

---

## Step 1: Install Fly.io CLI

Open PowerShell as Administrator and run:

```powershell
# Install flyctl using PowerShell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

After installation, close and reopen PowerShell, then verify:

```powershell
flyctl version
```

---

## Step 2: Sign Up / Login to Fly.io

```powershell
# Sign up for a new account (opens browser)
flyctl auth signup

# OR Login if you have an account
flyctl auth login
```

---

## Step 3: Create the Fly.io App

Navigate to your project directory:

```powershell
cd C:\Users\Skillnet\Desktop\Shalom_manager
```

Launch the app (this creates the app on Fly.io):

```powershell
flyctl launch --no-deploy
```

When prompted:
- **App name**: `sdscc` (or choose another unique name)
- **Region**: Select `fra` (Frankfurt) to match your database
- **PostgreSQL database**: Select `No` (we'll use external database)
- **Redis**: Select `No`

---

## Step 4: Set Up Secrets (Environment Variables)

Set all required secrets. Run these commands one by one:

### Django Secret Key
```powershell
flyctl secrets set DJANGO_SECRET_KEY="pzophIuIMD777t7bivreqFrGtF20SfKdS_1GfUU0KBzEo8_WzMdUQd0iBd3fjr0_h8k"
```

### Database URL (Supabase PostgreSQL)
```powershell
flyctl secrets set DATABASE_URL="postgresql://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
```

### Cloudinary (Media Storage)
```powershell
flyctl secrets set CLOUDINARY_URL="cloudinary://255412318838196:AI__C-l9NjTCu55PzkQO8LFAIPI@dik8dafa2"
```

### Verify All Secrets
```powershell
flyctl secrets list
```

---

## Step 5: Deploy the Application

```powershell
flyctl deploy
```

This will:
1. Build the Docker image
2. Push to Fly.io registry
3. Run database migrations
4. Start the application

---

## Step 6: Run Initial Setup (First Deployment Only)

After the first deployment, set up the initial data:

```powershell
# Open a console session to your app
flyctl ssh console

# Inside the container, run:
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_sdscc

# Exit the console
exit
```

---

## Step 7: Verify Deployment

```powershell
# Check app status
flyctl status

# View app logs
flyctl logs

# Open the app in browser
flyctl open
```

Your app will be available at: **https://sdscc.fly.dev**

---

## Common Commands Reference

### View Logs
```powershell
flyctl logs
```

### SSH into Container
```powershell
flyctl ssh console
```

### Restart App
```powershell
flyctl apps restart sdscc
```

### Scale App (if needed)
```powershell
# Scale to 2 machines
flyctl scale count 2

# Scale memory
flyctl scale memory 1024
```

### View App Info
```powershell
flyctl info
```

### Update Secrets
```powershell
flyctl secrets set SECRET_NAME="new_value"
```

### Remove a Secret
```powershell
flyctl secrets unset SECRET_NAME
```

---

## Updating the Application

After making code changes:

```powershell
# Commit your changes
git add .
git commit -m "Your commit message"

# Deploy updates
flyctl deploy
```

---

## Troubleshooting

### Deployment Fails
```powershell
# Check build logs
flyctl logs --instance <instance-id>

# Check recent deployments
flyctl releases
```

### Database Connection Issues
```powershell
# Verify DATABASE_URL is set correctly
flyctl secrets list

# Test connection from console
flyctl ssh console
python manage.py dbshell
```

### Static Files Not Loading
```powershell
# SSH and manually collect static files
flyctl ssh console
python manage.py collectstatic --noinput
```

### App Crashes on Startup
```powershell
# View detailed logs
flyctl logs -a sdscc

# Check machine status
flyctl machine list
```

---

## Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key (50+ chars) | Random string |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `CLOUDINARY_URL` | Cloudinary credentials | `cloudinary://key:secret@cloud` |
| `DJANGO_DEBUG` | Debug mode (auto-set to False) | `False` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts (auto-set) | `sdscc.fly.dev,localhost` |

---

## Supabase Database Setup

If you haven't set up your Supabase database yet:

1. Go to [supabase.com](https://supabase.com) and sign in
2. Create a new project in the Frankfurt region
3. Go to **Settings > Database**
4. Copy the **Connection string (URI)** 
5. Replace `[YOUR-PASSWORD]` with your database password
6. Use this as your `DATABASE_URL`

---

## Post-Deployment Checklist

- [ ] App accessible at https://sdscc.fly.dev
- [ ] Can login with superuser credentials
- [ ] Database migrations applied successfully
- [ ] Static files loading correctly
- [ ] Media uploads working (Cloudinary)
- [ ] All error pages displaying correctly (404, 500, etc.)

---

## Support

If you encounter issues:
1. Check Fly.io status: https://status.fly.io
2. Check Supabase status: https://status.supabase.com
3. Review logs: `flyctl logs`
4. Fly.io documentation: https://fly.io/docs

---

*Generated for SDSCC Church Management System*
*Deployment Region: Frankfurt (fra)*
