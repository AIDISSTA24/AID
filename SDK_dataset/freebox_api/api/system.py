class System:
    def __init__(self, access):
        self._access = access

    async def get_config(self):
        """
        Get system configuration:
        """
        return self._access.get("system/")

    async def reboot(self):
        """
        Reboot freebox
        """
        self._access.post("system/reboot")
