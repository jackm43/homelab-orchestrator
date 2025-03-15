output "item_uuid" {
  description = "The UUID of the created 1Password item"
  value       = onepassword_item.item.uuid
}

output "item_id" {
  description = "The full resource identifier of the created 1Password item"
  value       = onepassword_item.item.id
}

output "imported_items" {
  description = "The imported items from 1Password"
  value       = local.should_perform_import ? data.onepassword_item.import_items[0] : null
}

output "was_imported" {
  description = "Whether the item was imported in this run"
  value       = local.should_perform_import
}

output "generated_password" {
  description = "Whether a password was generated for this item"
  value       = local.effective_password_recipe != null
}

output "password_recipe_used" {
  description = "The password recipe that was used (if any)"
  value       = local.effective_password_recipe
}