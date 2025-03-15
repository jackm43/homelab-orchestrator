variable "zone_id" {
  description = "The Cloudflare Zone ID"
  type        = string
}

variable "dns_records" {
  description = "Map of DNS records to create"
  type = map(object({
    name    = string
    value   = string
    type    = string
    ttl     = optional(number)
    proxied = optional(bool)
  }))
} 