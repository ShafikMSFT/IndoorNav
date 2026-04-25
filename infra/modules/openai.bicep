@description('Name prefix for all resources')
param prefix string

@description('Location for resources')
param location string

@description('Tags for resources')
param tags object = {}

@description('GPT model name to deploy')
param gptModelName string = 'gpt-4o'

@description('GPT model version')
param gptModelVersion string = '2024-11-20'

@description('Embedding model name to deploy')
param embeddingModelName string = 'text-embedding-3-small'

@description('Embedding model version')
param embeddingModelVersion string = '1'

var openaiName = '${prefix}-openai'

resource openai 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: openaiName
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openaiName
    publicNetworkAccess: 'Enabled'
  }
}

resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openai
  name: 'gpt-4o'
  sku: {
    name: 'Standard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: gptModelName
      version: gptModelVersion
    }
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openai
  name: 'text-embedding-3-small'
  sku: {
    name: 'GlobalStandard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: embeddingModelVersion
    }
  }
  dependsOn: [gptDeployment]
}

output openaiName string = openai.name
output openaiEndpoint string = openai.properties.endpoint
output openaiId string = openai.id
output gptDeploymentName string = gptDeployment.name
output embeddingDeploymentName string = embeddingDeployment.name
