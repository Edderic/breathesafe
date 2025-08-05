# Heroku CLI Setup for GitHub Actions

## Required GitHub Secrets

You need to add these secrets to your GitHub repository:

### 1. Heroku API Key
1. Go to your Heroku account: https://dashboard.heroku.com/account
2. Scroll down to "API Key" section
3. Click "Reveal" to see your API key
4. Copy the API key
5. Add to GitHub secrets as `HEROKU_API_KEY`

### 2. Heroku App Names
Add these as GitHub secrets:
- `HEROKU_STAGING_APP`: `breathesafe-staging`
- `HEROKU_PRODUCTION_APP`: `breathesafe` (or your production app name)

### 3. Database Configuration
For staging database cloning:
- `HEROKU_PRODUCTION_APP`: Your production app name (e.g., `breathesafe`)

## How to Add Secrets to GitHub

1. Go to your GitHub repository
2. Click "Settings" tab
3. Click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each secret with the appropriate name and value

## Verification

After adding secrets, the workflow will be able to:
- Deploy to Heroku staging: `breathesafe-staging`
- Deploy to Heroku production: `breathesafe` (or your production app name)
- Clone production database to staging
- Run migrations on both environments 