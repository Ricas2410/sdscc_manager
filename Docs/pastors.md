

# ## **16. Pastor Role – Access, Permissions & Functionalities (Updated Final Version)**

Pastors are **not normal church members**. They are **spiritual leaders** and **staff-level users**, and may optionally serve as **administrators** when assigned as branch, district, or area admins.

The system must dynamically adjust **sidebar**, **permissions**, and **dashboard features** based on their pastoral rank and administrative assignment.

---

# ### **16.1 Pastor Account Rules**

### **Login Credentials**

Pastors log in using:

* **Member ID + PIN**
* **Default password:** `12345`

### **Password Reset**

* Reset same way as members
* Pastor can change password from Profile
* PIN remains separate for verification

### **Account Creation Requirements**

When creating a pastor account:

* Assign rank (Branch/District/Area/Mission)
* Assign default password (auto: 12345)
* Assign pastoral title
* Contribution fields NOT required

---

# ### **16.2 Pastor Access Modes**

Pastors operate in **two modes**, depending on administrative assignment:

---

## **Mode A: Default Pastor (Pastor-as-Staff)**

Pastor is *not* a branch/district/area admin.

**Pastor CAN:**

* View all financial data **read-only**
* Manage attendance
* Manage pastoral notes & member updates
* Create announcements/events (by pastoral rank)
* Access commission & payroll
* Access member directory
* View aggregated reports

**Pastor CANNOT:**

* Enter contributions
* Enter expenditures
* Configure contribution types
* Approve remittances
* Manage payroll
* Change financial records
* Access audit logs
* Access mission-wide restricted data

This is the **default and safest mode**.

---

## **Mode B: Pastor is Also Administrator**

If pastor is assigned as:

* **Branch Admin**
* **District Admin**
* **Area Admin**

they inherit all admin features of that level:

✔ enter contributions
✔ enter expenditures
✔ configure local contribution types
✔ manage local reports
✔ manage branch utilities/welfare

This is **optional** and controlled by the mission.

---

# ### **16.3 Pastor Sidebar (Dynamic)**

### **A. Default Pastor Sidebar (Staff Mode)**

```
Dashboard
My Profile
Member Directory
Announcements (by role level)
Events (by role level)
My Commission (if eligible)
My Payroll (mission level)
Attendance (Add/Edit/View)
Reports (View-only)
```

---

### **B. If Pastor is Branch Admin**

```
Dashboard
Member Directory
Contributions (General + Individual)
Expenditures
Utilities & Welfare
Inventory
Branch Reports
Announcements
Events
My Commission
My Payroll
Remittances (View-only)
Branch Settings (optional)
```

---

### **C. If Pastor is District/Area Pastor**

```
Dashboard (District/Area Overview)
All Branch Reports
All Branch Contributions (View-only)
All Expenditures (View-only)
Announcements (District/Area)
Events (District/Area)
Member Directory (District/Area)
My Commission
My Payroll
```

---

# ### **16.4 Pastor Dashboard**

The dashboard varies by role but includes:

### **Financial Overview (Read-only)**

* Weekly general contributions
* Individual contribution totals
* Monthly total collections
* Tithe target progress bar
* Comparison to previous month

### **Expenditure Overview (Read-only)**

* Monthly expenses by category
* Remaining local branch balance

### **Attendance Overview**

* Weekly + monthly attendance trends
* Service counts
* Missing or low-attendance alerts

### **Pastoral Metrics**

* New members this month
* Member activity
* Pastoral care notes
* Upcoming assignments
* Events & announcements

### **Pastor Commission Summary**

* Target achieved
* Commission amount
* Paid / Pending
* Month-by-month history

---

# ### **16.5 Member Management (Pastoral Functions)**

Pastors work heavily with members.

### **Pastors CAN:**

* View member profiles
* Search by ID / phone / name
* Filter by department or group
* Edit non-financial details:

  * Phone
  * Address
  * Active/Inactive
  * Pastoral notes
  * Counseling status
* View contribution history (read-only)

### **Pastors CANNOT:**

* Edit any financial record
* Change contribution history
* Enter contributions
* Delete members
* Change member IDs

---

# ### **16.6 Attendance Management**

Pastors manage:

* Sunday service
* Mid-week service
* Group meetings
* Special programs

### **Permissions**

* Add attendance
* Edit attendance
* View history
* Download attendance reports

---

# ### **16.7 Announcements & Events (Role-Based)**

### **Branch Pastor**

* Can create branch-level announcements/events

### **District Pastor**

* Can create district-wide announcements/events

### **Area Pastor**

* Can create area-wide announcements/events

### **Mission Pastor**

* Can create mission-wide announcements/events

### **Site Setting**

```
Allow Pastors to Create Announcements: ON/OFF
Allow Pastors to Create Events: ON/OFF
```

---

# ### **16.8 Pastor Tithe Commission Module**

Pastors have a dedicated sidebar module:

```
My Commission
```

### **Pastor Can View:**

* Monthly branch tithe target
* Tithe collected
* Qualification status
* Commission earned
* Commission paid/pending
* Full history

### **Pastor Cannot:**

* Modify target
* Modify tithe entries
* Change commission rules
* Select recipients

---

# ### **16.9 Pastor Payroll (Mission-Level)**

If the pastor is on mission payroll, they see:

* Salary
* Allowances
* Payment slips
* Paid/Pending status
* Full history

Branch pastors without payroll see nothing here.

---

# ### **16.10 Contribution Visibility & Rules**

Pastors **should NOT** see contribution entry tools unless they are admins.

### **Contribution Visibility Setting**

```
Show Pastor Contribution Panel: ON/OFF
Default: OFF
```

This prevents pastors from appearing “inactive.”

---

# ### **16.11 Summary (Copy/Paste)**

```
Pastors are privileged staff users with strong visibility into members, attendance, branch performance, and commission data, while maintaining strict read-only access to financial modules. Their permissions dynamically expand only when assigned as branch/district/area administrators. Pastors manage announcements, events, pastoral notes, and attendance, but never alter financial records unless explicitly granted administrative authority. Password handling matches members, with a default of 12345 and full reset support.
```

