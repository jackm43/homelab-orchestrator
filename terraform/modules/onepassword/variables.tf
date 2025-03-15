variable "vaults" {
  type = map(object({
    uuid = string
    name = string
  }))
  description = "Map of vault configurations. Key is vault name, value contains UUID and name."
}

variable "items" {
  type = map(object({
    title = string
    vault = string

    category = optional(string, "login")
    type     = optional(string)
    username = optional(string)
    password = optional(string)
    url      = optional(string)
    database = optional(string)
    hostname = optional(string)
    port     = optional(string)
    tags     = optional(list(string))

    sections = optional(map(object({
      label = string
      fields = map(object({
        type  = string
        value = string
      }))
    })))
    password_recipe = optional(object({
      length  = number
      symbols = optional(bool)
      digits  = optional(bool)
      letters = optional(bool)
    }))
  }))
  description = "Map of 1Password items to manage. See schema.md for detailed field documentation."
}

variable "op_cli_path" {
  type        = string
  default     = "/usr/bin/op"
  description = "Path to the 1Password CLI executable"
}

variable "op_account" {
  type        = string
  default     = null
  description = "1Password account identifier (for CLI authentication)"
}

variable "service_account_token" {
  type        = string
  default     = null
  description = "1Password service account token (for service account authentication)"
  sensitive   = true
}

variable "token" {
  type        = string
  default     = null
  description = "1Password connect token"
  sensitive   = true
}

variable "connect_url" {
  type        = string
  default     = null
  description = "1Password connect URL"
}

locals {
  auth_count = (var.op_account != null ? 1 : 0) + (var.token != null ? 1 : 0) + (var.service_account_token != null ? 1 : 0)
  auth_check = local.auth_count == 1 ? true : file("ERROR: Exactly one of op_account or token must be provided")

  vaults = {
    for vault in var.vaults : vault.name => vault
  }
  items = {
    for item in var.items : item.title => item
  }
  existing_vaults = {
    for vault in var.vaults : vault.name => vault
  }

  default_password_recipe = {
    length  = 32
    symbols = true
    digits  = true
    letters = true
  }
}
