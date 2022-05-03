import requests

testinfra_hosts = ["localhost"]


def test_access_to_transmission_web_interface(config):
    response = requests.get(
        f"http://{config.host}:9091",
        auth=(
            config.transmission.settings.rpc_username,
            config.transmission.settings.rpc_password,
        ),
        verify=False,
    )

    assert response.status_code == 200
