# 1Password Item Module Usage

This module manages 1Password items and provides functionality to automatically import and export item data.

## Basic Usage

```hcl
module "onepassword_item" {
  source = "./modules/onepassword/item"
  
  vault_id = "your-vault-uuid"
  title    = "My Item"
  
  # Optional fields
  category = "login"
  username = "user@example.com"
  # Password will be auto-generated if not provided
  url      = "https://example.com"
  
  # Import configuration
  should_import_items = true  # Enable importing
  force_reimport = false      # Only import if not already imported
  
  # Custom password generation (optional)
  password_recipe = {
    length  = 24
    digits  = true
    letters = true
    symbols = true
  }
  
  # Add sections if needed
  sections = [
    {
      label = "Custom Section"
      fields = [
        {
          label = "API Key"
          type  = "CONCEALED"
          value = "secret-api-key"
        }
      ]
    }
  ]
  
  # Add tags if needed
  tags = ["development", "api"]
}
```

## Password Management

The module provides smart password handling:

1. **Automatic Password Generation**:
   - If no password is provided, one will be automatically generated
   - Default recipe: 32 characters with letters, digits, and symbols
   - Can be customized using the `password_recipe` variable

2. **Manual Password Changes**:
   - Passwords changed directly in 1Password will not be overwritten
   - The module uses a lifecycle block to ignore changes to sensitive fields
   - This allows for manual updates without Terraform reverting them

Example password configurations:

```hcl
# Auto-generated password with default recipe
module "auto_password" {
  source   = "./modules/onepassword/item"
  vault_id = "vault-id"
  title    = "Auto Generated"
}

# Custom password recipe
module "custom_password" {
  source   = "./modules/onepassword/item"
  vault_id = "vault-id"
  title    = "Custom Generated"
  
  password_recipe = {
    length  = 16
    digits  = true
    letters = true
    symbols = false
  }
}

# Manual password
module "manual_password" {
  source   = "./modules/onepassword/item"
  vault_id = "vault-id"
  title    = "Manual Password"
  password = "my-specific-password"
}
```

## Import Feature

The module provides smart import functionality with two control variables:
- `should_import_items`: Enable/disable importing (default: false)
- `force_reimport`: Force a new import even if previously imported (default: false)

When `should_import_items` is set to `true`, the module will:
1. Check if the item has been previously imported
2. If not imported before (or if `force_reimport = true`):
   - Fetch the item data using the 1Password CLI
   - Store the item data as JSON in `modules/onepassword/item/imported/<item-title>.json`
   - Create a marker file to track that the item has been imported
3. Make the item data available through the `imported_items` output

## Manual Changes Protection

The module is designed to work well with manual changes made directly in 1Password:

1. **Protected Fields**:
   - Passwords
   - Secure notes
   - Custom sections and fields

2. **Behavior**:
   - Changes made in 1Password will not be overwritten by Terraform
   - The module will continue to manage other aspects of the item
   - You can still update these fields through Terraform if needed

## Outputs

- `item_uuid`: The UUID of the created/managed item
- `item_id`: The full resource identifier of the item
- `imported_items`: The complete item data when imported
- `was_imported`: Boolean indicating if the item was imported in this run
- `generated_password`: Boolean indicating if a password was generated

## Notes

- Ensure the 1Password CLI (`op`) is installed and authenticated
- The JSON export directory is created at `modules/onepassword/item/imported/`
- Import markers are stored in `modules/onepassword/item/imported/.imported_<vault_id>_<title>`
- Sensitive fields are marked as such and won't be displayed in logs
- Manual changes to passwords and secure notes in 1Password are preserved