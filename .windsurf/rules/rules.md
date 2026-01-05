---
trigger: always_on
---

You are modifying an EXISTING production codebase.

THIS IS A CONTROLLED REFACTOR.
DO NOT redesign the system.
DO NOT introduce new architecture.
DO NOT delete historical data.

Your task is to REMOVE year-as-state behavior and replace it with date-based reporting.

==================================================
GOAL
==================================================

Refactor the existing "Yearly Archive / Fiscal Year" logic so that:

- The system does NOT have a "current year"
- Years are NOT created, activated, or switched manually
- Data is NEVER moved out of core tables
- Reports (weekly, monthly, yearly) are based ONLY on date filtering
- Monthly closing logic REMAINS
- Yearly archiving logic is DISABLED or DEPRECATED

==================================================
CRITICAL CONSTRAINTS (DO NOT VIOLATE)
==================================================

- Do NOT rewrite the entire system
- Do NOT change core tables:
  Contribution, Expense, Remittance, Attendance, Member
- Do NOT delete any tables or data
- Do NOT introduce new models unless unavoidable
- Prefer DISABLING or DEPRECATING code over deleting it
- Changes must be minimal and reversible

==================================================
CURRENT PROBLEM (WHAT EXISTS NOW)
==================================================

The system currently:
- Uses a FiscalYear model with:
  - is_current
  - is_closed
- Requires admins to "create" a new year
- Automatically archives data into:
  - FinancialArchive
  - BranchArchive
  - MemberArchive
- Treats "year" as a system-wide state

THIS YEAR-AS-STATE LOGIC MUST STOP.

==================================================
TARGET DESIGN (FOLLOW EXACTLY)
==================================================

1. TIME MODEL
- Time is continuous
- All records stay in original tables
- Weekly / Monthly / Yearly = DATE FILTERS ONLY
- No global "current year" exists

2. FISCAL YEAR MODEL
- Keep FiscalYear ONLY as OPTIONAL METADATA
- IGNORE or DISABLE:
  - is_current
  - enforced single active year
  - automatic year switching
- FiscalYear must NOT control visibility or behavior

3. ARCHIVE TABLES
- FinancialArchive, BranchArchive, MemberArchive:
  - Are OPTIONAL SUMMARY TABLES
  - READ-ONLY
  - NOT authoritative
  - Must NOT replace real data
- If risky to remove, mark as:
  "DEPRECATED: year-as-state archive"

4. YEAR-END BEHAVIOR
- No admin action required at year end
- No automatic archiving
- No data migration
- Yearly reports use date ranges (e.g. Jan 1 – Dec 31)

5. MONTHLY CLOSING (KEEP THIS)
- MonthlyClose logic remains
- Monthly close:
  - locks edits
  - confirms totals
- Monthly close MUST NOT move data

6. UI CHANGES
- Disable or hide:
  - "Create New Fiscal Year"
  - "Set Current Year"
- Replace with:
  - Year selector (for reports only)
  - Date range filters
- Archived year views must read from date-filtered data

7. PERMISSIONS
- Mission admins and auditors:
  - Can view ALL historical data
- Branch admins:
  - Can view full history of their branch
- No user should ever "start a new year"

==================================================
TASKS TO PERFORM
==================================================

1. Locate all code paths that depend on:
   - FiscalYear.is_current
   - year switching logic
   - archive triggers

2. Refactor those paths to:
   - use date filters
   - NOT change system state

3. Add comments where logic is disabled:
   "DEPRECATED: Year-as-state architecture"

4. Ensure existing reports still work using date ranges

5. Do NOT add new abstractions or redesign reporting

==================================================
OUTPUT REQUIREMENTS
==================================================

After changes, provide:
- A list of what was DISABLED
- A list of what remains ACTIVE
- A short explanation of how yearly reports now work

==================================================
IMPORTANT
==================================================

If uncertain:
- DO NOT guess
- Leave TODO comments
- Stability is more important than elegance
