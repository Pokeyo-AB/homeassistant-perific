"""Perific API client wrapper (sync OpenAPI client wrapped for HA)."""
from __future__ import annotations

import logging
from typing import Any, List

from homeassistant.core import HomeAssistant

from .openapi_client.api_client import ApiClient
from .openapi_client.configuration import Configuration
from .openapi_client.api.default_api import DefaultApi
from .openapi_client.models.token_info import TokenInfo
from .openapi_client.models.item import Item
from .openapi_client.models.latest_item_packets import LatestItemPackets
from .openapi_client.models.authenticate_request import AuthenticateRequest
from .openapi_client.exceptions import ApiException
from .openapi_client.models.getlatestpackets_request import GetlatestpacketsRequest

_LOGGER = logging.getLogger(__name__)

class PerificDevice:
    #Wrapper around a Perific device with metadata + metrics.

    def __init__(self, device: Item) -> None:
        # Use PascalCase fields from OpenAPI schema
        self.id = getattr(device, "item_id", None)
        self.name = getattr(device, "name", None) or f"Perific {self.id}"
        self.mac = getattr(device, "mac_address", None)
        self.time_zone = getattr(device, "time_zone", None)
        # Firmware/hardware placeholders
        self.fw = getattr(device, "firmware", None)
        self.hw = getattr(device, "hardware", None)
        self.metrics: dict[str, Any] = {}
        # New attributes to handle other metadata
        self.system_name = getattr(device, "system_name", None)
        self.item_category = getattr(device, "item_category", None)
        self.item_type = getattr(device, "item_type", None)
        self.item_sub_type = getattr(device, "item_sub_type", None)
        self.creation_time = getattr(device, "creation_time", None)


    def update_metrics(self, packets: LatestItemPackets) -> None:
        #Extract metrics from LatestItemPackets into flat metric dict.
        lp = getattr(packets, "latest_packets", None)
        lp_dict = lp.to_dict() if hasattr(lp, "to_dict") else lp
        if not isinstance(lp_dict, dict):
            _LOGGER.debug("Unexpected latest_packets type: %r", type(lp))
            return

        metric_keys = {
            "huavg": "voltage",
            "hiavg": "current_avg_high",
            "pavg": "power",
            "freq": "frequency",
            "pf": "pf",
            "energy": "energy",
            "iavg": "current_avg",
            "imin": "current_min",
            "imax": "current_max",
            "qmin": "reactive_power_min",
            "qmax": "reactive_power_max",
            "eyepmin": "energy_positive_min",
            "eyepmax": "energy_positive_max",
            "eyepavg": "energy_positive_avg",
            "eyeemin": "energy_negative_min",
            "eyeemax": "energy_negative_max",
        }

        for source_name, source_model in lp_dict.items():
            data = getattr(source_model, "data", None)
            if data is None:
                continue

            for api_key, metric_name in metric_keys.items():
                value = getattr(data, api_key, None)
                if isinstance(value, list) and value:
                    # Store all 4 values separately (L1, L2, L3, N)
                    for idx, phase in enumerate(["L1", "L2", "L3", "N"]):
                        if idx < len(value):
                            key = f"{source_name.lower()}_{metric_name}_{phase}"
                            self.metrics[key] = value[idx]


class PerificHub:
    #Hub that talks to Perific API using the generated sync client (run in executor).

    def __init__(self, hass: HomeAssistant, host: str, username: str, password: str) -> None:
        self.hass = hass
        self.host = host
        self.username = username
        self.password = password

        self._config = Configuration(host=self.host)
        self._api: DefaultApi | None = None
        self._token: TokenInfo | None = None

    async def authenticate(self) -> bool:
        #Authenticate and store it for subsequent calls.
        if hasattr(self, "_token") and self._token:
            _LOGGER.debug("Perific: reusing existing valid token.")
            return True
        if self._token is not None:
            _LOGGER.debug("Perific: reusing existing valid token.")
            return True  # reuse existing token
        def _do_auth() -> TokenInfo: # Changed return type
            _LOGGER.debug("Attempting to get auth token...")
            with ApiClient(self._config) as api_client:
                api = DefaultApi(api_client)
                req = AuthenticateRequest(username=self.username, password=self.password)
                _LOGGER.debug("Sending authentication request with username: %s", self.username)
                return api.authenticate(req)
        try:
            auth_response = await self.hass.async_add_executor_job(_do_auth) # Changed variable name
            # Access the TokenInfo object and the token from it
            token_info = getattr(auth_response, "token_info", None)
            token_value = getattr(token_info, "token", None)
            _LOGGER.debug("Perific auth API error: TOKEN_INFO: %s ", token_info)
            _LOGGER.debug("Perific auth API error: TOKEN_VALUE: %s", token_value)
            if not token_info or not token_value:
                _LOGGER.debug("Perific: empty token from authenticate(). The API returned an invalid token.")
                return False
            #self._config.access_token = token_value
            #self._config.api_key["X-Authorization"] = token_value
            #self._config.api_key_prefix = {}
            # Set X-Authorization for all subsequent requests
            self._config.api_key["X-Authorization"] = token_value
            self._config.api_key_prefix["X-Authorization"] = ""
            _LOGGER.debug("Perific API config before defaultapiclient init: host=%s, api_key=%s, api_key_prefix=%s, headers=%s",getattr(self._config, "host", None),self._config.api_key,self._config.api_key_prefix,getattr(self._config, "default_headers", None))
            try:
                self._api = DefaultApi(ApiClient(self._config))
                _LOGGER.debug("Perific API client successfully initialized.")
            except Exception as e:
                _LOGGER.exception("Failed to initialize Perific API client: %s", e)
                raise
            #self._api = DefaultApi(ApiClient(self._config))
            self._token = token_info
            _LOGGER.debug("Authentication successful. Token stored.")
            return True
        except ApiException as e:
            _LOGGER.error("Perific auth API error: HTTP %s - %s", e.status, e.body)
            return False
        except Exception as e:
            _LOGGER.exception("Perific auth unexpected error during authentication.")
            return False

    async def async_get_devices(self) -> list[PerificDevice]:
        # Fetch account overview and wrap Items
        if not self._api:
            raise RuntimeError("Not authenticated")

        def _get_overview_items() -> list[Item]:
            from .openapi_client.api_client import ApiClient
            from .openapi_client.api.default_api import DefaultApi
            from urllib.parse import urljoin

            if not self._token or not getattr(self._token, "token", None):
                _LOGGER.debug("Token missing, quitting...")
                return []

            # Ensure token is in config
            self._config.api_key['x_authorization'] = self._token.token
            self._config.api_key_prefix['x_authorization'] = ''
            _LOGGER.debug("Using token: %s", self._token.token)

            # Reuse existing DefaultApi or create once
            if self._api is None:
                self._api = DefaultApi(ApiClient(self._config))
                _LOGGER.debug("Created new DefaultApi instance")
    
            api = self._api

            # Patch logging once
            if not getattr(api, "_logging_patched", False):
                original_call_api = api.api_client.call_api

                def logging_call_api(self, resource_path, method, *args, **kwargs):
                    _LOGGER.debug("Perific API call: %s %s", method, urljoin(self.configuration.host, resource_path))
                    _LOGGER.debug("call_api args: %s", args)
                    _LOGGER.debug("call_api kwargs: %s", kwargs)
                    response = original_call_api(resource_path, method, *args, **kwargs)
                    try:
                        _LOGGER.debug("Response status: %s, body: %s", getattr(response, "status", None), getattr(response, "data", None))
                    except Exception as e:
                        _LOGGER.debug("Failed logging response: %s", e)
                    return response

                api.api_client.call_api = logging_call_api.__get__(api.api_client, type(api.api_client))
                api._logging_patched = True

            try:
                _LOGGER.debug("Fetching account overview")
                overview = api.getaccountoverview("application/json")
                items = getattr(overview, "items", []) or []
                _LOGGER.debug("Overview items: %s", items)
                return items
            except Exception as e:
                _LOGGER.error("Failed to fetch overview items: %s", e)
                return []


        # Execute in executor since it’s synchronous
        try:
            items: list[Item] = await self.hass.async_add_executor_job(_get_overview_items)
            return [PerificDevice(d) for d in items if isinstance(d, Item)]
        except Exception as e:
            _LOGGER.error("Perific get devices unexpected error: %s", e)
            return []
  
    async def async_update_device_metrics(self, device: PerificDevice) -> None:
        #Fetch latest packets and update metrics for one device.
        if not self._api:
            raise RuntimeError("Not authenticated")

        def _get_packets() -> list[LatestItemPackets]:
            if not self._token or not getattr(self._token, "token", None):
                _LOGGER.debug("Token missing, quitting...")
                return []

            # Ensure token is in config (lowercase!)
            self._config.api_key['x_authorization'] = self._token.token
            self._config.api_key_prefix['x_authorization'] = ''
            _LOGGER.debug("Using token: %s", self._token.token)
            # Reuse existing DefaultApi or create once
            if self._api is None:
                self._api = DefaultApi(ApiClient(self._config))
                _LOGGER.debug("Created new DefaultApi instance")

            api = self._api

            # Patch logging once
            if not getattr(api, "_logging_patched", False):
                original_call_api = api.api_client.call_api

                def logging_call_api(self, resource_path, method, *args, **kwargs):
                    _LOGGER.debug(
                        "Perific API call: %s %s",
                        method,
                        urljoin(self.configuration.host, resource_path),
                    )
                    _LOGGER.debug("call_api args: %s", args)
                    _LOGGER.debug("call_api kwargs: %s", kwargs)
                    response = original_call_api(resource_path, method, *args, **kwargs)
                    try:
                        _LOGGER.debug(
                            "Response status: %s, body: %s",
                            getattr(response, "status", None),
                            getattr(response, "data", None),
                        )
                    except Exception as e:
                        _LOGGER.error("Failed logging response: %s", e)
                    return response

                api.api_client.call_api = logging_call_api.__get__(api.api_client, type(api.api_client))
                api._logging_patched = True

            try:
                
                #request_body = {"item_id": device.id}  # send item_id as request body
                #return api.getlatestpackets(request_body)
                #return api.getlatestpackets(request_body=request_body, content_type="application/json")
                #return api.getlatestpackets(request_body,x_authorization=self._config.api_key["X-Authorization"])

                request_obj = GetlatestpacketsRequest(item_id=device.id)
                _LOGGER.debug("Request object for getlatestpackets: %s", request_obj)
                #response: list[LatestItemPackets] = api.getlatestpackets(getlatestpackets_request=request_obj)
                response: list[LatestItemPackets] = api.getlatestpackets(getlatestpackets_request=request_obj)
                #response = api.getlatestpackets(getlatestpackets_request=request_obj)
                _LOGGER.debug("Device.id ItemId %s", device.id)
                _LOGGER.debug("Raw API response: %s",  response)
                _LOGGER.debug("Response0: %s", response[0])
                ## Return the first packet from the list if it exists.
                #if response and response[0]:
                #    return response[0]
                # The API returns a list, even for a single device request.
                if response and response[0]:
                    response[0].item_id = device.id
                    # This will now use the first item in the list, regardless of the item_id in the response.
                    return response[0]

                #response = api.getlatestpackets(request_body,content_type="application/json")
                #_LOGGER.error("Raw API response for device %s: %s", device.id, response)
                #return response
                #return api.getlatestpackets(request_body,content_type="application/json")
            except Exception as e:
                _LOGGER.error("Failed to fetch latest packets for device %s: %s", device.id, e)
                return []


        try:
            #packets_list: list[LatestItemPackets] = await self.hass.async_add_executor_job(_get_packets)
            #for pkt in packets_list or []:
            #    if getattr(pkt, "ItemId", None) == device.id:
            #        device.update_metrics(pkt)
            #        break
            # Get the single packet and update the device.
            packet = await self.hass.async_add_executor_job(_get_packets)
            packet.item_id = device.id
            _LOGGER.debug("Packet %s", packet)
            if packet:
                device.update_metrics(packet)

        except ApiException as e:
            _LOGGER.error("Perific latest packets API error for %s: %s", device.id, e)
            raise
        except Exception as e:
            _LOGGER.error("Perific latest packets unexpected error for %s: %s", device.id, e)
            raise
