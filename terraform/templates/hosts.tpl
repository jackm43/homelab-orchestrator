all:
  children:
    lxc_containers:
      hosts:
%{ for name, container in containers ~}
        ${name}:
          ansible_host: ${container.ip_address}
          ansible_user: root
%{ endfor ~}
%{ for tag in distinct(flatten([for name, container in containers : container.tags])) ~}
    ${tag}:
      hosts:
%{ for name, container in containers ~}
%{ if contains(container.tags, tag) ~}
        ${name}:
%{ endif ~}
%{ endfor ~}
%{ endfor ~}