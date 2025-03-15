variable "op_account" {
  description = "The account to use for the 1Password provider"
  type        = string
  default     = null
}

variable "service_account_token" {
  description = "The service account token to use for the 1Password provider"
  type        = string
  default     = null
  sensitive   = true
  validation {
    condition     = (var.service_account_token == null) || (var.service_account_token != null && var.connect_url != null)
    error_message = "When using service_account_token, connect_url must also be provided"
  }
}

variable "token" {
  description = "The token to use for the 1Password provider"
  type        = string
  default     = null
  sensitive   = true
  validation {
    condition     = (var.token == null) || (var.token != null && var.connect_url != null)
    error_message = "When using token, connect_url must also be provided"
  }
}

variable "connect_url" {
  description = "The URL to use for the 1Password provider"
  type        = string
  default     = null
  validation {
    condition     = (var.connect_url == null) || (var.connect_url != null && (var.service_account_token != null || var.token != null))
    error_message = "When using connect_url, either service_account_token or token must also be provided"
  }
}

variable "op_cli_path" {
  description = "The path to the 1Password CLI"
  type        = string
  default     = "/usr/bin/op"
}
