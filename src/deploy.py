from pyinfra import host
from pyinfra.operations import apt, files, server, systemd

#
# Variables
#

media_mount_point = "/media"
device_id = f"PARTUUID={host.data.media_device_partition_uuid}"

transmission_downloading = f"{media_mount_point}/downloading"
transmission_new = f"{media_mount_point}/new"


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

for path in [transmission_downloading, transmission_new]:
    files.directory(
        name=f"Ensure Transmission dir: {path}",
        path=path,
        present=True,
    )


#
# Transmission
# https://pimylifeup.com/raspberry-pi-transmission/
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

files.line(
    name="Configure incomplete-dir",
    path="/etc/transmission-daemon/settings.json",
    line='"incomplete-dir"',
    replace=f'"incomplete-dir": "{transmission_downloading}",',
    present=True,
    _sudo=True,
)

files.line(
    name="Enable incomplete-dir",
    path="/etc/transmission-daemon/settings.json",
    line='"incomplete-dir-enabled"',
    replace='"incomplete-dir-enabled": true,',
    present=True,
    _sudo=True,
)

files.line(
    name="Configure download-dir",
    path="/etc/transmission-daemon/settings.json",
    line='"download-dir"',
    replace=f'"download-dir": "{transmission_new}",',
    present=True,
    _sudo=True,
)

systemd.service(
    name="Ensure Transmission is not running during configuration",
    service="transmission-daemon",
    running=True,
    _sudo=True,
)
