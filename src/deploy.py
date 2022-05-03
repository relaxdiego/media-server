from pyinfra import host
from pyinfra.operations import apt, files, server, systemd

media = host.data.media_device
transmission = host.data.transmission

#
# Storage
#

files.line(
    name="Ensure /etc/fstab has media mount point",
    path="/etc/fstab",
    line=media.mount_point,
    replace=(
        f"{media.device_id} {media.mount_point} ext4 defaults,auto,users,rw,nofail 0 0"
    ),
    present=True,
    _sudo=True,
)

server.shell(
    name="Ensure all filesystems in /etc/fstab are mounted",
    commands=["mount -a"],
    _sudo=True,
)

for path in [
    transmission.settings.incomplete_dir,
    transmission.settings.download_dir,
]:
    files.directory(
        name=f"Ensure Transmission dir: {path}",
        path=path,
        present=True,
    )


#
# Transmission
#
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

settings = transmission.settings
transmission_config_items = {
    "incomplete-dir": settings.to_json_value("incomplete_dir"),
    "incomplete-dir-enabled": settings.to_json_value("incomplete_dir_enabled"),
    "download-dir": settings.to_json_value("download_dir"),
    "rpc-password": settings.to_json_value("rpc_password"),
    "rpc-username": settings.to_json_value("rpc_username"),
    "rpc-whitelist": settings.to_json_value("rpc_whitelist"),
    "rpc-whitelist-enabled": "true",
    "ratio-limit": 2,
    "ratio-limit-enabled": "true",
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
    replace=f"USER={transmission.service.user}",
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
        replace=f"User={transmission.service.user}",
        present=True,
        _sudo=True,
    )

systemd.daemon_reload(
    _sudo=True,
)

files.directory(
    name=f"Ensure {transmission.service.user} owns /etc/transmission-daemon",
    path="/etc/transmission-daemon",
    present=True,
    user=transmission.service.user,
    group=transmission.service.user,
    recursive=True,
    _sudo=True,
)

files.directory(
    name=f"Ensure {transmission.service.user} owns /var/lib/transmission-daemon",
    path="/var/lib/transmission-daemon",
    present=True,
    user=transmission.service.user,
    group=transmission.service.user,
    recursive=True,
    _sudo=True,
)

files.directory(
    name=f"Ensure Transmission config dir in {transmission.service.user} home dir",
    path=f"/home/{transmission.service.user}/.config/transmission-daemon/",
    present=True,
    user=transmission.service.user,
    group=transmission.service.user,
    recursive=True,
    _sudo=True,
)

files.link(
    name="Ensure symlink in config dir",
    path=f"/home/{transmission.service.user}/.config/transmission-daemon/settings.json",
    target="/etc/transmission-daemon/settings.json",
)

files.directory(
    name=f"Ensure {transmission.service.user} owns config dir",
    path=f"/home/{transmission.service.user}/.config/transmission-daemon/",
    present=True,
    user=transmission.service.user,
    group=transmission.service.user,
    recursive=True,
    _sudo=True,
)

systemd.service(
    name="Ensure Transmission is not running during configuration",
    service="transmission-daemon",
    running=True,
    _sudo=True,
)

#
# Plex Media Server
#
# https://pimylifeup.com/raspberry-pi-plex-server/

apt.packages(
    name="Ensure plex package prerequisites",
    packages=["apt-transport-https"],
    update=True,
    cache_time=3600,  # seconds
    _sudo=True,
)

plex_pubkey_path = "/root/PlexSign.key"

# We go through files.download first so that we can md5sum it
files.download(
    name="Download Plex apt repo pubkey",
    src="https://downloads.plex.tv/plex-keys/PlexSign.key",
    dest=plex_pubkey_path,
    md5sum="19930ce0357f723e590210e3101321a3",
    _sudo=True,
)

apt.key(
    name="Add Plex apt repo pubkey",
    src=plex_pubkey_path,
    _sudo=True,
)

apt.repo(
    name="Ensure Plex apt repo",
    src="deb https://downloads.plex.tv/repo/deb public main",
    _sudo=True,
)

apt.packages(
    name="Ensure plex package",
    packages=["plexmediaserver"],
    update=True,
    cache_time=3600,  # seconds
    _sudo=True,
)
