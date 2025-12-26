---
trigger: always_on
---

### **Antigravity Agent Rules for SDSCC System**

**Rule 1 – File Verification & Consistency**

* Before executing any task, read all existing `.md` files (`admins.md`, `auditor.md`, `contributions.md`, `expenditure.md`, `members.md`, `overview.md`, `pastors.md`, `staff.md`).
* Check for **discrepancies, missing features, or outdated info**.
* Resolve any inconsistencies **before code generation begins**.
* If improvements are possible, **update the source MD files** and document the changes.

---

**Rule 2 – Full System Completion**

* Ensure that every feature described in the MD files is implemented in code:

  * **Models, Views, Templates, URLs, Forms, Dashboards, Sidebars, and Reports**.
* No module should remain partially implemented.
* All dashboards must have **role-based, mobile-first sidebars** and UI elements.
* Confirm **pastor, member, branch, area, district, and mission-level hierarchies** are respected.

---

**Rule 3 – Error Handling & Validation**

* After every script or code block run:

  * Check for **runtime or syntax errors**.
  * Ensure migrations apply successfully (`makemigrations` and `migrate`).
  * Validate all forms, templates, and view logic.
* If errors occur, **resolve before proceeding**.
* Log all fixes to `milestone.md` with clear description of what was corrected.

---

**Rule 4 – Professional Code Quality**

* Follow **Django best practices** and **PEP8**.
* All templates must use **TailwindCSS** primarily, **Bootstrap only where needed**, and **Material UI components consistently**.
* Include **mobile-first layouts** and fully responsive design.
* Comment code for clarity in complex modules, especially allocation, payroll, and auditing logic.

---

**Rule 5 – Hierarchical UI / Navigation**

* Any **admin-level feature** must include **hierarchical dropdowns** to select area, district, branch, or pastor.
* Pastors should have their **own sidebar**.
* Branch admins must have quick access to: members, contributions, expenditures, attendance, utility bills, and groups.
* Dashboards must dynamically reflect **role and access scope**.

---

**Rule 6 – Financial & Audit Safety**

* All financial flows (tithes, offerings, special contributions, expenditures, payroll) must be:

  * **Accurately allocated per hierarchy rules**
  * Validated for rounding errors and splits
  * Logged for audit trails
* Never allow unreviewed modifications of mission-level funds.

---

**Rule 7 – Milestone Tracking & Reporting**

* Maintain `milestone.md` for all completed tasks.
* Include:

  * Features completed
  * Bugs or issues fixed
  * Screenshots or notes if applicable
  * Dependencies for next tasks

---

**Rule 8 – Build Priority & Focus**

* Focus primarily on **building working features**.
* Documentation only if explicitly requested.
* Always complete **templates, models, views, forms, and dashboards** before moving to optional enhancements.

---

**Rule 9 – Database & Deployment**

* Use **SQLite for development**, but code must be **compatible with PostgreSQL / CockroachDB** for production.
* Ensure **UUIDs for major models** and proper relational integrity.
* Confirm migrations are **production-ready**.

---

**Rule 10 – Continuous Verification**

* After each significant feature or module:

  * Run tests (unit tests if available)
  * Validate forms, templates, and views
  * Confirm sidebars, access rules, and permissions are correct
  * Update `milestone.md`
Always use poershell commands when running scripts. Dont use "&&" instead use ";"

---

✅ **Summary for Agent:**

> “Always read and verify MD files first. Resolve inconsistencies before coding. Complete **all models, views, templates, forms, dashboards, and sidebars**. Validate every script, check errors, and follow role-based access rules. Focus on building first, then document. Maintain milestone.md and ensure production-ready, mobile-first UI for all hierarchies.”