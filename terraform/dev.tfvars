op_cli_path = "/usr/local/bin/op"
op_account  = "your-account.1password.com"
token       = "your-token-here"
connect_url = "http://connect-server:8080"

vaults = {
  development = {
    uuid = "abcd1234-dev"
    name = "Development"
  }
  production = {
    uuid = "efgh5678-prod"
    name = "Production"
  }
}

items = {
  dev_api_key = {
    title    = "Development API Key"
    vault    = "development"
    category = "login"
    username = "api-user"
    tags     = ["development", "api"]
  }
  
  prod_db = {
    title    = "Production Database"
    vault    = "production"
    category = "database"
    username = "admin"
    type     = "postgresql"
    tags     = ["production", "database"]
  }
}



cloudflare_api_token = "op://services/cloudflare_api_token"

zones = {
  "1234567890" = {
    name = "example.com"
  }
}

records = {
  "1234567890" = {
    name = "example.com"
    type = "A"
  }
}

sites = {
  "1234567890" = {
    name = "example.com"
  }
}

