"""
Nanoleaf remote entity for Unfolded Circle integration.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import ucapi
from ucapi.remote import Commands, Features, States
from ucapi.ui import Buttons, Size, create_btn_mapping, create_ui_text, create_ui_icon, UiPage

from uc_intg_nanoleaf.client import NanoleafClient, NanoleafDevice

_LOG = logging.getLogger(__name__)


class NanoleafRemote:
    """Nanoleaf remote entity with scalable SKU-based UI organization."""
    
    def __init__(self, api: ucapi.IntegrationAPI, client: NanoleafClient, config: 'NanoleafConfig'):
        self._api = api
        self._client = client
        self._config = config
        self._device_throttle = {}
        self._global_throttle = 0
        self._device_states = {}
        
        self._discovered_devices = self._config.devices
        _LOG.info(f"Creating remote with {len(self._discovered_devices)} discovered devices")
        
        features = [Features.ON_OFF, Features.SEND_CMD]
        simple_commands = self._generate_simple_commands()
        button_mapping = self._generate_button_mapping()
        ui_pages = self._create_scalable_ui_pages()
        
        self.entity = ucapi.Remote(
            identifier="nanoleaf_remote_main",
            name={"en": "Nanoleaf Remote"},
            features=features,
            attributes={"state": States.ON},
            simple_commands=simple_commands,
            button_mapping=button_mapping,
            ui_pages=ui_pages,
            cmd_handler=self.cmd_handler
        )
        
        _LOG.info(f"Nanoleaf remote entity created with {len(simple_commands)} commands and {len(ui_pages)} UI pages")
    
    def _generate_simple_commands(self) -> List[str]:
        """Generate all available commands for discovered devices."""
        commands = []
        
        if not self._discovered_devices:
            return ["NO_DEVICES"]
        
        for device_id, device_info in self._discovered_devices.items():
            device_name = device_info.get("name", f"Device_{device_id}")
            clean_name = self._clean_command_name(device_name)
            
            # Power commands (all devices support)
            commands.extend([f"{clean_name}_ON", f"{clean_name}_OFF", f"{clean_name}_TOGGLE"])
            
            # Brightness commands (all devices support)
            if device_info.get("supports_brightness", True):
                commands.extend([
                    f"{clean_name}_BRIGHTNESS_UP", f"{clean_name}_BRIGHTNESS_DOWN",
                    f"{clean_name}_BRIGHTNESS_25", f"{clean_name}_BRIGHTNESS_50", 
                    f"{clean_name}_BRIGHTNESS_75", f"{clean_name}_BRIGHTNESS_100"
                ])
            
            # Color commands (all devices support)
            if device_info.get("supports_color", True):
                commands.extend([
                    f"{clean_name}_COLOR_RED", f"{clean_name}_COLOR_GREEN", 
                    f"{clean_name}_COLOR_BLUE", f"{clean_name}_COLOR_WHITE",
                    f"{clean_name}_COLOR_WARM", f"{clean_name}_COLOR_COOL",
                    f"{clean_name}_COLOR_PURPLE", f"{clean_name}_COLOR_YELLOW"
                ])
            
            # Color temperature commands
            if device_info.get("supports_color_temp", True):
                commands.extend([
                    f"{clean_name}_TEMP_WARM", f"{clean_name}_TEMP_COOL",
                    f"{clean_name}_TEMP_2700K", f"{clean_name}_TEMP_4000K", f"{clean_name}_TEMP_6500K"
                ])
            
            # Effect commands
            if device_info.get("supports_effects", True):
                effects_list = device_info.get("effects_list", [])
                for effect in effects_list[:10]:  # Limit to 10 effects per device
                    effect_name = self._clean_command_name(effect)
                    commands.append(f"{clean_name}_EFFECT_{effect_name}")
            
            # Identify command
            commands.append(f"{clean_name}_IDENTIFY")
        
        # Global commands for multiple devices
        if len(self._discovered_devices) > 1:
            commands.extend(["ALL_ON", "ALL_OFF", "ALL_TOGGLE", "ALL_IDENTIFY"])
        
        return sorted(list(set(commands)))
    
    def _clean_command_name(self, name: str) -> str:
        """Clean name for use in commands."""
        cleaned = "".join(c if c.isalnum() else "_" for c in name.upper())
        while "__" in cleaned:
            cleaned = cleaned.replace("__", "_")
        return cleaned.strip("_")
    
    def _generate_button_mapping(self) -> List[dict]:
        """Generate physical button mappings."""
        mappings = []
        
        if not self._discovered_devices:
            return mappings
        
        # Map power button to primary device
        primary_device = self._find_primary_device()
        if primary_device:
            device_name = self._clean_command_name(primary_device.get("name", "Device"))
            mappings.append(create_btn_mapping(Buttons.POWER, f"{device_name}_TOGGLE"))
        
        # Map volume buttons to brightness control
        brightness_device = self._find_device_with_capability("supports_brightness")
        if brightness_device:
            device_name = self._clean_command_name(brightness_device.get("name", "Device"))
            mappings.append(create_btn_mapping(Buttons.VOLUME_UP, f"{device_name}_BRIGHTNESS_UP"))
            mappings.append(create_btn_mapping(Buttons.VOLUME_DOWN, f"{device_name}_BRIGHTNESS_DOWN"))
        
        return mappings
    
    def _find_primary_device(self) -> Dict[str, Any]:
        """Find the primary device (first device or largest panel count)."""
        if not self._discovered_devices:
            return {}
        
        # Prioritize by panel count (larger installations first)
        best_device = None
        max_panels = 0
        
        for device_info in self._discovered_devices.values():
            panel_count = device_info.get("panel_count", 0)
            if panel_count > max_panels:
                max_panels = panel_count
                best_device = device_info
        
        return best_device or next(iter(self._discovered_devices.values()))
    
    def _find_device_with_capability(self, capability: str) -> Dict[str, Any]:
        """Find first device with specified capability."""
        for device_info in self._discovered_devices.values():
            if device_info.get(capability, False):
                return device_info
        return {}
    
    def _create_scalable_ui_pages(self) -> List[UiPage]:
        """Create scalable UI pages based on discovered devices."""
        pages = []
        
        if not self._discovered_devices:
            main_page = UiPage(page_id="main", name="No Devices", grid=Size(4, 6))
            main_page.add(create_ui_text("No devices found", 0, 0, Size(4, 1)))
            pages.append(main_page)
            return pages
        
        # Create device directory page
        device_directory = self._create_device_directory_page()
        pages.append(device_directory)
        
        # Create SKU-based control pages
        sku_pages = self._create_sku_control_pages()
        pages.extend(sku_pages)
        
        _LOG.info(f"Created scalable UI: 1 directory + {len(sku_pages)} SKU pages = {len(pages)} total pages")
        return pages
    
    def _create_device_directory_page(self) -> UiPage:
        """Create the main device directory page."""
        directory_page = UiPage(page_id="main", name="Nanoleaf Devices", grid=Size(4, 6))
        directory_page.add(create_ui_text("Nanoleaf Devices", 0, 0, Size(4, 1)))
        
        sku_groups = self._group_devices_by_sku()
        y = 1
        
        for sku, devices in sku_groups.items():
            if y >= 5:
                break
            
            device_type_name = self._get_sku_display_name(sku, devices)
            directory_page.add(create_ui_text(f"{device_type_name}:", 0, y, Size(4, 1)))
            y += 1
            
            for device_id, device_info in devices.items():
                if y >= 5:
                    break
                    
                device_name = device_info.get("name", f"Device {device_id}")
                display_name = device_name[:18] if len(device_name) > 18 else device_name
                panel_count = device_info.get("panel_count", 0)
                
                if panel_count > 0:
                    display_text = f"• {display_name} ({panel_count}p)"
                else:
                    display_text = f"• {display_name}"
                
                directory_page.add(create_ui_text(display_text, 0, y, Size(4, 1)))
                y += 1
        
        # Add global controls if multiple devices
        if len(self._discovered_devices) > 1 and y < 6:
            directory_page.add(create_ui_text("All On", 0, 5, Size(2, 1), "ALL_ON"))
            directory_page.add(create_ui_text("All Off", 2, 5, Size(2, 1), "ALL_OFF"))
        
        return directory_page
    
    def _group_devices_by_sku(self) -> Dict[str, Dict[str, Any]]:
        """Group devices by SKU/model."""
        sku_groups = {}
        
        for device_id, device_info in self._discovered_devices.items():
            sku = device_info.get("sku", "Unknown")
            
            if sku not in sku_groups:
                sku_groups[sku] = {}
            
            sku_groups[sku][device_id] = device_info
        
        return sku_groups
    
    def _get_sku_display_name(self, sku: str, devices: Dict[str, Any]) -> str:
        """Get display name for SKU group."""
        first_device = next(iter(devices.values()))
        device_type = first_device.get("device_type", "")
        
        type_names = {
            "light_panels": "Light Panels",
            "canvas": "Canvas",
            "shapes": "Shapes", 
            "elements": "Elements",
            "lines": "Lines",
            "strip": "LED Strips",
            "panels": "Panels"
        }
        
        friendly_name = type_names.get(device_type, "Devices")
        device_count = len(devices)
        
        if device_count > 1:
            return f"{friendly_name} ({sku}) - {device_count} devices"
        else:
            return f"{friendly_name} ({sku})"
    
    def _create_sku_control_pages(self) -> List[UiPage]:
        """Create control pages for each SKU group."""
        sku_groups = self._group_devices_by_sku()
        pages = []
        
        for sku, devices in sku_groups.items():
            page = self._create_sku_page(sku, devices)
            if page:
                pages.append(page)
        
        return pages
    
    def _create_sku_page(self, sku: str, devices: Dict[str, Any]) -> UiPage:
        """Create a control page for a specific SKU group."""
        page_name = self._get_sku_display_name(sku, devices)
        page_id = f"sku_{sku.replace('-', '_').lower()}"
        page = UiPage(page_id=page_id, name=page_name, grid=Size(4, 6))
        page.add(create_ui_text(page_name, 0, 0, Size(4, 1)))
        
        y = 1
        
        if len(devices) == 1:
            # Single device - full controls
            device_id, device_info = next(iter(devices.items()))
            y = self._add_single_device_controls(page, device_id, device_info, start_y=y)
        else:
            # Multiple devices - compact controls
            y = self._add_multi_device_controls(page, devices, start_y=y)
        
        _LOG.info(f"Created SKU page for {sku}: {len(devices)} devices, {y} rows used")
        return page
    
    def _add_single_device_controls(self, page: UiPage, device_id: str, device_info: Dict[str, Any], start_y: int) -> int:
        """Add comprehensive controls for a single device."""
        device_name = device_info.get("name", f"Device {device_id}")
        clean_name = self._clean_command_name(device_name)
        y = start_y
        
        # Power controls
        page.add(create_ui_text("On", 0, y, Size(1, 1), f"{clean_name}_ON"))
        page.add(create_ui_text("Off", 1, y, Size(1, 1), f"{clean_name}_OFF"))
        page.add(create_ui_text("Toggle", 2, y, Size(2, 1), f"{clean_name}_TOGGLE"))
        y += 1
        
        # Brightness presets
        if y < 6:
            page.add(create_ui_text("25%", 0, y, Size(1, 1), f"{clean_name}_BRIGHTNESS_25"))
            page.add(create_ui_text("50%", 1, y, Size(1, 1), f"{clean_name}_BRIGHTNESS_50"))
            page.add(create_ui_text("75%", 2, y, Size(1, 1), f"{clean_name}_BRIGHTNESS_75"))
            page.add(create_ui_text("100%", 3, y, Size(1, 1), f"{clean_name}_BRIGHTNESS_100"))
            y += 1
        
        # Color presets
        if y < 6:
            page.add(create_ui_text("Red", 0, y, Size(1, 1), f"{clean_name}_COLOR_RED"))
            page.add(create_ui_text("Green", 1, y, Size(1, 1), f"{clean_name}_COLOR_GREEN"))
            page.add(create_ui_text("Blue", 2, y, Size(1, 1), f"{clean_name}_COLOR_BLUE"))
            page.add(create_ui_text("White", 3, y, Size(1, 1), f"{clean_name}_COLOR_WHITE"))
            y += 1
        
        # Color temperature
        if y < 6:
            page.add(create_ui_text("Warm", 0, y, Size(2, 1), f"{clean_name}_TEMP_WARM"))
            page.add(create_ui_text("Cool", 2, y, Size(2, 1), f"{clean_name}_TEMP_COOL"))
            y += 1
        
        # Effects (first 4)
        effects_list = device_info.get("effects_list", [])
        if effects_list and y < 6:
            for i, effect in enumerate(effects_list[:4]):
                if y >= 6:
                    break
                effect_name = self._clean_command_name(effect)
                display_name = effect[:8] if len(effect) > 8 else effect
                page.add(create_ui_text(display_name, i, y, Size(1, 1), f"{clean_name}_EFFECT_{effect_name}"))
                
                if (i + 1) % 4 == 0:
                    y += 1
            
            if len(effects_list) % 4 != 0:
                y += 1
        
        # Identify button
        if y < 6:
            page.add(create_ui_text("Identify", 0, y, Size(2, 1), f"{clean_name}_IDENTIFY"))
        
        return y + 1
    
    def _add_multi_device_controls(self, page: UiPage, devices: Dict[str, Any], start_y: int) -> int:
        """Add compact controls for multiple devices."""
        y = start_y
        
        # List devices with toggle controls
        for device_id, device_info in devices.items():
            if y >= 5:
                break
                
            device_name = device_info.get("name", f"Device {device_id}")
            clean_name = self._clean_command_name(device_name)
            
            display_name = device_name[:12] if len(device_name) > 12 else device_name
            panel_count = device_info.get("panel_count", 0)
            
            if panel_count > 0:
                display_text = f"{display_name} ({panel_count}p)"
            else:
                display_text = display_name
            
            page.add(create_ui_text(display_text, 0, y, Size(2, 1)))
            page.add(create_ui_text("Toggle", 2, y, Size(2, 1), f"{clean_name}_TOGGLE"))
            y += 1
        
        # Global controls at bottom
        if y < 6:
            page.add(create_ui_text("All On", 0, 5, Size(2, 1), "ALL_ON"))
            page.add(create_ui_text("All Off", 2, 5, Size(2, 1), "ALL_OFF"))
        
        return y
    
    async def push_initial_state(self):
        """Push initial state to the remote entity."""
        _LOG.info("Setting initial remote entity state")
        
        if not self._api.configured_entities.contains(self.entity.id):
            _LOG.warning(f"Entity {self.entity.id} not in configured entities yet")
            return
        
        initial_state = States.ON
        initial_attributes = {"state": initial_state}
        self._api.configured_entities.update_attributes(self.entity.id, initial_attributes)
        _LOG.info(f"Initial state set successfully - remote entity is {initial_state}")

    async def _check_throttle(self, device_id: str) -> bool:
        """Check if command should be throttled."""
        import time
        
        current_time = time.time()
        
        # Global throttle
        if current_time - self._global_throttle < 0.1:
            return False
        
        # Device-specific throttle
        last_time = self._device_throttle.get(device_id, 0)
        if current_time - last_time < 0.3:
            return False
        
        self._global_throttle = current_time
        self._device_throttle[device_id] = current_time
        return True

    async def cmd_handler(self, entity: ucapi.Entity, cmd_id: str, params: dict[str, Any] | None) -> ucapi.StatusCodes:
        """Handle remote entity commands."""
        _LOG.info("Remote command: %s %s", cmd_id, params)
        
        if not self._client:
            return ucapi.StatusCodes.SERVICE_UNAVAILABLE
        
        try:
            if cmd_id == Commands.ON:
                return await self._handle_on()
            elif cmd_id == Commands.OFF:
                return await self._handle_off()
            elif cmd_id == Commands.SEND_CMD:
                return await self._handle_send_cmd(params)
            else:
                return ucapi.StatusCodes.NOT_IMPLEMENTED
                
        except Exception as e:
            _LOG.error("Error handling remote command %s: %s", cmd_id, e, exc_info=True)
            return ucapi.StatusCodes.SERVER_ERROR
    
    async def _handle_on(self) -> ucapi.StatusCodes:
        """Handle remote ON command."""
        self._api.configured_entities.update_attributes(self.entity.id, {"state": States.ON})
        return ucapi.StatusCodes.OK
    
    async def _handle_off(self) -> ucapi.StatusCodes:
        """Handle remote OFF command."""
        self._api.configured_entities.update_attributes(self.entity.id, {"state": States.OFF})
        return ucapi.StatusCodes.OK
    
    async def _handle_send_cmd(self, params: dict[str, Any] | None) -> ucapi.StatusCodes:
        """Handle SEND_CMD command."""
        if not params or "command" not in params:
            return ucapi.StatusCodes.BAD_REQUEST
        
        command = params["command"]
        success = await self._execute_nanoleaf_command(command)
        return ucapi.StatusCodes.OK if success else ucapi.StatusCodes.SERVER_ERROR
    
    async def _execute_nanoleaf_command(self, command: str) -> bool:
        """Execute a Nanoleaf command."""
        try:
            if not self._discovered_devices or command == "NO_DEVICES":
                return False
            
            if command.startswith("ALL_"):
                return await self._execute_global_command(command)
            
            return await self._execute_device_command(command)
            
        except Exception as e:
            _LOG.error(f"Error executing Nanoleaf command {command}: {e}")
            return False
    
    async def _execute_global_command(self, command: str) -> bool:
        """Execute global commands affecting all devices."""
        _LOG.info(f"Executing global command: {command} for {len(self._discovered_devices)} devices")
        
        tasks = []
        
        for device_id, device_info in self._discovered_devices.items():
            device_name = device_info.get('name', f"Device_{device_id}")
            _LOG.info(f"Creating task for device: {device_name} ({device_id})")
            
            if command == "ALL_ON":
                task = self._execute_device_action_safe(device_id, "turn_on", device_name)
            elif command == "ALL_OFF":
                task = self._execute_device_action_safe(device_id, "turn_off", device_name)
            elif command == "ALL_TOGGLE":
                task = self._execute_device_action_safe(device_id, "toggle", device_name)
            elif command == "ALL_IDENTIFY":
                task = self._execute_device_action_safe(device_id, "identify", device_name)
            else:
                _LOG.warning(f"Unknown global command: {command}")
                continue
            
            tasks.append(task)
        
        if tasks:
            _LOG.info(f"Executing {len(tasks)} device tasks for global command {command}")
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = 0
                
                for i, result in enumerate(results):
                    device_id = list(self._discovered_devices.keys())[i]
                    device_name = self._discovered_devices[device_id].get('name', f"Device_{device_id}")
                    
                    if isinstance(result, Exception):
                        _LOG.error(f"Exception for device {device_name}: {result}")
                    elif result is True:
                        success_count += 1
                        _LOG.info(f"SUCCESS: {device_name} completed {command}")
                    else:
                        _LOG.warning(f"FAILED: {device_name} failed {command}")
                
                _LOG.info(f"Global command {command} completed: {success_count}/{len(tasks)} devices succeeded")
                return success_count > 0
                
            except Exception as e:
                _LOG.error(f"Error executing global command {command}: {e}", exc_info=True)
                return False
        else:
            _LOG.warning(f"No tasks created for global command {command}")
            return False
    
    async def _execute_device_action_safe(self, device_id: str, action: str, device_name: str) -> bool:
        """Safely execute an action on a device."""
        try:
            _LOG.info(f"Executing {action} on device {device_name} ({device_id})")
            
            # Skip throttling for global commands to ensure all devices execute
            # Global commands are user-initiated and should execute immediately
            # if not await self._check_throttle(device_id):
            #     _LOG.debug(f"Throttle skipped for global command on {device_name}")
            #     return True
            
            device_info = self._discovered_devices.get(device_id)
            if not device_info:
                _LOG.error(f"Device info not found for {device_id}")
                return False
            
            # Create device object
            ip_address = device_info.get("ip_address")
            auth_token = device_info.get("auth_token")
            
            if not ip_address or not auth_token:
                _LOG.error(f"Missing IP ({ip_address}) or auth token for device {device_name}")
                return False
            
            device = NanoleafDevice(ip_address, auth_token, device_info)
            
            if action == "turn_on":
                _LOG.info(f"Turning ON device {device_name}")
                result = await self._client.turn_on(device)
                if result:
                    self._device_states[device_id] = True
                    _LOG.info(f"✅ Successfully turned ON {device_name}")
                else:
                    _LOG.error(f"❌ Failed to turn ON {device_name}")
                return result
            elif action == "turn_off":
                _LOG.info(f"Turning OFF device {device_name}")
                result = await self._client.turn_off(device)
                if result:
                    self._device_states[device_id] = False
                    _LOG.info(f"✅ Successfully turned OFF {device_name}")
                else:
                    _LOG.error(f"❌ Failed to turn OFF {device_name}")
                return result
            elif action == "toggle":
                # Get current state and toggle
                current_state = await self._get_device_state(device_id, device)
                _LOG.info(f"Toggle for {device_name}: current state is {'ON' if current_state else 'OFF'}")
                
                if current_state:
                    _LOG.info(f"Toggling {device_name} from ON to OFF")
                    result = await self._client.turn_off(device)
                    if result:
                        self._device_states[device_id] = False
                        _LOG.info(f"✅ Toggled {device_name} OFF")
                    else:
                        _LOG.error(f"❌ Failed to toggle {device_name} OFF")
                else:
                    _LOG.info(f"Toggling {device_name} from OFF to ON")
                    result = await self._client.turn_on(device)
                    if result:
                        self._device_states[device_id] = True
                        _LOG.info(f"✅ Toggled {device_name} ON")
                    else:
                        _LOG.error(f"❌ Failed to toggle {device_name} ON")
                
                return result
            elif action == "identify":
                _LOG.info(f"Identifying device {device_name}")
                result = await self._client.identify_device(device)
                if result:
                    _LOG.info(f"✅ Successfully identified {device_name}")
                else:
                    _LOG.error(f"❌ Failed to identify {device_name}")
                return result
            else:
                _LOG.error(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            _LOG.error(f"Exception executing {action} on device {device_name}: {e}", exc_info=True)
            return False

    async def _get_device_state(self, device_id: str, device: NanoleafDevice = None) -> bool:
        """Get current device state."""
        try:
            if device is None:
                device_info = self._discovered_devices.get(device_id)
                if not device_info:
                    return False
                
                ip_address = device_info.get("ip_address")
                auth_token = device_info.get("auth_token")
                device = NanoleafDevice(ip_address, auth_token, device_info)
            
            # Get fresh device info
            device_info = await self._client.get_device_info(device)
            if device_info and "state" in device_info:
                state = device_info["state"].get("on", {}).get("value", False)
                self._device_states[device_id] = state
                return state
            
            # Fallback to cached state
            return self._device_states.get(device_id, False)
            
        except Exception as e:
            _LOG.warning(f"Failed to get state for device {device_id}: {e}")
            return self._device_states.get(device_id, False)
    
    async def _execute_device_command(self, command: str) -> bool:
        """Execute a command on a specific device."""
        for device_id, device_info in self._discovered_devices.items():
            device_name = device_info.get("name", f"Device_{device_id}")
            device_prefix = self._clean_command_name(device_name)
            
            if command.startswith(device_prefix + "_"):
                if not await self._check_throttle(device_id):
                    return True
                
                action_part = command[len(device_prefix)+1:]
                
                try:
                    # Create device object
                    ip_address = device_info.get("ip_address")
                    auth_token = device_info.get("auth_token")
                    
                    if not ip_address or not auth_token:
                        _LOG.error(f"Missing IP or auth token for device {device_name}")
                        return False
                    
                    device = NanoleafDevice(ip_address, auth_token, device_info)
                    
                    return await self._execute_device_action(device, action_part, device_info, device_id)
                    
                except Exception as e:
                    _LOG.error(f"Exception executing action on device {device_name}: {e}")
                    return False
        
        return False
    
    async def _execute_device_action(self, device: NanoleafDevice, action: str, device_info: Dict[str, Any], device_id: str = None) -> bool:
        """Execute a specific action on a device."""
        try:
            if action == "ON":
                result = await self._client.turn_on(device)
                if result and device_id:
                    self._device_states[device_id] = True
                return result
            elif action == "OFF":
                result = await self._client.turn_off(device)
                if result and device_id:
                    self._device_states[device_id] = False
                return result
            elif action == "TOGGLE":
                if device_id:
                    current_state = await self._get_device_state(device_id, device)
                    _LOG.info(f"Toggle for {device.name}: current state is {'ON' if current_state else 'OFF'}")
                    
                    if current_state:
                        result = await self._client.turn_off(device)
                        if result:
                            self._device_states[device_id] = False
                    else:
                        result = await self._client.turn_on(device)
                        if result:
                            self._device_states[device_id] = True
                    
                    return result
                else:
                    # Fallback - just turn on
                    return await self._client.turn_on(device)
            elif action == "IDENTIFY":
                return await self._client.identify_device(device)
            elif action.startswith("BRIGHTNESS_"):
                if "UP" in action:
                    brightness = min(100, device.brightness + 20)
                elif "DOWN" in action:
                    brightness = max(1, device.brightness - 20)
                else:
                    # Extract percentage
                    parts = action.split("_")
                    brightness = 50
                    for part in parts:
                        if part.isdigit():
                            brightness = int(part)
                            break
                return await self._client.set_brightness(device, brightness)
            elif action.startswith("COLOR_"):
                color_map = {
                    "RED": (0, 100),      # Hue, Saturation
                    "GREEN": (120, 100),
                    "BLUE": (240, 100),
                    "WHITE": (0, 0),
                    "PURPLE": (300, 100),
                    "YELLOW": (60, 100),
                    "WARM": (30, 50),
                    "COOL": (210, 30)
                }
                color_name = action.replace("COLOR_", "")
                if color_name in color_map:
                    hue, sat = color_map[color_name]
                    await self._client.set_hue(device, hue)
                    await self._client.set_saturation(device, sat)
                    return True
                return False
            elif action.startswith("TEMP_"):
                device_type = device_info.get("device_type", "")
                
                # Elements devices should use color commands instead of temperature commands
                if device_type == "elements":
                    _LOG.info(f"Elements device detected, converting TEMP command to COLOR command for {device.name}")
                    # Convert TEMP command to COLOR command for Elements
                    if action == "TEMP_WARM":
                        color_action = "COLOR_WARM"
                    elif action == "TEMP_COOL":
                        color_action = "COLOR_COOL"
                    else:
                        # For specific Kelvin values, map to closest color
                        if "2700K" in action:
                            color_action = "COLOR_WARM"
                        elif "4000K" in action or "6500K" in action:
                            color_action = "COLOR_COOL"
                        else:
                            _LOG.warning(f"Unknown temperature action for Elements: {action}")
                            return False
                    
                    # Execute as color command instead
                    _LOG.info(f"Executing {color_action} instead of {action} for Elements device")
                    return await self._execute_device_action(device, color_action, device_info, device_id)
                
                # Non-Elements devices use normal temperature commands
                temp_map = {
                    "WARM": 2700,
                    "COOL": 6500,
                    "2700K": 2700,
                    "4000K": 4000,
                    "6500K": 6500
                }
                
                temp_name = action.replace("TEMP_", "")
                if temp_name in temp_map:
                    kelvin = temp_map[temp_name]
                    _LOG.info(f"Setting color temperature to {kelvin}K for device {device.name} (type: {device_type})")
                    result = await self._client.set_color_temperature(device, kelvin)
                    _LOG.info(f"Color temperature command result: {result}")
                    return result
                _LOG.warning(f"Unknown temperature setting: {temp_name}")
                return False
            elif action.startswith("EFFECT_"):
                effect_name = action.replace("EFFECT_", "").replace("_", " ")
                
                # Find matching effect from device's effect list
                effects_list = device_info.get("effects_list", [])
                for effect in effects_list:
                    if self._clean_command_name(effect) == self._clean_command_name(effect_name):
                        return await self._client.set_effect(device, effect)
                
                # If not found, try direct name
                if effect_name in effects_list:
                    return await self._client.set_effect(device, effect_name)
                
                return False
            else:
                _LOG.warning(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            _LOG.error(f"Error executing action {action}: {e}", exc_info=True)
            return False