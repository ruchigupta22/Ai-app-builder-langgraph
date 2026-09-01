terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "2f0c9007-152b-4dce-86d0-2d73dc52ec59"
}

resource "azurerm_resource_group" "main" {
  name     = "ai-app-builder-rg"
  location = "centralindia"
}

resource "azurerm_container_registry" "main" {
  name                = "aiappbuilderacrruchi2026"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = "ai-app-builder-aks"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  dns_prefix          = "ai-app-bui-ai-app-builder-r-2f0c90"

  default_node_pool {
    name       = "nodepool1"
    node_count = 1
    vm_size    = "standard_b2s_v2"
  }

  identity {
    type = "SystemAssigned"
  }
}