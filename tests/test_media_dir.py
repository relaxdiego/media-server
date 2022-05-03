def test_happy_path(host):
    media_dir = host.file("/media")

    assert media_dir.exists
    assert media_dir.is_directory
