# Nanoleaf Smart Lighting Integration for Unfolded Circle Remote Two/3

[![GitHub Release](https://img.shields.io/github/release/mase1981/uc-intg-nanoleaf.svg)](https://github.com/mase1981/uc-intg-nanoleaf/releases)
[![GitHub License](https://img.shields.io/github/license/mase1981/uc-intg-nanoleaf.svg)](https://github.com/mase1981/uc-intg-nanoleaf/blob/main/LICENSE)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg)](https://paypal.me/mmiyara)

Transform your Unfolded Circle Remote Two/3 into a powerful Nanoleaf smart lighting command center. Control all your Nanoleaf devices with intelligent organization, dynamic UI generation, and comprehensive lighting control.

**NOTE:** This integration uses direct local network communication - no cloud services required.

## 🏠 Features

### Universal Device Support
- **Light Panels**: Original triangular panels with comprehensive RGB control
- **Canvas**: Square touch-sensitive panels with interactive control
- **Shapes**: Hexagonal and triangular modular panels
- **Elements**: Wood-look hexagonal panels with ambient lighting
- **Lines**: Linear LED light bars for accent lighting
- **LED Strips**: Flexible lighting strips for any installation

### Intelligent Remote Interface
- **Scalable UI Architecture**: Adapts from 1 device to 50+ devices elegantly
- **SKU-Based Organization**: Groups devices by model for clean interface
- **Dynamic Page Generation**: Creates appropriate controls based on actual device capabilities
- **Device Directory**: Overview page with organized device listing
- **Control Pages**: Dedicated pages per device type with full controls

### Advanced Lighting Features
- **Color Temperature**: Warm to cool white (1200K-6500K)
- **Dynamic Effects**: Access to device effects and scenes
- **Custom Colors**: Red, Green, Blue, White, Warm, Cool presets
- **Brightness Presets**: Quick 25%, 50%, 75%, 100% brightness control
- **Identify Function**: Flash device for easy identification

### Easy Setup
- **Simultaneous Pairing**: Pair multiple devices at once (breakthrough innovation)
- **Auto-Discovery**: Finds all Nanoleaf devices on your network via mDNS
- **Device Selection**: Choose which devices to integrate during setup
- **Friendly Names**: Displays actual device names instead of IP addresses
- **Progress Feedback**: Real-time setup progress with clear instructions

## 📋 Prerequisites

### Hardware Requirements
- **Nanoleaf Smart Devices**: Any Nanoleaf devices with API support (firmware 3.0+)
- **Remote Two/3**: Unfolded Circle Remote Two/3
- **Network**: Both devices connected to same local network
- **Nanoleaf Account**: Optional (for initial device setup via app)

### Software Requirements

#### Required Setup
1. **Nanoleaf App** (Mobile) - Optional after initial device setup
   - Download: iOS App Store / Google Play Store
   - Required: Only for initial device configuration and firmware updates

#### Network Requirements
- **Local Network Access**: Both Remote and Nanoleaf devices on same network
- **No Internet Required**: Works completely offline after setup
- **No Port Forwarding**: Uses standard Nanoleaf API (port 16021)
- **No Cloud Services**: Direct device communication for maximum privacy and speed

## 🚀 Quick Start

### Step 1: Prepare Your Nanoleaf Devices

#### Setup Nanoleaf Devices (if not already done)
1. **Download Nanoleaf App** on your smartphone
2. **Create Account** and log in (optional)
3. **Add All Devices** to your network following app instructions
4. **Update Firmware**: Ensure all devices have firmware 3.0+ for API support
5. **Test Functionality**: Ensure all devices work properly
6. **Note Device Locations**: Remember locations for easier identification

#### Verify API Access
1. **Check Device Status**: All devices should be powered on and connected to WiFi
2. **Network Connectivity**: Ensure devices are on same network as Remote Two/3
3. **No Special Configuration**: API is enabled by default on modern firmware

### Step 2: Install Integration on Remote

#### Via Remote Two/3 Web Interface
1. **Access Web Configurator**
   ```
   http://YOUR_REMOTE_IP/configurator
   ```

2. **Install Integration**
   - Navigate to: **Integrations** → **Add New** / **Install Custom**
   - Upload: **uc-intg-nanoleaf-***.tar.gz
   - Click: **Upload**

3. **Configure Integration**
   - **Auto-Discovery**: Wait for automatic device discovery (~5 seconds)
   - **Device Selection**: Select which devices to integrate (up to 3 for quick setup)
   - **Simultaneous Pairing**: Follow on-screen instructions to pair all selected devices
   - **Complete Setup**: Integration automatically configures all selected devices

4. **Add Entity**
   - **Nanoleaf Remote** (Remote Entity) - for comprehensive device control
   - Add to your desired activities

### Step 3: Device Pairing Process

#### Breakthrough Simultaneous Pairing
1. **Device Discovery**: Integration automatically finds all Nanoleaf devices
2. **Device Selection**: Choose which devices to integrate (checkboxes)
3. **Pairing Instructions**: 
   - Press and hold power button on ALL selected devices for 5-7 seconds
   - LEDs will start flashing to indicate pairing mode
   - Click "Continue" in setup interface
4. **Automatic Pairing**: All selected devices pair simultaneously
5. **Setup Complete**: All devices ready for control

**⚠️ Important Notes**:
- **Pairing Window**: 30 seconds to complete all device pairings
- **Simultaneous Control**: Press buttons on all devices before clicking Continue
- **LED Confirmation**: Flashing LEDs confirm pairing mode activation
- **Automatic Retry**: Integration handles temporary connection issues

## 🎮 Using the Integration

### Scalable Remote Interface

The integration creates an intelligent remote interface that automatically adapts to your devices:

#### Single Device Setup:
- **Page 1**: "Nanoleaf Devices" - Device overview
- **Page 2**: "Device Controls" - Full control interface with all functions

#### Multiple Device Setup:
- **Page 1**: "Nanoleaf Devices" - Device directory organized by SKU
- **Page 2+**: SKU-specific control pages (e.g., "Light Panels (NL22)", "Canvas (NL29)")

#### Example Layouts:

**3 Devices, Same Model**:
```
Page 1: Device Directory
Page 2: Light Panels (NL22) - 3 devices with individual toggles
```

**5 Devices, 3 Models**:
```
Page 1: Device Directory
Page 2: Light Panels (NL22) - 2 devices
Page 3: Canvas (NL29) - 2 devices  
Page 4: Shapes (NL52) - 1 device
```

**12 Devices, 4 Models**:
```
Page 1: Device Directory (overview)
Page 2: Light Panels (NL22) - 4 devices
Page 3: Canvas (NL29) - 3 devices
Page 4: Shapes (NL52) - 3 devices
Page 5: Elements (NL64) - 2 devices
```

### Device Controls by Type

#### Universal Controls (All Devices):
- **Power**: On/Off/Toggle buttons
- **Brightness Presets**: 25%, 50%, 75%, 100% quick select
- **Color Presets**: Red, Green, Blue, White, Warm, Cool
- **Color Temperature**: Warm (2700K), Cool (6500K), and intermediate values
- **Identify**: Flash device for identification
- **Fine Control**: Brightness +/- buttons for precise adjustment

#### Light Panels (NL22) Specific:
- **Triangle Layout**: Optimized for triangular panel layouts
- **Classic Effects**: Northern Lights, Flames, Forest, Snowfall
- **Touch Response**: Interactive touch controls (where supported)

#### Canvas (NL29) Specific:
- **Square Layout**: Optimized for square panel arrangements  
- **Touch Controls**: Full touch gesture support
- **Advanced Effects**: Meteor Shower, Sound reactive effects
- **Gesture Controls**: Tap, swipe, and touch interactions

#### Shapes (NL52/NL59) Specific:
- **Modular Layouts**: Support for complex geometric arrangements
- **Enhanced Effects**: Aurora, Kaleidoscope, Prism effects
- **Mix & Match**: Support for hexagon and triangle combinations

#### Elements (NL64) Specific:
- **Wood Aesthetic**: Specialized controls for wood-look panels
- **Ambient Lighting**: Optimized for accent and mood lighting
- **Warm Color Palette**: Enhanced warm color temperature support

#### Lines (NL69) Specific:
- **Linear Controls**: Optimized for linear light arrangements
- **Zone Control**: Individual section control where supported
- **Directional Effects**: Left-to-right flowing effects

### Global Controls

#### Multi-Device Commands:
- **ALL_ON**: Turn on all Nanoleaf devices
- **ALL_OFF**: Turn off all Nanoleaf devices  
- **ALL_TOGGLE**: Toggle all Nanoleaf devices
- **ALL_IDENTIFY**: Flash all devices for identification

#### Physical Remote Buttons:
The integration maps physical Remote Two/3 buttons:
- **Power Button**: Toggle primary device (largest panel count prioritized)
- **Volume Up/Down**: Brightness control for primary device

## 🔧 Configuration

### Integration Settings

Located at: `config.json` in integration directory

```json
{
  "devices": {
    "10_2_9_118_16021": {
      "ip_address": "10.2.9.118",
      "port": 16021,
      "auth_token": "your_device_auth_token",
      "name": "Living Room Panels",
      "model": "NL22",
      "device_type": "light_panels",
      "sku": "NL22",
      "supports_color": true,
      "supports_brightness": true,
      "supports_effects": true,
      "supports_color_temp": true,
      "supports_layout": true,
      "effects_list": [
        "Northern Lights", "Flames", "Forest", "Snowfall"
      ],
      "panel_count": 6
    }
  }
}
```

### Environment Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `UC_INTEGRATION_HTTP_PORT` | Integration HTTP port | `9090` |
| `UC_INTEGRATION_INTERFACE` | Bind interface | `0.0.0.0` |
| `UC_CONFIG_HOME` | Configuration directory | `./` |
| `UC_MDNS_LOCAL_HOSTNAME` | Override mDNS hostname | Auto-detected |

### Rate Limiting Settings

The integration includes built-in device protection:
- **Global Throttle**: 100ms between any commands
- **Device Throttle**: 300ms between commands to same device
- **Command Batching**: Efficient handling of rapid commands
- **Connection Pooling**: Optimized HTTP connections

## 🛠️ Troubleshooting

### Setup Issues

**Problem**: Integration setup fails with "No Devices Found"

**Solutions**:
1. **Verify Network Connectivity**:
   - Ensure Remote Two/3 and Nanoleaf devices on same network
   - Test: ping from Remote to device IP
   - Check firewall settings
2. **Check Device Status**:
   - Verify devices are powered on and connected to WiFi
   - Test devices work in Nanoleaf app
   - Ensure firmware is 3.0+ for API support
3. **Network Discovery**:
   - Wait longer for mDNS discovery (up to 10 seconds)
   - Try manual IP entry if auto-discovery fails
   - Check for network congestion

**Problem**: Device pairing fails during setup

**Solutions**:
1. **Timing Issues**:
   - Press ALL device power buttons within 5 seconds
   - Click "Continue" immediately after pressing buttons
   - Ensure LEDs are flashing before proceeding
2. **Device State**:
   - Verify devices are not already paired to another system
   - Reset devices if previously paired
   - Try pairing one device at a time
3. **Network Issues**:
   - Check network stability during pairing
   - Ensure no network interruptions
   - Move closer to devices if WiFi signal weak

**Problem**: "Connection Refused" or HTTP errors

**Solutions**:
1. **API Port Access**:
   ```bash
   # Test API connectivity
   curl http://DEVICE_IP:16021/api/v1/
   # Expected: HTTP 401 Unauthorized (normal for unauthenticated)
   ```
2. **Firewall Configuration**:
   - Ensure port 16021 is accessible
   - Check router/firewall settings
   - Temporarily disable firewall for testing
3. **Device API Status**:
   - Verify API is enabled (default on modern firmware)
   - Check device manual for API requirements
   - Update firmware if API not working

### Runtime Issues

**Problem**: Device commands not working

**Solutions**:
1. **Check Device Status**:
   - Verify devices are online and responsive
   - Test manual control through Nanoleaf app
   - Check power and network connections
2. **Authentication Issues**:
   - Auth tokens may have expired
   - Re-run integration setup to refresh tokens
   - Check if devices were reset
3. **Network Connectivity**:
   - Ensure stable local network connection
   - Test ping to device IP addresses
   - Check for network congestion
4. **Device Capability**:
   - Some effects may not be available on all models
   - Check device manual for supported features
   - Verify firmware compatibility

**Problem**: "HTTP 401 Unauthorized" errors

**Solutions**:
1. **Token Expiration**:
   - Auth tokens may have been invalidated
   - Re-pair devices through integration setup
   - Check if devices were factory reset
2. **Token Storage**:
   - Verify config.json contains valid tokens
   - Check file permissions for config directory
   - Backup and restore configuration if needed
3. **Device Reset**:
   - If devices were reset, tokens become invalid
   - Delete integration and set up again
   - Follow pairing process for all devices

**Problem**: Some devices missing from interface

**Solutions**:
1. **Network Discovery**:
   - Not all devices may be discovered initially
   - Try restarting integration
   - Use manual device addition if available
2. **API Compatibility**:
   - Very old devices may not support API
   - Check firmware version (need 3.0+)
   - Update firmware through Nanoleaf app
3. **Configuration Issues**:
   - Check config.json for all devices
   - Verify device entries are properly formatted
   - Re-run setup to refresh device list

### Debug Information

**Check Integration Logs**:
```bash
# Via web configurator
http://YOUR_REMOTE_IP/configurator → settings → development → Logs → choose Nanoleaf logs
```

**Test Device API Access**:
```bash
# Test API connectivity (should return 401)
curl http://DEVICE_IP:16021/api/v1/

# Test device pairing
curl -X POST http://DEVICE_IP:16021/api/v1/new

# Test authenticated access (replace TOKEN)
curl http://DEVICE_IP:16021/api/v1/TOKEN
```

**Verify mDNS Discovery**:
```bash
# List Nanoleaf services (Linux/Mac)
avahi-browse -rt _nanoleafapi._tcp

# Windows equivalent
dns-sd -B _nanoleafapi._tcp
```

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "No Devices Found" | mDNS discovery failed | Check network connectivity |
| "Pairing Failed" | Device not in pairing mode | Hold power button until LEDs flash |
| "HTTP 401 Unauthorized" | Invalid/expired auth token | Re-run integration setup |
| "Connection Refused" | Network/firewall issue | Check port 16021 accessibility |
| "Device Offline" | Device not reachable | Check device power and network |

## 🗃️ Advanced Setup

### Network Configuration

**Optimal Network Setup**:
- Use 2.4GHz WiFi for maximum range and stability
- Ensure strong signal strength at all device locations
- Avoid network congestion during setup
- Consider mesh network for large installations

**Firewall Configuration**:
```bash
# Required ports (if using firewall)
Port 16021/TCP  # Nanoleaf API
Port 5353/UDP   # mDNS discovery
```

### Device Organization Tips

**Naming Strategy**:
```bash
# Use descriptive names in Nanoleaf app
"Living Room Main Panels"    # Better than "Light Panels"
"Kitchen Canvas"             # Better than "Canvas 1"
"Bedroom Reading Light"      # Better than "Shapes"
```

**Layout Planning**:
- Group devices by room for logical organization
- Consider lighting zones for complex setups
- Plan for future expansion with consistent naming

### Performance Optimization

**Network Optimization**:
- Use wired connection for Remote Two/3 when possible
- Ensure stable WiFi for all Nanoleaf devices
- Monitor for interference on 2.4GHz band
- Consider QoS for smart home traffic

**Device Management**:
- Keep device firmware updated through Nanoleaf app
- Regularly test device responsiveness
- Clean device panels for optimal light output
- Monitor power consumption for large installations

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/mase1981/uc-intg-nanoleaf.git
cd uc-intg-nanoleaf

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Testing

```bash
# Run integration directly
python -m uc_intg_nanoleaf.driver

# Test with debug logging
UC_INTEGRATION_HTTP_PORT=9090 python uc_intg_nanoleaf/driver.py

# Test specific functionality
python -c "
from uc_intg_nanoleaf.client import NanoleafClient
import asyncio

async def test():
    client = NanoleafClient()
    devices = await client.discover_devices()
    print(f'Found {len(devices)} devices')

asyncio.run(test())
"
```

### Testing with Simulator

```bash
# Start device simulator (for development)
python nanoleaf_simulator.py

# The simulator provides:
# - Living Room Panels (NL22) on port 16021
# - Bedroom Canvas (NL29) on port 16022  
# - Office Shapes (NL52) on port 16023
```

### Building Release Package

```bash
# Create distribution package
tar -czf uc-intg-nanoleaf-v0.1.0.tar.gz \
  --exclude-vcs \
  --exclude='.github' \
  --exclude='tests' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='dist' \
  --exclude='build' \
  --exclude='nanoleaf_simulator.py' \
  .
```

### Code Structure

```
uc_intg_nanoleaf/
├── __init__.py          # Package initialization
├── client.py            # Nanoleaf API client with discovery
├── config.py            # Configuration management  
├── driver.py            # Main integration driver
├── remote.py            # Scalable remote entity with SKU-based UI
└── setup.py             # Breakthrough setup flow with simultaneous pairing
```

## 📄 License

This project is licensed under the MPL-2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Community Resources

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-nanoleaf/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Nanoleaf Support**: [Official Nanoleaf device support](https://nanoleaf.me/support)

### Frequently Asked Questions

**Q: How many devices can the integration handle?**
A: The integration scales from 1 to 50+ devices with intelligent UI organization.

**Q: Do I need internet access for the integration to work?**
A: No, the integration works completely offline using local network communication.

**Q: Can I control devices when away from home?**
A: Only if your Remote Two/3 is on the same local network as the Nanoleaf devices.

**Q: What happens if my network goes down?**
A: Device control requires local network connectivity. Devices maintain their last state.

**Q: Can I use devices paired to multiple systems?**
A: Each device can only be paired to one API client at a time. Re-pairing invalidates previous connections.

**Q: Which Nanoleaf models are supported?**
A: All modern Nanoleaf devices with API support (firmware 3.0+): Light Panels, Canvas, Shapes, Elements, Lines.

**Q: Can I add more devices after initial setup?**
A: Yes, run the integration setup again and select additional devices for pairing.

---

**Made with ❤️ for the Unfolded Circle Community**

**Author**: Meir Miyara
