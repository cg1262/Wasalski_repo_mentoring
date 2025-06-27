# Bicep - po co i gdzie używać?

## Co to jest Bicep?

Bicep to **Domain Specific Language (DSL)** od Microsoft do tworzenia szablonów Azure Resource Manager (ARM). To nowoczesna alternatywa dla JSON-owych szablonów ARM.

### Główne cechy:
- 🎯 **Azure-specific** - tylko dla Microsoft Azure
- 📝 **Czytelny syntax** - łatwiejszy niż JSON ARM
- 🔄 **Transpiluje do ARM** - Bicep → JSON ARM
- 🔧 **IntelliSense** - wsparcie w VS Code
- 🚀 **Szybkie wdrażanie** - natywne wsparcie Azure CLI

## Bicep vs ARM Templates

### ARM Template (JSON) - tradycyjny sposób:
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "storageAccountName": {
      "type": "string",
      "metadata": {
        "description": "Name of the storage account"
      }
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "Location for the storage account"
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2021-06-01",
      "name": "[parameters('storageAccountName')]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2",
      "properties": {
        "accessTier": "Hot"
      }
    }
  ]
}
```

### Bicep - nowoczesny sposób:
```bicep
// Parametry
@description('Name of the storage account')
param storageAccountName string

@description('Location for the storage account')
param location string = resourceGroup().location

// Zasób
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}
```

**Różnica**: 30 linii JSON vs 15 linii Bicep! 🎯

## Instalacja i setup

### Wymagania:
```bash
# Azure CLI (zawiera Bicep)
az --version

# Lub osobno Bicep CLI
az bicep install

# Sprawdź wersję
az bicep version

# VS Code extension
# Zainstaluj "Bicep" extension w VS Code
```

### Pierwszy projekt:
```bash
# Utwórz folder
mkdir my-bicep-project
cd my-bicep-project

# Utwórz plik main.bicep
touch main.bicep
```

## Podstawowe przykłady

### 1. **Storage Account**:
```bicep
// main.bicep
@description('Storage account name')
@minLength(3)
@maxLength(24)
param storageAccountName string

@description('Storage account location')
param location string = resourceGroup().location

@description('Storage account SKU')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_ZRS'
  'Premium_LRS'
])
param storageSku string = 'Standard_LRS'

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// Output
output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
output primaryEndpoints object = storageAccount.properties.primaryEndpoints
```

### 2. **Web App z App Service Plan**:
```bicep
// webapp.bicep
@description('Name of the web app')
param webAppName string

@description('Location for resources')
param location string = resourceGroup().location

@description('App Service Plan SKU')
@allowed([
  'F1'
  'B1'
  'B2'
  'S1'
  'S2'
  'P1v2'
])
param appServicePlanSku string = 'F1'

@description('Runtime stack')
@allowed([
  'NODE|18-lts'
  'PYTHON|3.9'
  'DOTNETCORE|6.0'
  'PHP|8.0'
])
param runtimeStack string = 'NODE|18-lts'

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2021-02-01' = {
  name: '${webAppName}-plan'
  location: location
  sku: {
    name: appServicePlanSku
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Web App
resource webApp 'Microsoft.Web/sites@2021-02-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: runtimeStack
      appSettings: [
        {
          name: 'WEBSITE_NODE_DEFAULT_VERSION'
          value: '18.x'
        }
      ]
    }
    httpsOnly: true
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${webAppName}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
  }
}

// Outputs
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
```

### 3. **Kompletna infrastruktura - LAMP Stack**:
```bicep
// lamp-stack.bicep
@description('Admin username for the VM')
param adminUsername string

@description('Admin password for the VM')
@secure()
param adminPassword string

@description('Prefix for resource names')
param resourcePrefix string = 'lamp'

@description('Location for all resources')
param location string = resourceGroup().location

// Variables
var vmName = '${resourcePrefix}-vm'
var vnetName = '${resourcePrefix}-vnet'
var subnetName = '${resourcePrefix}-subnet'
var nsgName = '${resourcePrefix}-nsg'
var publicIPName = '${resourcePrefix}-ip'
var nicName = '${resourcePrefix}-nic'
var storageAccountName = '${resourcePrefix}${uniqueString(resourceGroup().id)}'

// Network Security Group
resource networkSecurityGroup 'Microsoft.Network/networkSecurityGroups@2021-02-01' = {
  name: nsgName
  location: location
  properties: {
    securityRules: [
      {
        name: 'SSH'
        properties: {
          priority: 1001
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '22'
        }
      }
      {
        name: 'HTTP'
        properties: {
          priority: 1002
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '80'
        }
      }
      {
        name: 'HTTPS'
        properties: {
          priority: 1003
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
    ]
  }
}

// Virtual Network
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: '10.0.0.0/24'
          networkSecurityGroup: {
            id: networkSecurityGroup.id
          }
        }
      }
    ]
  }
}

// Public IP
resource publicIP 'Microsoft.Network/publicIPAddresses@2021-02-01' = {
  name: publicIPName
  location: location
  properties: {
    publicIPAllocationMethod: 'Dynamic'
    dnsSettings: {
      domainNameLabel: '${resourcePrefix}-${uniqueString(resourceGroup().id)}'
    }
  }
}

// Network Interface
resource networkInterface 'Microsoft.Network/networkInterfaces@2021-02-01' = {
  name: nicName
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: publicIP.id
          }
          subnet: {
            id: '${virtualNetwork.id}/subnets/${subnetName}'
          }
        }
      }
    ]
  }
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

// Virtual Machine
resource virtualMachine 'Microsoft.Compute/virtualMachines@2021-07-01' = {
  name: vmName
  location: location
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_B2s'
    }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      adminPassword: adminPassword
      customData: base64(loadTextContent('cloud-init.txt'))
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-focal'
        sku: '20_04-lts-gen2'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: 'Premium_LRS'
        }
      }
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: networkInterface.id
        }
      ]
    }
    diagnosticsProfile: {
      bootDiagnostics: {
        enabled: true
        storageUri: storageAccount.properties.primaryEndpoints.blob
      }
    }
  }
}

// Outputs
output sshConnection string = 'ssh ${adminUsername}@${publicIP.properties.dnsSettings.fqdn}'
output webUrl string = 'http://${publicIP.properties.dnsSettings.fqdn}'
```

### 4. **cloud-init.txt** (instalacja LAMP):
```bash
#cloud-config
package_update: true
packages:
  - apache2
  - mysql-server
  - php
  - php-mysql
  - libapache2-mod-php

runcmd:
  - systemctl enable apache2
  - systemctl start apache2
  - systemctl enable mysql
  - systemctl start mysql
  - echo "<?php phpinfo(); ?>" > /var/www/html/info.php
  - echo "<h1>LAMP Stack deployed with Bicep!</h1>" > /var/www/html/index.html
  - mysql -e "CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'password123';"
  - mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'webuser'@'localhost';"
  - mysql -e "FLUSH PRIVILEGES;"
```

## Deployment i zarządzanie

### Podstawowe komendy:
```bash
# Transpiluj Bicep do ARM
az bicep build --file main.bicep

# Deploy do resource group
az deployment group create \
  --resource-group myResourceGroup \
  --template-file main.bicep \
  --parameters storageAccountName=mystorageaccount

# Deploy z parametrami z pliku
az deployment group create \
  --resource-group myResourceGroup \
  --template-file main.bicep \
  --parameters @parameters.json

# Validate przed deployment
az deployment group validate \
  --resource-group myResourceGroup \
  --template-file main.bicep \
  --parameters storageAccountName=mystorageaccount

# What-if - zobacz co się zmieni
az deployment group what-if \
  --resource-group myResourceGroup \
  --template-file main.bicep \
  --parameters storageAccountName=mystorageaccount
```

### Plik parametrów:
```json
// parameters.json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "storageAccountName": {
      "value": "mystorageaccount"
    },
    "location": {
      "value": "westeurope"
    },
    "storageSku": {
      "value": "Standard_GRS"
    }
  }
}
```

## Zaawansowane funkcje

### 1. **Moduły**:
```bicep
// modules/storage.bicep
@description('Storage account name')
param storageAccountName string

@description('Location')
param location string = resourceGroup().location

@description('SKU')
param sku string = 'Standard_LRS'

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: sku
  }
  kind: 'StorageV2'
}

output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
```

```bicep
// main.bicep - użycie modułu
module storage 'modules/storage.bicep' = {
  name: 'storageModule'
  params: {
    storageAccountName: 'mystorageaccount'
    location: location
    sku: 'Standard_GRS'
  }
}

// Używaj output z modułu
output storageId string = storage.outputs.storageAccountId
```

### 2. **Pętle i warunki**:
```bicep
// Array parametr
@description('Storage account names')
param storageAccountNames array = [
  'storage1'
  'storage2'
  'storage3'
]

// Pętla - utwórz wiele storage accountów
resource storageAccounts 'Microsoft.Storage/storageAccounts@2021-06-01' = [for name in storageAccountNames: {
  name: '${name}${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}]

// Warunek
@description('Create public IP?')
param createPublicIP bool = true

resource publicIP 'Microsoft.Network/publicIPAddresses@2021-02-01' = if (createPublicIP) {
  name: 'myPublicIP'
  location: location
  properties: {
    publicIPAllocationMethod: 'Dynamic'
  }
}
```

### 3. **Existing resources**:
```bicep
// Referencja do istniejącego zasobu
resource existingVnet 'Microsoft.Network/virtualNetworks@2021-02-01' existing = {
  name: 'existing-vnet'
}

// Użycie istniejącego zasobu
resource subnet 'Microsoft.Network/virtualNetworks/subnets@2021-02-01' = {
  parent: existingVnet
  name: 'new-subnet'
  properties: {
    addressPrefix: '10.0.1.0/24'
  }
}
```

## CI/CD z Bicep

### GitHub Actions:
```yaml
# .github/workflows/deploy.yml
name: Deploy Bicep

on:
  push:
    branches: [ main ]
    paths: [ 'bicep/**' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy Bicep
      uses: azure/arm-deploy@v1
      with:
        subscriptionId: ${{ secrets.AZURE_SUBSCRIPTION }}
        resourceGroupName: 'myResourceGroup'
        template: './bicep/main.bicep'
        parameters: './bicep/parameters.json'
        failOnStdErr: false
```

### Azure DevOps:
```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main
  paths:
    include:
    - bicep/*

variables:
  resourceGroupName: 'myResourceGroup'
  location: 'westeurope'

stages:
- stage: Validate
  jobs:
  - job: ValidateBicep
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: AzureCLI@2
      displayName: 'Validate Bicep'
      inputs:
        azureSubscription: 'MyServiceConnection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az deployment group validate \
            --resource-group $(resourceGroupName) \
            --template-file bicep/main.bicep \
            --parameters bicep/parameters.json

- stage: Deploy
  dependsOn: Validate
  jobs:
  - deployment: DeployBicep
    environment: 'production'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: 'Deploy Bicep'
            inputs:
              azureSubscription: 'MyServiceConnection'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az deployment group create \
                  --resource-group $(resourceGroupName) \
                  --template-file bicep/main.bicep \
                  --parameters bicep/parameters.json
```

## Best practices

### 1. **Struktura projektu**:
```
bicep-project/
├── main.bicep
├── parameters/
│   ├── dev.json
│   ├── staging.json
│   └── prod.json
├── modules/
│   ├── network/
│   ├── compute/
│   └── storage/
├── scripts/
│   └── deploy.sh
└── README.md
```

### 2. **Naming conventions**:
```bicep
// Używaj camelCase dla parametrów
param storageAccountName string
param resourceGroupLocation string

// Używaj descriptive names
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: 'vnet-${projectName}-${environment}'
  // ...
}

// Consistent tagging
var commonTags = {
  Environment: environment
  Project: projectName
  ManagedBy: 'Bicep'
  Owner: 'DevOps'
}
```

### 3. **Security**:
```bicep
// Zawsze używaj @secure() dla haseł
@secure()
param adminPassword string

// Nie hardcode-uj secrets
param keyVaultName string
param secretName string

resource keyVault 'Microsoft.KeyVault/vaults@2021-06-01-preview' existing = {
  name: keyVaultName
}

// Pobierz secret z Key Vault
var secretValue = keyVault.getSecret(secretName)
```

## Bicep vs konkurencja

| Narzędzie | Scope | Syntax | Learning Curve |
|-----------|-------|--------|----------------|
| **Bicep** | Azure only | Clean DSL | Low |
| **Terraform** | Multi-cloud | HCL | Medium |
| **ARM Templates** | Azure only | JSON | High |
| **Pulumi** | Multi-cloud | Programming languages | High |

## Podsumowanie

### ✅ Używaj Bicep gdy:
- Pracujesz tylko z Azure
- Chcesz Infrastructure as Code
- Potrzebujesz czytelny syntax
- Masz zespół DevOps
- Chcesz natywną integrację z Azure

### ❌ Unikaj Bicep gdy:
- Multi-cloud wymagania
- Nie używasz Azure
- Preferujesz Terraform
- Bardzo proste deployments

**Bicep = ARM Templates made easy!** 💪