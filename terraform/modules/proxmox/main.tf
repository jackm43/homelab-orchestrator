module "onepassword_proxmox_credentials" {
  source = "./modules/onepassword"

provider "proxmox" {
  endpoint = var.virtual_environment_endpoint

  # Choose one authentication method:
  api_token = var.virtual_environment_api_token
  # OR
  username  = var.virtual_environment_username
  password  = var.virtual_environment_password
  # OR
  auth_ticket           = var.virtual_environment_auth_ticket
  csrf_prevention_token = var.virtual_environment_csrf_prevention_token
}