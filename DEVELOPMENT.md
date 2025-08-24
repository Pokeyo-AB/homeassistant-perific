# How to create the openapi_client


1. Create perific_api.yaml, get the link to the file (ie https://raw.githubusercontent.com/Pokeyo-AB/homeassistant-perific/refs/heads/main/perific_api.yaml)
2. Create the openapi_client:
3. mkdir /local
4. docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate -i https://raw.githubusercontent.com/Pokeyo-AB/homeassistant-perific/refs/heads/main/perific_api.yaml   -g python  -o /local/perific/python --enable-post-process-file
5. copy the directory openapi_client to your repo in subdirectory openapi_client

## Fix the "paths" in the generated code:
```
TO DO:
I don't know how the fix this problem with paths to the file and what HA expect in custom_component
So you need to either fix openapi-generate command or do i manually as below:
```
api/__init__.py:
```
from openapi_client.api.default_api import DefaultApi
TO:
from .default_api import DefaultApi
```
api/default_api-py:
```from openapi_client.models.account_overview_response import AccountOverviewResponse
from openapi_client.models.auth_response import AuthResponse
from openapi_client.models.authenticate_request import AuthenticateRequest
from openapi_client.models.getlatestpackets_request import GetlatestpacketsRequest
from openapi_client.models.latest_item_packets import LatestItemPackets

from openapi_client.api_client import ApiClient, RequestSerialized
from openapi_client.api_response import ApiResponse
from openapi_client.rest import RESTResponseType
TO:
from ..models.account_overview_response import AccountOverviewResponse
from ..models.auth_response import AuthResponse
from ..models.authenticate_request import AuthenticateRequest
from ..models.getlatestpackets_request import GetlatestpacketsRequest
from ..models.latest_item_packets import LatestItemPackets

from ..api_client import ApiClient, RequestSerialized
from ..api_response import ApiResponse
from ..rest import RESTResponseType
```
models/__init__.py:
```
from openapi_client.models.account_overview_response import AccountOverviewResponse
from openapi_client.models.auth_response import AuthResponse
from openapi_client.models.authenticate_request import AuthenticateRequest
from openapi_client.models.getlatestpackets_request import GetlatestpacketsRequest
from openapi_client.models.item import Item
from openapi_client.models.latest_item_packets import LatestItemPackets
from openapi_client.models.latest_packets import LatestPackets
from openapi_client.models.latest_packets_data import LatestPacketsData
from openapi_client.models.token_info import TokenInfo
TO:
from .account_overview_response import AccountOverviewResponse
from .auth_response import AuthResponse
from .authenticate_request import AuthenticateRequest
from .getlatestpackets_request import GetlatestpacketsRequest
from .item import Item
from .latest_item_packets import LatestItemPackets
from .latest_packets import LatestPackets
from .latest_packets_data import LatestPacketsData
from .token_info import TokenInfo
```
models/account_overview_response.py
```from openapi_client.models.item import Item
TO:
from .item import Item
```
models/auth_response.py
```
from openapi_client.models.token_info import TokenInfo
TO:
from .token_info import TokenInfo
```
models/latest_item_packets.py
```
from openapi_client.models.latest_packets import LatestPackets
TO:
from .latest_packets import LatestPackets
```
models/latest_packets.py
```
from openapi_client.models.latest_packets_data import LatestPacketsData
TO:
from .latest_packets_data import LatestPacketsData
```
__init__.py
```
# import apis into sdk package
from openapi_client.api.default_api import DefaultApi as DefaultApi
# import ApiClient
from openapi_client.api_response import ApiResponse as ApiResponse
from openapi_client.api_client import ApiClient as ApiClient
from openapi_client.configuration import Configuration as Configuration
from openapi_client.exceptions import OpenApiException as OpenApiException
from openapi_client.exceptions import ApiTypeError as ApiTypeError
from openapi_client.exceptions import ApiValueError as ApiValueError
from openapi_client.exceptions import ApiKeyError as ApiKeyError
from openapi_client.exceptions import ApiAttributeError as ApiAttributeError
from openapi_client.exceptions import ApiException as ApiException
# import models into sdk package
from openapi_client.models.account_overview_response import AccountOverviewResponse as AccountOverviewResponse
from openapi_client.models.auth_response import AuthResponse as AuthResponse
from openapi_client.models.authenticate_request import AuthenticateRequest as AuthenticateRequest
from openapi_client.models.getlatestpackets_request import GetlatestpacketsRequest as GetlatestpacketsRequest
from openapi_client.models.item import Item as Item
from openapi_client.models.latest_item_packets import LatestItemPackets as LatestItemPackets
from openapi_client.models.latest_packets import LatestPackets as LatestPackets
from openapi_client.models.latest_packets_data import LatestPacketsData as LatestPacketsData
from openapi_client.models.token_info import TokenInfo as TokenInfo
TO:
# import apis into sdk package
from .api.default_api import DefaultApi as DefaultApi
# import ApiClient
from .api_response import ApiResponse as ApiResponse
from .api_client import ApiClient as ApiClient
from .configuration import Configuration as Configuration
from .exceptions import OpenApiException as OpenApiException
from .exceptions import ApiTypeError as ApiTypeError
from .exceptions import ApiValueError as ApiValueError
from .exceptions import ApiKeyError as ApiKeyError
from .exceptions import ApiAttributeError as ApiAttributeError
from .exceptions import ApiException as ApiException
# import models into sdk package
from .models.account_overview_response import AccountOverviewResponse as AccountOverviewResponse
from .models.auth_response import AuthResponse as AuthResponse
from .models.authenticate_request import AuthenticateRequest as AuthenticateRequest
from .models.getlatestpackets_request import GetlatestpacketsRequest as GetlatestpacketsRequest
from .models.item import Item as Item
from .models.latest_item_packets import LatestItemPackets as LatestItemPackets
from .models.latest_packets import LatestPackets as LatestPackets
from .models.latest_packets_data import LatestPacketsData as LatestPacketsData
from .models.token_info import TokenInfo as TokenInfo
```
api_client.py:
```
from openapi_client.configuration import Configuration
from openapi_client.api_response import ApiResponse, T as ApiResponseT
import openapi_client.models
from openapi_client import rest
from openapi_client.exceptions import (
TO:
from .configuration import Configuration
from .api_response import ApiResponse, T as ApiResponseT
from .models import *
from . import rest
from .exceptions import (

on row 456 something:
                # klass = getattr(openapi_client.models, klass)
                klass = getattr(importlib.import_module('.models', __package__), klass)
and add:
import importlib
at the top of the file.
```
rest.py:
```
from openapi_client.exceptions import ApiException, ApiValueError
TO:
from .exceptions import ApiException, ApiValueError
```
# Possible bug in Perific Api
Regardless what item_id is sent to getlatestpackets only values from the first device is returned from the API, this solution is prepared for the api returning the correct values in the vent that Perific fix the bug to retur the correct values

# Good to know
Working CURLS:

```
curl -v -X PUT "https://api.enegic.com/createtoken" -H "Content-Type: application/json" -d '{  "username": "<redacted>", "password": "<redacted>"}'
```
Respons:
```
{"TokenInfo":{"Token":"bbe76481-9c14-4782-bf92-ca8d89b941e2","Created":"2025-08-20T21:22:01.1099716Z","ValidTo":"2026-08-20T21:22:01.1099717Z"},"User":{"UserId":<redacted>,"Username":"<redacted>","Domain":"Evify","ParentDomain":"Perific","Agent":"None","Rights":[],"Capabilities":[{"Id":10,"Name":"IntegrationMonta","Description":"Allows the creation of a Monta Settings.","MaxValue":null},{"Id":11,"Name":"IntegrationEasee","Description":"Allows the creation of a Easee Settings.","MaxValue":null},{"Id":12,"Name":"IntegrationZaptec","Description":"Allows the creation of a Zaptec Settings.","MaxValue":null},{"Id":13,"Name":"IntegrationChargeAmps","Description":"Allows the creation of a Amp Guards Settings.","MaxValue":null},{"Id":14,"Name":"IntegrationOpenReporter","Description":"Allows the creation of a OpenReporter Settings.","MaxValue":null},{"Id":15,"Name":"IntegrationWallbox","Description":"Allows the creation of a Wallbox Settings.","MaxValue":null},{"Id":16,"Name":"IntegrationAutel","Description":"Allows the creation of a Autel Settings.","MaxValue":null},{"Id":17,"Name":"IntegrationClenergy","Description":"Allows the creation of a Clenergy Settings.","MaxValue":null},{"Id":18,"Name":"IntegrationVourity","Description":"Allows the creation of a Vourity Settings.","MaxValue":null},{"Id":19,"Name":"IntegrationEfuel","Description":"Allows the creation of a Efuel Settings.","MaxValue":null},{"Id":20,"Name":"IntegrationEinride","Description":"Allows the creation of a Einride Settings","MaxValue":null},{"Id":22,"Name":"IntegrationNexBlue","Description":"Allows the creation of a NexBlue Settings","MaxValue":null},{"Id":24,"Name":"IntegrationGo-e","Description":"Allows the creation of a go-e Settings","MaxValue":null},{"Id":27,"Name":"IntegrationAmpeco","Description":"Capability to integrate with Ampeco","MaxValue":null},{"Id":31,"Name":"IntegrationEllsy","Description":"Capability to integrate with Ellsy","MaxValue":null},{"Id":32,"Name":"IntegrationWevo","Description":"Capability to integrate with Wevo","MaxValue":null},{"Id":35,"Name":"IntegrationV2C","Description":"Capability to integrate to V2C","MaxValue":null},{"Id":38,"Name":"Pair","Description":"Capability to create Pair reporters","MaxValue":null},{"Id":39,"Name":"IntegrationConnectGO","Description":"Capability to create Connect Go reporters","MaxValue":null},{"Id":40,"Name":"IntegrationDEFA","Description":"Capability to integrate with DEFA","MaxValue":null},{"Id":41,"Name":"IntegrationEmabler","Description":"Capability to integrate with eMabler","MaxValue":null},{"Id":42,"Name":"IntegrationVektoEcharge","Description":"Capability to integrate to Vekto eCharge","MaxValue":null},{"Id":45,"Name":"IntegrationEnua","Description":"Capability to integrate with enua","MaxValue":null},{"Id":46,"Name":"IntegrationOddes","Description":"Capability to integrate with \"\"Oddes\"\"","MaxValue":null},{"Id":47,"Name":"Solar","Description":"Enables the user to use the solar functionality for our integrations and controlling devices.","MaxValue":null},{"Id":48,"Name":"MonitorHistory","Description":"Enables the user to see historical data from the monitor devices","MaxValue":null},{"Id":49,"Name":"IntegrationVirta","Description":"Capability to integrate to Virta","MaxValue":null},{"Id":50,"Name":"IntegrationAssemblinCharge","Description":"Capability to integrate to Assemblin Charge","MaxValue":null},{"Id":51,"Name":"IntegrationZpark","Description":"Capability to integrate with Zpark","MaxValue":null},{"Id":52,"Name":"IntegrationChargePanelEnterprise","Description":"Capability to integrate with ChargePanel Enterprise","MaxValue":null},{"Id":53,"Name":"IntegrationAssetBook","Description":"Capability to integrate with AssetBook","MaxValue":null},{"Id":56,"Name":"IntegrationOcpp","Description":"Integration with OCPP Chargers","MaxValue":null},{"Id":60,"Name":"IntegrationWaybler","Description":"Capability to integrate with Waybler","MaxValue":null}],"CreationTime":"2023-10-09T13:23:45","ActivationTime":"2023-10-09T22:31:41","MustChangePassword":false,"MainUserId":-1,"* Connection #0 to host api.enegic.com left intact AgreementAccepted":"2023-10-09T22:31:41","StripeId":"cus_RLTlTRyOuajvYN","DomainCountryId":2}}
```
```
curl -v -X GET "https://api.enegic.com/getaccountoverview"   -H "X-Authorization: <your token>"   -H "Content-Type: application/json"
```
Respons:
```
{"User":{"UserId":<reducted>,"Username":"<reducted>","Domain":"Evify","ParentDomain":"Perific","Agent":"None","Rights":[],"Capabilities":[{"Id":10,"Name":"IntegrationMonta","Description":"Allows the creation of a Monta Settings.","MaxValue":null},{"Id":11,"Name":"IntegrationEasee","Description":"Allows the creation of a Easee Settings.","MaxValue":null},{"Id":12,"Name":"IntegrationZaptec","Description":"Allows the creation of a Zaptec Settings.","MaxValue":null},{"Id":13,"Name":"IntegrationChargeAmps","Description":"Allows the creation of a Amp Guards Settings.","MaxValue":null},{"Id":14,"Name":"IntegrationOpenReporter","Description":"Allows the creation of a OpenReporter Settings.","MaxValue":null},{"Id":15,"Name":"IntegrationWallbox","Description":"Allows the creation of a Wallbox Settings.","MaxValue":null},{"Id":16,"Name":"IntegrationAutel","Description":"Allows the creation of a Autel Settings.","MaxValue":null},{"Id":17,"Name":"IntegrationClenergy","Description":"Allows the creation of a Clenergy Settings.","MaxValue":null},{"Id":18,"Name":"IntegrationVourity","Description":"Allows the creation of a Vourity Settings.","MaxValue":null},{"Id":19,"Name":"IntegrationEfuel","Description":"Allows the creation of a Efuel Settings.","MaxValue":null},{"Id":20,"Name":"IntegrationEinride","Description":"Allows the creation of a Einride Settings","MaxValue":null},{"Id":22,"Name":"IntegrationNexBlue","Description":"Allows the creation of a NexBlue Settings","MaxValue":null},{"Id":24,"Name":"IntegrationGo-e","Description":"Allows the creation of a go-e Settings","MaxValue":null},{"Id":27,"Name":"IntegrationAmpeco","Description":"Capability to integrate with Ampeco","MaxValue":null},{"Id":31,"Name":"IntegrationEllsy","Description":"Capability to integrate with Ellsy","MaxValue":null},{"Id":32,"Name":"IntegrationWevo","Description":"Capability to integrate with Wevo","MaxValue":null},{"Id":35,"Name":"IntegrationV2C","Description":"Capability to integrate to V2C","MaxValue":null},{"Id":38,"Name":"Pair","Description":"Capability to create Pair reporters","MaxValue":null},{"Id":39,"Name":"IntegrationConnectGO","Description":"Capability to create Connect Go reporters","MaxValue":null},{"Id":40,"Name":"IntegrationDEFA","Description":"Capability to integrate with DEFA","MaxValue":null},{"Id":41,"Name":"IntegrationEmabler","Description":"Capability to integrate with eMabler","MaxValue":null},{"Id":42,"Name":"IntegrationVektoEcharge","Description":"Capability to integrate to Vekto eCharge","MaxValue":null},{"Id":45,"Name":"IntegrationEnua","Description":"Capability to integrate with enua","MaxValue":null},{"Id":46,"Name":"IntegrationOddes","Description":"Capability to integrate with \"\"Oddes\"\"","MaxValue":null},{"Id":47,"Name":"Solar","Description":"Enables the user to use the solar functionality for our integrations and controlling devices.","MaxValue":null},{"Id":48,"Name":"MonitorHistory","Description":"Enables the user to see historical data from the monitor devices","MaxValue":null},{"Id":49,"Name":"IntegrationVirta","Description":"Capability to integrate to Virta","MaxValue":null},{"Id":50,"Name":"IntegrationAssemblinCharge","Description":"Capability to integrate to Assemblin Charge","MaxValue":null},{"Id":51,"Name":"IntegrationZpark","Description":"Capability to integrate with Zpark","MaxValue":null},{"Id":52,"Name":"IntegrationChargePanelEnterprise","Description":"Capability to integrate with ChargePanel Enterprise","MaxValue":null},{"Id":53,"Name":"IntegrationAssetBook","Description":"Capability to integrate with AssetBook","MaxValue":null},{"Id":56,"Name":"IntegrationOcpp","Description":"Integration with OCPP Chargers","MaxValue":null},{"Id":60,"Name":"IntegrationWaybler","Description":"Capability to integrate with Waybler","MaxValue":null}],"CreationTime":"<reducted>","ActivationTime":"<reducted>","MustChangePassword":false,"MainUserId":-1,"AgreementAccepted":"<reducted>","StripeId":"cus_RLTlTRyOuajvYN","DomainCountryId":2},"Items":[{"ItemId":<reducted>,"UserId":<reducted>,"Name":"Measurement","SystemName":"Measurement","ItemCategory":"LocalPhysical","ItemType":"Phase","ItemSubType":"EM1","UserSettings":{},"SystemSettings":{},"MacAddress":"<reducted>","TimeZone":"<reducted>","GroupId":null,"ClusterId":null,"CreationTime":"<reducted>","DeletionTime":null,"SharedDeviceOwner":null,"FlashSeqNo":952009,"LatestPacketFromItem":{"hdr":1002,"iid":<reducted>,"ts":<reducted>,"seqno":3380,"it":"Phase","pv":2,"fw":"4.2.3","rssi":-74,"data":{
  "imin": [
    0.48,
    0.56,
    0.61,
    0.0
  ],
  "imax": [
    0.52,
    0.64,
    0.85,
    0.0
  ],
  "iavg": [
    0.49,
    0.58,
    0.76,
    0.0
  ],
  "qmin": [
    313217918379,
    151382948307,
    161354668165,
    59443418133
  ],
  "qmax": [
    313217923256,
    151382954045,
    161354675731,
    59443418133
  ],
  "eyepmin": [
    0
  ],
  "eyepmax": [
    0
  ],
  "eyepavg": [
    0
  ],
  "eyeemin": [
    0
  ],
  "eyeemax": [
    0
  ]
}},"ActualItemUserParameters":{
  "UserId": <reducted>,
  "ItemId": <reducted>,
  "Mac": "<reducted>",
  "ItemType": "Phase",
  "ItemSubType": "EM1",
  "ItemCategory": "LocalPhysical",
  "Name": "Measurement",
  "SystemName": "Measurement",
  "ServerUdpAddr": "phase.device.enegic.com",
  "ServerUdpPort": 65110,
  "TimeZone": "<reducted>",
  "Ai": 32,
  "Ks": 50,
  "PkWh": 1000
}},{"ItemId":<reducted>,"UserId":<reducted>,"Name":"Zaptec Charge Control","SystemName":null,"ItemCategory":"LocalVirtual","ItemType":"Reporter","ItemSubType":"ZaptecReporter","UserSettings":{
  "zaptecGuid": "<reducted>",
  "safeModeLevel": "6",
  "chargerFuseLevel": "25"
},"SystemSettings":{},"MacAddress":"<reducted>","TimeZone":"<reducted>","GroupId":null,"ClusterId":null,"CreationTime":"<reducted>","DeletionTime":null,"SharedDeviceOwner":null,"FlashSeqNo":0,"LatestPacketFromItem":{},"ActualItemUserParameters":{}},{"ItemId":<reducted>,"UserId":<reducted>,"Name":"CarCharger","SystemName":null,"ItemCategory":"LocalVirtual","ItemType":"Charger","ItemSubType":"ZaptecCharger","UserSettings":{
  "ChargerId": "<reducted>",
  "ReporterId": "<reducted>",
  "InstallationId": "<reducted>"
* Connection #0 to host api.enegic.com left intact
},"SystemSettings":{},"MacAddress":"<reducted>","TimeZone":"<reducted>","GroupId":null,"ClusterId":null,"CreationTime":"<reducted>","DeletionTime":null,"SharedDeviceOwner":null,"FlashSeqNo":0,"LatestPacketFromItem":{},"ActualItemUserParameters":{}}],"Chargers":[]}
```
```
curl -v -X PUT "https://api.enegic.com/getlatestpackets" -H "X-Authorization: <your token>" -H "Content-Type: application/json" -d '{"item_id": <your itemid>}'
```
Respons:
```
[{"ItemId":<redacted>,"LatestPackets":{"PhaseMinute":{"hdr":1004,"iid":<redacted>,"ts":<redacted>,"seqno":952000,"it":"Phase","pv":2,"fw":"4.2.3","rssi":-74,"data":{"imin":[0.44,0.90,0.59,0.00],"imax":[0.56,1.02,0.79,0.00],"iavg":[0.48,0.94,0.66,0.00],"qmin":[313216351249,151382478910,161352957877,59443418133],"qmax":[313216380083,151382535266,161352997310,59443418133],"eyepmin":[0],"eyepmax":[0],"eyepavg":[0],"eyeemin":[0],"eyeemax":[0]}},"PhaseDay":{"hdr":1006,"iid":<redacted>,"ts":<redacted>,"seqno":951437,"it":"Phase","pv":2,"fw":"4.2.3","rssi":-71,"data":{"imin":[0.34,0.52,0.49,0.00],"imax":[22.87,26.85,15.12,0.00],"iavg":[3.61,3.08,1.60,-0.00],"qmin":[312873759235,151083101603,161183298976,59443418133],"qmax":[313185465984,151348957615,161321742203,59443418133],"eyepmin":[0],"eyepmax":[0],"eyepavg":[0],"eyeemin":[0],"eyeemax":[0]}},"PhaseHour":{"hdr":1005,"iid":<redacted>,"ts":<redacted>,"seqno":951986,"it":"Phase","pv":2,"fw":"4.2.3","rssi":-74,"data":{"imin":[0.39,0.52,0.56,0.00],* Connection #0 to host api.enegic.com left intact "imax":[16.09,15.94,7.62,0.00],"iavg":[2.18,1.98,1.13,0.00],"qmin":[313208118328,151374835218,161347306897,59443418133],"qmax":[313215962465,151381947098,161351376947,59443418133],"eyepmin":[0],"eyepmax":[0],"eyepavg":[0],"eyeemin":[0],"eyeemax":[0]}},"PhaseRealTime":{"hdr":1002,"iid":<redacted>,"ts":<redacted>,"seqno":3325,"it":"Phase","pv":2,"fw":"4.2.3","rssi":-74,"data":{"imin":[0.46,0.90,0.61,0.00],"imax":[0.52,1.00,0.88,0.00],"iavg":[0.49,0.94,0.72,0.00],"qmin":[313216384903,151382544575,161353003895,59443418133],"qmax":[313216389748,151382553934,161353011047,59443418133],"eyepmin":[0],"eyepmax":[0],"eyepavg":[0],"eyeemin":[0],"eyeemax":[0]}}},"State":{},"Control":{"DesiredParameters":{},"ActualParameters":{}}}]
```
