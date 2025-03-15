provider "onepassword" {
  account               = var.op_account != null ? var.op_account : null
  service_account_token = var.service_account_token != null ? var.service_account_token : null
  token                 = var.token != null ? var.token : null
  url                   = var.connect_url != null ? var.connect_url : null
  op_cli_path           = var.op_cli_path
}