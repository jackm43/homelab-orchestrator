1. Declare modules
module "onepassword_vault_example" {
  source   = "./modules/onepassword/vault"
  vault_id = "your-vault-id"
}

module "onepassword_item_example" {
  source   = "./modules/onepassword/item"
  vault_id = module.onepassword_vault_example.vault_id
  title    = "Example Item"
  # ... etc
}