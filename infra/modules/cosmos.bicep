@description('Name prefix for all resources')
param prefix string

@description('Location for resources')
param location string

@description('Tags for resources')
param tags object = {}

var accountName = '${prefix}-cosmos'
var databaseName = 'indoornav'
var graphName = 'spatial-graph'
var metadataContainerName = 'metadata'

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: accountName
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    capabilities: [
      {
        name: 'EnableGremlin'
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
  }
}

resource gremlinDatabase 'Microsoft.DocumentDB/databaseAccounts/gremlinDatabases@2024-05-15' = {
  parent: cosmosAccount
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
  }
}

resource gremlinGraph 'Microsoft.DocumentDB/databaseAccounts/gremlinDatabases/graphs@2024-05-15' = {
  parent: gremlinDatabase
  name: graphName
  properties: {
    resource: {
      id: graphName
      partitionKey: {
        paths: ['/mapId']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [
          { path: '/*' }
        ]
      }
    }
    options: {
      autoscaleSettings: {
        maxThroughput: 4000
      }
    }
  }
}

// Separate SQL API account for metadata
var sqlAccountName = '${prefix}-cosmos-sql'

resource cosmosSqlAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: sqlAccountName
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
  }
}

resource sqlDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmosSqlAccount
  name: '${databaseName}-sql'
  properties: {
    resource: {
      id: '${databaseName}-sql'
    }
  }
}

resource metadataContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: sqlDatabase
  name: metadataContainerName
  properties: {
    resource: {
      id: metadataContainerName
      partitionKey: {
        paths: ['/mapId']
        kind: 'Hash'
      }
    }
    options: {
      autoscaleSettings: {
        maxThroughput: 4000
      }
    }
  }
}

output accountName string = cosmosAccount.name
output endpoint string = cosmosSqlAccount.properties.documentEndpoint
output gremlinEndpoint string = 'wss://${cosmosAccount.name}.gremlin.cosmos.azure.com:443/'
output accountId string = cosmosAccount.id
output sqlAccountName string = cosmosSqlAccount.name
output sqlEndpoint string = cosmosSqlAccount.properties.documentEndpoint
