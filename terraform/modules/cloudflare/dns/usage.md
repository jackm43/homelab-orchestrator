# Cloudflare DNS Module

This module manages DNS records in Cloudflare.

## Requirements

- Cloudflare API token with DNS edit permissions
- Environment variable `CLOUDFLARE_API_TOKEN` set

## Usage

```hcl
module "dns" {
  source = "./modules/cloudflare/dns"

  zone_id = "your_zone_id"
  dns_records = {
    app = {
      name  = "app"
      value = "192.168.1.100"
      type  = "A"
    }
    www = {
      name    = "www"
      value   = "app.example.com"
      type    = "CNAME"
      proxied = true
    }
  }
}
```

## Variables

| Name | Description | Type | Required |
|------|-------------|------|----------|
| zone_id | Cloudflare Zone ID | string | yes |
| dns_records | Map of DNS records to create | map(object) | yes |

Each DNS record object supports:
- name: Record name (required)
- value: Record value (required)
- type: Record type (required)
- ttl: Time to live (optional, defaults to 1/automatic)
- proxied: Whether to proxy through Cloudflare (optional, defaults to true) 