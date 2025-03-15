terraform {
  required_providers {
    onepassword = {
      source  = "1password/onepassword"
      version = "~> 2.0.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2.0"
    }
  }
} 