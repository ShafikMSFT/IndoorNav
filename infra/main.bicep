targetScope = 'subscription'

@description('Azure region for all resources')
param location string = 'swedencentral'

@description('Name prefix for all resources')
param prefix string = 'indoornav'

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

var tags = {
  project: 'indoor-navigation'
  environment: environment
}

var rgName = '${prefix}-${environment}-rg'

// Resource Group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgName
  location: location
  tags: tags
}

// Monitoring (deploy first — other modules depend on connection string)
module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    prefix: '${prefix}-${environment}'
    location: location
    tags: tags
  }
}

// Storage
module storage 'modules/storage.bicep' = {
  name: 'storage'
  scope: resourceGroup
  params: {
    prefix: '${prefix}${environment}'
    location: location
    tags: tags
  }
}

// Cosmos DB (Gremlin + SQL)
module cosmos 'modules/cosmos.bicep' = {
  name: 'cosmos'
  scope: resourceGroup
  params: {
    prefix: '${prefix}-${environment}'
    location: location
    tags: tags
  }
}

// Azure AI Vision
module aiVision 'modules/ai-vision.bicep' = {
  name: 'ai-vision'
  scope: resourceGroup
  params: {
    prefix: '${prefix}-${environment}'
    location: location
    tags: tags
  }
}

// Azure OpenAI
module openai 'modules/openai.bicep' = {
  name: 'openai'
  scope: resourceGroup
  params: {
    prefix: '${prefix}-${environment}'
    location: location
    tags: tags
  }
}

// App Service (Backend API)
module appService 'modules/app-service.bicep' = {
  name: 'app-service'
  scope: resourceGroup
  params: {
    prefix: '${prefix}-${environment}'
    location: location
    tags: tags
    appInsightsConnectionString: monitoring.outputs.connectionString
  }
}

// Azure Functions (Video processing)
module functions 'modules/functions.bicep' = {
  name: 'functions'
  scope: resourceGroup
  params: {
    prefix: '${prefix}-${environment}'
    location: location
    tags: tags
    storageAccountName: storage.outputs.storageAccountName
    appInsightsConnectionString: monitoring.outputs.connectionString
    appServicePlanId: appService.outputs.appServicePlanId
  }
}

// SignalR
module signalr 'modules/signalr.bicep' = {
  name: 'signalr'
  scope: resourceGroup
  params: {
    prefix: '${prefix}-${environment}'
    location: location
    tags: tags
  }
}

// AI Search
module aiSearch 'modules/ai-search.bicep' = {
  name: 'ai-search'
  scope: resourceGroup
  params: {
    prefix: '${prefix}-${environment}'
    location: location
    tags: tags
  }
}

// ─── Outputs ───
output resourceGroupName string = resourceGroup.name
output storageAccountName string = storage.outputs.storageAccountName
output blobEndpoint string = storage.outputs.blobEndpoint
output cosmosEndpoint string = cosmos.outputs.sqlEndpoint
output gremlinEndpoint string = cosmos.outputs.gremlinEndpoint
output visionEndpoint string = aiVision.outputs.visionEndpoint
output openaiEndpoint string = openai.outputs.openaiEndpoint
output gptDeployment string = openai.outputs.gptDeploymentName
output embeddingDeployment string = openai.outputs.embeddingDeploymentName
output apiUrl string = appService.outputs.appUrl
output functionsUrl string = functions.outputs.functionAppUrl
output signalrHostName string = signalr.outputs.signalrHostName
output searchEndpoint string = aiSearch.outputs.searchEndpoint
output appInsightsConnectionString string = monitoring.outputs.connectionString
