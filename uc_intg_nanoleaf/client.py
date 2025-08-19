"""
Nanoleaf API client implementation.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import logging
import socket
import ssl
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

_LOG = logging.getLogger(__name__)


class NanoleafAPIError(Exception):
    """Custom exception for Nanoleaf API errors."""

    def __init__(self, message: str, code: int = None) -> None:
        super().__init__(message)
        self.code = code


class NanoleafDevice:
    """Represents a Nanoleaf device with its capabilities."""

    def __init__(self, ip_address: str, auth_token: str = None, device_info: Dict[str, Any] = None) -> None:
        self.ip_address = ip_address
        self.auth_token = auth_token
        self.port = 16021  # Default Nanoleaf API port
        
        # Device information
        if device_info:
            self.name = device_info.get("name", f"Nanoleaf {ip_address}")
            self.model = device_info.get("model", "Unknown")
            self.serial_no = device_info.get("serialNo", "")
            self.firmware_version = device_info.get("firmwareVersion", "")
            self.manufacturer = device_info.get("manufacturer", "Nanoleaf")
            
            # State information
            state = device_info.get("state", {})
            self.is_on = state.get("on", {}).get("value", False)
            self.brightness = state.get("brightness", {}).get("value", 100)
            self.hue = state.get("hue", {}).get("value", 0)
            self.saturation = state.get("sat", {}).get("value", 0)
            self.color_temp = state.get("ct", {}).get("value", 4000)
            self.color_mode = state.get("colorMode", "effect")
            
            # Effects information
            effects = device_info.get("effects", {})
            self.current_effect = effects.get("select", "")
            self.effects_list = effects.get("effectsList", [])
            
            # Panel layout information
            layout = device_info.get("panelLayout", {}).get("layout", {})
            self.panel_count = layout.get("numPanels", 0)
            self.panel_layout = layout.get("positionData", [])
            
            # Determine capabilities
            self.supports_color = True  # All Nanoleaf devices support color
            self.supports_brightness = True  # All Nanoleaf devices support brightness
            self.supports_effects = len(self.effects_list) > 0
            self.supports_color_temp = True  # Most Nanoleaf devices support color temperature
            self.supports_layout = len(self.panel_layout) > 0
            
            # Device type determination
            self.device_type = self._determine_device_type()
            self.sku = self._determine_sku()
        else:
            # Default values for new devices
            self.name = f"Nanoleaf {ip_address}"
            self.model = "Unknown"
            self.device_type = "panels"
            self.sku = "Unknown"
            self.supports_color = True
            self.supports_brightness = True
            self.supports_effects = True
            self.supports_color_temp = True
            self.supports_layout = True
            self.effects_list = []
            self.panel_count = 0

    def _determine_device_type(self) -> str:
        """Determine device type based on model."""
        model = self.model.upper()
        
        if "NL22" in model or "NL42" in model:
            return "light_panels"
        elif "NL29" in model:
            return "canvas"
        elif "NL52" in model or "NL59" in model:
            return "shapes"
        elif "NL64" in model:
            return "elements"
        elif "NL69" in model:
            return "lines"
        elif "STRIP" in self.name.upper():
            return "strip"
        else:
            return "panels"

    def _determine_sku(self) -> str:
        """Determine SKU/model identifier."""
        if self.model and self.model != "Unknown":
            return self.model
        return self.device_type.upper()

    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Get a summary of device capabilities."""
        return {
            "device_type": self.device_type,
            "sku": self.sku,
            "supports_color": self.supports_color,
            "supports_brightness": self.supports_brightness,
            "supports_effects": self.supports_effects,
            "supports_color_temp": self.supports_color_temp,
            "supports_layout": self.supports_layout,
            "effects_count": len(self.effects_list),
            "panel_count": self.panel_count,
            "brightness_range": (1, 100),
            "color_temp_range": (1200, 6500),
            "effects_list": self.effects_list[:10]  # Limit for summary
        }

    def __str__(self) -> str:
        return f"NanoleafDevice(ip={self.ip_address}, name={self.name}, model={self.model}, type={self.device_type})"


class NanoleafDiscovery:
    """Nanoleaf device discovery using mDNS."""
    
    def __init__(self):
        self.discovered_devices: List[Tuple[str, int]] = []
        self.zeroconf = None
        self.browser = None

    async def discover_devices(self, timeout: float = 10.0) -> List[Tuple[str, int]]:
        """Discover Nanoleaf devices on the network using mDNS."""
        _LOG.info("Starting Nanoleaf device discovery via mDNS...")
        
        try:
            self.discovered_devices = []
            
            async with AsyncZeroconf() as zeroconf:
                listener = NanoleafServiceListener(self.discovered_devices)
                browser = ServiceBrowser(zeroconf.zeroconf, "_nanoleafapi._tcp.local.", listener)
                
                # Wait for discovery
                await asyncio.sleep(timeout)
                
                browser.cancel()
                
            _LOG.info(f"Discovery completed. Found {len(self.discovered_devices)} devices")
            return self.discovered_devices
            
        except Exception as e:
            _LOG.error(f"Error during device discovery: {e}")
            return []

    async def scan_ip_range(self, base_ip: str = "192.168.1", start: int = 1, end: int = 254) -> List[Tuple[str, int]]:
        """Scan IP range for Nanoleaf devices (fallback method)."""
        _LOG.info(f"Scanning IP range {base_ip}.{start}-{end} for Nanoleaf devices...")
        
        found_devices = []
        tasks = []
        
        for i in range(start, end + 1):
            ip = f"{base_ip}.{i}"
            task = self._check_nanoleaf_device(ip, 16021)
            tasks.append(task)
        
        # Process in batches to avoid overwhelming the network
        batch_size = 20
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            results = await asyncio.gather(*batch, return_exceptions=True)
            
            for j, result in enumerate(results):
                if result is True:
                    ip = f"{base_ip}.{start + i + j}"
                    found_devices.append((ip, 16021))
                    _LOG.info(f"Found Nanoleaf device at {ip}:16021")
        
        _LOG.info(f"IP scan completed. Found {len(found_devices)} devices")
        return found_devices

    async def _check_nanoleaf_device(self, ip: str, port: int) -> bool:
        """Check if a device at IP:port is a Nanoleaf device."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                # Try to connect to the Nanoleaf API endpoint
                async with session.get(f"http://{ip}:{port}/api/v1/", timeout=2) as response:
                    # Nanoleaf API returns 401 for unauthorized requests
                    return response.status == 401
        except:
            return False


class NanoleafServiceListener(ServiceListener):
    """mDNS service listener for Nanoleaf devices."""
    
    def __init__(self, devices_list: List[Tuple[str, int]]):
        self.devices_list = devices_list

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info:
            for addr in info.addresses:
                ip = socket.inet_ntoa(addr)
                port = info.port
                self.devices_list.append((ip, port))
                _LOG.info(f"Discovered Nanoleaf device: {name} at {ip}:{port}")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass


class NanoleafClient:
    """Nanoleaf API client with device management."""

    def __init__(self) -> None:
        self.session: Optional[aiohttp.ClientSession] = None
        self.discovery = NanoleafDiscovery()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self) -> None:
        """Create HTTP session."""
        if self.session is None:
            # Create SSL context for HTTP connections
            ssl_context = ssl.create_default_context()
            
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )

    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def discover_devices(self, use_mdns: bool = True, scan_network: bool = False) -> List[Tuple[str, int]]:
        """Discover Nanoleaf devices on the network."""
        found_devices = []
        
        if use_mdns:
            mdns_devices = await self.discovery.discover_devices()
            found_devices.extend(mdns_devices)
        
        if scan_network and not found_devices:
            # Fallback to IP scanning if mDNS finds nothing
            scanned_devices = await self.discovery.scan_ip_range()
            found_devices.extend(scanned_devices)
        
        return found_devices

    async def pair_device(self, ip_address: str, port: int = 16021) -> Optional[str]:
        """Pair with a Nanoleaf device to get auth token."""
        if not self.session:
            await self.connect()

        url = f"http://{ip_address}:{port}/api/v1/new"
        
        try:
            _LOG.info(f"Attempting to pair with Nanoleaf device at {ip_address}:{port}")
            _LOG.info("Please press and hold the power button on your Nanoleaf device for 5-7 seconds until the LED starts flashing")
            
            async with self.session.post(url) as response:
                if response.status == 200:
                    data = await response.json()
                    auth_token = data.get("auth_token")
                    if auth_token:
                        _LOG.info(f"Successfully paired with device at {ip_address}")
                        return auth_token
                    else:
                        _LOG.error("No auth token received from device")
                        return None
                elif response.status == 401:
                    _LOG.error("Unauthorized - device is not in pairing mode")
                    return None
                elif response.status == 403:
                    _LOG.error("Forbidden - pairing window may have closed")
                    return None
                else:
                    _LOG.error(f"Pairing failed with status {response.status}")
                    return None
                    
        except Exception as e:
            _LOG.error(f"Error pairing with device at {ip_address}: {e}")
            return None

    async def get_device_info(self, device: NanoleafDevice) -> Optional[Dict[str, Any]]:
        """Get complete device information."""
        if not self.session:
            await self.connect()

        url = f"http://{device.ip_address}:{device.port}/api/v1/{device.auth_token}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOG.error(f"Failed to get device info: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            _LOG.error(f"Error getting device info: {e}")
            return None

    async def test_connection(self, device: NanoleafDevice) -> bool:
        """Test connection to a Nanoleaf device."""
        try:
            device_info = await self.get_device_info(device)
            return device_info is not None
        except Exception as e:
            _LOG.error(f"Connection test failed for {device.ip_address}: {e}")
            return False

    async def turn_on(self, device: NanoleafDevice) -> bool:
        """Turn on the Nanoleaf device."""
        return await self._set_power(device, True)

    async def turn_off(self, device: NanoleafDevice) -> bool:
        """Turn off the Nanoleaf device."""
        return await self._set_power(device, False)

    async def _set_power(self, device: NanoleafDevice, on: bool) -> bool:
        """Set power state of the device."""
        if not self.session:
            await self.connect()

        url = f"http://{device.ip_address}:{device.port}/api/v1/{device.auth_token}/state"
        data = {"on": {"value": on}}
        
        try:
            async with self.session.put(url, json=data) as response:
                success = response.status == 204
                if success:
                    device.is_on = on
                    _LOG.debug(f"Set power {on} for device {device.name}")
                return success
                
        except Exception as e:
            _LOG.error(f"Error setting power state: {e}")
            return False

    async def set_brightness(self, device: NanoleafDevice, brightness: int, duration: int = 0) -> bool:
        """Set brightness of the device (1-100)."""
        if not self.session:
            await self.connect()

        brightness = max(1, min(100, brightness))
        url = f"http://{device.ip_address}:{device.port}/api/v1/{device.auth_token}/state"
        
        data = {"brightness": {"value": brightness}}
        if duration > 0:
            data["brightness"]["duration"] = duration
        
        try:
            async with self.session.put(url, json=data) as response:
                success = response.status == 204
                if success:
                    device.brightness = brightness
                    _LOG.debug(f"Set brightness {brightness} for device {device.name}")
                return success
                
        except Exception as e:
            _LOG.error(f"Error setting brightness: {e}")
            return False

    async def set_hue(self, device: NanoleafDevice, hue: int) -> bool:
        """Set hue of the device (0-360)."""
        if not self.session:
            await self.connect()

        hue = max(0, min(360, hue))
        url = f"http://{device.ip_address}:{device.port}/api/v1/{device.auth_token}/state"
        data = {"hue": {"value": hue}}
        
        try:
            async with self.session.put(url, json=data) as response:
                success = response.status == 204
                if success:
                    device.hue = hue
                    _LOG.debug(f"Set hue {hue} for device {device.name}")
                return success
                
        except Exception as e:
            _LOG.error(f"Error setting hue: {e}")
            return False

    async def set_saturation(self, device: NanoleafDevice, saturation: int) -> bool:
        """Set saturation of the device (0-100)."""
        if not self.session:
            await self.connect()

        saturation = max(0, min(100, saturation))
        url = f"http://{device.ip_address}:{device.port}/api/v1/{device.auth_token}/state"
        data = {"sat": {"value": saturation}}
        
        try:
            async with self.session.put(url, json=data) as response:
                success = response.status == 204
                if success:
                    device.saturation = saturation
                    _LOG.debug(f"Set saturation {saturation} for device {device.name}")
                return success
                
        except Exception as e:
            _LOG.error(f"Error setting saturation: {e}")
            return False

    async def set_color_temperature(self, device: NanoleafDevice, kelvin: int) -> bool:
        """Set color temperature of the device (1200-6500K)."""
        if not self.session:
            await self.connect()

        kelvin = max(1200, min(6500, kelvin))
        url = f"http://{device.ip_address}:{device.port}/api/v1/{device.auth_token}/state"
        data = {"ct": {"value": kelvin}}
        
        try:
            async with self.session.put(url, json=data) as response:
                success = response.status == 204
                if success:
                    device.color_temp = kelvin
                    _LOG.debug(f"Set color temperature {kelvin}K for device {device.name}")
                return success
                
        except Exception as e:
            _LOG.error(f"Error setting color temperature: {e}")
            return False

    async def set_effect(self, device: NanoleafDevice, effect_name: str) -> bool:
        """Set effect on the device."""
        if not self.session:
            await self.connect()

        if effect_name not in device.effects_list:
            _LOG.warning(f"Effect '{effect_name}' not available on device {device.name}")
            return False

        url = f"http://{device.ip_address}:{device.port}/api/v1/{device.auth_token}/effects"
        data = {"select": effect_name}
        
        try:
            async with self.session.put(url, json=data) as response:
                success = response.status == 204
                if success:
                    device.current_effect = effect_name
                    _LOG.debug(f"Set effect '{effect_name}' for device {device.name}")
                return success
                
        except Exception as e:
            _LOG.error(f"Error setting effect: {e}")
            return False

    async def identify_device(self, device: NanoleafDevice) -> bool:
        """Make the device flash to identify it."""
        if not self.session:
            await self.connect()

        url = f"http://{device.ip_address}:{device.port}/api/v1/{device.auth_token}/identify"
        
        try:
            async with self.session.put(url) as response:
                success = response.status == 204
                if success:
                    _LOG.info(f"Device {device.name} should now be flashing for identification")
                return success
                
        except Exception as e:
            _LOG.error(f"Error identifying device: {e}")
            return False