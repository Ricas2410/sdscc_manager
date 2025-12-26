# **Mission Admin User Guide - Complete System Manual**

## **Table of Contents**
1. [Introduction](#introduction)
2. [Login & Dashboard Overview](#login--dashboard-overview)
3. [System Configuration](#system-configuration)
4. [Hierarchy Management](#hierarchy-management)
5. [Financial Management](#financial-management)
6. [Contribution Management](#contribution-management)
7. [Expenditure Management](#expenditure-management)
8. [Remittance Management](#remittance-management)
9. [Payroll Management](#payroll-management)
10. [User Management](#user-management)
11. [Audit & Reports](#audit--reports)
12. [Announcements & Communication](#announcements--communication)
13. [Monthly Closing Process](#monthly-closing-process)
14. [Year-End Procedures](#year-end-procedures)
15. [Troubleshooting & Support](#troubleshooting--support)

---

## **Introduction**

### **Who is a Mission Admin?**
The **Mission Admin** (also called System Administrator or National Admin) is the **highest authority** in the SDSCC Church Management System. You have complete control over:

- **All church levels**: Mission → Areas → Districts → Branches → Members
- **All financial operations**: Contributions, expenditures, remittances, payroll
- **System configuration**: Settings, user roles, permissions
- **Audit trails**: Full visibility into all system activities
- **Reporting**: Generate any report across the entire organization

### **Your Responsibilities**
- Ensure financial accountability across all branches
- Configure and maintain system settings
- Manage user accounts and permissions
- Oversee monthly and annual financial cycles
- Generate and approve reports
- Maintain church hierarchy structure

---

## **Login & Dashboard Overview**

### **How to Login**
1. Open your church management system URL
2. Enter your **Member ID** (e.g., "ADM001")
3. Enter your **password** (default: `12345` for first-time login)
4. Click **"Login"**

### **First Time: Change Your Password**
1. After login, click **"My Profile"** in the sidebar
2. Click **"Change Password"**
3. Enter current password (`12345`)
4. Enter new password (minimum 8 characters)
5. Confirm new password
6. Click **"Update Password"**

### **Your Dashboard Overview**

Your dashboard provides a **complete national overview** with these sections:

#### **📊 Key Statistics Cards**
- **Total Branches**: Number of active church branches
- **Total Members**: All registered members across all branches
- **Total Districts**: Number of active districts
- **Total Areas**: Number of active areas

#### **💰 Financial Summary**
- **Monthly Contributions**: Total contributions this month
- **Monthly Expenditure**: Total expenses this month
- **Pending Remittances**: Branch payments awaiting verification
- **Recent Contributions**: Latest contribution entries across all branches

#### **⚡ Quick Actions**
- **System Configuration**: Access contribution types, settings
- **Manage Branches**: Add/edit/deactivate branches
- **User Management**: Create and manage user accounts
- **Generate Reports**: Access financial and operational reports

#### **📋 Recent Activities**
- **Recent Branches**: Newly created or updated branches
- **Pending Remittances List**: Branch payments needing your verification
- **System Alerts**: Important notifications and warnings

---

## **System Configuration**

### **Accessing System Settings**
1. In the sidebar, click **"System Settings"**
2. You'll see several configuration sections

### **🎨 Branding Configuration**
#### **Church Identity**
- **Site Name**: Your church organization name (default: "SDSCC")
- **Tagline**: Church motto or description
- **Logo Upload**: Upload your church logo (recommended: 200x200px)
- **Favicon**: Small icon for browser tabs

#### **Visual Settings**
- **Primary Color**: Main theme color
- **Secondary Color**: Accent color
- **Login Background**: Background image for login page

### **📞 Contact Information**
- **Church Email**: Official church email address
- **Phone Number**: Main church contact number
- **Address**: Church headquarters address
- **Website**: Official church website URL
- **Social Media**: Facebook, YouTube, Twitter, Instagram links

### **💰 Financial Settings**
#### **Currency Configuration**
- **Currency Symbol**: e.g., "GHS", "$", "£"
- **Currency Code**: 3-letter currency code

#### **Commission Settings**
- **Commission Percentage**: Default pastor commission rate (usually 10%)
- **Commission Eligibility Rules**: Who qualifies for commissions

#### **Fiscal Year**
- **Start Date**: When your fiscal year begins
- **End Date**: When your fiscal year ends

### **🔐 Security Settings**
#### **Password Requirements**
- **Minimum Length**: Minimum password characters
- **Strong Password Rules**: Require special characters, numbers
- **Session Timeout**: Auto-logout after inactivity

#### **Login Security**
- **Max Login Attempts**: Lock account after failed attempts
- **Lockout Duration**: How long to lock account
- **Two-Factor Authentication**: Enable/disable 2FA

### **🔧 Feature Toggles**
You can enable/disable system modules:
- **Contributions Module**: Turn on/off contribution tracking
- **Attendance Module**: Enable/disable attendance tracking
- **Payroll Module**: Control access to payroll features
- **PWA Mode**: Progressive Web App features
- **Offline Mode**: Allow offline access

---

## **Hierarchy Management**

### **Church Structure Overview**
Your church follows this hierarchy:
```
Mission (National HQ)
├── Area 1
│   ├── District 1
│   │   ├── Branch A
│   │   └── Branch B
│   └── District 2
│       ├── Branch C
│       └── Branch D
└── Area 2
    └── District 3
        └── Branch E
```

### **Creating Areas**
1. In sidebar, click **"Areas"**
2. Click **"Add New Area"**
3. Fill in:
   - **Area Name**: e.g., "Greater Accra Area"
   - **Area Code**: Unique code (e.g., "GA")
   - **Description**: Optional details
   - **Status**: Active/Inactive
4. Click **"Save Area"**

### **Creating Districts**
1. In sidebar, click **"Districts"**
2. Click **"Add New District"**
3. Fill in:
   - **District Name**: e.g., "Tema District"
   - **District Code**: Unique code (e.g., "TD")
   - **Area**: Select which area this district belongs to
   - **Description**: Optional details
   - **Status**: Active/Inactive
4. Click **"Save District"**

### **Creating Branches**
1. In sidebar, click **"Branches"**
2. Click **"Add New Branch"**
3. Fill in:
   - **Branch Name**: e.g., "Tema Community Branch"
   - **Branch Code**: Unique code for member IDs (e.g., "TCB")
   - **District**: Select the district
   - **Address**: Physical branch address
   - **Phone**: Branch contact number
   - **Pastor**: Assign branch pastor (if already created)
   - **Monthly Tithe Target**: Set monthly goal
   - **Status**: Active/Inactive
4. Click **"Save Branch"**

### **Assigning Leaders**
#### **Area Executives**
1. Go to **"User Management"** → **"Users"**
2. Find or create the user
3. Click **"Edit"**
4. Set **Role** to **"Area Executive"**
5. In **"Managed Area"**, select the area
6. Click **"Save User"**

#### **District Executives**
1. Find or create the user
2. Click **"Edit"**
3. Set **Role** to **"District Executive"**
4. In **"Managed District"**, select the district
5. Click **"Save User"**

#### **Branch Executives**
1. Find or create the user
2. Click **"Edit"**
3. Set **Role** to **"Branch Executive"**
4. In **"Branch Assignment"**, select the branch
5. Click **"Save User"**

---

## **Financial Management**

### **🏦 Banking & Financial Setup**
#### **Bank Accounts**
1. Go to **"System Settings"** → **"Financial Settings"**
2. Add church bank accounts:
   - **Account Name**: e.g., "SDSCC General Account"
   - **Bank Name**: Bank institution
   - **Account Number**: Full account number
   - **Account Type**: Savings/Current/Corporate

#### **Financial Categories**
1. **Income Categories**: Contribution types, donations, etc.
2. **Expense Categories**: Utilities, welfare, salaries, etc.
3. **Fund Categories**: Different funds for specific purposes

### **💳 Payment Methods**
Configure accepted payment methods:
- **Cash**: Physical cash collections
- **Bank Transfer**: Direct bank deposits
- **Mobile Money**: MTN MoMo, Vodafone Cash, etc.
- **Cheque**: Bank cheque payments
- **Online Payment**: Future integration with payment gateways

---

## **Contribution Management**

### **Understanding Contribution Types**
Contributions can be:
- **General**: Collected from everyone (e.g., offerings)
- **Individual**: Tracked per person (e.g., tithes, pledges)
- **Closeable**: Temporary campaigns with end dates
- **Ongoing**: Regular, continuous contributions

### **Creating Contribution Types**
1. In sidebar, click **"Contributions"** → **"Contribution Types"**
2. Click **"Add New Type"**
3. Configure:

#### **Basic Information**
- **Name**: e.g., "Sunday Offering", "Tithe", "Building Fund"
- **Description**: What this contribution is for
- **Code**: Unique short code (e.g., "OFF", "TIT", "BLD")

#### **Type Configuration**
- **Contribution Type**: 
  - General (collected from everyone)
  - Individual (tracked per person)
- **Frequency**: 
  - One-time
  - Daily
  - Weekly
  - Monthly
- **Is Closeable**: Can this be closed when complete?

#### **Financial Rules**
- **Mission Percentage**: % goes to headquarters
- **Area Percentage**: % goes to area (if applicable)
- **District Percentage**: % goes to district (if applicable)
- **Branch Percentage**: % stays at branch
- **Example**: Tithe might be 70% Mission, 30% Branch

#### **Target Settings** (Optional)
- **Monthly Target**: Goal amount for this contribution
- **Reward Commission**: Enable commission for achieving target
- **Commission Percentage**: % to pay as commission

4. Click **"Save Contribution Type"**

### **Managing Existing Contribution Types**
1. Go to **"Contributions"** → **"Contribution Types"**
2. You'll see all contribution types with:
   - **Status**: Active/Closed
   - **Total Collected**: Running total
   - **This Month**: Current month collections
   - **Actions**: Edit, Close, View Reports

#### **Closing a Contribution Type**
1. Find the contribution type
2. Click **"Close"** (only for closeable types)
3. Enter reason (optional)
4. Click **"Confirm Close"**
- **Note**: Closed types cannot receive new entries
- **History remains visible** in reports

### **Viewing Contributions**
#### **National Overview**
1. Click **"Contributions"** → **"All Contributions"**
2. You see:
   - **All branches** contribution data
   - **Filter by**: Date range, branch, contribution type
   - **Export options**: Excel, PDF, CSV
   - **Total sums**: Mission-wide totals

#### **Branch-Level View**
1. Click **"Contributions"** → **"By Branch"**
2. Select a branch to see:
   - Their specific contribution entries
   - **Monthly breakdowns**
   - **Target achievement**
   - **Commission eligibility**

---

## **Expenditure Management**

### **Understanding Expenditures**
Expenditures are money spent by:
- **Mission HQ**: National-level expenses
- **Branches**: Local branch expenses
- **Areas/Districts**: Regional expenses (if configured)

### **Adding Mission Expenditures**
1. Click **"Expenditures"** → **"Add Expenditure"**
2. Fill in:
   - **Description**: What was paid for
   - **Amount**: Total amount spent
   - **Category**: e.g., "Utilities", "Salaries", "Welfare"
   - **Date**: When payment was made
   - **Payment Method**: Cash, Bank, Mobile Money, etc.
   - **Reference Number**: Receipt or transaction number
   - **Receipt Upload**: Photo or PDF of receipt
   - **Notes**: Additional details
3. Click **"Save Expenditure"**

### **Viewing Branch Expenditures**
1. Click **"Expenditures"** → **"Branch Expenditures"**
2. **Filter by**:
   - Branch
   - Date range
   - Category
   - Amount range
3. **Export data** for audit purposes

### **Expenditure Categories Management**
1. Click **"Expenditures"** → **"Categories"**
2. **Add categories** like:
   - Utilities (electricity, water, internet)
   - Rent & Maintenance
   - Welfare & Support
   - Office Supplies
   - Transportation
   - Communications
   - Insurance

### **Utility Bills Management**
Special tracking for regular expenses:
1. Click **"Expenditures"** → **"Utilities"**
2. **Add utility bills**:
   - Electricity bills
   - Water bills
   - Internet/Phone bills
   - Rent payments
3. **Track due dates** and **payment status**

---

## **Remittance Management**

### **Understanding Remittances**
**Remittances** are payments from branches to Mission HQ based on contribution splits:
- Branches collect contributions
- System calculates Mission's share
- Branches send (remit) Mission's portion
- You verify receipt

### **Remittance Workflow**
#### **Branch Side**
1. Branch calculates amount owed to Mission
2. Records payment details in system
3. Marks status as **"Sent"**
4. Uploads payment proof

#### **Mission Side (Your Role)**
1. You see pending remittances on dashboard
2. Review payment evidence
3. Mark as **"Verified (Paid)"** or **"Pending"**

### **Processing Remittances**
1. Click **"Remittances"** → **"Pending Verification"**
2. You'll see branches awaiting verification
3. For each remittance:
   - **Branch Name**: Which branch sent it
   - **Amount**: How much was sent
   - **Month**: Which month this covers
   - **Payment Method**: How they paid
   - **Reference**: Transaction reference
   - **Attachment**: Payment proof
   - **Date Sent**: When they recorded it

4. **Review the evidence**:
   - Check bank statement screenshots
   - Verify mobile money confirmations
   - Match amount to expected calculation

5. **Update Status**:
   - **"Verify & Mark Paid"**: If confirmed
   - **"Return to Pending"**: If needs clarification
   - **"Reject"**: If incorrect (add reason)

### **Remittance Reports**
1. Click **"Remittances"** → **"Reports"**
2. **Generate reports** showing:
   - **All branches** remittance history
   - **Late payments** list
   - **Payment patterns** analysis
   - **Outstanding amounts**

### **Handling Issues**
#### **Missing Remittances**
- Branches appear in **"Overdue"** list
- Dashboard shows alerts
- Send reminders through system

#### **Payment Discrepancies**
- If amount doesn't match expected calculation
- Contact branch for clarification
- Record adjustment with proper audit trail

---

## **Payroll Management**

### **Who Gets Payroll?**
- **Mission Staff**: National office employees
- **Area/District Staff**: Regional officers (if applicable)
- **Pastors**: Through commission system (separate from payroll)

### **Setting Up Payroll**
1. Click **"Payroll"** → **"Staff Management"**
2. **Add staff members**:
   - Select existing user or create new
   - **Job Title**: Position/Role
   - **Salary Amount**: Monthly base salary
   - **Allowances**: Housing, transport, etc.
   - **Deductions**: Taxes, insurance, etc.
   - **Bank Details**: For payment
   - **Start Date**: When employment began

### **Monthly Payroll Processing**
1. Click **"Payroll"** → **"Generate Monthly Payroll"**
2. **Select month and year**
3. **Review calculations**:
   - Base salary
   - Allowances
   - Deductions
   - Net pay
4. **Approve payroll**
5. **Generate pay slips** (PDF for staff)
6. **Mark as paid** after processing

### **Payroll Reports**
1. Click **"Payroll"** → **"Reports"**
2. **Available reports**:
   - **Monthly payroll summary**
   - **Year-to-date totals**
   - **Staff cost analysis**
   - **Tax reports** (if applicable)

---

## **User Management**

### **User Roles Overview**
| Role | Access Level | Primary Function |
|------|-------------|------------------|
| Mission Admin | Full system | National oversight |
| Area Executive | Area-wide | District oversight |
| District Executive | District-wide | Branch oversight |
| Branch Executive | Branch-level | Local management |
| Auditor | Read-only | Financial oversight |
| Pastor | Limited | Spiritual leadership |
| Staff | Limited | Specific duties |
| Member | Personal | Personal data only |

### **Creating New Users**
1. Click **"User Management"** → **"Add User"**
2. **Personal Information**:
   - **First Name**, **Last Name**, **Other Names**
   - **Member ID**: Unique ID (system can generate)
   - **Email**, **Phone**
   - **Date of Birth**, **Gender**
   - **Profile Picture** (optional)

3. **Role Assignment**:
   - **Select Role**: Choose appropriate role
   - **Pastoral Rank** (if pastor): Associate, Branch, District, etc.
   - **Branch Assignment**: Which branch they belong to

4. **Administrative Assignment** (if applicable):
   - **Managed Area** (for Area Executives)
   - **Managed District** (for District Executives)
   - **Branch Admin** (for Branch Executives)

5. **Login Credentials**:
   - **Default Password**: `12345` (auto-set)
   - **PIN**: 5-digit PIN (default: `12345`)
   - **User must change password** on first login

6. **Salary Information** (if staff/pastor):
   - **Qualifies for Salary**: Yes/No
   - **Base Salary**: Monthly amount

7. Click **"Create User"**

### **Managing Existing Users**
1. Click **"User Management"** → **"Users"**
2. **Find user** using search or filters
3. **Actions available**:
   - **Edit**: Update information
   - **Reset Password**: Set back to `12345`
   - **Reset PIN**: Set back to `12345`
   - **Deactivate**: Temporarily disable
   - **Delete**: Remove permanently (with confirmation)

### **Bulk User Operations**
#### **Importing Members**
1. Click **"User Management"** → **"Import Members"**
2. **Download template** CSV file
3. **Fill template** with member data
4. **Upload completed file**
5. **Review import results**:
   - Successfully imported
   - Errors with reasons
   - Duplicate entries

#### **Password Reset for Multiple Users**
1. Select multiple users
2. Click **"Bulk Actions"** → **"Reset Passwords"**
3. Confirm action

---

## **Audit & Reports**

### **Audit Trail Access**
1. Click **"Auditing"** → **"Audit Logs"**
2. **See all system changes**:
   - **Who made the change**
   - **What was changed**
   - **When it was changed**
   - **Before/after values**
3. **Filter by**:
   - User
   - Date range
   - Action type
   - Module

### **Generating Reports**
1. Click **"Reports"** → **"Generate Reports"**
2. **Report Categories**:

#### **Financial Reports**
- **Contribution Reports**: By type, branch, period
- **Expenditure Reports**: By category, branch, period
- **Remittance Reports**: Branch payment history
- **Commission Reports**: Pastor commission tracking
- **Balance Sheets**: Financial position

#### **Membership Reports**
- **Member Statistics**: Growth, demographics
- **Attendance Reports**: Service attendance patterns
- **Group Reports**: Ministry group participation

#### **Operational Reports**
- **Branch Performance**: Comparative analysis
- **Activity Reports**: System usage statistics
- **Compliance Reports**: Rule adherence

### **Custom Report Builder**
1. Click **"Reports"** → **"Custom Builder"**
2. **Select data sources**
3. **Set filters and parameters**
4. **Choose output format** (PDF, Excel, CSV)
5. **Save report template** for future use

---

## **Announcements & Communication**

### **Creating Announcements**
1. Click **"Announcements"** → **"Create Announcement"**
2. **Announcement Details**:
   - **Title**: Clear, descriptive title
   - **Message**: Full announcement text
   - **Priority**: Normal, Important, Urgent
   - **Visibility Level**:
     - Mission (everyone sees)
     - Area (specific area only)
     - District (specific district only)
     - Branch (specific branch only)

3. **Scheduling**:
   - **Publish Immediately**: Show right away
   - **Schedule for Later**: Set date/time to publish
   - **Expiry Date**: When to remove automatically

4. **Attachments** (optional):
   - PDF documents
   - Images
   - Videos (links)

5. Click **"Publish Announcement"**

### **Managing Announcements**
1. Click **"Announcements"** → **"Manage"**
2. **See all announcements** with:
   - **Status**: Published, Scheduled, Draft, Expired
   - **Visibility**: Who can see it
   - **Engagement**: Views, clicks
   - **Actions**: Edit, unpublish, delete

### **Communication Features**
#### **Targeted Messaging**
- Send to specific roles (all pastors, all branch executives)
- Send to specific branches/areas/districts
- Send to individual members

#### **Push Notifications** (Future Feature)
- Mobile app notifications
- Email notifications
- SMS notifications

---

## **Monthly Closing Process**

### **What is Monthly Closing?**
Monthly closing freezes the financial data for a month and:
- Locks contribution entries
- Calculates commission eligibility
- Generates monthly reports
- Triggers remittance requirements

### **Monthly Closing Steps**
1. **Pre-Closing Checklist**:
   - All contributions entered?
   - All expenditures recorded?
   - Branch remittances up to date?
   - Any corrections needed?

2. **Initiate Closing**:
   - Click **"Financial"** → **"Monthly Closing"**
   - Select month to close
   - Review summary data
   - Click **"Initiate Closing"**

3. **System Processes**:
   - Calculates monthly totals
   - Determines commission eligibility
   - Generates branch reports
   - Creates audit entries

4. **Post-Closing Actions**:
   - Review commission calculations
   - Approve/deny commissions
   - Verify remittance requirements
   - Publish monthly reports

### **Commission Management**
1. Click **"Contributions"** → **"Commission Management"**
2. **Review eligible branches**:
   - **Target vs Actual**: Tithe collection
   - **Achievement %**: Percentage of target met
   - **Commission Amount**: Calculated commission
   - **Pastor Details**: Payment information

3. **Process Commissions**:
   - **Approve**: Mark as approved for payment
   - **Pay**: Record payment details
   - **Reject**: Decline with reason

---

## **Year-End Procedures**

### **Year-End Rollover**
At the end of each fiscal year:
1. **Backup Current Data**
   - Generate annual reports
   - Export all financial data
   - Backup member data

2. **Initiate Rollover**:
   - Click **"System"** → **"Year-End Rollover"**
   - Confirm fiscal year end
   - System archives current year data
   - New fiscal year begins

3. **Post-Rollover**:
   - Set new targets
   - Update contribution types
   - Review and adjust settings
   - Communicate changes to users

### **Annual Report Generation**
1. Click **"Reports"** → **"Annual Report"**
2. **Select fiscal year**
3. **Choose report sections**:
   - Financial summary
   - Membership statistics
   - Branch performance
   - Commission summary
   - Recommendations

4. **Generate and publish**:
   - Create PDF report
   - Make available to members
   - Present to leadership

---

## **Troubleshooting & Support**

### **Common Issues & Solutions**

#### **Login Problems**
**Issue**: Cannot login
- **Check**: Correct Member ID and password
- **Solution**: Reset password to `12345`

**Issue**: Account locked
- **Cause**: Too many failed attempts
- **Solution**: Wait 30 minutes or contact admin

#### **Financial Issues**
**Issue**: Contribution totals don't match
- **Check**: Date range filters
- **Check**: Include/exclude closed types
- **Solution**: Run audit report to find discrepancies

**Issue**: Remittance calculation wrong
- **Check**: Contribution type split percentages
- **Check**: Date range for calculation
- **Solution**: Verify contribution entries for period

#### **User Management Issues**
**Issue**: User cannot see expected data
- **Check**: User role assignment
- **Check**: Branch/area/district assignment
- **Solution**: Update user role and assignments

**Issue**: Pastor cannot see commission
- **Check**: Commission eligibility settings
- **Check**: If pastor is marked as recipient
- **Solution**: Update commission settings

### **System Maintenance**
#### **Regular Tasks**
- **Weekly**: Review pending remittances
- **Monthly**: Process monthly closing
- **Quarterly**: Generate financial reports
- **Annually**: Year-end rollover

#### **Data Backup**
- **Daily**: Automatic database backup
- **Weekly**: Export financial data
- **Monthly**: Create system state backup

### **Getting Help**
#### **Internal Support**
- **System Documentation**: This guide
- **Audit Logs**: Track system issues
- **User Activity**: Monitor usage patterns

#### **Technical Support**
- **Error Messages**: Note exact wording
- **Steps Taken**: What you did before error
- **Browser Info**: Chrome, Firefox, Safari version
- **Screenshot**: Visual of error if possible

---

## **Quick Reference Cards**

### **Mission Admin Quick Actions**
| Task | Navigation | Frequency |
|------|------------|-----------|
| Check Dashboard | Dashboard | Daily |
| Review Remittances | Remittances → Pending | Daily |
| Process Commissions | Contributions → Commission | Monthly |
| Monthly Closing | Financial → Monthly Closing | Monthly |
| User Management | User Management → Users | As needed |
| Generate Reports | Reports → Generate | As needed |
| System Settings | System Settings | Quarterly |

### **Important Deadlines**
- **Monthly**: 5th of each month - Previous month closing due
- **Quarterly**: 15th following quarter end - Quarterly reports
- **Annually**: 31st January - Previous year rollover complete

### **Contact Information**
- **System Administrator**: [Your IT Contact]
- **Financial Auditor**: [Auditor Contact]
- **Technical Support**: [Support Email/Phone]

---

## **Conclusion**

As Mission Admin, you are the **guardian of the system's integrity and functionality**. Your role ensures that:

1. **Financial accountability** is maintained across all levels
2. **System operations** run smoothly and efficiently
3. **User access** is properly managed and secure
4. **Reporting** provides accurate insights for decision-making
5. **Compliance** with church governance requirements

Regular use of this guide will help you master the system and serve your church organization effectively. Remember that the system is designed to **support transparency, accountability, and efficient church management**.

For additional training or specific questions, refer to the system's built-in help documentation or contact your technical support team.

---

**Last Updated**: [Current Date]
**Version**: 1.0
**System**: SDSCC Church Management System
