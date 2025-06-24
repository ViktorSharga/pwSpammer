# Email Notification Setup

To enable email notifications for test results, you need to set up the following GitHub secrets:

## Required Secrets

1. **EMAIL_USERNAME**: Your Gmail address (e.g., `your.email@gmail.com`)
2. **EMAIL_PASSWORD**: Your Gmail app password (NOT your regular password)
3. **EMAIL_TO**: The email address to receive notifications

## How to Set Up

### 1. Create Gmail App Password
1. Go to https://myaccount.google.com/security
2. Enable 2-factor authentication if not already enabled
3. Search for "App passwords"
4. Create a new app password for "Mail"
5. Copy the 16-character password

### 2. Add Secrets to GitHub
1. Go to your repository: https://github.com/ViktorSharga/pwSpammer
2. Click on Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `EMAIL_USERNAME`: Your Gmail address
   - `EMAIL_PASSWORD`: The app password from step 1
   - `EMAIL_TO`: Your email address to receive reports

## What You'll Receive

The email will include:
- Test execution status (success/failure)
- Number of tests run, passed, failed, and skipped
- Test duration
- Links to full GitHub Actions results
- Attached files:
  - `test_summary.txt`: Human-readable summary
  - `report.json`: Machine-readable test results (can be parsed by Claude)
  - `coverage.xml`: Code coverage data

## Alternative Email Providers

If you prefer not to use Gmail, you can modify the workflow to use other SMTP servers:
- Outlook: `smtp-mail.outlook.com` (port 587)
- Yahoo: `smtp.mail.yahoo.com` (port 587)
- Custom SMTP: Update server_address and server_port accordingly