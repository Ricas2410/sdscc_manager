# SDSCC Deployment Setup Script
# Run this script in PowerShell to set up all secrets for Fly.io deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SDSCC Fly.io Deployment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if flyctl is installed
if (!(Get-Command flyctl -ErrorAction SilentlyContinue)) {
    Write-Host "Fly CLI not found. Installing..." -ForegroundColor Yellow
    powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
    Write-Host "Please restart PowerShell and run this script again." -ForegroundColor Red
    exit
}

# Check if logged in
Write-Host "Checking Fly.io login status..." -ForegroundColor Yellow
$whoami = flyctl auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in. Opening browser for login..." -ForegroundColor Yellow
    flyctl auth login
}

Write-Host ""
Write-Host "Setting up secrets..." -ForegroundColor Green
Write-Host ""

# Django Secret Key (generated)
$secretKey = "psmtleua4+g#ys!2t=t@qhnuvd+-uklm^rpyjj!ykl-rlrs2x"
Write-Host "Setting DJANGO_SECRET_KEY..." -ForegroundColor Yellow
flyctl secrets set DJANGO_SECRET_KEY="$secretKey"

# Cloudinary URL
$cloudinaryUrl = "cloudinary://255412318838196:AI__C-l9NjTCu55PzkQO8LFAIPI@dik8dafa2"
Write-Host "Setting CLOUDINARY_URL..." -ForegroundColor Yellow
flyctl secrets set CLOUDINARY_URL="$cloudinaryUrl"

# Database URL - User needs to provide this
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  DATABASE_URL Required" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please enter your Supabase DATABASE_URL:" -ForegroundColor Cyan
Write-Host "(Format: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres)" -ForegroundColor Gray
$dbUrl = Read-Host "DATABASE_URL"

if ($dbUrl) {
    Write-Host "Setting DATABASE_URL..." -ForegroundColor Yellow
    flyctl secrets set DATABASE_URL="$dbUrl"
} else {
    Write-Host "Skipping DATABASE_URL - you'll need to set this manually:" -ForegroundColor Red
    Write-Host 'flyctl secrets set DATABASE_URL="your-database-url"' -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Secrets configured:" -ForegroundColor Cyan
flyctl secrets list

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: flyctl deploy" -ForegroundColor White
Write-Host "2. Wait for deployment to complete" -ForegroundColor White
Write-Host "3. Run: flyctl open" -ForegroundColor White
Write-Host ""
