def test_happy_path(host, config):
    media_dir = host.file(config.media_device.mount_point)

    assert media_dir.exists
    assert media_dir.is_directory
