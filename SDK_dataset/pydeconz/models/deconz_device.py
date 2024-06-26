"""Python library to connect deCONZ and Home Assistant to work together."""

from api import APIItem


class DeconzDevice(APIItem):
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    @property
    def etag(self) -> str:
        """HTTP etag change on any action to the device."""
        raw: dict[str, str] = self.raw
        return raw.get("etag") or ""

    @property
    def manufacturer(self) -> str:
        """Device manufacturer."""
        raw: dict[str, str] = self.raw
        return raw.get("manufacturername") or ""

    @property
    def model_id(self) -> str:
        """Device model."""
        raw: dict[str, str] = self.raw
        return raw.get("modelid") or ""

    @property
    def name(self) -> str:
        """Name of the device."""
        raw: dict[str, str] = self.raw
        return raw.get("name") or ""

    @property
    def software_version(self) -> str:
        """Firmware version."""
        raw: dict[str, str] = self.raw
        return raw.get("swversion") or ""

    @property
    def type(self) -> str:
        """Human readable type of the device."""
        raw: dict[str, str] = self.raw
        return raw.get("type") or ""

    @property
    def unique_id(self) -> str:
        """Id for unique device identification."""
        raw: dict[str, str] = self.raw
        return raw.get("uniqueid") or ""
