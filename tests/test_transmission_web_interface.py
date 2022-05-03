import requests

testinfra_hosts = ["localhost"]


def test_access_to_transmission_web_interface():
    response = requests.get(
        "http://10.10.1.37:9091",
        auth=(
            "transmission",
            "password",
        ),
        verify=False,
    )

    assert response.status_code == 200
