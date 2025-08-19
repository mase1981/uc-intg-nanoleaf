"""
Configuration management for Nanoleaf integration.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import json
import logging
from typing import Any, Dict, Optional

_LOG = logging.getLogger(__name__)


class NanoleafConfig:
    """Configuration management for Nanoleaf integration."""
    
    def __init__(self, config_file_path: str):
        self._config_file_path = config_file_path
        self._config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        try:
            with open(self._config_file_path, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
            _LOG.debug("Configuration loaded successfully")
        except FileNotFoundError:
            _LOG.debug("Configuration file not found, starting with empty config")
            self._config_data = {}
        except json.JSONDecodeError as e:
            _LOG.error("Error parsing configuration file: %s", e)
            self._config_data = {}
        except Exception as e:
            _LOG.error("Error loading configuration: %s", e)
            self._config_data = {}
    
    def _save_config(self) -> bool:
        try:
            with open(self._config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
            _LOG.debug("Configuration saved successfully")
            return True
        except Exception as e:
            _LOG.error("Error saving configuration: %s", e)
            return False
    
    def is_configured(self) -> bool:
        devices = self.devices
        return len(devices) > 0 and any(device.get("auth_token") for device in devices.values())
    
    @property
    def devices(self) -> Dict[str, Any]:
        return self._config_data.get("devices", {})

    @devices.setter
    def devices(self, value: Dict[str, Any]) -> None:
        self._config_data["devices"] = value
        self._save_config()

    def get_device_config(self, device_id: str) -> Dict[str, Any]:
        return self.devices.get(device_id, {})

    def set_device_config(self, device_id: str, config: Dict[str, Any]) -> None:
        devices = self.devices.copy()
        devices[device_id] = config
        self.devices = devices

    def add_device(self, ip_address: str, auth_token: str, device_info: Dict[str, Any], port: int = 16021) -> None:
        """Add a new Nanoleaf device to configuration."""
        device_id = f"{ip_address.replace('.', '_')}_{port}"
        
        device_config = {
            "ip_address": ip_address,
            "port": port,  # Store port for future reference
            "auth_token": auth_token,
            "name": device_info.get("name", f"Nanoleaf {device_id}"),
            "model": device_info.get("model", "Unknown"),
            "serial_no": device_info.get("serialNo", ""),
            "firmware_version": device_info.get("firmwareVersion", ""),
            "manufacturer": device_info.get("manufacturer", "Nanoleaf"),
            "effects": device_info.get("effects", {}),
            "supports_color": True,  # All Nanoleaf devices support color
            "supports_brightness": True,  # All Nanoleaf devices support brightness
            "supports_effects": len(device_info.get("effects", {}).get("effectsList", [])) > 0,
            "supports_color_temp": True,  # Most Nanoleaf devices support color temperature
            "supports_layout": "panelLayout" in device_info,
            "effects_list": device_info.get("effects", {}).get("effectsList", []),
            "current_effect": device_info.get("effects", {}).get("select", ""),
            "panel_count": device_info.get("panelLayout", {}).get("layout", {}).get("numPanels", 0),
            "device_type": self._determine_device_type(device_info),
            "sku": self._determine_sku(device_info)
        }
        
        devices = self.devices.copy()
        devices[device_id] = device_config
        self.devices = devices
        
        _LOG.info(f"Added Nanoleaf device: {device_config['name']} ({device_config['model']}) at {ip_address}:{port}")

    def _determine_device_type(self, device_info: Dict[str, Any]) -> str:
        """Determine device type based on device information."""
        model = device_info.get("model", "").upper()
        name = device_info.get("name", "").upper()
        
        # Check model first
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
        
        # If model detection fails, check name
        if "ELEMENTS" in name:
            return "elements"
        elif "CANVAS" in name:
            return "canvas"
        elif "SHAPES" in name:
            return "shapes"
        elif "LINES" in name:
            return "lines"
        elif "STRIP" in name:
            return "strip"
        
        # Default fallback
        return "panels"

    def _determine_sku(self, device_info: Dict[str, Any]) -> str:
        """Determine SKU/model identifier."""
        model = device_info.get("model", "Unknown")
        if model and model != "Unknown":
            return model
        
        # Fallback to device type if model unknown
        device_type = self._determine_device_type(device_info)
        return device_type.upper()

    def remove_device(self, device_id: str) -> bool:
        """Remove a device from configuration."""
        devices = self.devices.copy()
        if device_id in devices:
            del devices[device_id]
            self.devices = devices
            _LOG.info(f"Removed device: {device_id}")
            return True
        return False

    def get_device_by_ip(self, ip_address: str, port: int = 16021) -> Optional[Dict[str, Any]]:
        """Get device configuration by IP address and port."""
        device_id = f"{ip_address.replace('.', '_')}_{port}"
        return self.devices.get(device_id)

    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration with auth tokens hidden."""
        safe_config = self._config_data.copy()
        if "devices" in safe_config:
            safe_devices = {}
            for device_id, device_config in safe_config["devices"].items():
                safe_device = device_config.copy()
                if "auth_token" in safe_device:
                    safe_device["auth_token"] = "***HIDDEN***"
                safe_devices[device_id] = safe_device
            safe_config["devices"] = safe_devices
        return safe_config

    def clear(self) -> None:
        """Clear all configuration."""
        self._config_data = {}
        self._save_config()

    def save(self) -> None:
        """Force save configuration."""
        self._save_config()