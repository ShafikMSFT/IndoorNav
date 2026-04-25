<#
.SYNOPSIS
    Register Entra ID (Azure AD) applications for Indoor Navigation.

.DESCRIPTION
    Creates two app registrations:
    1. Backend API — exposes an API scope, validates JWT tokens
    2. Frontend SPA — public client, requests API scope

    Run after deploy.ps1 has provisioned infrastructure.

.PARAMETER SkipLogin
    Skip az login if you're already authenticated.
#>
param(
    [switch]$SkipLogin
)

$ErrorActionPreference = 'Stop'

$prefix      = 'indoornav'
$apiAppName  = "$prefix-api"
$spaAppName  = "$prefix-spa"
$backendUrl  = "https://$prefix-dev-api.azurewebsites.net"
$frontendUrl = "http://localhost:5173"

Write-Host "`n=== Entra ID App Registration ===" -ForegroundColor Cyan

if (-not $SkipLogin) {
    Write-Host "Logging in to Azure (device code flow)..." -ForegroundColor Yellow
    az login --use-device-code --output none
}

# ── 1. Backend API registration ──
Write-Host "`nCreating Backend API app: $apiAppName" -ForegroundColor Yellow

$apiApp = az ad app create `
    --display-name $apiAppName `
    --sign-in-audience AzureADMyOrg `
    --output json | ConvertFrom-Json

$apiAppId = $apiApp.appId
$apiObjectId = $apiApp.id
Write-Host "  App ID (client): $apiAppId"

# Generate a unique scope ID
$scopeId = [guid]::NewGuid().ToString()

# Expose an API scope: api://<appId>/access_as_user
$apiIdentifierUri = "api://$apiAppId"

az ad app update --id $apiObjectId `
    --identifier-uris $apiIdentifierUri `
    --output none

# Add the oauth2 permission scope
$scopeJson = @"
{
  "oauth2PermissionScopes": [
    {
      "adminConsentDescription": "Allow the app to access Indoor Navigation API on behalf of the signed-in user.",
      "adminConsentDisplayName": "Access Indoor Navigation API",
      "id": "$scopeId",
      "isEnabled": true,
      "type": "User",
      "userConsentDescription": "Allow the app to access Indoor Navigation API on your behalf.",
      "userConsentDisplayName": "Access Indoor Navigation API",
      "value": "access_as_user"
    }
  ]
}
"@

$scopeFile = [System.IO.Path]::GetTempFileName()
$scopeJson | Out-File -FilePath $scopeFile -Encoding utf8
az ad app update --id $apiObjectId --set api=@$scopeFile --output none
Remove-Item $scopeFile

# Create service principal for the API app
az ad sp create --id $apiAppId --output none 2>$null

Write-Host "  API scope: $apiIdentifierUri/access_as_user" -ForegroundColor Green

# ── 2. Frontend SPA registration ──
Write-Host "`nCreating Frontend SPA app: $spaAppName" -ForegroundColor Yellow

$spaApp = az ad app create `
    --display-name $spaAppName `
    --sign-in-audience AzureADMyOrg `
    --public-client-redirect-uris "$frontendUrl" "$frontendUrl/blank.html" "$backendUrl/.auth/login/aad/callback" `
    --output json | ConvertFrom-Json

$spaAppId = $spaApp.appId
$spaObjectId = $spaApp.id
Write-Host "  App ID (client): $spaAppId"

# Configure SPA redirect URIs (for MSAL.js)
$spaRedirectJson = @"
{
  "spa": {
    "redirectUris": [
      "$frontendUrl",
      "$frontendUrl/blank.html",
      "$backendUrl/.auth/login/aad/callback"
    ]
  }
}
"@

$spaRedirectFile = [System.IO.Path]::GetTempFileName()
$spaRedirectJson | Out-File -FilePath $spaRedirectFile -Encoding utf8
az ad app update --id $spaObjectId --set web=@$spaRedirectFile --output none
Remove-Item $spaRedirectFile

# Grant SPA permission to call the API
$apiResourceId = (az ad sp list --filter "appId eq '$apiAppId'" --query "[0].id" -o tsv)

az ad app permission add `
    --id $spaObjectId `
    --api $apiAppId `
    --api-permissions "$scopeId=Scope" `
    --output none

Write-Host "  SPA redirect URIs: $frontendUrl" -ForegroundColor Green

# ── 3. Get tenant ID ──
$tenantId = az account show --query tenantId -o tsv
Write-Host "`nTenant ID: $tenantId" -ForegroundColor Green

# ── 4. Write config files ──
Write-Host "`n=== Writing auth configuration ===" -ForegroundColor Cyan

# Backend .env additions
$backendEnvPath = Join-Path $PSScriptRoot 'backend\.env'
$authEnv = @"

# Entra ID Auth (added by setup-auth.ps1)
AZURE_TENANT_ID=$tenantId
AZURE_CLIENT_ID=$apiAppId
AZURE_API_SCOPE=$apiIdentifierUri/access_as_user
"@

Add-Content -Path $backendEnvPath -Value $authEnv
Write-Host "  Updated: backend\.env" -ForegroundColor Green

# Frontend auth config
$frontendAuthConfig = @"
export const msalConfig = {
  auth: {
    clientId: "$spaAppId",
    authority: "https://login.microsoftonline.com/$tenantId",
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

export const apiScope = "$apiIdentifierUri/access_as_user";
"@

$frontendAuthPath = Join-Path $PSScriptRoot 'frontend\src\authConfig.ts'
$frontendAuthConfig | Out-File -FilePath $frontendAuthPath -Encoding utf8 -Force
Write-Host "  Created: frontend\src\authConfig.ts" -ForegroundColor Green

# ── Summary ──
Write-Host "`n=== Registration Complete ===" -ForegroundColor Cyan
Write-Host "Backend API App ID : $apiAppId"
Write-Host "Frontend SPA App ID: $spaAppId"
Write-Host "Tenant ID          : $tenantId"
Write-Host "API Scope          : $apiIdentifierUri/access_as_user"
Write-Host ""
Write-Host "Next: run 'pip install -r requirements.txt' and 'npm install' to pick up auth packages." -ForegroundColor Yellow
Write-Host ""
