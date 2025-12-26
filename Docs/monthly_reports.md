# Monthly Reports System

## Overview
The Monthly Reports system provides comprehensive financial and attendance tracking for each branch on a monthly basis. It automates the collection of data from contributions, expenditures, and attendance to create standardized reports for mission oversight.

## Features

### 1. Automatic Data Collection
- **Contributions**: Automatically sums tithe, offering, and special contributions
- **Expenditures**: Tracks utility expenses, maintenance, and other operational costs
- **Attendance**: Calculates service count, average attendance, and visitor statistics
- **Mission Remittance**: Automatically calculates 10% of tithe as mission due

### 2. Report Workflow
The system follows a clear approval workflow:
1. **Draft** - Initial state when report is generated
2. **Submitted** - Branch executive submits for review
3. **Approved** - Mission admin/auditor approves the report
4. **Paid** - Mission remittance is recorded as paid
5. **Archived** - Report is archived for historical reference

### 3. Payment Management
- **Two-way Approval**: Branch can mark as paid (requesting approval), Mission admin approves
- **Overdue Tracking**: System flags reports with payments overdue (due by 10th of next month)
- **Payment Details**: Track payment date, reference number, and method
- **Balance Calculation**: Automatic calculation of branch balance after payments

### 4. Access Control
- **Branch Executives**: Can generate and submit reports for their branch
- **Mission Admins**: Can view, approve, and manage all branch reports
- **Auditors**: Full access to all reports for financial oversight
- **Pastors**: View-only access to their branch reports

## User Interface

### Monthly Reports List Page
- **Filtering**: By month, year, branch, and status
- **Summary Cards**: Total reports, amount due, overdue amount
- **Quick Actions**: Export PDF, generate new report
- **Status Indicators**: Visual indicators for overdue payments

### Report Detail Page
- **Financial Summary**: Detailed breakdown of contributions and expenditures
- **Attendance Statistics**: Service count, average attendance, new members
- **Mission Remittance**: Due amount, paid amount, balance
- **Payment Recording**: Form to record mission payments
- **Audit Trail**: Complete history of submissions and approvals

### Generate Report Page
- **Automatic Data**: Pulls data from existing records
- **Validation**: Prevents duplicate reports for same period
- **Preview**: Shows what data will be included before generation

## PDF Export
- **Single Report**: Export individual branch report as PDF
- **Bulk Export**: Export all reports for a month/year period
- **Professional Format**: Clean, printable format with church branding
- **Download Options**: Direct download or email functionality

## Integration Points
- **Contributions Module**: Automatically pulls contribution data
- **Expenditure Module**: Pulls expense data by category
- **Attendance Module**: Calculates attendance statistics
- **Payroll Module**: Links to staff salary information
- **Audit Module**: Logs all report actions for compliance

## Notifications
- **Overdue Alerts**: Automatic alerts for overdue payments
- **Submission Notifications**: When reports are submitted for review
- **Approval Notifications**: When reports are approved or paid
- **Monthly Reminders**: Reminders to generate monthly reports

## Reports & Analytics
- **Branch Performance**: Compare branches by contributions and attendance
- **Trend Analysis**: Month-over-month growth tracking
- **Compliance Reports**: Track overdue payments and submission status
- **Mission Income**: Project and track expected mission remittances

## Security & Compliance
- **Role-based Access**: Strict access control based on user roles
- **Audit Logging**: Complete audit trail of all actions
- **Data Integrity**: Validation to ensure accurate calculations
- **Approval Workflow**: Multi-level approval for financial accuracy
