@description('Name prefix for all resources')
param prefix string

@description('Location for resources')
param location string

@description('Tags for resources')
param tags object = {}

var signalrName = '${prefix}-signalr'

resource signalr 'Microsoft.SignalRService/signalR@2024-03-01' = {
  name: signalrName
  location: location
  tags: tags
  sku: {
    name: 'Free_F1'
    capacity: 1
  }
  properties: {
    features: [
      {
        flag: 'ServiceMode'
        value: 'Default'
      }
    ]
    cors: {
      allowedOrigins: ['*']
    }
    tls: {
      clientCertEnabled: false
    }
  }
}

output signalrName string = signalr.name
output signalrHostName string = signalr.properties.hostName
output signalrId string = signalr.id
