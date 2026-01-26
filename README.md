# Nanoleaf Smart Lighting Integration for Unfolded Circle Remote 2/3

Control your Nanoleaf smart lighting panels, canvas, shapes, elements, and LED strips directly from your Unfolded Circle Remote 2 or Remote 3 with comprehensive lighting control, **real-time state monitoring**, and **complete API-based control**.

![Nanoleaf](https://img.shields.io/badge/Nanoleaf-Smart%20Lighting-green)
[![GitHub Release](https://img.shields.io/github/v/release/mase1981/uc-intg-nanoleaf?style=flat-square)](https://github.com/mase1981/uc-intg-nanoleaf/releases)
![License](https://img.shields.io/badge/license-MPL--2.0-blue?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/mase1981/uc-intg-nanoleaf?style=flat-square)](https://github.com/mase1981/uc-intg-nanoleaf/issues)
[![Community Forum](https://img.shields.io/badge/community-forum-blue?style=flat-square)](https://community.unfoldedcircle.com/)
[![Discord](https://badgen.net/discord/online-members/zGVYf58)](https://discord.gg/zGVYf58)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mase1981/uc-intg-nanoleaf/total?style=flat-square)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg?style=flat-square)](https://paypal.me/mmiyara)
[![Github Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-30363D?&logo=GitHub-Sponsors&logoColor=EA4AAA&style=flat-square)](https://github.com/sponsors/mase1981)


## Features

This integration provides comprehensive control of Nanoleaf smart lighting through the native OpenAPI, delivering seamless integration with your Unfolded Circle Remote for complete lighting control and effects management.

---
## ❤️ Support Development ❤️

If you find this integration useful, consider supporting development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/mase1981)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mmiyara)

Your support helps maintain this integration. Thank you! ❤️
---

### 💡 **Light Control**

#### **Power Management**
- **Power On/Off** - Turn lights on and off
- **State Feedback** - Real-time power state monitoring

#### **Brightness Control**
- **Brightness Up/Down** - Precise brightness adjustment
- **Set Brightness** - Direct brightness control (0-100 scale)
- **Brightness Slider** - Visual brightness control
- **Brightness Presets** - Quick 25%, 50%, 75%, 100% brightness control
- **Real-time Updates** - Instant brightness feedback

#### **Color Control**
- **RGB Color Selection** - Full color spectrum control
- **Color Temperature** - Adjust warm/cool white tones (1200K-6500K)
- **Hue & Saturation** - Precise color tuning
- **Custom Colors** - Red, Green, Blue, White, Warm, Cool presets

#### **Effects & Scenes**
- **Built-in Effects** - Access all Nanoleaf dynamic effects
- **Scene Selection** - Quick scene switching
- **Effect Speed** - Adjust animation speed
- **Device-Specific Effects** - Northern Lights, Flames, Forest, Snowfall, Meteor Shower, Aurora

#### **Advanced Features**
- **Touch Gestures** - Enable/disable panel touch controls (Canvas models)
- **Rhythm Mode** - Music-reactive lighting (if supported)
- **Layout Detection** - Automatic panel layout recognition
- **Identify Function** - Flash device for easy identification

### 📊 **Sensor Entities**

Real-time monitoring of device state:

- **State Sensor** - Current power state (On/Off)
- **Brightness Sensor** - Current brightness level percentage
- **Color Mode Sensor** - Current color mode (RGB, CT, Effect)
- **Effect Sensor** - Currently active effect name

### **Universal Device Support**

- **Light Panels** - Original triangular panels (NL22)
- **Canvas** - Square touch-sensitive panels (NL29)
- **Shapes** - Hexagonal and triangular modular panels (NL52/NL59)
- **Elements** - Wood-look hexagonal panels (NL64)
- **Lines** - Linear LED light bars (NL69)
- **LED Strips** - Flexible lighting strips

### **Protocol Requirements**

- **Protocol**: Nanoleaf OpenAPI
- **HTTP Port**: 16021 (default)
- **Network Access**: Device must be on same local network
- **Authentication**: API token (auto-generated during setup)
- **Real-time Updates**: Regular polling for instant state changes

### **Network Requirements**

- **Local Network Access** - Integration requires same network as Nanoleaf device
- **HTTP Protocol** - OpenAPI via HTTP (port 16021)
- **Static IP Recommended** - Device should have static IP or DHCP reservation
- **Firewall** - Must allow HTTP traffic
- **mDNS Discovery** - Optional for automatic device discovery

## Installation

### Option 1: Remote Web Interface (Recommended)
1. Navigate to the [**Releases**](https://github.com/mase1981/uc-intg-nanoleaf/releases) page
2. Download the latest `uc-intg-uc_intg_nanoleaf-<version>-aarch64.tar.gz` file
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

### Option 2: Docker (Advanced Users)

The integration can be run as a standalone Docker container:

**Docker Compose:**
```yaml
services:
  uc-intg-nanoleaf:
    image: ghcr.io/mase1981/uc-intg-nanoleaf:latest
    container_name: uc-intg-nanoleaf
    network_mode: host
    volumes:
      - </local/path>:/data
    environment:
      - UC_CONFIG_HOME=/data
      - UC_INTEGRATION_HTTP_PORT=9090
      - UC_INTEGRATION_INTERFACE=0.0.0.0
      - PYTHONPATH=/app
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name uc-nanoleaf --restart unless-stopped --network host -v nanoleaf-config:/app/config -e UC_CONFIG_HOME=/app/config -e UC_INTEGRATION_INTERFACE=0.0.0.0 -e UC_INTEGRATION_HTTP_PORT=9090 -e PYTHONPATH=/app ghcr.io/mase1981/uc-intg-nanoleaf:latest
```

## Configuration

### Step 1: Prepare Your Nanoleaf Devices

**IMPORTANT**: Nanoleaf devices must be powered on and connected to your network before adding the integration.

#### Verify Network Connection:
1. Check that devices are connected to network (WiFi)
2. Note IP addresses from Nanoleaf mobile app
3. Ensure device firmware is up to date (3.0+ required)
4. Verify devices are accessible on local network

#### Network Setup:
- **WiFi Connection**: 2.4GHz or 5GHz supported
- **Static IP**: Recommended via DHCP reservation
- **Firewall**: Allow HTTP traffic (port 16021)
- **Network Isolation**: Must be on same subnet as Remote

### Step 2: Setup Integration

1. After installation, go to **Settings** → **Integrations**
2. The Nanoleaf integration should appear in **Available Integrations**
3. Click **"Configure"** to begin setup:

#### **Configuration:**
- **Device Discovery**: Integration will auto-discover Nanoleaf devices on network
- **Manual Entry**: Enter device IP if auto-discovery fails
- **Authentication**: Hold power button on device for 5-7 seconds when prompted
- **API Token**: Automatically generated and stored
- **Multi-Device**: Repeat pairing for each device
- Click **Complete Setup**

#### **Connection Test:**
- Integration verifies device connectivity
- API authentication confirmed
- Setup fails if device unreachable or auth fails

4. Integration will create entities:
   - **Light**: `light.nanoleaf_[device_name]` for each device
   - **Sensors**: Multiple sensor entities for state monitoring

## Using the Integration

### Light Entity

The light entity provides complete control:

- **Power Control**: On/Off/Toggle with state feedback
- **Brightness Control**: Brightness slider (0-100) and presets
- **Color Control**: RGB color picker with full spectrum
- **Color Temperature**: Warm/cool white adjustment (1200K-6500K)
- **Effects**: Dropdown with all available device-specific effects
- **Scene Selection**: Quick access to saved scenes

### Sensor Entities

| Sensor | Description |
|--------|-------------|
| State Sensor | Current power state |
| Brightness Sensor | Current brightness level percentage |
| Color Mode Sensor | Current color mode (RGB, CT, Effect) |
| Effect Sensor | Currently active effect name |

### Multi-Device Control

- **Scalable UI**: Automatically adapts from 1 to 50+ devices
- **SKU-Based Organization**: Groups devices by model for clean interface
- **Global Commands**: Control all devices simultaneously
- **Device Directory**: Overview page with organized device listing

## Credits

- **Developer**: Meir Miyara
- **Nanoleaf**: Smart modular lighting systems
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **Protocol**: Nanoleaf OpenAPI
- **Community**: Testing and feedback from UC community

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see LICENSE file for details.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-nanoleaf/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)
- **Nanoleaf Support**: [Official Nanoleaf Support](https://helpdesk.nanoleaf.me/)

---

**Made with ❤️ for the Unfolded Circle and Nanoleaf Communities**

**Thank You**: Meir Miyara
