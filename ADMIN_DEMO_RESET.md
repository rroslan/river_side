# Admin Demo Data Reset Feature

## Overview

The River Side Food Court admin interface now includes a comprehensive demo data reset feature that allows administrators to quickly reset the system to a clean state for demonstrations, testing, or maintenance purposes.

## Features

### 🔄 Management Command
- **Command**: `python manage.py reset_demo_data`
- **Options**: `--force` (skip confirmation prompt)
- **Purpose**: Reset all orders and return system to clean demonstration state

### 🖥️ Admin Interface
- **URL**: `/admin/data-reset/`
- **Features**: 
  - Interactive web interface with real-time progress
  - Confirmation dialogs to prevent accidental resets
  - Live command output display
  - Status indicators and progress tracking

### 📊 Admin Dashboard Integration
- **Location**: Admin home page (`/admin/`)
- **Features**:
  - Real-time statistics display (Orders Today, Unpaid Orders, Active Tables, Total Orders)
  - Quick access button to reset functionality
  - Auto-refreshing stats every 30 seconds
  - Manual refresh button

### ⚡ Admin Actions
- **Location**: Orders admin page
- **Action**: "🔄 Reset All Demo Data"
- **Usage**: Select any orders and choose the action from the dropdown

### 📈 Stats API
- **Endpoint**: `/admin/api/stats/`
- **Method**: GET
- **Authentication**: Staff member required
- **Response**: JSON with current system statistics

## What Gets Reset

When you trigger a demo data reset, the following actions occur:

1. **Orders Deleted**: All existing orders and order items are permanently deleted
2. **Order History Cleared**: All order status history is removed
3. **Cart Data Cleared**: All shopping cart data is cleared
4. **Tables Reset**: Ensures 25 tables are available (creates missing ones if needed)
5. **Vendors Preserved**: All vendor, category, and menu item data remains intact
6. **Users Preserved**: All user accounts and authentication data remains intact

## Usage Instructions

### Method 1: Command Line
```bash
# With confirmation prompt
python manage.py reset_demo_data

# Force reset without prompt (for scripts)
python manage.py reset_demo_data --force
```

### Method 2: Admin Interface
1. Log into Django admin at `/admin/`
2. Click "🗑️ Reset All Demo Data" on the dashboard
3. Review the warning and click "🗑️ Reset All Demo Data"
4. Confirm in the popup dialog
5. Watch real-time progress and output
6. Return to admin dashboard when complete

### Method 3: Admin Action
1. Go to the Orders admin page at `/admin/orders/order/`
2. Select any orders (selection doesn't matter for this action)
3. Choose "🔄 Reset All Demo Data" from the Actions dropdown
4. Click "Go"
5. Check messages for confirmation

### Method 4: Direct URL
- Navigate directly to `/admin/data-reset/` (requires staff login)

## Security & Permissions

- **Authentication Required**: All methods require Django admin login
- **Staff Permission**: User must have `is_staff=True`
- **Confirmation Required**: Multiple confirmation steps prevent accidental resets
- **Logging**: All reset operations are logged for audit purposes

## Expected Results

After a successful reset, you should see:

```
📊 Orders Today: 0
💰 Unpaid Orders: 0  
🪑 Active Tables: 0
📦 Total Orders: 0
🪑 Available Tables: 25
```

All vendors will show as "Ready for orders" and the system will be in a clean state ready for fresh demonstrations.

## Integration Details

### Files Added/Modified

**New Files:**
- `core/management/commands/reset_demo_data.py` - Django management command
- `core/admin.py` - Custom admin site with reset functionality
- `templates/admin/data_reset.html` - Reset interface template
- `templates/admin/index.html` - Enhanced admin dashboard

**Modified Files:**
- `core/settings.py` - Added 'core' to INSTALLED_APPS
- `core/urls.py` - Import custom admin configuration
- `orders/admin.py` - Added reset action to OrderAdmin

### Technical Implementation

1. **Custom Admin Site**: Extends Django's default admin with additional URLs and functionality
2. **Management Command**: Proper Django management command with colored output and error handling
3. **AJAX Interface**: Real-time updates using fetch API with CSRF protection
4. **Stats API**: RESTful endpoint for dashboard statistics
5. **Template Integration**: Responsive admin templates with modern styling

## Error Handling

The system includes comprehensive error handling:

- **Database Errors**: Graceful handling of database connection issues
- **Permission Errors**: Clear messages for insufficient permissions
- **Template Errors**: Fallback mechanisms for missing templates
- **Network Errors**: Client-side error handling for API calls
- **Validation Errors**: Input validation and sanitization

## Best Practices

1. **Backup First**: Always backup your database before running resets in production
2. **Use --force in Scripts**: Use the `--force` flag when running automated scripts
3. **Monitor Logs**: Check Django logs after resets to ensure completion
4. **Test Environment**: Use this feature primarily in development/demo environments
5. **Regular Resets**: Reset demo data regularly to maintain clean demonstration state

## Troubleshooting

### Common Issues

**Permission Denied**
- Ensure user has `is_staff=True` permission
- Check Django admin login status

**Template Not Found**
- Verify templates are in correct directory structure
- Check TEMPLATES setting in Django settings

**Command Not Found**
- Ensure 'core' app is in INSTALLED_APPS
- Run `python manage.py collectstatic` if needed

**AJAX Errors**
- Check CSRF token configuration
- Verify admin URLs are correctly configured
- Check browser developer console for errors

### Getting Help

1. Check Django logs in `logs/django.log`
2. Run `python manage.py check` for configuration issues
3. Test management command directly: `python manage.py reset_demo_data --force`
4. Verify database connectivity and permissions

## Version History

- **v1.0**: Initial implementation with basic reset functionality
- **v1.1**: Added admin interface and real-time progress tracking
- **v1.2**: Enhanced with stats API and dashboard integration
- **v1.3**: Added admin actions and improved error handling

## Future Enhancements

Potential future improvements:
- Selective data reset (e.g., reset only today's orders)
- Scheduled automatic resets
- Data export before reset
- Reset templates for different demo scenarios
- Email notifications for reset operations