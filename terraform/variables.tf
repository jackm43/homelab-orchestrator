############################################################################################################
# Proxmox Variables
############################################################################################################

variable "proxmox_api_url" {
  description = "The URL of Proxmox API (https://{domain}/api2/json)"
  type        = string
}

variable "proxmox_api_token_id" {
  description = "The ID of the Proxmox API token"
  type        = string
}

variable "proxmox_api_token_secret" {
  description = "The secret of the Proxmox API token"
  type        = string
  sensitive   = true
}

variable "lxc_password" {
  description = "Password for LXC containers"
  type        = string
  sensitive   = true
}

variable "proxmox_node" {
  description = "The name of the Proxmox node"
  type        = string
  default     = "pve"
}

variable "lxc_containers" {
  description = "Map of LXC containers to create"
  type = map(object({
    vmid         = number
    hostname     = string
    cores        = number
    memory       = number
    storage_size = string
    ip_address   = string
    gateway      = string
    template     = string
    description  = string
    tags         = list(string)
  }))
}


############################################################################################################
# OnePassword Variables
############################################################################################################

variable "op_cli_path" {
  description = "Path to the 1Password CLI"
  type        = string
  default     = "/usr/local/bin/op"
}

variable "op_account" {
  description = "1Password account details"
  type        = string
}

variable "token" {
  description = "1Password service account token"
  type        = string
  sensitive   = true
}

variable "connect_url" {
  description = "1Password Connect server URL"
  type        = string
}

variable "vaults" {
  description = "Map of 1Password vaults to import"
  type = map(object({
    uuid = string
    name = string
  }))
}

variable "should_import_items" {
  description = "Whether to import items from 1Password"
  type        = bool
  default     = true
}

variable "force_reimport" {
  description = "Whether to force reimport of items from 1Password"
  type        = bool
  default     = false
}


variable "items" {
  description = "Map of 1Password items to manage"
  type = map(object({
    title    = string
    vault    = string
    category = optional(string)
    username = optional(string)
    password = optional(string)
    url      = optional(string)
    tags     = optional(list(string))
    sections = optional(list(object({
      label = string
      fields = optional(list(object({
        label    = string
        type     = optional(string)
        purpose  = optional(string)
        value    = optional(string)
      })))
    })))
  }))
  default = {}
}

variable "ssh_public_key" {
  description = "SSH public key for Proxmox"
  type        = string
  default     = null
}



############################################################################################################
# Cloudflare Variables
############################################################################################################

variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
  default     = null
}

variable "zones" {
  description = "Map of Cloudflare zones to create"
  type = map(object({
    zone_id = string
    name    = string
  }))
}

variable "records" {
  description = "Map of Cloudflare records to create"
  type = map(object({
    zone_id = string
    name    = string
    type    = string
  }))
}

############################################################################################################
# Caddy Variables
############################################################################################################

variable "sites" {
  description = "List of sites to proxy"
  type = list(object({
    domain   = string
    upstream = string
  }))
}

variable "caddy_config_path" {
  description = "Path to the Caddy config file"
  type        = string
  default     = "/etc/caddy/Caddyfile"
}
