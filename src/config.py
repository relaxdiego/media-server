from pydantic import BaseModel


class MediaDeviceConfig(BaseModel):
    mount_point: str
    device_id: str


class TransmissionConfigSettings(BaseModel):
    incomplete_dir: str
    incomplete_dir_enabled: bool
    download_dir: str
    rpc_username: str
    rpc_password: str
    rpc_whitelist: str

    def to_json_value(self, attr):
        val = getattr(self, attr)

        if isinstance(val, bool) and val is True:
            val = "true"
        elif isinstance(val, bool):
            val = "false"
        elif isinstance(val, str):
            val = f'"{val}"'

        return val


class TransmissionConfigService(BaseModel):
    user: str


class TransmissionConfig(BaseModel):
    settings: TransmissionConfigSettings
    service: TransmissionConfigService


class ConfigFile(BaseModel):
    media_device: MediaDeviceConfig
    transmission: TransmissionConfig
