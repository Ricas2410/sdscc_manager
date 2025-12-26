

# ## **17. Mission Admin / System Admin – Full Role Specification**

The **Mission Admin** (also referred to as **System Administrator**, **National Admin**, or **HQ Admin**) is the **highest authority** in the SDSCC management system.

They have **unrestricted, system-wide access** across all modules including contributions, expenditures, remittances, payroll, branch setup, auditing, announcements, settings, and user management.

Mission Admins ensure **financial accountability**, **system configuration**, **pastoral oversight**, and **church-wide operations** run seamlessly.

This role includes **both technical system administration and executive mission leadership controls**.

---

# ### **17.1 Mission Admin Access Summary**

Mission Admins have full **READ + WRITE + CONFIGURATION** access across all features.

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

---

# ### **17.2 Mission Admin Dashboard**

Mission Admin sees the **full national overview**, including:

### **1. Financial Summary**

* Total Mission Income
* Total Branch Income (aggregate)
* Graph of General Contributions
* Graph of Individual Contributions
* Tithe Target Progress for every branch
* Mission-wide monthly comparison

### **2. Remittance Summary**

* Paid / Pending / Overdue remittances
* Verification queue
* Breakdown by Area → District → Branch

### **3. Expenditure Summary**

* Mission expenditures by category
* Total expenses from every branch
* Net balance after allocations and payroll

### **4. Staff & Pastor Summary**

* Total mission payroll
* Pastors with commission eligibility
* Commission payout status

### **5. Alerts**

* Missing reports
* Late tithe submissions
* Overspending warnings
* Abnormal contribution detection
* Branches below target

---

# ### **17.3 System-Wide Contribution Management**

Mission Admin controls the **entire financial configuration**.

### **Mission Admin Can:**

* Create mission-wide contribution types
* Create Area/District/Branch contribution types if needed
* Close contribution types (temporary projects, pledges)
* Edit split rules:

  * Mission %
  * Area %
  * District %
  * Branch %
* Define whether a contribution is:

  * General or Individual
  * Closeable
  * Monthly/Weekly/One-time
* View all contributions from all branches
* Edit or correct entries (with audit trail)
* Delete (with justification prompt)
* Enable/disable pastors being shown contribution tabs
* Freeze monthly tithe calculations
* Set rules for late entries and commission eligibility

This connects directly to the **monthly closing system**.

---

# ### **17.4 Monthly Closing & Tithe Commission Cycle**

Mission Admin manages the full monthly tithe cycle:

### **Steps:**

1. System aggregates **monthly tithe totals** per branch
2. System checks target achievement
3. Mission Admin reviews results
4. Mission Admin freezes month
5. Late entries get flagged
6. Commission calculation runs
7. Mission Admin approves/declines commission payments

### **Commission Configuration:**

* Set commission percentage
* Choose eligible pastors/staff
* Override eligibility
* Approve payouts
* Mark as paid

Mission Admin sees detailed branch-by-branch stat breakdown.

---

# ### **17.5 Remittance Management (Branch → Mission)**

Mission Admin handles **all remittance verifications**.

### **Branch Workflow:**

1. Branch Admin selects month
2. Records amount sent, attachment, reference number
3. Marks status: **Sent**

### **Mission Admin Workflow:**

1. Views all branches’ monthly remittances
2. Opens remittance record
3. Reviews payment evidence
4. Marks status:

   * **Verified (Paid)**
   * **Pending**

This creates **unbreakable audit traceability.**

---

# ### **17.6 Expenditures (Mission-Level & Branch-Level Oversight)**

Mission Admin has control over ALL expenditures.

### **Mission Admin Can:**

* Add mission expenditures
* Approve/review branch expenditures
* Upload receipts
* Categorize expenditure types
* Review utilities (electricity, water, rent)
* Add welfare payments
* Deduct expenditures automatically from balances

Includes both **mission funds** and **branch local funds**.

---

# ### **17.7 Payroll (Mission Staff Only)**

Since branches currently *do not* have payroll, Mission Admin manages **national payroll**:

### **Payroll Features:**

* Add mission staff
* Assign salaries
* Add allowances & deductions
* Generate monthly pay slips
* Track staff loans/advances
* Export payroll statements
* Approve payments

Pastors are managed separately via tithe commission system.

---

# ### **17.8 Announcements (Hierarchical Messaging)**

Mission Admin can create announcements visible to:

* Entire Mission
* All Areas
* All Districts
* All Branches
* All Members

Supports:

* Title
* Message Body
* Optional attachments
* Scheduled publishing
* Push/email integration (future)

This is the top-most broadcast authority.

---

# ### **17.9 Hierarchy / Structure Management**

Mission Admin manages the entire church structure:

### **Can:**

* Create Areas
* Create Districts
* Create Branches
* Assign:

  * Area Executives
  * District Executives
  * Branch Executives
  * Pastors
* Approve transfers
* Deactivate inactive branches
* Merge or split districts/areas

This ensures correct relationship structure:

Mission → Area → District → Branch → Members

---

# ### **17.10 User & Account Management**

Mission Admin controls all users in the system.

### **Mission Admin Can:**

* Create any user type
* Assign multiple roles
* Reset PINs & Passwords
* Disable accounts
* Switch roles for pastors, staff, admins
* Set default password (e.g., 12345)
* Manage security flags

Includes **pastors, branch executives, district executives, area executives, auditors, staff, and members**.

---

# ### **17.11 Sermon Platform Oversight**

Mission Admin can:

* View all sermons uploaded by pastors
* Approve or hide sermons
* Delete inappropriate content
* Upload national sermons

---

# ### **17.12 Inventory & Asset Management**

Mission Admin handles both mission and aggregated branch inventories.

### Features:

* Add inventory items
* Assign to branches
* Mark damaged items
* Track quantity & depreciation
* Approve branch requests
* Download inventory reports

---

# ### **17.13 Attendance Management (Viewing Rights)**

Mission Admin sees all attendance records:

* Sunday Services
* Mid-Week
* Ministries (Youth, Women, Men, Choir)
* Special Events

Edit ability can be optionally enabled.

---

# ### **17.14 Auditing System (Full Control)**

Mission Admin has full auditing capabilities:

### **Can:**

* View ALL audit logs
* Generate yearly financial reports
* Export financial statements
* Identify inconsistencies
* Compare branch performance
* Approve/dismiss auditor reports
* Control what the public or members see

---

# ### **17.15 Year-End Rollover**

Mission Admin initiates the yearly rollover:

* Moves all contributions to “Previous Year”
* Locks previous year records
* Generates annual summary
* Resets all targets for the new year
* Publishes the official annual report

---

# ### **17.16 System Configuration**

Mission Admin controls:

* Church branding (logo, name)
* PWA settings (manifest/service worker)
* Global settings
* Default member PIN
* Pastor contribution visibility toggle
* Security settings
* Data backup/export (optional)

---

# ### **17.17 Groups / Departments Management**

Mission Admin can manage:

* Ministries (Choir, Youth, Men, Women, Children)
* Committees
* Workers groups
* Assign members to groups

Supports:

* Optional assignment
* Multi-group membership

---

# ### **17.18 Member Registration Enhancement Controls**

Mission Admin configures:

* Profile picture capture (optional)
* Emergency contact fields
* Mandatory vs optional registration fields
* Custom fields for branches

---

# ### **17.19 Mission Admin Summary (Copy/Paste Block)**

```
The Mission Admin is the supreme administrator of the SDSCC system with complete access to all church levels, all financial modules, all configuration settings, all users, all auditing features, all contribution controls, expenditure systems, payroll, announcements, hierarchical management, and monthly/annual financial cycles. This role ensures total operational oversight, financial accountability, and structural integrity across the entire Mission, Areas, Districts, Branches, and Members.
```
