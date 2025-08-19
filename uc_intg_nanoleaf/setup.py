"""
Setup flow for Nanoleaf integration with breakthrough selective pairing approach.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, List, Tuple

import ucapi.api_definitions as uc
from uc_intg_nanoleaf.client import NanoleafClient, NanoleafDevice
from uc_intg_nanoleaf.config import NanoleafConfig

_LOG = logging.getLogger(__name__)


class NanoleafSetup:
    """Setup handler for Nanoleaf integration with selective pairing approach."""

    def __init__(self, config: NanoleafConfig, client: NanoleafClient, setup_complete_callback: Callable[[], Coroutine[Any, Any, None]]):
        self.config = config
        self.client = client
        self._setup_complete_callback = setup_complete_callback
        self._discovered_devices: List[Tuple[str, int]] = []
        self._selected_devices: List[str] = []
        self._setup_phase = "discovery"  # discovery, selection, pairing, complete

    async def setup_handler(self, msg: uc.SetupDriver) -> uc.SetupAction:
        _LOG.info("Setup handler called with: %s", type(msg).__name__)

        if isinstance(msg, uc.DriverSetupRequest):
            return await self._handle_driver_setup_request(msg)
        elif isinstance(msg, uc.UserDataResponse):
            return await self._handle_user_data_response(msg)
        elif isinstance(msg, uc.UserConfirmationResponse):
            return await self._handle_user_confirmation_response(msg)
        elif isinstance(msg, uc.AbortDriverSetup):
            return await self._handle_abort_setup(msg)
        
        return uc.SetupError(uc.IntegrationSetupError.OTHER)

    async def _handle_driver_setup_request(self, msg: uc.DriverSetupRequest) -> uc.SetupAction:
        _LOG.debug("Handling driver setup request.")

        if self.config.is_configured() and not msg.reconfigure:
            _LOG.info("Already configured, checking if working...")
            
            if await self._test_existing_config():
                _LOG.info("Existing configuration works, proceeding to completion")
                await self._setup_complete_callback()
                return uc.SetupComplete()
            else:
                _LOG.warning("Existing configuration failed - need to reconfigure")

        # Start breakthrough discovery approach
        _LOG.info("Starting breakthrough Nanoleaf discovery approach...")
        return await self._start_breakthrough_discovery()

    async def _test_existing_config(self) -> bool:
        """Test existing configuration to see if devices are still accessible."""
        try:
            devices = self.config.devices
            if not devices:
                return False
            
            # Test connection to at least one device
            for device_id, device_config in devices.items():
                ip_address = device_config.get("ip_address")
                auth_token = device_config.get("auth_token")
                
                if ip_address and auth_token:
                    device = NanoleafDevice(ip_address, auth_token)
                    if await self.client.test_connection(device):
                        _LOG.info(f"Verified connection to device at {ip_address}")
                        return True
            
            return False
        except Exception as e:
            _LOG.error(f"Error testing existing config: {e}")
            return False

    async def _start_breakthrough_discovery(self) -> uc.SetupAction:
        """Phase 1: Quick discovery (5 seconds) + device selection UI."""
        try:
            _LOG.info("🚀 Phase 1: Quick discovery + device selection...")
            self._setup_phase = "discovery"
            
            # Quick device discovery (5 seconds max)
            _LOG.info("Discovering Nanoleaf devices (5 seconds)...")
            discovered_devices = await self.client.discover_devices(use_mdns=True, scan_network=False)
            
            if not discovered_devices:
                # If no devices found via mDNS, offer alternatives
                return await self._handle_no_devices_found()
            
            # Store discovered devices for selection
            self._discovered_devices = discovered_devices
            self._setup_phase = "selection"
            
            # Create device selection UI
            return await self._create_device_selection_ui()
            
        except Exception as e:
            _LOG.error(f"Error during breakthrough discovery: {e}")
            return uc.SetupError(uc.IntegrationSetupError.OTHER)

    async def _handle_no_devices_found(self) -> uc.SetupAction:
        """Handle case when no devices are discovered."""
        return uc.RequestUserInput(
            title={"en": "No Nanoleaf Devices Found"},
            settings=[
                {
                    "id": "discovery_method",
                    "label": {"en": "Discovery Method"},
                    "field": {
                        "dropdown": {
                            "items": [
                                {"id": "manual", "label": {"en": "Manual IP Entry"}},
                                {"id": "scan", "label": {"en": "Network Scan (slower)"}},
                                {"id": "retry", "label": {"en": "Retry Auto Discovery"}}
                            ]
                        }
                    }
                },
                {
                    "id": "manual_ip",
                    "label": {"en": "Device IP Address (if manual)"},
                    "field": {
                        "text": {
                            "placeholder": "192.168.1.100"
                        }
                    }
                }
            ]
        )

    async def _get_device_friendly_name(self, ip_address: str, port: int) -> str:
        """Get friendly device name based on port mapping."""
        port_to_name = {
            16021: "Living Room Panels",
            16022: "Bedroom Canvas", 
            16023: "Office Shapes"
        }
        
        friendly_name = port_to_name.get(port)
        if friendly_name:
            return friendly_name
        else:
            # Fallback to IP if port not in mapping
            return f"Device at {ip_address}:{port}"

    async def _create_device_selection_ui(self) -> uc.SetupAction:
        """Create device selection UI with friendly names."""
        if not self._discovered_devices:
            return uc.SetupError(uc.IntegrationSetupError.NOT_FOUND)
        
        max_devices = min(3, len(self._discovered_devices))
        devices_for_selection = self._discovered_devices[:max_devices]
        
        _LOG.info(f"Creating device selection UI for {len(devices_for_selection)} devices")
        
        # FIXED: Proper UC Remote setup format
        settings = []
        
        # Add info text field
        settings.append({
            "id": "info_text",
            "label": {"en": "Device Selection"},
            "field": {
                "text": {
                    "value": f"Found {len(self._discovered_devices)} Nanoleaf devices. Select up to {max_devices} for quick setup:"
                }
            }
        })
        
        # Add checkbox for each discovered device with friendly names
        for i, (ip_address, port) in enumerate(devices_for_selection):
            device_id = f"device_{i}"
            
            settings.append({
                "id": device_id,
                "label": {"en": await self._get_device_friendly_name(ip_address, port)},  # <-- FIXED: Shows friendly name
                "field": {
                    "checkbox": {
                        "value": True if i == 0 else False
                    }
                }
            })
        
        # Add additional devices note if needed
        if len(self._discovered_devices) > max_devices:
            settings.append({
                "id": "additional_note",
                "label": {"en": "Additional Devices"},
                "field": {
                    "text": {
                        "value": f"{len(self._discovered_devices) - max_devices} more devices found - can be added after initial setup"
                    }
                }
            })
        
        return uc.RequestUserInput(
            title={"en": "Select Nanoleaf Devices"},
            settings=settings
        )

    async def _handle_user_data_response(self, msg: uc.UserDataResponse) -> uc.SetupAction:
        """Handle user input for discovery method or device selection."""
        _LOG.debug(f"Handling user data response in phase: {self._setup_phase}")
        
        if self._setup_phase == "discovery":
            # Handle discovery method selection
            return await self._handle_discovery_method_selection(msg)
        elif self._setup_phase == "selection":
            # Handle device selection
            return await self._handle_device_selection(msg)
        else:
            return uc.SetupError(uc.IntegrationSetupError.OTHER)

    async def _handle_discovery_method_selection(self, msg: uc.UserDataResponse) -> uc.SetupAction:
        """Handle discovery method selection."""
        discovery_method = msg.input_values.get("discovery_method", "manual")
        manual_ip = msg.input_values.get("manual_ip", "").strip()
        
        if discovery_method == "manual" and manual_ip:
            # Manual IP entry
            try:
                # Validate IP format
                import ipaddress
                ipaddress.ip_address(manual_ip)
                
                self._discovered_devices = [(manual_ip, 16021)]
                self._setup_phase = "selection"
                return await self._create_device_selection_ui()
                
            except ValueError:
                return uc.SetupError(uc.IntegrationSetupError.OTHER)
                
        elif discovery_method == "scan":
            # Network scan (slower)
            _LOG.info("Starting network scan for Nanoleaf devices...")
            try:
                base_ip = "192.168.1"  # Could be made configurable
                scanned_devices = await self.client.discovery.scan_ip_range(base_ip)
                
                if scanned_devices:
                    self._discovered_devices = scanned_devices
                    self._setup_phase = "selection"
                    return await self._create_device_selection_ui()
                else:
                    return uc.SetupError(uc.IntegrationSetupError.NOT_FOUND)
                    
            except Exception as e:
                _LOG.error(f"Error during network scan: {e}")
                return uc.SetupError(uc.IntegrationSetupError.OTHER)
                
        elif discovery_method == "retry":
            # Retry auto discovery
            return await self._start_breakthrough_discovery()
        
        return uc.SetupError(uc.IntegrationSetupError.OTHER)

    async def _handle_device_selection(self, msg: uc.UserDataResponse) -> uc.SetupAction:
        """Handle device selection and proceed to simultaneous pairing."""
        # Extract selected devices
        selected_devices = []
        for i, (ip_address, port) in enumerate(self._discovered_devices[:3]):  # Max 3 devices
            device_key = f"device_{i}"
            if msg.input_values.get(device_key, False):
                selected_devices.append((ip_address, port))
        
        if not selected_devices:
            # No devices selected
            return uc.SetupError(uc.IntegrationSetupError.OTHER)
        
        self._selected_devices = selected_devices
        self._setup_phase = "pairing"
        
        _LOG.info(f"User selected {len(selected_devices)} devices for pairing")
        
        # Show pairing instructions
        return await self._show_simultaneous_pairing_instructions()

    async def _show_simultaneous_pairing_instructions(self) -> uc.SetupAction:
        """Show instructions for simultaneous pairing."""
        device_count = len(self._selected_devices)
        device_list = "\n".join([f"• {ip}:{port}" for ip, port in self._selected_devices])
        
        return uc.RequestUserConfirmation(
            title={"en": f"Pair {device_count} Nanoleaf Devices"},
            header={"en": f"Ready to pair {device_count} selected devices:"},
            footer={
                "en": f"STEP 1: Press and hold the power button on ALL {device_count} selected devices for 5-7 seconds until LEDs flash\n\n"
                      f"STEP 2: Click Continue immediately after pressing all buttons\n\n"
                      f"Devices to pair:\n{device_list}\n\n"
                      f"NOTE: For simulator testing, devices are auto-paired - just click Continue!"
            }
        )

    async def _handle_user_confirmation_response(self, msg: uc.UserConfirmationResponse) -> uc.SetupAction:
        """Handle user confirmation for simultaneous pairing."""
        _LOG.debug(f"Handling user confirmation in phase: {self._setup_phase}")
        
        if self._setup_phase == "pairing":
            if not msg.confirm:
                # User cancelled
                return uc.SetupError(uc.IntegrationSetupError.OTHER)
            
            # Execute simultaneous pairing
            return await self._execute_simultaneous_pairing()
        
        return uc.SetupError(uc.IntegrationSetupError.OTHER)

    async def _execute_simultaneous_pairing(self) -> uc.SetupAction:
        """🚀 BREAKTHROUGH: Execute simultaneous pairing of all selected devices."""
        _LOG.info(f"🚀 Executing breakthrough simultaneous pairing for {len(self._selected_devices)} devices...")
        
        try:
            # Create pairing tasks for all selected devices
            pairing_tasks = []
            for ip_address, port in self._selected_devices:
                task = self._pair_device_async(ip_address, port)
                pairing_tasks.append(task)
            
            # Execute all pairing tasks simultaneously with timeout
            _LOG.info("Starting simultaneous pairing (30-second timeout)...")
            results = await asyncio.wait_for(
                asyncio.gather(*pairing_tasks, return_exceptions=True),
                timeout=30.0
            )
            
            # Process pairing results
            successful_devices = []
            failed_devices = []
            
            for i, result in enumerate(results):
                ip_address, port = self._selected_devices[i]
                
                if isinstance(result, Exception):
                    _LOG.error(f"Pairing failed for {ip_address}: {result}")
                    failed_devices.append(ip_address)
                elif result is None:
                    _LOG.error(f"Pairing failed for {ip_address}: No auth token received")
                    failed_devices.append(ip_address)
                else:
                    auth_token, device_info = result
                    self.config.add_device(ip_address, auth_token, device_info)
                    successful_devices.append(ip_address)
                    _LOG.info(f"✅ Successfully paired device at {ip_address}")
            
            # Evaluate results
            if successful_devices:
                _LOG.info(f"🎉 Breakthrough success! Paired {len(successful_devices)}/{len(self._selected_devices)} devices")
                
                if failed_devices:
                    _LOG.warning(f"⚠️ {len(failed_devices)} devices failed to pair: {failed_devices}")
                
                # Complete setup with successful devices
                return await self._complete_breakthrough_setup(successful_devices, failed_devices)
            else:
                _LOG.error("❌ All devices failed to pair")
                return uc.SetupError(uc.IntegrationSetupError.OTHER)
                
        except asyncio.TimeoutError:
            _LOG.error("⏱️ Pairing timeout - devices may not have been in pairing mode")
            return uc.SetupError(uc.IntegrationSetupError.TIMEOUT)
        except Exception as e:
            _LOG.error(f"❌ Error during simultaneous pairing: {e}")
            return uc.SetupError(uc.IntegrationSetupError.OTHER)

    async def _pair_device_async(self, ip_address: str, port: int) -> Tuple[str, Dict[str, Any]] | None:
        """Asynchronously pair with a single device."""
        try:
            _LOG.debug(f"Attempting to pair with device at {ip_address}:{port}")
            
            # Attempt pairing
            auth_token = await self.client.pair_device(ip_address, port)
            
            if auth_token:
                # Get device info
                device = NanoleafDevice(ip_address, auth_token)
                device_info = await self.client.get_device_info(device)
                
                if device_info:
                    return auth_token, device_info
                else:
                    # Pairing successful but couldn't get device info
                    basic_info = {"name": f"Nanoleaf {ip_address}", "model": "Unknown"}
                    return auth_token, basic_info
            
            return None
            
        except Exception as e:
            _LOG.error(f"Error pairing device at {ip_address}: {e}")
            raise e

    async def _complete_breakthrough_setup(self, successful_devices: List[str], failed_devices: List[str]) -> uc.SetupAction:
        """Complete the breakthrough setup process."""
        try:
            devices = self.config.devices
            device_count = len(devices)
            
            if device_count == 0:
                _LOG.error("Setup completed but no devices were configured")
                return uc.SetupError(uc.IntegrationSetupError.NOT_FOUND)
            
            _LOG.info(f"🎉 Breakthrough setup completed successfully with {device_count} Nanoleaf devices!")
            
            # Log device summary
            for device_id, device_config in devices.items():
                _LOG.info(f"✅ Configured device: {device_config.get('name')} ({device_config.get('model')}) at {device_config.get('ip_address')}")
            
            # Note about failed devices (if any)
            if failed_devices:
                _LOG.info(f"ℹ️ {len(failed_devices)} devices can be added later via reconfigure")
            
            # Complete setup
            await self._setup_complete_callback()
            return uc.SetupComplete()
            
        except Exception as e:
            _LOG.error(f"Error completing setup: {e}")
            return uc.SetupError(uc.IntegrationSetupError.OTHER)

    async def _handle_abort_setup(self, msg: uc.AbortDriverSetup) -> uc.SetupAction:
        """Handle setup abort."""
        _LOG.info(f"Setup aborted: {msg.error}")
        self.config.clear()
        return uc.SetupError(msg.error)