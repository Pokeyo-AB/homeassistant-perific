
# Home Assistant Perific Custom Integration

This custom integration allows you to connect your **Perific energy meter** with Home Assistant.  
It now includes a **full OpenAPI-based client** (generated from the Perific API spec) for more reliable communication and future extensibility.

---

## ✨ Features

- Fetches real-time and historical energy metrics from Perific Cloud.
- Uses **OpenAPI-generated Python client** (`openapi_client/`) for strong typing and stability.
- Exposes detailed device metadata (firmware, hardware, MAC, system name, creation time).
- Supports multiple Perific devices under the same account.
- Integrates seamlessly into Home Assistant’s **device registry** and **sensor platform**.

---

## 📦 Installation Instructions

### 1. Download the Integration

Open a terminal on your Home Assistant server and run:

```sh
cd /config/custom_components
git clone https://github.com/Pokeyo-AB/homeassistant-perific.git homeassistant-perific
````

### 2. Restart Home Assistant

* Go to **Settings > System > Restart** in Home Assistant, or run:

  ```sh
  ha core restart
  ```

### 3. Configure the Integration

* After restart, go to **Settings > Devices & Services > Integrations**.
* Click **Add Integration** and search for **Perific**.
* Enter your **Perific Cloud username and password**.
* Home Assistant will authenticate against the Perific API via the OpenAPI client.

---

## ⚙️ Sample Configuration

Optional: you may add sensors in `configuration.yaml` for energy statistics:

```yaml
utility_meter:
  monthly_energy:
    source: sensor.energiforbrukning
    cycle: monthly
  daily_energy:
    source: sensor.energiforbrukning
    cycle: daily

sensor:
  - platform: integration
    name: "Energiförbrukning"
    unique_id: house_energy_total
    source: sensor.lastbalancer_perific_lastbalancer_power_total
    method: left
    round: 3
```

* Adjust the sensor names as needed to match your setup.
* Restart Home Assistant after updating your configuration.

---

## 🔒 Notes

* Authentication uses a **token-based flow** from the Perific API (`/createtoken`).
* Tokens are automatically refreshed and stored securely in Home Assistant.
* Keep your **Perific account credentials** private — do not share them.
* This integration is **cloud-polling** (data retrieved from Perific Cloud every \~30s).

---

## 🛠 Development
Developers can regenerate or patch the OpenAPI client if the API changes.
See DEVELOPMENT.md for detailed steps, including:
* How to regenerate openapi_client/ from perific_api.yaml.
* Required manual import path fixes after generation
* Example working cURL requests
* Known quirks in the current Perific API

---

## 📄 License

MIT License – see [LICENSE](LICENSE) for details.


