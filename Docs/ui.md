

# **SDSCC Admin UI Flow – Split by User Type**

---

## **1. Branch Admins / Executives**

**Primary Responsibilities**: Manage local branch members, contributions, attendance, expenditures, groups, and limited pastor oversight (if assigned branch-level roles).

### **1.1 Sidebar Modules**

```
Dashboard
├─ Members
│  ├─ Add Member
│  ├─ Member List
│  └─ Attendance
│      ├─ Sabbath Worship
│      ├─ Mid-week Service
│      └─ Special Programs
├─ Pastors (if branch-admin role)
│  ├─ Pastor List
│  └─ Assign Branch Role
├─ Contributions
│  ├─ Add Contribution
│  └─ Contribution History
├─ Expenditures
│  ├─ Add Expenditure
│  └─ Expenditure History
├─ Reports
│  ├─ Branch Financial Summary
│  ├─ Attendance Reports
│  └─ Contributions Reports
├─ Groups
│  ├─ Add Group
│  └─ Assign Members
├─ Announcements (Branch only)
├─ Sermons (view only)
├─ Profile / Settings
└─ Logout
```

### **1.2 Key UI Features**

* **Hierarchical Dropdowns** for members/pastors:

  * Branch → Member/Pastor
  * Search-as-you-type
* **Attendance UI**

  * Sabbath Worship (primary)
  * Bulk marking for efficiency
* **Contribution UI**

  * Add contributions locally
  * Percentage allocation to Mission/Branch
* **Expenditures**

  * Add local branch expenses with receipts
* **Reports**

  * Branch-only reports
  * Export to Excel/PDF
* **Groups**

  * Branch-level groups
  * Assign members for ministry/workflow

---

## **2. Auditors / Board of Trustees**

**Primary Responsibilities**: Audit contributions, expenditures, attendance, payroll, and generate reports across branches, districts, and areas.

### **2.1 Sidebar Modules**

```
Dashboard
├─ Reports
│  ├─ Branch / District / Area Financial Reports
│  ├─ Attendance Reports
│  ├─ Contribution Summary
│  └─ Audit Summaries
├─ Auditing
│  ├─ Pending Approvals
│  └─ Audit Logs
├─ Members (view-only)
├─ Pastors (view-only)
├─ Groups (view-only)
├─ Notifications
├─ Profile / Settings
└─ Logout
```

### **2.2 Key UI Features**

* **Reports**

  * Filter by Mission → Area → District → Branch
  * Compare contributions, expenditures, attendance
  * Exportable PDFs/Excel
* **Auditing**

  * Approve/Disapprove contributions & expenditures
  * Track audit history per branch
* **Member / Pastor Lookup**

  * Read-only view
  * Search by name, phone, or ID
* **Group Overview**

  * View group assignments
  * Ensure proper allocation and compliance
* **Dashboard**

  * Key KPIs for top/bottom performing branches
  * Pending audit notifications

---

## **3. Mission / General Admins**

**Primary Responsibilities**: System-wide management including all branches, districts, areas, pastors, contributions, payroll, auditing, groups, and configurations.

### **3.1 Sidebar Modules**

```
Dashboard
├─ Members
│  ├─ Add Member (Mission-wide)
│  ├─ Member List
│  └─ Attendance
│      ├─ Sabbath Worship
│      ├─ Mid-week Service
│      └─ Special Programs
├─ Pastors
│  ├─ Add Pastor
│  ├─ Pastor List
│  └─ Assign Roles / Branch / District / Area
├─ Contributions
│  ├─ Add Contribution
│  ├─ Contribution History
│  └─ Allocation Settings
├─ Expenditures
│  ├─ Add Expenditure
│  └─ Expenditure History
├─ Payroll
│  ├─ Staff Payroll
│  ├─ Salary Structures
│  └─ Payslip Generation
├─ Reports
│  ├─ Mission-wide Reports
│  ├─ Area/District/Branch Reports
│  ├─ Attendance Reports
│  └─ Contribution & Expenditure Summaries
├─ Auditing
│  ├─ Pending Approvals
│  └─ Audit Logs
├─ Groups
│  ├─ Add Group (National/Mission)
│  └─ Assign Members / Branches
├─ Announcements
├─ Sermons
├─ Utilities / Assets / Inventory
├─ System Configuration
│  ├─ Roles & Permissions
│  ├─ Branding & Settings
│  └─ Security Controls
├─ Notifications
├─ Profile / Settings
└─ Logout
```

### **3.2 Key UI Features**

* **Hierarchical Member / Pastor Selection**

  * Mission → Area → District → Branch → Members / Pastors
  * Search-as-you-type
  * Multi-select for bulk actions
* **Contribution Management**

  * Add Mission-wide contributions
  * Allocate percentages to all hierarchy levels
* **Expenditure & Payroll**

  * Mission-level payroll and staff payments
  * Expenditure approvals and global visibility
* **Reports & Dashboards**

  * Mission-wide financial overview
  * Attendance summary across all branches
  * KPI charts & quick filters by hierarchy
* **Groups Management**

  * Create National-level groups
  * Assign members/pastors across branches
* **Pastor Management**

  * Assign roles at branch, district, area
  * Track commission eligibility
* **System Configuration**

  * Manage RBAC, PIN policies, branding
  * Security and audit logging

---

### **4. Cross-Cutting Features**

| Feature            | Branch Admin              | Auditor/Board | Mission Admin      |
| ------------------ | ------------------------- | ------------- | ------------------ |
| Sabbath Attendance | ✔ Add/Edit                | ✔ View Only   | ✔ Add/Edit         |
| Member Search      | ✔ ✔                       | ✔ View        | ✔ Full             |
| Pastor Management  | Conditional (branch role) | View Only     | Full               |
| Contributions      | ✔ Branch                  | View Only     | ✔ Full             |
| Expenditures       | ✔ Branch                  | View Only     | ✔ Full             |
| Payroll            | ❌                         | ❌             | ✔ Full             |
| Reports            | ✔ Branch                  | ✔ Multi-level | ✔ Mission-wide     |
| Groups             | ✔ Branch                  | View Only     | ✔ Mission/National |
| Bulk Actions       | ✔                         | ❌             | ✔                  |

---

This split ensures **clear responsibilities**, **role-specific dashboards**, **efficient hierarchical navigation**, and **ease of managing pastors, members, contributions, and attendance at scale**.
