# SDSCC - Church Management System

**Seventh Day Sabbath Church of Christ - National Church Management System**

A comprehensive, mobile-first Progressive Web App (PWA) for managing church operations across Mission → Area → District → Branch → Members hierarchy.

## Features

### Core Modules
- **Member Management** - Complete member profiles, registration, transfers
- **Contributions** - General & individual contributions, tithe tracking, allocation splits
- **Expenditures** - Branch and mission-level expense tracking with receipts
- **Remittances** - Branch to Mission fund transfers with verification
- **Attendance** - Sabbath worship, mid-week, and special programs tracking
- **Payroll** - Mission staff salary, allowances, deductions, payslips
- **Announcements** - Hierarchical messaging system
- **Sermons** - Text, audio, video sermon library
- **Groups & Ministries** - Department and ministry management
- **Audit System** - Complete audit trails and financial reports

### Role-Based Access
- **Mission Admin** - Full system control
- **Area/District/Branch Executives** - Hierarchical management
- **Auditors/Board of Trustees** - Read-only oversight
- **Pastors** - Ministry and commission management
- **Members** - Personal dashboard and contributions

### PWA Features
- Install on iOS, Android, and Desktop
- Offline capability
- Push notifications (configurable)
- Mobile-first responsive design

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Frontend**: TailwindCSS, Material Icons
- **Charts**: Chart.js
- **Deployment**: fly.io ready

## Quick Start (Development)

```powershell
# Clone repository
git clone <repo-url>
cd Shalom_manager

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://localhost:8000` and login with your superuser credentials.

## Deployment to fly.io

### Prerequisites
1. Install [flyctl](https://fly.io/docs/hands-on/install-flyctl/)
2. Create a fly.io account: `fly auth signup`

### Deploy Steps

```powershell
# Login to fly.io
fly auth login

# Launch app (first time)
fly launch --name sdscc

# Create PostgreSQL database
fly postgres create --name sdscc-db

# Attach database to app
fly postgres attach sdscc-db --app sdscc

# Set secrets
fly secrets set DJANGO_SECRET_KEY="your-super-secret-key-here"
fly secrets set DJANGO_DEBUG="False"

# Deploy
fly deploy

# Run migrations
fly ssh console -C "python manage.py migrate"

# Create superuser
fly ssh console -C "python manage.py createsuperuser"
```

Your app will be live at: `https://sdscc.fly.dev`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | (development key) |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL connection URL | SQLite |

## Project Structure

```
Shalom_manager/
├── accounts/       # User authentication & management
├── announcements/  # Church announcements
├── attendance/     # Attendance tracking
├── auditing/       # Audit logs & reports
├── contributions/  # Financial contributions
├── core/           # Dashboard, hierarchy, settings
├── expenditure/    # Expense management
├── groups/         # Ministries & departments
├── members/        # Member management
├── payroll/        # Staff payroll
├── reports/        # Report generation
├── sermons/        # Sermon library
├── static/         # Static files (CSS, JS, images)
├── templates/      # HTML templates
├── Docs/           # System documentation
└── sdscc/          # Django project settings
```

## Default Credentials

- **Default PIN/Password**: `12345`
- Members login with: `Member ID + PIN`

## License

Proprietary - SDSCC Ghana

## Support

For support, contact the SDSCC IT Department.
