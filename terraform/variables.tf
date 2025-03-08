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

variable "lxc_templates" {
  description = "List of available LXC templates with friendly names"
  type = map(string)
  default = {
    "debian_12"   = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst",
    "debian_11"   = "local:vztmpl/debian-11-standard_11.7-1_amd64.tar.zst",
    "alpine_321"  = "local:vztmpl/alpine-3.21-default_20241217_amd64.tar.xz",
    "alpine_319"  = "local:vztmpl/alpine-3.19-default_20240207_amd64.tar.xz"
  }
}