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

variable "existing_items" {
  type = map(object({
    title = string
    vault = string
  }))
  description = "Map of existing 1Password items to manage. See schema.md for detailed field documentation."
}

data "onepassword_item" "existing_items" {
  for_each = var.existing_items
  title    = each.value.title
  vault    = each.value.vault
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

  default_password_recipe = {
    length  = 32
    symbols = true
    digits  = true
    letters = true
  }
}

provider "onepassword" {
  account               = var.op_account != null ? var.op_account : null
  service_account_token = var.service_account_token != null ? var.service_account_token : null
  token                 = var.token != null ? var.token : null
  url                   = var.connect_url != null ? var.connect_url : null
  op_cli_path           = var.op_cli_path
}

data "onepassword_vault" "vaults" {
  for_each = local.vaults
  uuid     = each.value.uuid
}

resource "onepassword_item" "items" {
  for_each = local.items

  vault = data.onepassword_vault.vaults[each.value.vault].uuid
  title = each.value.title

  category = each.value.category
  type     = each.value.type
  username = each.value.username
  password = each.value.password
  url      = each.value.url
  database = each.value.database
  hostname = each.value.hostname
  port     = each.value.port
  tags     = each.value.tags

  dynamic "section" {
    for_each = each.value.sections != null ? each.value.sections : {}
    content {
      label = section.value.label

      dynamic "field" {
        for_each = section.value.fields
        content {
          label = field.key
          type  = field.value.type
          value = field.value.value
        }
      }
    }
  }

  dynamic "password_recipe" {
    for_each = each.value.password_recipe != null ? [each.value.password_recipe] : [local.default_password_recipe]
    content {
      length  = password_recipe.value.length
      symbols = password_recipe.value.symbols
      digits  = password_recipe.value.digits
      letters = password_recipe.value.letters
    }
  }
}
