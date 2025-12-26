

# **Church Management System – Comprehensive Overview**

## **1. Introduction**

This document outlines the full architecture and operational flow of the **SDSCC (Seventh Day Sabbath Church of Christ) National Church Management System** — a unified digital platform designed to manage church members, finances, attendance, contributions, auditing, announcements, payroll, and communication across **Mission → Area → District → Branch → Members**.

The system is fully **mobile-first**, supports **PWA installation**, and provides offline capability through `manifest.json` and `serviceworker.js`.

### **Branding & Identity**

* Application Name: **SDSCC**
* Logo: Uploaded by Mission Admin via General Settings
* Theme colors and branding managed under Site Settings

### **Technology Stack**

* **Django (Full Stack Framework)**
* **TailwindCSS** (primary styling)
* **Bootstrap** (fallback components)
* **Material UI Components** (modern UI widgets)
* **PostgreSQL** (primary database)
* Optional Enhancements: Redis, Celery, DRF API, Push Notifications

This system centralizes the entire nationwide church operation under a secure, role-based access model.

---

## **2. Church Hierarchy Structure**

SDSCC operates under a well-defined hierarchical model:

### **2.1 Organizational Levels**

1. **Mission (National Headquarters)**
2. **Area**
3. **District**
4. **Branch**
5. **Members**

Each level has its own administrative officers with varying degrees of permissions and financial oversight.

### **2.2 Relationship Flow**

* **Members** belong to a **Branch**
* **Branches** belong to a **District**
* **Districts** belong to an **Area**
* **Areas** report to the **Mission HQ**

This structure defines visibility, financial responsibility, reporting lines, and access permissions.

---

## **3. User Roles & Permission Scopes**

The system uses a **Role-Based Access Control (RBAC)** model.
Each role has strictly defined permissions to avoid data conflicts and maintain transparency.

| Role                            | Scope & Description                                                          |
| ------------------------------- | ---------------------------------------------------------------------------- |
| **Super Admin / Mission Admin** | Full system authority, settings, permissions, payroll, national finances     |
| **National Auditor**            | Full monitoring, verification, audit logs, publishes annual reports          |
| **Board of Trustees**           | High-level oversight and financial evaluation                                |
| **General Overseer**            | Top spiritual & administrative authority with system-wide visibility         |
| **Area Executive**              | Oversees all districts/branches in the area; manages area finances           |
| **District Executive**          | Oversees branches in district; manages district finances                     |
| **Branch Executive**            | Full branch operations: finance, members, attendance, announcements          |
| **Pastors**                     | Limited admin, attendance, pastoral records, commissions, view-only finances |
| **Staff / Workers**             | Member-like access + payroll, tasks, and work functions                      |
| **Members**                     | Personal dashboard, contributions, sermons, attendance, announcements        |

---

## **4. Member Management**

The system provides complete tools to track and manage all member-related data.

### **4.1 Core Features**

* Add, edit, update, or deactivate members
* Auto-generate **member ID** based on branch code
* Default 5-digit PIN assigned to each member (changeable on profile)
* CSV import option for mass onboarding
* Member profile includes:

  * Personal details (name, phone, date of birth, gender)
  * Spiritual journey (baptism date, departments, roles held)
  * Marital status, employment/profession
  * Emergency contact details (name, relationship, phone)
  * Optional **profile picture upload or camera capture**
  * Optional **group assignments**

### **4.2 Groups & Departments**

Admins can:

* Create departments or ministry groups (Choir, Youth Ministry, Men Fellowship, etc.)
* Add/remove members from groups
* Assign members to multiple groups during registration or later

Group assignment is **optional**.

---

## **5. Contributions & Financial Management**

The system supports all types of church giving across levels.

### **5.1 Contribution Types**

Admins (based on level) can create:

1. National / Mission-level contributions
2. Area contributions
3. District contributions
4. Branch contributions
5. Individual contributions (Tithe, personal pledges)
6. Non-individual contributions (Offerings, Charity, Thanksgiving)
7. **Funeral Contributions** (per deceased entry, partial payments supported)
8. Special Events / Fundraising

Each contribution type can be customized:

* Name
* Type (offering, tithe, funeral, charity, etc.)
* Frequency (one-time, daily, weekly, monthly)
* Allocation percentages to Mission/Area/District/Branch

### **5.2 Entry & Processing**

Branch Executives:

* Select contribution type
* Enter title/description
* Input amounts paid
* Upload receipts if needed
* The system auto-calculates allocations

### **5.3 Financial Rules**

* Some contributions remain fully at the branch
* Others must be fully remitted to Mission
* Others use split percentages
* Higher levels can view all transactions for transparency
* All edits are logged with **Audit Trails**

---

## **6. Funeral Contribution System**

* Register deceased members or relatives
* Contributions from members can be logged in **installments**
* System tracks outstanding amounts
* Funeral-specific reporting (amounts, contributors, balances)

---

## **7. Offerings & Non-Individual Collections**

Supports:

* Sunday offerings
* Mid-week offerings
* Charity contributions
* Thanksgiving
* Special programs or events

Automatically visible in dashboards with charts and analytics.

---

## **8. Expenditure Management**

Each administrative level (Branch, District, Area, Mission) can:

* Record expenses
* Add descriptions
* Upload receipts (images/PDF)
* Categorize spending
* Deduct from their **local balance**
* Include or exclude from reports

Higher levels have view-only access to lower-level expenditures.

---

## **9. Year-End Rollover**

At year-end:

* Current year contributions archived as “Previous Contributions”
* Attendance moved to historical logs
* Financial summaries stored per year
* Staff, members, and pastors retain access to personal historical data
* Auditors and admins generate the **Annual National Report**

---

## **10. Auditing System**

### **10.1 National Auditor Tools**

* Verify financial records from all levels
* Access all audit logs and historical changes
* Generate and publish **annual audit reports**
* Approve or reject Area/District/Branch reports
* Choose which data is visible to members
* Analyze:

  * Top-performing branches
  * District performance
  * Area performance
  * Total national annual income

---

## **11. Announcement System**

Announcements follow hierarchy-based visibility:

| Level    | Who Sees It                         |
| -------- | ----------------------------------- |
| Mission  | Everyone                            |
| Area     | The area + its districts & branches |
| District | District + its branches             |
| Branch   | Only branch members                 |

Each announcement includes:

* Title
* Description
* Optional attachments
* Scheduled or immediate publishing

---

## **12. Sermon Management**

Branch Pastors or authorized staff can upload:

* Text sermons
* PDF notes
* Video links (YouTube, Vimeo)
* Audio files

Members can search by:

* Topic
* Date
* Pastor
* Branch

---

## **13. Attendance Management**

Track attendance for:

* Sunday service
* Weekday service
* Youth ministry
* Women’s ministry
* Men’s fellowship
* Children’s ministry
* Special programs

Future enhancement: **QR Code Check-In**

---

## **14. Payroll Management**

For paid staff and pastors:

* Mark a member as **Paid Staff**
* Set salary, allowances, deductions
* Generate monthly pay slips
* Staff can download PDF pay slips
* National Admin can edit and finalize payroll

---

## **15. Analytics & Dashboards**

Each role gets a custom dashboard:

### Includes:

* Contribution totals
* Expenditure totals
* Net balances
* Graphs & charts
* Tithe progress
* Comparison reports (District/Area levels)
* Attendance analytics
* Quick shortcuts
* Remittances & pending items

Modern UI built with:

* TailwindCSS
* Material UI charts and widgets

---

## **16. Security & Access Control**

* RBAC (Role-Based Access Control)
* PIN-based login for members and pastors
* Encrypted passwords for all users
* Optional 2FA for administrators
* Full audit logs of all actions

---

## **17. Notifications System**

Real-time notification system for keeping users informed:

### **17.1 Notification Types**
* Member added notifications
* Contribution recorded alerts
* Expenditure approvals
* Announcement broadcasts
* Remittance confirmations
* Birthday/Anniversary reminders
* Prayer request updates
* System alerts

### **17.2 Features**
* AJAX-powered notification dropdown in topbar
* Unread badge counter with real-time updates
* Full notification list page with read/unread filtering
* Mark as read functionality
* Role-based notification targeting

---

## **18. Prayer Request System**

Community prayer support module:

### **18.1 Core Features**
* Submit prayer requests with title and description
* Visibility scope options:
  - Branch Only (default)
  - District Wide
  - Area Wide
  - Mission Wide
* Approval workflow - requests require pastor/admin approval before visibility
* "I Prayed" button with prayer count tracking
* Testimony field for answered prayers
* Status tracking: Pending → Prayed For → Answered → Closed

### **18.2 Privacy & Access**
* Regular members see only approved requests in their scope
* Pastors/Executives see all branch requests for approval
* Mission Admin has full visibility
* Users always see their own requests regardless of approval status

---

## **19. Visitor Follow-up System**

Track and convert first-time visitors:

### **19.1 Visitor Management**
* Record visitor details (name, phone, email, address)
* Track how they heard about the church
* Record who invited them (member reference)
* Assign follow-up responsibilities

### **19.2 Follow-up Workflow**
* Status tracking: New → Contacted → Follow-up → Returned → Converted
* Record follow-up interactions with notes
* Track conversion rates per branch
* Dashboard with visitor statistics

---

## **20. Birthday & Anniversary Celebrations**

Automated celebration reminders:

### **20.1 Features**
* Track member birthdays and wedding anniversaries
* Configurable date range viewing (7, 14, 30 days)
* Age and years calculation
* Branch-level celebration lists
* Optional notification triggers

---

## **21. Data Export & Import**

Comprehensive data management tools:

### **21.1 Export Features**
* Excel export for members (using openpyxl)
* Excel export for contributions
* PDF export for contribution statements (using reportlab)
* JSON configuration backup for system settings

### **21.2 Import Features**
* CSV bulk member import with validation
* Template download for proper formatting
* Error reporting for failed imports

### **21.3 Member Statements**
* Individual printable contribution statements
* Date range selection
* PDF download for personal records

---

## **22. System Settings**

Comprehensive configuration panel for Mission Admin:

### **22.1 Branding Settings**
* Site name and tagline
* Primary and secondary colors
* Logo and favicon upload

### **22.2 Contact Information**
* Church email, phone, address
* Website URL
* Social media links (Facebook, YouTube, Twitter, Instagram)

### **22.3 Financial Settings**
* Currency symbol and code
* Commission percentage
* Fiscal year configuration
* Default tithe targets

### **22.4 Feature Toggles**
* Enable/disable system modules (Contributions, Attendance, Payroll, etc.)
* PWA and offline mode settings
* Notification preferences
* Role-specific permissions

### **22.5 Security Settings**
* Session timeout configuration
* Max login attempts and lockout duration
* Strong password requirements
* Two-factor authentication toggle

### **22.6 Maintenance Mode**
* Enable/disable maintenance mode
* Custom maintenance message
* Allowed IP addresses during maintenance

### **22.7 Backup Settings**
* Automatic backup scheduling
* Backup frequency configuration
* Data retention period

---

## **23. Calendar System**

Modern event calendar for church activities:

### **23.1 Features**
* Monthly calendar view with event indicators
* Compact, responsive design with sidebar for events
* Quick navigation (previous/next month, today button)
* Event type color coding
* Click-to-view event details modal
* Yearly theme and theme verse display

### **23.2 Event Management**
* Create events with title, description, location
* Set event type (Service, Meeting, Special, Holiday)
* Custom color coding per event
* Time scheduling

---

## **24. Progressive Web App (PWA)**

Mobile-first installable application:

### **24.1 Features**
* Installable on mobile and desktop devices
* Offline page for connectivity issues
* Service worker for caching
* Custom app icons (192x192, 512x512)
* App shortcuts for quick access

### **24.2 Technical Implementation**
* manifest.json with app metadata
* Service worker with network-first strategy
* Static asset caching
* Automatic offline fallback

---

## **25. Deployment Configuration**

Production-ready deployment setup:

### **25.1 Fly.io Deployment**
* Dockerfile with Python 3.12
* fly.toml configuration
* PostgreSQL database support
* WhiteNoise for static files

### **25.2 Environment Configuration**
* DATABASE_URL for production database
* SECRET_KEY management
* DEBUG mode toggle
* CSRF trusted origins

### **25.3 Security Features**
* HTTPS enforcement
* Secure cookies
* HSTS headers
* Content security headers

---

## **26. Technology Stack**

### **Backend**
* **Django 4.2+** - Full-stack framework
* **Django ORM** - Database abstraction
* **SQLite** (development) / **PostgreSQL** (production)
* **Gunicorn** - WSGI server

### **Frontend**
* **TailwindCSS** - Primary styling framework
* **Material Icons** - Icon library
* **Chart.js** - Analytics charts
* **Alpine.js** - Lightweight interactivity

### **Libraries**
* **openpyxl** - Excel export
* **reportlab** - PDF generation
* **dj-database-url** - Database configuration
* **whitenoise** - Static file serving

### **DevOps**
* **Docker** - Containerization
* **Fly.io** - Cloud deployment
* **GitHub** - Version control

---

## **27. Future Enhancements**

Planned features for future releases:

* **SMS Integration** - Twilio/Africa's Talking
* **WhatsApp Sharing** - Announcement sharing
* **Online Giving** - PayStack/MTN MoMo integration
* **Mobile App** - Flutter/React Native
* **Multi-language Support** - French, Twi, Ewe
* **Skills Database** - Member talents tracking
* **Event RSVP** - Attendance confirmation
* **Video Conferencing** - Zoom/Meet integration
* **AI Sermon Search** - Semantic content discovery



cloudinar API:
CLOUDINARY_URL=cloudinary://255412318838196:AI__C-l9NjTCu55PzkQO8LFAIPI@dik8dafa2

SUperbase:
Publishable key: sb_publishable_pEr0Uevve2mhAhxHXKay3g_g3kwxMCk

Secret keys:
Name: default
 API Key: sb_secret_SGX5iHND6vFU-EpgwsAlvA_AYWy8GSe

 postgresql://postgres:[YOUR_PASSWORD]@db.morzzxtqhzorjkbtzyib.supabase.co:5432/postgres
