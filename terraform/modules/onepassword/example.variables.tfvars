op_account = "your-account-here_uuid"
token = "your-token-here"
connect_url = "http://192.168.1.182:8080"
op_cli_path = "/usr/bin/op"
vaults = {
  services = {
    uuid = "xxxxx"
    name = "services"
  }
  private = {
    uuid = "xxxxx"
    name = "private"
  }
  shared = {
    uuid = "xxxxxx"
    name = "shared"
  }
}

existing_items = {
  proxmox_credentials = {
    title = "proxmox_credentials"
    vault = "services"
  }
  connect_token = {
    title = "connect_token"
    vault = "services"
  }
  teslamate_encryption_key = {
    title = "teslamate_encryption_key"
    vault = "services"
  }
  nas_project_files_user = {
    title = "nas_project_files_user"
    vault = "services"
  }
}

