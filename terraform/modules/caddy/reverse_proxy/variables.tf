variable "sites" {
  description = "List of sites to proxy"
  type = list(object({
    domain   = string
    upstream = string
  }))
}

variable "config_path" {
  description = "Path to write the Caddy config file"
  type        = string
  default     = "/etc/caddy/Caddyfile.json"
} 