# Home Assistant Perific Custom Integration

## Installation Instructions

### 1. Generate a GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
2. Click "Generate new token".
3. Give it a name, set an expiration, and select at least the `repo` scope.
4. Copy the generated token (you will need it in the next step).

### 2. Download the Integration

Open a terminal on your Home Assistant server and run:

```sh
cd /config/custom_components
git clone https://<YOUR_GITHUB_USERNAME>:<YOUR_PERSONAL_ACCESS_TOKEN>@github.com/Pokeyo-AB/homeassistant-perific.git homeassistant-perific
```

Replace:

- `<YOUR_GITHUB_USERNAME>` with your GitHub username
- `<YOUR_PERSONAL_ACCESS_TOKEN>` with the token from step 1

### 3. Restart Home Assistant

- Go to **Settings > System > Restart** in Home Assistant, or run:
  ```sh
  ha core restart
  ```

### 4. Configure the Integration

- After restart, go to **Settings > Devices & Services > Integrations**.
- Click "Add Integration" and search for "Perific" (or the integration name).
- Follow the setup instructions.

---

**Note:**

- Keep your token secure and do not share it.
- You can remove the token from your GitHub account after installation if you wish.
