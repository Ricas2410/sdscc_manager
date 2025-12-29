# User Roles Guide

## Overview
The SDSCC Church Management System uses a hierarchical role-based access control system to ensure users have appropriate access to data and features.

## Role Hierarchy

### 1. Mission Administrator
**Highest Level - Full System Access**

#### Permissions
- Manage all branches, areas, districts
- Create and manage all user accounts
- Access all financial data
- Override month closures
- System configuration
- Global reports and analytics

#### Key Features
- View all branches simultaneously
- Create/edit contribution types globally
- Approve any welfare request
- Access audit logs
- System-wide notifications

#### Typical Users
- General Overseer
- National Administrator
- IT Administrator

---

### 2. Area Administrator
**Regional Level - Multiple Districts**

#### Permissions
- Manage all districts in area
- Create district and branch admins
- View financial data for area
- Generate area reports
- Monitor branch performance

#### Key Features
- Hierarchical dropdown for district selection
- Area-wide financial summaries
- Branch comparison tools
- District oversight

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

#### Permissions
- Manage branch members
- Process contributions and expenditures
- Close monthly finances
- Manage branch staff
- Generate branch reports

#### Key Features
- Branch-only data view
- Monthly closing capabilities
- Local financial management
- Member administration

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

#### Permissions
- Manage assigned branch members
- View member contributions
- Record pastoral activities
- Manage member groups
- Generate member reports

#### Key Features
- Member management tools
- Attendance tracking
- Pastoral care records
- Member communication
- Limited financial view

#### Typical Users
- Branch Pastor
- Associate Pastor
- Assistant Pastor

---

### 7. Member
**Basic Access - Personal Information**

#### Permissions
- View personal profile
- Update personal information
- View own contributions
- Access announcements
- View church calendar

#### Key Features
- Profile management
- Photo upload
- Contribution history
- Communication access
- Mobile app access

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
