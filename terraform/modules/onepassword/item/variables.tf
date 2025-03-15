variable "should_import_items" {
  description = "Do you want to import items from 1Password?"
  type        = bool
  default     = false
}

variable "force_reimport" {
  description = "Force reimport even if the item was previously imported"
  type        = bool
  default     = false
}

variable "vault_id" {
  description = "The UUID of the vault where the item will be created"
  type        = string
}

variable "title" {
  description = "The title of the item"
  type        = string
}

variable "category" {
  description = "The category of the item"
  type        = string
  default     = null
  validation {
    condition     = var.category == null || contains(["login", "password", "database", "secure_note"], var.category)
    error_message = "Category must be one of: login, password, database, secure_note"
  }
}

variable "username" {
  description = "Username for this item"
  type        = string
  default     = null
}

variable "password" {
  description = "Password for this item"
  type        = string
  default     = null
  sensitive   = true
}

variable "url" {
  description = "The primary URL for the item"
  type        = string
  default     = null
}

variable "note_value" {
  description = "Secure Note value"
  type        = string
  default     = null
  sensitive   = true
}

variable "tags" {
  description = "An array of strings of the tags assigned to the item"
  type        = list(string)
  default     = null
}

variable "database" {
  description = "The name of the database (only applies to database category)"
  type        = string
  default     = null
}

variable "hostname" {
  description = "The address where the database can be found (only applies to database category)"
  type        = string
  default     = null
}

variable "port" {
  description = "The port the database is listening on (only applies to database category)"
  type        = string
  default     = null
}

variable "type" {
  description = "The type of database (only applies to database category)"
  type        = string
  default     = null
  validation {
    condition     = var.type == null || contains(["db2", "filemaker", "msaccess", "mssql", "mysql", "oracle", "postgresql", "sqlite", "other"], var.type)
    error_message = "Database type must be one of: db2, filemaker, msaccess, mssql, mysql, oracle, postgresql, sqlite, other"
  }
}

variable "password_recipe" {
  description = "The recipe used to generate a new value for a password"
  type = object({
    length  = optional(number)
    digits  = optional(bool)
    letters = optional(bool)
    symbols = optional(bool)
  })
  default = null
}

variable "sections" {
  description = "A list of custom sections in the item"
  type = list(object({
    label = string
    fields = optional(list(object({
      label   = string
      type    = optional(string)
      purpose = optional(string)
      value   = optional(string)
      password_recipe = optional(object({
        length  = optional(number)
        digits  = optional(bool)
        letters = optional(bool)
        symbols = optional(bool)
      }))
    })))
  }))
  default = null
} 