from pyinfra import host
from pyinfra.operations import apt, files, server, systemd

#
# Variables
#

media_mount_point = "/media"
device_id = f"PARTUUID={host.data.media_device_partition_uuid}"

transmission_dir_downloading = f"{media_mount_point}/downloading"
transmission_dir_completed = f"{media_mount_point}/new"
transmission_rpc_username = "transmission"
transmission_rpc_password = "password"
transmission_rpc_whitelist = "10.10.*.*"
transmission_service_user = "pi"


#
# Storage
#

files.line(
    name="Ensure /etc/fstab has media mount point",
    path="/etc/fstab",
    line=media_mount_point,
    replace=(f"{device_id} {media_mount_point} ext4 defaults,auto,users,rw,nofail 0 0"),
    present=True,
    _sudo=True,
)

server.shell(
    name="Ensure all filesystems in /etc/fstab are mounted",
    commands=["mount -a"],
    _sudo=True,
)

for path in [
    transmission_dir_downloading,
    transmission_dir_completed,
]:
    files.directory(
        name=f"Ensure Transmission dir: {path}",
        path=path,
        present=True,
    )


#
# Transmission
# https://pimylifeup.com/raspberry-pi-transmission/
# https://askubuntu.com/questions/290943/transmission-daemon-error-loading-working-config-file-user-priveliges
#

apt.packages(
    name="Ensure transmission-daemon is installed",
    packages=["transmission-daemon"],
    update=True,
    _sudo=True,
)

# Ensure Transmission is stopped while we re-configure it;
# otherwise it will overwrite what we've written when
# it gets restarted further down this module.

systemd.service(
    name="Ensure Transmission is not running during configuration",
    service="transmission-daemon",
    running=False,
    _sudo=True,
)

transmission_config_items = {
    "incomplete-dir": f'"{transmission_dir_downloading}"',
    "incomplete-dir-enabled": "true",
    "download-dir": f'"{transmission_dir_completed}"',
    "rpc-password": f'"{transmission_rpc_password}"',
    "rpc-username": f'"{transmission_rpc_username}"',
    "rpc-whitelist": f'"{transmission_rpc_whitelist}"',
    "rpc-whitelist-enabled": "true",
}

for key, value in transmission_config_items.items():
    files.line(
        name=f"Configure {key}",
        path="/etc/transmission-daemon/settings.json",
        line=f'"{key}"',
        replace=f'"{key}": {value},',
        present=True,
        _sudo=True,
    )


files.line(
    name="Fix USER in /etc/init.d/transmission-daemon",
    path="/etc/init.d/transmission-daemon",
    line="^USER=.*$",
    replace=f"USER={transmission_service_user}",
    present=True,
    _sudo=True,
)

systemd_files = [
    "/etc/systemd/system/multi-user.target.wants/transmission-daemon.service",
    "/lib/systemd/system/transmission-daemon.service",
]

for systemd_file in systemd_files:
    files.line(
        name=f"Fix user in {systemd_file}",
        path=systemd_file,
        line="^[Uu]ser=.*$",
        replace=f"User={transmission_service_user}",
        present=True,
        _sudo=True,
    )

systemd.daemon_reload(
    _sudo=True,
)

files.directory(
    name=f"Ensure {transmission_service_user} owns /etc/transmission-daemon",
    path="/etc/transmission-daemon",
    present=True,
    user=transmission_service_user,
    group=transmission_service_user,
    recursive=True,
    _sudo=True,
)

files.directory(
    name=f"Ensure {transmission_service_user} owns /var/lib/transmission-daemon",
    path="/var/lib/transmission-daemon",
    present=True,
    user=transmission_service_user,
    group=transmission_service_user,
    recursive=True,
    _sudo=True,
)

files.directory(
    name=f"Ensure Transmission config dir in {transmission_service_user} home dir",
    path=f"/home/{transmission_service_user}/.config/transmission-daemon/",
    present=True,
    user=transmission_service_user,
    group=transmission_service_user,
    recursive=True,
    _sudo=True,
)

files.link(
    name="Ensure symlink in config dir",
    path=f"/home/{transmission_service_user}/.config/transmission-daemon/settings.json",
    target="/etc/transmission-daemon/settings.json",
)

files.directory(
    name=f"Ensure {transmission_service_user} owns config dir",
    path=f"/home/{transmission_service_user}/.config/transmission-daemon/",
    present=True,
    user=transmission_service_user,
    group=transmission_service_user,
    recursive=True,
    _sudo=True,
)

systemd.service(
    name="Ensure Transmission is not running during configuration",
    service="transmission-daemon",
    running=True,
    _sudo=True,
)
