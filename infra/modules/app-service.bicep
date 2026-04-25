@description('Name prefix for all resources')
param prefix string

@description('Location for resources')
param location string

@description('Tags for resources')
param tags object = {}

@description('App Service Plan SKU')
param skuName string = 'P1v3'

@description('Application Insights connection string')
param appInsightsConnectionString string

var planName = '${prefix}-plan'
var appName = '${prefix}-api'

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  tags: tags
  kind: 'linux'
  sku: {
    name: skuName
  }
  properties: {
    reserved: true // Linux
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  tags: tags
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

output appServicePlanId string = appServicePlan.id
output appName string = webApp.name
output appUrl string = 'https://${webApp.properties.defaultHostName}'
