terraform {
  required_providers {
    onepassword = {
      source  = "1password/onepassword"
      version = "~> 2.0.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}
