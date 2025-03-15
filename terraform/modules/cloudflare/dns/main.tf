resource "cloudflare_record" "dns_record" {
  for_each = var.dns_records

  zone_id = var.zone_id
  name    = each.value.name
  value   = each.value.value
  type    = each.value.type
  ttl     = try(each.value.ttl, 1) # 1 = automatic
  proxied = try(each.value.proxied, true)
} 