# Currency Symbol Fixes - Phase 2
## Quick Reference Guide

---

## 📋 FILES TO FIX (13 files, ~30 instances)

### 1. Core Templates (1 file)
- [ ] `templates/core/tithe_targets.html` - Line 228
  - 1 instance to fix

### 2. Expenditure Templates (4 files)
- [ ] `templates/expenditure/assets_list.html` - Lines 35, 46, 156
  - 3 instances to fix (likely in summary cards and form labels)
  
- [ ] `templates/expenditure/expenditure_form.html` - Lines 35, 37
  - 2 instances to fix (likely in amount field label and prefix)
  
- [ ] `templates/expenditure/utility_bills.html` - Line 164
  - 1 instance to fix (likely in form label)
  
- [ ] `templates/expenditure/welfare_payments.html` - Line 100
  - 1 instance to fix (likely in form label)

### 3. Payroll Templates (5 files)
- [ ] `templates/payroll/commissions_list.html` - Line 51
  - 1 instance to fix (likely in summary card)
  
- [ ] `templates/payroll/my_payroll.html` - Line 335
  - 1 instance to fix (JavaScript - currency formatting)
  
- [ ] `templates/payroll/payroll_runs.html` - Line 37
  - 1 instance to fix (likely in summary card)
  
- [ ] `templates/payroll/staff_form.html` - Lines 65, 69, 73
  - 3 instances to fix (likely in salary/allowance fields)
  
- [ ] `templates/payroll/staff_payroll_management.html` - Lines 221, 226, 242, 255, 269, 282, 329
  - 7 instances to fix (likely in table headers, form labels, and JavaScript)

### 4. Reports Templates (3 files)
- [ ] `templates/reports/contribution_report.html` - Lines 63, 67
  - 2 instances to fix (likely in summary cards)
  
- [ ] `templates/reports/expenditure_report.html` - Line 131
  - 1 instance to fix (JavaScript - chart label)
  
- [ ] `templates/reports/financial_report.html` - Lines 160, 200
  - 2 instances to fix (JavaScript - chart tooltips)

---

## 🔧 FIX PATTERNS

### Pattern 1: HTML Labels
**Before:**
```html
<label class="form-label">Amount (GH₵)</label>
```

**After:**
```html
<label class="form-label">Amount ({{ site_settings.currency_symbol }})</label>
```

### Pattern 2: HTML with Prefix Span
**Before:**
```html
<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">GH₵</span>
```

**After:**
```html
<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">{{ site_settings.currency_symbol }}</span>
```

### Pattern 3: Display Values (Use Currency Filter)
**Before:**
```html
<p class="text-2xl font-bold">GH₵{{ amount|floatformat:2 }}</p>
```

**After:**
```html
<p class="text-2xl font-bold">{{ amount|currency }}</p>
```

### Pattern 4: JavaScript String Concatenation
**Before:**
```javascript
document.getElementById('amount').textContent = 'GH₵' + amount.toFixed(2);
```

**After:**
```javascript
document.getElementById('amount').textContent = '{{ site_settings.currency_symbol }}' + amount.toFixed(2);
```

### Pattern 5: JavaScript Chart Labels
**Before:**
```javascript
label: 'Amount (GH₵)'
```

**After:**
```javascript
label: 'Amount ({{ site_settings.currency_symbol }})'
```

### Pattern 6: JavaScript Tooltips
**Before:**
```javascript
return label + ': GH₵' + value.toFixed(2);
```

**After:**
```javascript
return label + ': {{ site_settings.currency_symbol }}' + value.toFixed(2);
```

---

## ✅ TESTING CHECKLIST

After fixing each file:
- [ ] Check that the page loads without errors
- [ ] Verify currency symbol displays correctly
- [ ] Test with different currency settings (if possible)
- [ ] Check mobile responsiveness
- [ ] Verify JavaScript functionality (if applicable)

---

## 📝 NOTES

1. **Currency Filter:** The `{{ amount|currency }}` filter automatically formats the amount with the correct currency symbol and decimal places.

2. **Site Settings:** The `{{ site_settings.currency_symbol }}` variable is available in all templates through the context processor.

3. **JavaScript:** In JavaScript code within Django templates, you can use `{{ site_settings.currency_symbol }}` because Django processes the template before sending it to the browser.

4. **Testing:** After all fixes, run a comprehensive search to ensure no hardcoded symbols remain:
   ```powershell
   Get-ChildItem -Path "templates" -Recurse -Include *.html | Select-String -Pattern "₦|GH₵" | Where-Object { $_.Line -notmatch "currency" }
   ```

---

## 🎯 ESTIMATED TIME

- **Core Templates:** 5 minutes
- **Expenditure Templates:** 20-30 minutes
- **Payroll Templates:** 30-40 minutes
- **Reports Templates:** 20-30 minutes
- **Testing:** 15-20 minutes

**Total:** 1.5 - 2 hours

---

**Start with expenditure templates as they are simpler, then move to payroll, and finally reports (which have JavaScript).**

