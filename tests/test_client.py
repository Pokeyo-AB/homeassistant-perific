import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import AsyncMock, patch
from perific.client import Client, Token, AuthenticationError

"""
Tests for perific.client.Client class.

Covers:
- authenticate() method (valid, invalid, unauthorized)
- getAccountOverview() method (success, unauthorized, server error)
- getLatestPackets() method (success, unauthorized, server error)

All tests use pytest and unittest.mock.AsyncMock to simulate aiohttp responses.
"""

# ============================================================
# Tests for authenticate() method
# ============================================================

#Valid
@pytest.mark.asyncio
async def test_authenticate_success():
    """Should return a valid Token object when authentication succeeds."""
    client = Client("https://api.enegic.com")

    fake_response = {
        "TokenInfo": {
            "Token": "fake123",
            "Created": "2025-04-21T07:04:40.896Z",
            "ValidTo": "2026-04-21T07:04:40.896Z"
        }
    }

    with patch("aiohttp.ClientSession.put") as mock_put:
        mock_put.return_value.__aenter__.return_value.status = 200
        mock_put.return_value.__aenter__.return_value.json = AsyncMock(return_value=fake_response)

        token = await client.authenticate("user", "pass")

        assert isinstance(token, Token)
        assert token.token == "fake123"

#Invalid
@pytest.mark.asyncio
async def test_authenticate_invalid_response():
    """Should raise Exception when API response is missing TokenInfo."""
    client = Client("https://api.enegic.com")

    fake_response = {"SomethingMore": "err"}

    with patch("aiohttp.ClientSession.put") as mock_put:
        mock_put.return_value.__aenter__.return_value.status = 200
        mock_put.return_value.__aenter__.return_value.json = AsyncMock(return_value=fake_response)

        with pytest.raises(Exception) as exc:
            await client.authenticate("user", "pass")

        assert "TokenInfo not found" in str(exc.value)

 #unauthorized
@pytest.mark.asyncio
async def test_authenticate_unauthorized():
    """Should raise Exception when API returns 401 Unauthorized."""
    client = Client("https://api.enegic.com")

    with patch("aiohttp.ClientSession.put") as mock_put:
        mock_put.return_value.__aenter__.return_value.status = 401
        mock_put.return_value.__aenter__.return_value.text = AsyncMock(return_value="Unauthorized")

        with pytest.raises(Exception) as exc:
            await client.authenticate("user", "wrongpass")

        assert "Authentication failed" in str(exc.value)
# ============================================================
# Tests for getAccountOverview() method
# ============================================================

#success
@pytest.mark.asyncio
async def test_get_account_overview_success():
    """Should return AccountOverviewResponse when API returns valid JSON."""
    client = Client("https://api.enegic.com")

    fake_response = {
        "Items": [
            {
                "ItemId": 1,
                "Name": "Device 01",
                "SystemName": "SYS-A",
                "ItemCategory": "Sensor",
                "ItemType": "Type-A",
                "ItemSubType": "Sub-A",
                "MacAddress": "00:11:22:33:44:55",
                "TimeZone": "UTC",
                "CreationTime": "2025-04-21T07:04:40.896Z"
            }
        ]
    }

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=fake_response)

        result = await client.getAccountOverview("fake_token")

        assert result.items[0].name == "Device 01"
        assert result.items[0].mac_address == "00:11:22:33:44:55"


#unauthorized
@pytest.mark.asyncio
async def test_get_account_overview_unauthorized():
    """Should raise AuthenticationError when API returns 401 Unauthorized."""
    client = Client("https://api.enegic.com")

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 401

        with pytest.raises(AuthenticationError) as exc: 
            await client.getAccountOverview("invalid_token")

        assert "Unauthorized access" in str(exc.value) 


# server error
@pytest.mark.asyncio
async def test_get_account_overview_server_error():
    """Should raise Exception when API returns 500."""
    client = Client("https://api.enegic.com")

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 500
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="Internal Server Error")

        with pytest.raises(Exception) as exc:
            await client.getAccountOverview("fake_token")

        assert "Failed to get account overview" in str(exc.value)
# ============================================================
# Tests for getLatestPackets() method
# ============================================================
#success
@pytest.mark.asyncio
async def test_get_latest_packets_success():
    """Should return a list of LatestItemPackets when API returns valid JSON."""
    client = Client("https://api.enegic.com")

    fake_response = [
        {
            "ItemId": 1,
            "LatestPackets": {
                "PhaseDay": {
                    "hdr": 1, "iid": 10, "ts": 12345, "seqno": 1, "it": "test",
                    "pv": 5, "fw": "1.0", "rssi": -30, "data": {"dv": 10}
                },
                "PhaseHour": None,
                "PhaseMinute": None,
                "PhaseRealTime": None
            }
        }
    ]

    with patch("aiohttp.ClientSession.put") as mock_put:
        mock_put.return_value.__aenter__.return_value.status = 200
        mock_put.return_value.__aenter__.return_value.json = AsyncMock(return_value=fake_response)

        result = await client.getLatestPackets("fake_token")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].item_id == 1
        assert result[0].latest_packets.phase_day.hdr == 1


#unauthorized
@pytest.mark.asyncio
async def test_get_latest_packets_unauthorized():
    """Should raise AuthenticationError when API returns 401 Unauthorized."""
    client = Client("https://api.enegic.com")

    with patch("aiohttp.ClientSession.put") as mock_put:
        mock_put.return_value.__aenter__.return_value.status = 401

        with pytest.raises(AuthenticationError) as exc:
            await client.getLatestPackets("invalid_token")

        assert "Failed to get latest packets" in str(exc.value) or "Unauthorized" in str(exc.value)


#server error
@pytest.mark.asyncio
async def test_get_latest_packets_server_error():
    """Should raise Exception when API returns 500."""
    client = Client("https://api.enegic.com")

    with patch("aiohttp.ClientSession.put") as mock_put:
        mock_put.return_value.__aenter__.return_value.status = 500
        mock_put.return_value.__aenter__.return_value.text = AsyncMock(return_value="Internal Server Error")

        with pytest.raises(Exception) as exc:
            await client.getLatestPackets("fake_token")

        assert "Failed to get latest packets" in str(exc.value)

