# System Administrator Guide

## Overview
This guide provides comprehensive information for system administrators managing the SDSCC Church Management System.

## System Architecture
- **Framework:** Django 4.2+
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Deployment:** Fly.io with CockroachDB
- **File Storage:** Cloudinary
- **Authentication:** Custom backend with PIN system

## User Management

### User Roles
1. **Mission Admin:** Full system access
2. **Area Admin:** Area-level oversight
3. **District Admin:** District management
4. **Branch Admin:** Branch operations
5. **Auditor:** Read-only financial access
6. **Pastor:** Member management
7. **Member:** Basic access

### Creating Users
1. Navigate to Accounts → Users
2. Click "Add User"
3. Fill required fields:
   - Username (unique)
   - Email
   - Full name
   - Role
   - Branch assignment
   - PIN (4 digits)
4. Set initial password
5. Assign permissions

### User Permissions
- Defined in user roles
- Custom permissions available
- Hierarchical access control
- Scope-based data visibility

## Financial Management

### Monthly Closing
- **Location:** /monthly-closing/
- **Process:** Month-end locking
- **Permissions:** Branch Admin+
- **Features:** PDF reports, edit locks

### Contribution Types
- **Branch Types:** /contributions/branch-types/
- **Global Types:** Mission admin only
- **Allocations:** Percentage-based
- **Validation:** 100% total required

### Remittances
- **Auto-calculation:** Based on allocations
- **Tracking:** Status monitoring
- **Reports:** Monthly summaries
- **Compliance:** Audit trails

## System Configuration

### Settings Management
- **Site Settings:** Basic configuration
- **Currency:** Symbol and format
- **Time Zone:** Africa/Accra
- **Email:** SMTP settings
- **Storage:** Cloudinary config

### Notification System
- **Context Processor:** Auto-loads counts
- **Types:** Announcements, events, approvals
- **Delivery:** In-app + email
- **Preferences:** User-configurable

## Security Settings

### Authentication
- **PIN System:** 4-digit access
- **Password Policy:** 8+ characters
- **Session Timeout:** 24 hours
- **Failed Login:** Lockout after attempts

### Data Protection
- **Encryption:** HTTPS enforced
- **Backups:** Daily automated
- **Audit Logs:** All actions tracked
- **Access Control:** Role-based

## Maintenance Tasks

### Daily
- Check system logs
- Monitor backup status
- Review error reports
- Verify user activity

### Weekly
- Update security patches
- Review performance metrics
- Clean temporary files
- Check disk space

### Monthly
- Database maintenance
- User access review
- Security audit
- Performance tuning

## Troubleshooting

### Common Issues
1. **Login Problems**
   - Check user status
   - Reset PIN/password
   - Verify permissions
   - Clear browser cache

2. **Data Issues**
   - Check database status
   - Verify migrations
   - Review logs
   - Restore backup if needed

3. **Performance**
   - Check server resources
   - Optimize queries
   - Clear cache
   - Restart services

### Error Codes
- **500:** Server error
- **403:** Permission denied
- **404:** Page not found
- **400:** Bad request

## Backup and Recovery

### Automated Backups
- **Database:** Daily at 2 AM
- **Files:** Weekly full backup
- **Retention:** 30 days
- **Storage:** Cloud storage

### Manual Backup
```bash
# Database backup
python manage.py dumpdata > backup.json

# Media backup
rsync -av media/ backup/media/
```

### Recovery Process
1. Identify backup point
2. Stop application
3. Restore database
4. Restore files
5. Verify integrity
6. Restart services

## Performance Optimization

### Database
- Index optimization
- Query optimization
- Connection pooling
- Regular maintenance

### Caching
- Static file caching
- Database query cache
- Session caching
- CDN integration

### Monitoring
- Response time tracking
- Error rate monitoring
- Resource utilization
- User activity metrics

## Deployment

### Production Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Deploy to Fly.io
fly deploy
```

### Environment Variables
- `DATABASE_URL`: Database connection
- `SECRET_KEY`: Django secret
- `DEBUG`: Debug mode
- `CLOUDINARY_URL`: File storage

## Support Contacts

### Technical Support
- **Email:** tech@sdscc.org
- **Phone:** +233-XXX-XXXX
- **Hours:** 8 AM - 6 PM GMT

### Emergency Contacts
- **Critical Issues:** +233-XXX-XXXX
- **After Hours:** +233-XXX-XXXX

## Documentation
- **User Guides:** Located in /DOCS/
- **API Documentation:** /api/docs/
- **Training Materials:** /training/
- **FAQ:** /help/faq/

## Updates and Upgrades

### Version Control
- **Repository:** Git
- **Branching:** Feature branches
- **Testing:** Staging environment
- **Deployment:** CI/CD pipeline

### Upgrade Process
1. Review release notes
2. Test in staging
3. Schedule maintenance window
4. Backup production
5. Deploy update
6. Verify functionality

## Compliance
- **Data Protection:** GDPR compliant
- **Financial Standards:** Audit ready
- **Accessibility:** WCAG 2.0
- **Security:** ISO 27001 standards

## Training Resources
- **Video Tutorials:** YouTube channel
- **Webinars:** Monthly sessions
- **Documentation:** Online help
- **Support:** Live chat available
