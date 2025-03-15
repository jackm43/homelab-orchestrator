#!/bin/bash
set -euo pipefail

# Helper function to sanitize names for Terraform
sanitize_name() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g'
}

# Import a single vault
import_vault() {
  local vault_name="$1"
  local vault_id="$2"
  local safe_name=$(sanitize_name "$vault_name")
  
  echo "Importing vault: $vault_name ($vault_id)"
  terraform import "module.onepassword_vault_${safe_name}.onepassword_vault.vault" "${vault_id}" || {
    echo "Failed to import vault: $vault_name"
    return 1
  }
}

# Import a single item
import_item() {
  local vault_id="$1"
  local item_title="$2"
  local item_id="$3"
  local safe_name=$(sanitize_name "$item_title")
  
  echo "Importing item: $item_title ($item_id) from vault $vault_id"
  terraform import "module.onepassword_item_${safe_name}.onepassword_item.item" "vaults/${vault_id}/items/${item_id}" || {
    echo "Failed to import item: $item_title"
    return 1
  }
}

# List and import all vaults
import_all_vaults() {
  echo "Fetching vault list..."
  op vault list --format=json | jq -c '.[]' | while read -r vault; do
    name=$(echo "$vault" | jq -r '.name')
    id=$(echo "$vault" | jq -r '.id')
    import_vault "$name" "$id"
  done
}

# List and import all items from a specific vault
import_vault_items() {
  local vault_id="$1"
  local vault_name="$2"
  
  echo "Fetching items from vault: $vault_name..."
  op item list --vault="$vault_id" --format=json | jq -c '.[]' | while read -r item; do
    title=$(echo "$item" | jq -r '.title')
    id=$(echo "$item" | jq -r '.id')
    import_item "$vault_id" "$title" "$id"
  done
}

# Import items from a specific vault by ID
import_items_from_vault() {
  local vault_id="$1"
  if [ -z "$vault_id" ]; then
    echo "Usage: $0 import-items-from-vault <vault_id>"
    exit 1
  fi
  
  vault_name=$(op vault get "$vault_id" --format=json | jq -r '.name')
  import_vault_items "$vault_id" "$vault_name"
}

# Main execution
case "${1:-all}" in
  "vaults")
    import_all_vaults
    ;;
  "items")
    if [ -z "${2:-}" ]; then
      echo "Usage: $0 items <vault_id>"
      exit 1
    fi
    import_items_from_vault "$2"
    ;;
  "all")
    echo "Importing all vaults and items..."
    import_all_vaults
    op vault list --format=json | jq -c '.[]' | while read -r vault; do
      vault_id=$(echo "$vault" | jq -r '.id')
      vault_name=$(echo "$vault" | jq -r '.name')
      import_vault_items "$vault_id" "$vault_name"
    done
    ;;
  *)
    echo "Usage: $0 [vaults|items <vault_id>|all]"
    exit 1
    ;;
esac

