class Freeplug:
    def __init__(self, access):
        self._access = access

    async def get_freeplug_networks(self):
        """
        Get freeplug networks
        """
        return self._access.get("freeplug/")

    async def reset_freeplug(self, freeplug_id):
        """
        Reset freeplug
        """
        self._access.post(f"freeplug/{freeplug_id}/reset/")
