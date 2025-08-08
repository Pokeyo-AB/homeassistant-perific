import logging
from .perific import Client, Item, LatestItemPackets, Token
from .perific.client import AuthenticationError

_LOGGER = logging.getLogger(__name__)

class Hub:

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host
        self.client = Client(host)
        self.token: Token = None
        self.username: str = None
        self.password: str = None
        

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
        self.username = username
        self.password = password
        _LOGGER.info("Authentication successful for user: %s", username)
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
        except AuthenticationError:
            _LOGGER.error("Authentication failed")
            if not self.username or not self.password:
                _LOGGER.error("Username or password not set for re-authentication")
                return None
            await self.authenticate(self.username, self.password)
            return await self.client.getLatestPackets(self.token.token)
        except Exception as e:
            _LOGGER.exception("Unhandled error in get_sensor_data for user '%s': %s", self.username, e)
            return None
