# Home Assistant Perific Custom Integration

## Installation Instructions

### 1. Download the Integration

Open a terminal on your Home Assistant server and run:

```sh
cd /config/custom_components
git clone https://github.com/Pokeyo-AB/homeassistant-perific.git homeassistant-perific
```

### 2. Restart Home Assistant

- Go to **Settings > System > Restart** in Home Assistant, or run:
  ```sh
  ha core restart
  ```

### 3. Configure the Integration

- After restart, go to **Settings > Devices & Services > Integrations**.
- Click "Add Integration" and search for "Perific" (or the integration name).
- Follow the setup instructions.

---

## Sample Configuration

Add the following to your `configuration.yaml`:

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

- Adjust the sensor names as needed to match your setup.
- Restart Home Assistant after updating your configuration.

---

**Note:**

- Keep your token secure and do not share it.
- You can remove the token from your GitHub account after installation if you wish.
