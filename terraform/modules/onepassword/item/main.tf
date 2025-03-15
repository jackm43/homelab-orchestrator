locals {
  import_marker_file = "${path.module}/imported/.imported_${var.vault_id}_${var.title}"
  should_perform_import = (var.should_import_items &&
  (!fileexists(local.import_marker_file) || var.force_reimport))
  default_password_recipe = {
    length  = 32
    digits  = true
    letters = true
    symbols = true
  }

  effective_password_recipe = var.password == null ? (
    var.password_recipe != null ? var.password_recipe : local.default_password_recipe
  ) : null
}

data "onepassword_item" "import_items" {
  count = local.should_perform_import ? 1 : 0
  title = var.title
  vault = var.vault_id
}

resource "null_resource" "export_item" {
  count = local.should_perform_import ? 1 : 0

  triggers = {
    title      = var.title
    vault_id   = var.vault_id
    force_reimport = var.force_reimport ? timestamp() : "false"
  }

  provisioner "local-exec" {
    command = <<-EOT
      op item get '${var.title}' --vault='${var.vault_id}' --format=json > '${path.module}/imported/${var.title}.json' && \
      touch '${local.import_marker_file}'
    EOT
  }

  depends_on = [data.onepassword_item.import_items]
}

resource "onepassword_item" "item" {
  vault = var.vault_id
  title = var.title

  dynamic "section" {
    for_each = var.sections != null ? var.sections : []
    content {
      label = section.value.label

      dynamic "field" {
        for_each = section.value.fields != null ? section.value.fields : []
        content {
          label   = field.value.label
          type    = field.value.type
          purpose = field.value.purpose
          value   = field.value.value

          dynamic "password_recipe" {
            for_each = field.value.password_recipe != null ? [field.value.password_recipe] : []
            content {
              length  = password_recipe.value.length
              digits  = password_recipe.value.digits
              letters = password_recipe.value.letters
              symbols = password_recipe.value.symbols
            }
          }
        }
      }
    }
  }

  category   = var.category
  username   = var.username
  password   = var.password
  url        = var.url
  note_value = var.note_value
  tags       = var.tags

  database = var.database
  hostname = var.hostname
  port     = var.port
  type     = var.type

  dynamic "password_recipe" {
    for_each = local.effective_password_recipe != null ? [local.effective_password_recipe] : []
    content {
      length  = password_recipe.value.length
      digits  = password_recipe.value.digits
      letters = password_recipe.value.letters
      symbols = password_recipe.value.symbols
    }
  }

  lifecycle {
    ignore_changes = [
      password,
      note_value,
      section,
    ]
  }
}