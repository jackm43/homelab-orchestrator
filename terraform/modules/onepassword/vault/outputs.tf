output "vault_id" {
  description = "The UUID of the vault"
  value       = data.onepassword_vault.vault.uuid
}

output "vault_name" {
  description = "The name of the vault"
  value       = data.onepassword_vault.vault.name
}
