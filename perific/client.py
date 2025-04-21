import aiohttp
from pydantic import BaseModel, Field

class Token(BaseModel):
    token: str = Field(alias="Token")
    created: str = Field(alias="Created")
    valid_to: str = Field(alias="ValidTo")
    
class Item(BaseModel):
    id: int = Field(alias="ItemId")
    name: str = Field(alias="Name")
    system_name: str|None = Field(alias="SystemName")
    item_category: str = Field(alias="ItemCategory")
    item_type: str = Field(alias="ItemType")
    item_sub_type: str = Field(alias="ItemSubType")
    mac_address: str = Field(alias="MacAddress")
    time_zone: str = Field(alias="TimeZone")
    creation_time: str = Field(alias="CreationTime")
    
class AccountOverviewResponse(BaseModel):
    items: list[Item] = Field(alias="Items")

class ItemPacketData(BaseModel):
    dv: int = Field(alias="dv")
    """
    Amp
    """
    hiavg: list[float] = Field(alias="hiavg")
    """
    Voltage
    """
    huavg: list[float] = Field(alias="huavg")
    #himin: list[float] = Field(alias="himin")
    #himax: list[float] = Field(alias="himax")

class ItemPacket(BaseModel):
    hdr: int = Field(alias="hdr")
    iid: int = Field(alias="iid")
    ts: int = Field(alias="ts")
    seqno: int = Field(alias="seqno")
    it: str = Field(alias="it")
    pv: int = Field(alias="pv")
    fw: str = Field(alias="fw")
    rssi: int = Field(alias="rssi")
    data: ItemPacketData = Field(alias="data")

class LatestPackets(BaseModel):
    phase_day: ItemPacket = Field(alias="PhaseDay")
    phase_hour: ItemPacket = Field(alias="PhaseHour")
    phase_minute: ItemPacket = Field(alias="PhaseMinute")
    phase_real_time: ItemPacket = Field(alias="PhaseRealTime")

class LatestItemPackets(BaseModel):
    item_id: int = Field(alias="ItemId")
    latest_packets: LatestPackets = Field(alias="LatestPackets")
        

class Client:
    
    def __init__(self, host: str):
        self.host = host
        
    async def authenticate(self, username: str, password: str) -> Token:
        # PUT https://api.enegic.com/createtoken
        # Payload: {"username": "your_username", "password": "your_password"}
        # Example response:
        # "TokenInfo": {
        #     "Token": "<token>",
        #     "Created": "2025-04-21T07:04:40.8966467Z",
        #     "ValidTo": "2026-04-21T07:04:40.8966468Z"
        # },
        url = f"{self.host}/createtoken"
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url,
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token_info = data.get("TokenInfo")
                    if token_info:
                        token_instance = Token(**token_info)
                        return token_instance
                    else:
                        raise Exception("Invalid response: TokenInfo not found")
                else:
                    raise Exception(f"Authentication failed: {response.status} {response.text}")        
    
    async def getLatestPackets(self, token: str) -> list[LatestItemPackets]:
        # GET https://api.enegic.com/getlatestpackets
        # Headers
        # Authorization
        url = f"{self.host}/getlatestpackets"
        headers = {
            "X-Authorization": token,
            "Content-Type": "application/json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    latest_packets = [LatestItemPackets(**item) for item in data]
                    return latest_packets
                else:
                    raise Exception(f"Failed to get latest packets: {response.status} {response.text}")
    
    async def getAccountOverview(self, token: str) -> AccountOverviewResponse:
        # GET https://api.enegic.com/getaccountoverview
        # Headers
        # Authorization: <token>
        url = f"{self.host}/getaccountoverview"
        headers = {
            "X-Authorization": token,
            "Content-Type": "application/json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    account_overview = AccountOverviewResponse(**data)
                    return account_overview
                else:
                    raise Exception(f"Failed to get account overview: {response.status} {response.text}")