locals {
  config = {
    apps = {
      http = {
        servers = {
          main = {
            listen = [":443"]
            routes = [
              for site in var.sites : {
                match = [{
                  host = [site.domain]
                }]
                handle = [{
                  handler = "reverse_proxy"
                  upstreams = [{
                    dial = site.upstream
                  }]
                }]
                terminal = true
              }
            ]
            tls_connection_policies = [{
              match = {
                sni = [for site in var.sites : site.domain]
              }
            }]
          }
        }
      }
    }
  }
}

resource "local_file" "caddy_config" {
  content  = jsonencode(local.config)
  filename = var.config_path

  depends_on = [data.onepassword_item.certificates]
} 