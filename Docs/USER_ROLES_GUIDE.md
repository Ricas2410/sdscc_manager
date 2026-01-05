# User Roles Guide

## Overview
The SDSCC Church Management System uses a hierarchical role-based access control system to ensure users have appropriate access to data and features.

## Role Hierarchy

### 1. Mission Administrator
**Highest Level - Full System Access**

The **Mission Admin** (also referred to as **System Administrator**, **National Admin**, or **HQ Admin**) is the **highest authority** in the SDSCC management system.

They have **unrestricted, system-wide access** across all modules including contributions, expenditures, remittances, payroll, branch setup, auditing, announcements, settings, and user management.

Mission Admins ensure **financial accountability**, **system configuration**, **pastoral oversight**, and **church-wide operations** run seamlessly.

This role includes **both technical system administration and executive mission leadership controls**.

#### Permissions
- Manage all branches, areas, districts
- Create and manage all user accounts
- Access all financial data
- Override month closures
- System configuration
- Global reports and analytics
- Full READ + WRITE + CONFIGURATION access across all features

| Module                                    | Mission Admin Permissions |
| ----------------------------------------- | ------------------------- |
| Contributor System (General + Individual) | Full                      |
| Contribution Types (Create/Close/Edit)    | Full                      |
| Expenditures (Mission + All Branches)     | Full                      |
| Utilities & Welfare                       | Full                      |
| Branch Local Balances                     | Full                      |
| Mission Funds                             | Full                      |
| Member Records                            | Full                      |
| Groups / Departments                      | Full                      |
| Sermon Management                         | Full                      |
| Attendance (All levels)                   | View Only (edit optional) |
| Pastor Commission Configuration           | Full                      |
| Monthly Closing                           | Full                      |
| Remittances                               | Full                      |
| Payroll (Mission staff)                   | Full                      |
| Inventory and Assets                      | Full                      |
| Announcements (Mission → All levels)      | Full                      |
| District / Area Executive Management      | Full                      |
| Branch Admin Management                   | Full                      |
| User Account + Roles                      | Full                      |
| Audit Logs                                | Full                      |
| Settings & System Configuration           | Full                      |
| PWA / Branding / Logo                     | Full                      |
| Security (PIN, Password reset)            | Full                      |
| Reports (All branches, all levels)        | Full                      |

#### Key Features
- View all branches simultaneously
- Create/edit contribution types globally
- Approve any welfare request
- Access audit logs
- System-wide notifications
- Full national overview dashboard with financial summaries, remittance tracking, expenditure monitoring, staff summaries, and alerts
- System-wide contribution management, monthly closing control, remittance verification, payroll management, announcements, hierarchy management, user management, auditing, and configuration

#### Typical Users
- General Overseer
- National Administrator
- IT Administrator

---

### 2. Area Administrator
**Regional Level - Multiple Districts**

Area Executives manage finances **only at their assigned level**, with visibility into lower levels but not higher levels.

#### Permissions
- Manage all districts in area
- Create district and branch admins
- View financial data for area
- Generate area reports
- Monitor branch performance
- Edit financials within area
- View lower levels (districts and branches)

#### Key Features
- Hierarchical dropdown for district selection
- Area-wide financial summaries
- Branch comparison tools
- District oversight
- Area → Districts → Branches scope

#### Typical Users
- Area Overseer
- Regional Pastor
- Area Supervisor

---

### 3. District Administrator
**Sub-regional Level - Multiple Branches**

#### Permissions
- Manage all branches in district
- Create branch admins and pastors
- View district financial data
- Generate district reports
- Coordinate branch activities

#### Key Features
- Branch selection dropdown
- District financial tracking
- Branch performance monitoring
- Pastoral oversight

#### Typical Users
- District Overseer
- District Pastor
- District Supervisor

---

### 4. Branch Administrator
**Local Level - Single Branch**

Branch Executives are the **primary operational admins** of the church.
They handle all **member management, contributions, expenditures, attendance, utilities, welfare, and reporting** for their local branch.

#### Permissions
- Manage branch members
- Process contributions and expenditures
- Close monthly finances
- Manage branch staff
- Generate branch reports
- Full member management (add, edit, deactivate)
- General contributions full control
- Individual contributions full control
- Create branch-only contribution types
- Expenditures add/edit/approve
- Utilities & welfare full control
- Attendance management
- Branch announcements creation
- Sermon uploads
- Remittance recording

| Module                    | Permission                                   |
| ------------------------- | -------------------------------------------- |
| Member Management         | Full (add, edit, deactivate)                 |
| General Contributions     | Full (add, edit, close, upload receipt)      |
| Individual Contributions  | Full (add, edit, delete with reason + audit) |
| Contribution Types        | Create branch-only types                     |
| Pledges / Closeable Types | Record, update, close                        |
| Expenditures              | Add / edit / approve local expenses          |
| Utilities & Welfare       | Full control                                 |
| Branch Balance            | Full view                                    |
| Mission Allocations       | View-only                                    |
| Attendance                | Add, edit, view                              |
| Announcements             | Create (branch level only)                   |
| Sermons                   | Upload (branch pastor optional)              |
| Remittance to Mission     | Record "Sent" payment                        |

#### Key Features
- Branch-only data view
- Monthly closing capabilities
- Local financial management
- Member administration
- Branch balance monitoring
- Welfare and utility management
- Local reporting and analytics

#### Typical Users
- Branch Pastor
- Branch Secretary
- Branch Treasurer

---

### 5. Auditor
**Financial Oversight - Read-Only Access**

#### Permissions
- View all financial transactions
- Generate audit reports
- Export financial data
- Track compliance
- Monitor remittances

#### Key Features
- Comprehensive audit dashboard
- Transaction trails
- Variance analysis
- Compliance reporting
- No editing capabilities

#### Typical Users
- External Auditor
- Finance Committee
- Audit Team Member

---

### 6. Pastor
**Pastoral Care - Member Focus**

Pastors are **not normal church members**. They are **spiritual leaders** and **staff-level users**, and may optionally serve as **administrators** when assigned as branch, district, or area admins.

The system must dynamically adjust **sidebar**, **permissions**, and **dashboard features** based on their pastoral rank and administrative assignment.

#### Permissions
- Manage assigned branch members
- View member contributions
- Record pastoral activities
- Manage member groups
- Generate member reports
- View all financial data read-only (if not admin)
- Manage attendance
- Create announcements/events (by pastoral rank)
- Access commission & payroll
- Access member directory
- View aggregated reports
- If assigned as admin, inherit full admin permissions for that level

#### Key Features
- Member management tools
- Attendance tracking
- Pastoral care records
- Member communication
- Limited financial view
- Dynamic sidebar based on role (staff mode vs admin mode)
- Dashboard with financial overview (read-only), attendance metrics, pastoral metrics, commission summary
- Member directory with search and edit capabilities for non-financial details
- Announcements & events creation based on rank
- Tithe commission module for eligible pastors

#### Typical Users
- Branch Pastor
- Associate Pastor
- Assistant Pastor
- District Pastor
- Area Pastor

---

### 7. Member
**Basic Access - Personal Information**

Members are the **core users** of the SDSCC system.
They represent the **final level of the church hierarchy**, with access strictly limited to **their own data**, **general church content**, and **allowed financial views**.

Members **cannot** access or view anything outside their personal scope.

#### Permissions
- View personal profile
- Update personal information
- View own contributions
- Access announcements
- View church calendar
- View own attendance
- Access sermons
- View assigned groups
- Limited financial views (own contributions only)

| Module                              | Member Permission          |
| ----------------------------------- | -------------------------- |
| Own Contributions                   | Full view (no edit)        |
| Contribution Types List             | View only (if allowed)     |
| General Offering Summaries          | View only                  |
| Funeral Contributions               | View own only              |
| Branch Announcements                | Full view                  |
| District/Area/Mission Announcements | View only                  |
| Sermons                             | Full access                |
| Attendance                          | View own attendance        |
| Member Profile                      | View + edit limited fields |
| Groups/Departments                  | View assigned groups       |
| Pastoral Notes                      | Not visible                |
| Branch Finances                     | No access                  |
| Branch Expenditures                 | No access                  |
| Payroll                             | No access                  |
| Remittance                          | No access                  |
| Utilities & Welfare                 | No access                  |
| Audit Logs                          | No access                  |
| System Settings                     | No access                  |

#### Key Features
- Profile management
- Photo upload
- Contribution history
- Communication access
- Mobile app access
- Personal contribution overview
- General church announcements
- Sermon access
- Church events and calendar

#### Typical Users
- Church Members
- Regular Attendees
- New Converts

## Permission Matrix

| Feature | Mission | Area | District | Branch | Auditor | Pastor | Member |
|---------|---------|------|----------|--------|---------|--------|--------|
| User Management | ✓ All | ✓ Area | ✓ District | ✓ Branch | ✗ | ✗ | ✗ |
| Financial Reports | ✓ All | ✓ Area | ✓ District | ✓ Branch | ✓ All | ✓ Branch | ✓ Own |
| Edit Contributions | ✓ All | ✗ | ✗ | ✓ Branch | ✗ | ✗ | ✗ |
| Monthly Closing | ✓ All | ✗ | ✗ | ✓ Branch | ✗ | ✗ | ✗ |
| Welfare Approval | ✓ All | ✗ | ✗ | ✓ Branch | ✗ | ✗ | ✗ |
| Member Management | ✓ All | ✓ Area | ✓ District | ✓ Branch | ✗ | ✓ Branch | ✓ Own |
| System Settings | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Access Control Features

### Hierarchical Filtering
- **Mission Admin:** Sees all levels
- **Area Admin:** Filters by area first
- **District Admin:** Filters by district first
- **Branch Admin:** Sees only branch
- **Others:** Limited to assigned scope

### Data Visibility
- **Upward Visibility:** Can see levels below
- **No Upward Access:** Cannot see above
- **Peer Access:** Only same level with permission
- **Cross-Branch:** Limited by role

### Approval Workflows
- **Branch Level:** Initial approvals
- **District Level:** Review and override
- **Area Level:** Regional oversight
- **Mission Level:** Final authority

## Security Features

### Authentication
- **PIN System:** 4-digit access
- **Password Recovery:** Email-based
- **Session Management:** Auto-timeout
- **Multi-device:** Supported

### Authorization
- **Role-Based:** Permissions by role
- **Scope-Based:** Data by hierarchy
- **Feature-Based:** Function by permission
- **Time-Based:** Access expiration

### Audit Trail
- **All Actions:** Logged
- **User Tracking:** Who did what
- **Timestamp:** When accessed
- **Data Changes:** Before/after

## Best Practices

### For Administrators
1. Assign minimum necessary permissions
2. Regular permission reviews
3. Monitor user activity
4. Update role assignments promptly
5. Document access decisions

### For Users
1. Protect login credentials
2. Log out when finished
3. Report suspicious activity
4. Use role-appropriate features
5. Follow data policies

## Role Changes

### Promotion Process
1. Identify need for change
2. Get appropriate approval
3. Update user role
4. Notify user of change
5. Provide training if needed

### Demotion Process
1. Document reason
2. Get approval
3. Update role
4. Revoke excess permissions
5. Confirm access changes

## Troubleshooting

### Access Issues
- **Permission Denied:** Check role assignment
- **Missing Features:** Verify role permissions
- **Data Not Visible:** Confirm scope settings
- **Login Problems:** Reset credentials

### Solutions
1. Contact system administrator
2. Verify user status
3. Check role assignments
4. Clear browser cache
5. Update browser if needed

## Training Requirements

### Mission Admin
- System administration
- User management
- Financial oversight
- Security protocols
- Emergency procedures

### Branch Admin
- Daily operations
- Financial processes
- Member management
- Reporting basics
- Compliance requirements

### Member
- Basic navigation
- Profile management
- Contribution viewing
- Communication tools
- Mobile app usage

## Support Contacts

### Role Issues
- **Primary:** Branch Administrator
- **Escalation:** District Administrator
- **Final:** Mission Administrator
- **Technical:** IT Support

### Training Resources
- **Online Help:** System documentation
- **Video Guides:** Feature tutorials
- **Live Training:** Scheduled sessions
- **Quick Reference:** Role cheat sheets
