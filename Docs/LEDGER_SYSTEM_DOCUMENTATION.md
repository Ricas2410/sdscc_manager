# Ledger-Centric Financial System Documentation

## Overview

This document describes the ledger-centric financial system implemented for the Church Financial Management System. The system implements **custody vs ownership** accounting to ensure correct financial tracking.

## Core Principle: Custody vs Ownership

When money is collected at a branch:
- **Ownership** may belong to Mission (based on allocation percentages)
- **Custody** (physical cash) remains with the Branch until remittance

The system distinguishes between:
- **Money earned but not yet received** (RECEIVABLE)
- **Money physically available for spending** (CASH)

## LedgerEntry Model

Located at: `core/ledger_models.py`

### Entry Types

| Type | Description | Spendable? |
|------|-------------|------------|
| `CASH` | Physically held funds | ✅ Yes |
| `RECEIVABLE` | Owed but not yet received | ❌ No |
| `PAYABLE` | Owed to another level | N/A |

### Owner Types

- `MISSION` - National level
- `AREA` - Area level
- `DISTRICT` - District level
- `BRANCH` - Local branch
- `MEMBER` - Individual member (optional)

### Source Types

- `CONTRIBUTION` - From contributions
- `EXPENDITURE` - From expenditures
- `REMITTANCE` - From branch remittances
- `COMMISSION` - From pastor commissions
- `EXTERNAL_INCOME` - Other income
- `ADJUSTMENT` - Manual adjustments
- `OPENING_BALANCE` - Starting balances

## Contribution Flow

When a member pays **100 GHS tithe** at Branch A (split 60% branch / 40% mission):

### Ledger Entries Created:

1. **Branch CASH +100**
   - Owner: Branch A
   - Type: CASH
   - Amount: 100 GHS
   - Description: Full amount received

2. **Mission RECEIVABLE +40**
   - Owner: Mission
   - Type: RECEIVABLE
   - Counterparty: Branch A
   - Amount: 40 GHS
   - Description: Mission allocation owed by branch

3. **Branch PAYABLE +40**
   - Owner: Branch A
   - Type: PAYABLE
   - Counterparty: Mission
   - Amount: 40 GHS
   - Description: Amount owed to Mission

### Key Points:
- ❌ Mission CANNOT see this 40 GHS as spendable cash
- ✅ Mission sees it as "Expected from Branch A"
- ✅ Branch can only spend 60 GHS (cash minus payables)

## Remittance Flow

When Branch A remits 40 GHS to Mission:

### Ledger Entries Created:

1. **Branch CASH -40** (outflow)
2. **Branch PAYABLE -40** (cleared)
3. **Mission RECEIVABLE -40** (cleared)
4. **Mission CASH +40** (now spendable)

### Result:
- Mission now has 40 GHS in spendable CASH
- Branch payable is cleared
- Mission receivable is cleared

## Expenditure Rules

### CRITICAL: Spending Validation

**Mission can ONLY spend CASH, never RECEIVABLE.**

Before any expenditure:
1. System checks available CASH balance
2. If expenditure > CASH, it is **blocked**
3. Error message explains the limitation

**Branch can only spend their spendable amount:**
- Spendable = CASH - PAYABLES
- Cannot spend money owed to Mission

## Monthly Closing

Monthly closing now:
1. Locks contributions & expenditures
2. Freezes receivables & payables
3. Locks all ledger entries for the month
4. Generates branch outstanding balances
5. Identifies remittance status per branch

**Does NOT:**
- Move or archive data
- Change fiscal year state
- Delete any records

## API Endpoints

### Ledger Balance API
`GET /api/ledger/balance/`

Parameters:
- `owner_type`: 'mission' or 'branch'
- `branch_id`: Required if owner_type is 'branch'

Returns:
```json
{
  "cash": 10000.00,
  "receivables": 5000.00,
  "spendable": 10000.00,
  "can_spend": true
}
```

## Views & URLs

| URL | View | Description |
|-----|------|-------------|
| `/ledger/` | `ledger_dashboard` | Main ledger dashboard |
| `/ledger/mission-position/` | `mission_financial_position` | Mission CASH vs RECEIVABLE |
| `/ledger/branch/<id>/` | `branch_financial_position` | Branch financial position |
| `/ledger/outstanding/` | `outstanding_remittances` | Branches with pending remittances |
| `/ledger/audit-trail/` | `ledger_audit_trail` | Full audit trail |
| `/ledger/branch/<id>/contributions/` | `branch_contributions_readonly` | Read-only branch contributions |

## Permissions

### Mission Admin
- View all ledger entries
- View all branch financial positions
- View branch contributions (read-only)
- Cannot edit branch data directly

### Auditor
- View all ledger entries
- View full audit trail
- View all financial positions
- Read-only access

### Branch Executive
- View own branch ledger entries
- View own branch financial position
- Cannot view other branches

## Signal Handlers

Located at: `core/ledger_signals.py`

Automatically creates ledger entries when:
- Contribution is saved (status = 'verified')
- Remittance is verified
- Expenditure is approved/paid
- Commission is paid

## Service Class

Located at: `core/ledger_service.py`

Key methods:
- `create_contribution_entries(contribution)`
- `create_remittance_entries(remittance, amount)`
- `create_expenditure_entries(expenditure)`
- `get_balance(owner_type, entry_type, ...)`
- `get_mission_cash_balance()`
- `get_mission_receivables()`
- `get_branch_cash_balance(branch)`
- `get_branch_payables(branch)`
- `get_branch_spendable_cash(branch)`
- `can_mission_spend(amount)`
- `can_branch_spend(branch, amount)`
- `lock_entries_for_month(month, year, branch)`

## UI Changes

### New Sidebar Items (Mission Admin)
- **Financial Ledger** - Main ledger dashboard
- **Outstanding Balances** - Branches owing money

### New Sidebar Items (Auditor)
- **Ledger Dashboard** - Financial overview
- **Outstanding Balances** - Pending remittances
- **Ledger Audit Trail** - Full transaction history

### Removed/Consolidated
- Duplicate "Remittances" link (consolidated)
- Duplicate "Mission Expenditures" link (consolidated)
- Duplicate "Branch Expenditures" link (consolidated)

## Migration

Migration file: `core/migrations/0013_ledger_entry.py`

Creates the `LedgerEntry` table with:
- All required fields
- Indexes for performance
- Foreign key relationships

## Important Notes

1. **Existing data is preserved** - No historical data is deleted
2. **Backward compatible** - Existing flows continue to work
3. **Signals auto-create entries** - New transactions automatically create ledger entries
4. **Spending validation** - Prevents overspending based on actual cash

## Yearly Reports

Yearly reports now work via **date filtering only**:
- No fiscal year state required
- Filter by date range (e.g., Jan 1 - Dec 31)
- All data stays in original tables
- Archive tables are DEPRECATED (read-only)
