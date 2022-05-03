def test_service_is_running(host):
    service = host.service("transmission-daemon")

    assert service.is_running
