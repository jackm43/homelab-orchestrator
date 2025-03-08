output "lxc_ips" {
  value = {
    for name, container in proxmox_lxc.containers : 
    name => split("/", container.network[0].ip)[0]
  }
}