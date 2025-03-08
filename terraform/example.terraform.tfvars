proxmox_api_url        = "https://proxmox.domain.me/api2/json"
proxmox_api_token_id   = "root@pam!terraform"
proxmox_api_token_secret = "123"
lxc_password           = "password"
proxmox_node           = "pxe" 

lxc_templates = {
    "debian_12"   = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst",
    "debian_11"   = "local:vztmpl/debian-11-standard_11.7-1_amd64.tar.zst",
    "alpine_321"  = "local:vztmpl/alpine-3.21-default_20241217_amd64.tar.xz",
    "alpine_319"  = "local:vztmpl/alpine-3.19-default_20240207_amd64.tar.xz"
}

lxc_containers = {
  "caddy-tf" = {
    hostname     = "caddy-tf"
    vmid         = "120"
    cores        = 1
    memory       = 512
    template     = "alpine_321"
    storage_size = "8G"
    ip_address   = "192.168.1.169/24"
    gateway      = "192.168.1.1"
    description  = "caddy reverse proxy"
    tags         = ["web", "proxy"]
  }
}