# Caddy Reverse Proxy Module

This module generates a Caddy configuration file for reverse proxying multiple sites.

## Requirements

- Caddy v2 installed on the target system
- Write permissions to the config file location

## Usage

```hcl
module "reverse_proxy" {
  source = "./modules/caddy/reverse_proxy"

  sites = [
    {
      domain   = "app.example.com"
      upstream = "localhost:3000"
    },
    {
      domain   = "api.example.com"
      upstream = "localhost:8080"
    }
  ]

  config_path = "/etc/caddy/Caddyfile.json"
}
```

## Variables

| Name | Description | Type | Required | Default |
|------|-------------|------|----------|---------|
| sites | List of sites to proxy | list(object) | yes | - |
| config_path | Path to write the Caddy config file | string | no | "/etc/caddy/Caddyfile.json" |

Each site object requires:
- domain: The domain name to match
- upstream: The upstream server to proxy to (format: host:port)

## Notes

- The module generates a JSON configuration file for Caddy
- HTTPS is enabled by default with automatic certificate management
- All sites are configured to use TLS
- The configuration uses the reverse_proxy handler with default settings 