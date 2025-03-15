module "onepassword_vaults" {
  source    = "./modules/onepassword/vault"
  for_each  = var.vaults
  vault_id  = each.value.uuid
}

module "onepassword_items" {
  source    = "./modules/onepassword/item"
  for_each  = var.items

  vault_id  = module.onepassword_vaults[each.value.vault].vault_id
  title     = each.value.title

  should_import_items = var.should_import_items
  force_reimport     = var.force_reimport

  category  = each.value.category
  username  = each.value.username
  password  = each.value.password
  url       = each.value.url
  tags      = each.value.tags
  sections  = each.value.sections

  depends_on = [module.onepassword_vaults]
}

module "cloudflare_zones" {
  source    = "./modules/cloudflare/zone"
  for_each  = var.zones
  zone_id   = each.value.zone_id
  name      = each.value.name
}

module "cloudflare_records" {
  source    = "./modules/cloudflare/record"
  for_each  = var.records
  zone_id   = module.cloudflare_zones[each.value.zone_id].zone_id
  name      = each.value.name
  type      = each.value.type
}

module "caddy_reverse_proxy" {
  source    = "./modules/caddy/reverse_proxy"
  sites     = var.sites
  config_path = var.caddy_config_path
}