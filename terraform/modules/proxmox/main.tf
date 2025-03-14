data "onepassword_item" "proxmox_credentials" {
  title = "proxmox_credentials"
  vault = "services"
}


provider "proxmox" {
  endpoint = "http://192.168.1.240:8006/"

  username = "root@pam"
  password = data.onepassword_item.proxmox_credentials.password

  insecure = true

  ssh {
    agent = true
  }
}