import logging
from .perific import Client, Item, LatestItemPackets, Token

_LOGGER = logging.getLogger(__name__)

class Hub:

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host
        self.client = Client(host)
        self.token: Token = None
        

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        try:
            self.token = await self.client.authenticate(username, password)
            if not self.token:
                _LOGGER.error("Authentication failed")
                return False
        except Exception as e:
            _LOGGER.error("Error during authentication: %s", e)
            return False
        return True
    
    async def fetch_devices(self) -> list[Item]:
        """"""
        overview = await self.client.getAccountOverview(self.token.token)
        return overview.items

    async def get_sensor_data(self) -> list[LatestItemPackets] | None:
        """Get sensor data for a specific device and type."""
        try:
            latest_packets = await self.client.getLatestPackets(self.token.token)
            return latest_packets
        except Exception as e:
            _LOGGER.error("Error fetching sensor data: %s", e)
        return None