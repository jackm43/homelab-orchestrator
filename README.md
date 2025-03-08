### Terraform Deployment

Initialize the Terraform directory:

```bash
cd terraform
terraform init
```

Plan the deployment:

```bash
terraform plan
```

Apply the configuration:

```bash
terraform apply
```

### Ansible Configuration

Once Terraform has created your LXC containers, run Ansible to configure them:

```bash
cd ../ansible
ansible-playbook -i inventory/hosts.yml site.yml
```

## Adding More Containers

To add more LXC containers, simply update the `lxc_containers` map in your `terraform.tfvars` file:

```hcl
lxc_containers = {
  "caddy" = {
    hostname     = "caddy"
    cores        = 2
    memory       = 2048
    storage_size = "8G"
    ip_address   = "192.168.1.100/24"
    gateway      = "192.168.1.1"
    description  = "Caddy reverse proxy"
    tags         = ["web", "proxy"]
  },
  "adguard" = {
    hostname     = "adguard"
    cores        = 1
    memory       = 1024
    storage_size = "4G"
    ip_address   = "192.168.1.83/24"
    gateway      = "192.168.1.1"
    description  = "AdGuard Home"
    tags         = ["dns"]
  }
}
```