@description('Name prefix for all resources')
param prefix string

@description('Location for resources')
param location string

@description('Tags for resources')
param tags object = {}

var visionName = '${prefix}-vision'

resource aiVision 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: visionName
  location: location
  tags: tags
  kind: 'ComputerVision'
  sku: {
    name: 'S1'
  }
  properties: {
    customSubDomainName: visionName
    publicNetworkAccess: 'Enabled'
  }
}

output visionName string = aiVision.name
output visionEndpoint string = aiVision.properties.endpoint
output visionId string = aiVision.id
