
# **1. Contribution Entry Overview**

* Contributions are **General** or **Individual**.
* Branch admins enter contributions weekly (general) or per member (individual).
* Mission HQ can view all contributions and generate reports.
* Contribution types may have split rules (mission % / branch %).
* Contributions can be temporary/pledge and may be closed when complete.
* Monthly reports automatically track all contributions for mission remittance.

---

# **2. General Contributions**

### **Entry Page**

* Branch Admin → Weekly Report → General Contributions Table

| Contribution Type      | Amount Box | Notes (optional) |
| ---------------------- | ---------- | ---------------- |
| Offering               | [   ]      | [   ]            |
| Tithe (General)        | [   ]      | [   ]            |
| Donations (General)    | [   ]      | [   ]            |
| Funeral Levy (General) | [   ]      | [   ]            |

**Flow:**

1. Admin selects date/week
2. Enters amounts only
3. Click **Submit Week**
4. System:

   * Creates transactions
   * Applies splits
   * Updates targets & allocations
   * Updates branch + mission reports

**Mission/HQ visibility:**

* Mission sees all general contributions per branch
* Audit totals per week/month

---

# **3. Individual Contributions**

### **UI Model: Member Contribution Grid**

**Steps:**

1. Select Contribution Type
2. Select Date
3. Grid shows all members with:

| Member   | Amount | Notes |
| -------- | ------ | ----- |
| Member 1 | [   ]  | [   ] |
| Member 2 | [   ]  | [   ] |
| ...      |        |       |

**Features:**

* Show only contributors or filter members
* Auto-save drafts
* Submit creates transactions, applies splits, updates reports

**Mission/HQ view:**

* Aggregated totals
* Individual contributions only for `is_individual = true` types

---

# **4. Contribution Type Management**

## **Mission-Level Types**

* Applies to all branches (Offering, Tithe, Welfare, etc.)
* Admins define: name, general/individual, splits, target, reward

## **Branch-Level Types**

* Local types only branch can use
* Mission sees for audit
* Branch can close; Mission can close if needed

---

# **5. Closeable Contribution Types**

* Property: `is_closeable: boolean`, `is_closed: boolean`, `closed_on: datetime`

**Rules:**

* Closed types cannot receive new entries
* All history visible
* Locked in reports and dashboards
* For pledges, freeze balances, retain history

**UI behavior:**

* Dropdown shows closed types greyed out
* Contribution type page shows "Closed on: DATE"
* Reports show `[Closed]` badge

**Audit logs required:**

* Who closed, branch/mission, timestamp, optional reason

---

# **6. Tithe System Configuration**

* Mission sets per-branch monthly target
* Split rules: mission % / branch %
* Reward rules: define commission recipients
* Branch sees target but cannot edit
* System calculates:

  * Target progress
  * Mission allocation
  * Branch retained
  * Reward eligibility

---

# **7. Reporting System (Branch + Mission)**

### Branch

* Weekly/monthly summary
* Breakdown by contribution type
* Individual contributor lists
* Target achievement & reward report

### Mission

* Total contributions per branch
* Contribution type breakdown
* Branch performance vs target
* Reward payouts
* Audit logs
* Filters by date, type, member, general/individual

---

# **8. Access Control (HQ vs Branch)**

### Branch Admin

* Record general & individual contributions
* View branch data
* Print/download reports
* Create branch-level types

### Mission Admin

* View all contributions
* Configure global contribution types
* Configure tithe rules & rewards
* Audit all branches
* Generate mission-wide reports

---

# **9. Monthly Remittance & Tithe Commission**

## **9.1 Monthly Tithe Cycle Rules**

* Contributions accumulate to **monthly target**
* Month-end closing freezes totals, triggers commission & remittance workflow
* New month starts fresh

## **9.2 Branch → Mission Remittance**

1. System calculates mission allocation owed
2. Branch records: amount, date, method, reference, notes
3. Mission verifies: Paid / Pending

**Status definitions:**

* Paid → Mission confirmed receipt
* Pending → Not yet paid or verified

## **9.3 Dashboards**

**Branch:** allocation owed, amount sent, status, monthly history
**Mission:** all branch remittances, total funds received, verification panel, overdue indicators

## **9.4 Commission Qualification**

* Monthly check: `if monthly_tithe_total >= monthly_target → Eligible`
* Commission = total_tithe * reward_percentage

## **9.5 Selecting Commission Recipients**

* Mission selects eligible recipients per branch
* Only selected users see “My Commission” menu

## **9.6 Commission Dashboard**

* Branch, target, collected, % achieved
* Qualification status
* Commission amount
* Paid / Pending
* Date paid
* Notes

## **9.7 Commission Payment Workflow**

1. System calculates eligibility
2. Mission approves & marks Paid/Pending
3. Recipients see update immediately

## **9.8 Monthly Commission Workflow**

**Automatic Calculation:**
- Tithe contributions are tracked weekly but calculated monthly
- Commissions are calculated when "Generate Commissions" is clicked
- System calculates: `if tithe_collected >= target → Qualified`
- Commission = tithe_collected × commission_percentage (default 10%)

**Commission Management Page (`/contributions/commission-management/`):**
1. Filter by month/year
2. View all branches with targets, collected, achievement %, commission
3. Qualified branches are highlighted in green
4. Shows pastor name and phone/MoMo number for payment
5. **Approve** - Mark commission as approved
6. **Pay** - Enter payment reference, creates expenditure record
7. Paid commissions are tracked for audit

**Note:** Tithes are general contributions (not individual). Branch enters total tithe collected each week.

---

# **10. Alerts & Notifications**

### Branch

* Pending remittance
* Target achieved
* Commission ready

### Mission

* Branch overdue
* Branch met target
* Commission payment pending

### Recipients

* Qualified for commission
* Commission paid

