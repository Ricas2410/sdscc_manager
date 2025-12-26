
# 📦 **15. Financial Management Extensions (Expenditures, Utilities, Welfare & Mission Payroll)**

This section adds the required financial management features to support both **branch-level** and **mission-level** accounting.
It integrates with contributions, reporting, remittance, and auditing already defined.

---

## **15.1 Branch-Level Expenditures**

Branches do **not** have payroll but they have regular and occasional expenses.
These expenses must deduct from **branch local funds only**, never from mission funds.

### **15.1.1 Types of Branch Expenditures**

Branches can record three major expenditure categories:

### **A. Operations / Projects**

Examples:

* Building materials
* Repairs and maintenance
* Cleaning and sanitation
* Branch events
* Instruments, chairs, speakers
* Decoration
* Consumables

### **B. Welfare / Social Support**

Examples:

* Support for school fees
* Hospital or medical support
* Travel support
* Emergency assistance
* Aid to members in need

### **C. Utilities (Recurring or One-Time)**

Examples:

* Electricity
* Water
* Internet bundles
* Generator fuel or diesel
* Rent (if applicable)

---

## **15.1.2 Branch Expenditure Entry UI**

Path: **Branch Admin → Finance → Add Expenditure**

Fields:

* Date
* Category: Operations / Welfare / Utilities
* Sub-Category (changes based on category)
* Amount
* Description / Notes
* Optional: Receipt or photo upload
* Created by (auto)
* Updated by & Reason (for audit)

### **Behavior**

* Deducts from **branch local funds**.
* Mission can *view* but cannot *modify* branch expenditures.
* Late month entries should be allowed but marked as **late_entry = true**.

---

## **15.1.3 Branch Monthly Summary (Auto-Calculated)**

Every monthly report generated for branches must include:

### **Income**

* Total general contributions
* Total individual contributions
* Any extra funds added

### **Expenditure Breakdown**

* Operations Total
* Welfare Total
* Utilities Total

### **Final Branch Balance**

```
branch_local_income
- branch_total_expenditure
= remaining_local_balance
```

### **Additional Flags**

* Show late entries
* Show expenditure receipts
* Group by category

---

# **15.2 Mission-Level Expenditures**

Mission office manages funds beyond branches and requires full accounting.

Mission expenditures include:

### **A. Mission Operational Expenditures**

* Conferences
* Transport
* Office supplies
* Repairs
* Technology & equipment purchases

### **B. Mission Projects**

* Mission building
* Land acquisition
* Regional events
* Special programs

### **C. Mission Payroll (Full Payroll System)**

Mission staff must be handled with a proper payroll system.

---

## **15.2.1 Mission Payroll Features**

### **Mission Staff Fields**

* Full name
* Role / Position
* Base salary
* Payment cycle (usually monthly)
* Status (Active / Inactive)

### **Payroll Payment Recording**

Path: **Mission Admin → Payroll → Pay Staff**

Fields:

* Staff member
* Salary or amount paid
* Date paid
* Payment method
* Notes
* Optional receipt upload
* Created by

### **Payroll Deduction Rule**

* Mission payroll always deducts from **mission funds only**.
* Branches cannot create or modify payroll entries.

---

# **15.3 Mission Monthly Summary**

Mission’s monthly financial report must include:

### **Income**

* Branch remittances
* Mission-level contributions
* Other mission income

### **Expenditures**

* Mission operations
* Mission projects
* Mission payroll
* Any miscellaneous mission expenses

### **Final Mission Balance**

```
mission_total_income
- mission_total_expenditure
= remaining_mission_balance
```

### **Audit Trail**

* Every entry must track:

  * created_by
  * updated_by
  * updated_at
  * edit_reason

---

# **15.4 Inventory Tracking (Optional Minimal Version)**

If enabled:

### **Branch Inventory**

* Automatically generated when a branch records an expenditure for physical items
* Tracks quantity, cost, and remaining items

### **Mission Inventory**

* Tracks mission-owned equipment, supplies, and assets

### **Inventory Rules**

* Tied to expenditures
* Does not affect contribution or remittance workflows

---

# **15.5 Permissions Summary**

### **Branch Admins**

* Can add/edit/delete **branch expenditures**
* Can upload receipts
* Can view branch inventories
* Cannot modify mission funds or payroll
* Cannot add mission expenditure

### **Mission Admins**

* Full control over:

  * Mission expenditures
  * Mission payroll
  * Branch expenditure audits
  * Mission inventory
* Read-only access to branch expenditures
* Can verify remittances

---

# **15.6 Integration With Existing Contribution System**

These financial extensions integrate with:

### **Monthly Reports**

* Combined contributions + expenditures
* Consolidated financial overview
* Commission calculations unaffected

### **Remittance**

* Branch expenditures reduce branch local funds
* Mission expenditures reduce mission funds
* Remittance calculations remain based on contribution splits

### **Audit System**

* Every financial entry logged
* Late entries flagged
* Receipts available for verification
