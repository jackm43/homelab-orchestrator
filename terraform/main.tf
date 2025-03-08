terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = ">=2.9.0"
    }
  }
}

provider "proxmox" {
  pm_api_url          = var.proxmox_api_url
  pm_api_token_id     = var.proxmox_api_token_id
  pm_api_token_secret = var.proxmox_api_token_secret
  pm_tls_insecure     = true
}

locals {
  ssh_public_key = file("~/.ssh/id_rsa.pub")
}

resource "proxmox_lxc" "containers" {
  for_each    = var.lxc_containers
  
  target_node = var.proxmox_node
  hostname    = each.value.hostname
  ostemplate  = var.lxc_templates[each.value.template]
  password    = var.lxc_password
  
  cores       = each.value.cores
  memory      = each.value.memory
  swap        = 512
  
  rootfs {
    storage = "local-lvm"
    size    = each.value.storage_size
  }
  
  network {
    name   = "eth0"
    bridge = "vmbr0"
    ip     = each.value.ip_address
    gw     = each.value.gateway
  }
  
  features {
    nesting = true
  }
  
  start = true
  
  ssh_public_keys = local.ssh_public_key

  unprivileged = true
  
  description = each.value.description
  tags        = join(";", each.value.tags)
  onboot = true
}

resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/templates/hosts.tpl", {
    containers = {
      for name, container in proxmox_lxc.containers : name => {
        ip_address = split("/", container.network[0].ip)[0]
        hostname   = container.hostname
        tags       = split(";", container.tags)
      }
    }
  })
  filename = "${path.module}/../ansible/inventory/hosts.yml"
}