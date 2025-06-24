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

## Troubleshooting Email Issues

If email fails with SSL errors, try these alternatives:

### Option 1: Use Outlook instead of Gmail
Replace the email configuration with:
```yaml
server_address: smtp-mail.outlook.com
server_port: 587
```

### Option 2: Alternative Email Action
Replace the send-mail step with:
```yaml
- name: Send email notification
  uses: cinotify/github-action@main
  with:
    to: ${{ secrets.EMAIL_TO }}
    subject: "Test Results - ${{ github.repository }}"
    body: "Test completed with status: ${{ job.status }}"
```

### Option 3: No Email (GitHub Notifications Only)
Remove the email step entirely and rely on GitHub's built-in notifications in the Actions tab.