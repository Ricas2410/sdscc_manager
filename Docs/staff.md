# ## **19. Administrative Roles (Branch, District, Area, Auditor/Board)**

This section outlines the combined responsibilities and permissions of all remaining administrative roles **below Mission Admin** but **above Pastors and Members**.

It includes:

* Branch Executives
* District Executives
* Area Executives
* Auditors / Board of Trustees

Each role inherits permissions based on church hierarchy but with strict boundaries and financial controls.

---

# ## **19.1 Hierarchical Permission Model**

| Role                             | Scope Coverage                                 | Can Edit Financials?  | Can View Lower Levels? |
| -------------------------------- | ---------------------------------------------- | --------------------- | ---------------------- |
| **Area Executive**               | Area → Districts → Branches                    | Yes (within Area)     | Yes                    |
| **District Executive**           | District → Branches                            | Yes (within District) | Yes                    |
| **Branch Executive**             | Branch only                                    | Yes (branch only)     | No                     |
| **Auditors / Board of Trustees** | Whole Mission (read-only except audit actions) | No                    | Yes                    |

Executives manage finances **only at their assigned level**, with visibility into lower levels but not higher levels.

---

# ## **19.2 Branch Executive (Local Administrator)**

Branch Executives are the **primary operational admins** of the church.
They handle all **member management, contributions, expenditures, attendance, utilities, welfare, and reporting** for their local branch.

### **19.2.1 Branch Executive Permissions**

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
| Reports                   | Full report generation                       |
| Payroll                   | No access                                    |
| Audit Logs                | Own branch only                              |
| System Settings           | No access                                    |

---

### **19.2.2 Branch Executive Dashboard**

Includes:

* Weekly general contribution totals
* Individual contributions overview
* Tithe target progress (branch-level)
* Remaining local funds
* Monthly expenditures chart
* Pending remittances
* Upcoming events & announcements
* Attendance analytics

---

### **19.2.3 Branch-Level Financial Workflows**

#### **A. Contribution Recording**

Executives can:

* Enter weekly general contributions
* Enter individual contributions using simplified **multi-column grid**
* Upload receipts or images
* Edit with reason (audit logged)
* Close contribution types (for pledges, temporary types)

#### **B. Expenditure & Welfare**

Executives can:

* Add local expenses
* Upload receipts
* Categorize by:

  * Maintenance
  * Utility bills
  * Welfare (school fees, hospital bills, travel support, emergencies)
* Deduct from **branch local funds only**
* Cannot touch mission funds

#### **C. Remittances**

Executives record:

* Amount “Sent to Mission”
* Payment channel
* Remittance reference
* Mission Admin later marks **Verified / Paid**

---

### **19.2.4 Branch Reports**

Executives can generate:

* Weekly contribution report
* Monthly financial summary
* Local expenditure report
* Individual contribution statements
* Tithe target report
* Remittance summary
* Group/Department reports
* Attendance reports

---

# ## **19.3 District Executive**

District Executives supervise multiple branches under their district.

### **19.3.1 Permissions**

| Module                 | Permission                          |
| ---------------------- | ----------------------------------- |
| Branch Finances        | View only                           |
| District Contributions | Full                                |
| District Expenditures  | Full                                |
| Branch Expenditures    | View only                           |
| District Announcements | Create                              |
| Reports                | District-level only                 |
| Member Records         | Read-only                           |
| Attendance             | View only                           |
| Contribution Types     | Create district-level (optional)    |
| Remittances            | View district branches’ remittances |
| Payroll                | No access                           |
| Audit Logs             | No access                           |

---

### **19.3.2 District Executive Dashboard**

Displays:

* All branch performance under district
* Total district income
* District expenditures
* District-level contributions
* Weekly and monthly summaries
* Leaderboard of branches (top performers)
* Pending remittances from branches

---

### **19.3.3 District Reports**

Executives can generate:

* District-wide contribution summary
* Branch comparison chart
* District expenditure report
* District remittance summary
* Growth and attendance trends

---

# ## **19.4 Area Executive**

Area Executives manage the districts and branches under their entire area.

### **19.4.1 Permissions**

| Module             | Permission                           |
| ------------------ | ------------------------------------ |
| Area Contributions | Full                                 |
| Area Expenditures  | Full                                 |
| District Finances  | View only                            |
| Branch Finances    | View only                            |
| Area Announcements | Create                               |
| Reports            | Area-level only                      |
| Contribution Types | Create area-level types              |
| Remittance         | View all district/branch remittances |
| Member Records     | Read-only                            |
| Payroll            | No access                            |
| Audit Logs         | No access                            |

---

### **19.4.2 Area Dashboard**

Displays:

* Total area income
* Area-level expenditures
* District contribution summaries
* Branch performance under districts
* Area vs previous month comparison
* Support tracking (e.g. welfare, maintenance)
* Area-level events & announcements

---

### **19.4.3 Area Reports**

* Area contribution summary
* District comparison analytics
* Expenditure summary
* Area-wide financial breakdown
* Remittance overview by district

---

# ## **19.5 National Auditor / Board of Trustees Role**

The Auditor and Board roles focus entirely on **monitoring**, **verifying**, and **publishing official audit reports**.

### **19.5.1 Auditor Permissions**

| Module                                    | Permission                     |
| ----------------------------------------- | ------------------------------ |
| All Branch/Area/District Finances         | View only                      |
| Remittance Tracking                       | View only                      |
| Expenditure Reports                       | View only                      |
| Contribution Reports                      | View only                      |
| Detailed Financial Logs                   | Full view                      |
| Audit Logs                                | Full view                      |
| Publish Annual Audit Report               | Full                           |
| Approve/Reject Branch or District Reports | Full                           |
| Announcements                             | No access                      |
| Settings                                  | No access                      |
| Payroll                                   | View only (for national staff) |

---

### **19.5.2 Auditor Dashboard**

Contains:

* Full mission income overview
* Yearly trends
* Expenditure audit matrix
* Branch/district/area ranking
* Pending verifications
* Report approval queue

---

### **19.5.3 Annual Audit Publishing Workflow**

1. Auditor reviews all branch, district, area income & expenditure
2. Auditor generates national report
3. Auditor selects what to publish to:

   * Branch executives
   * Members
   * Only mission admin
4. Auditor signs (digital signature)
5. Auditor publishes final report

Members see *only* what auditor decides to reveal.

---

# ## **19.6 Combined Feature Table for All Admin Roles**

| Feature                  | Branch Exec   | District Exec     | Area Exec     | Auditor   |
| ------------------------ | ------------- | ----------------- | ------------- | --------- |
| Manage Members           | Yes           | No                | No            | No        |
| Add Contributions        | Yes           | District only     | Area only     | No        |
| Individual Contributions | Yes           | No                | No            | No        |
| General Contributions    | Yes           | District (if any) | Area (if any) | No        |
| Expenditures             | Branch only   | District only     | Area only     | No        |
| Remittance Entry         | Create (Sent) | View              | View          | View      |
| Remittance Verification  | No            | No                | No            | No        |
| Create Announcements     | Branch        | District          | Area          | No        |
| Sermons                  | Optional      | No                | No            | No        |
| Attendance               | Add/Edit      | View only         | View only     | View only |
| Payroll                  | No            | No                | No            | View only |
| Audit Logs               | Own branch    | No                | No            | Full      |

---

# ## **19.7 Summary (Copy/Paste Block)**

```
Branch Executives manage all local church operations including member records, contributions, expenditures, welfare, and announcements. District and Area Executives oversee their respective lower levels with limited financial editing restricted to their scope. The Board of Trustees and Auditors have system-wide read-only access with the ability to verify reports and publish annual audits. Each role functions within strict hierarchical boundaries to ensure security, transparency, and proper accountability across the entire church system.
```
