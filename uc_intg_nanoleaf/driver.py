#!/usr/bin/env python3
"""
Nanoleaf integration driver for Unfolded Circle Remote.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""
import asyncio
import logging
import os
import signal
from typing import Optional

import ucapi

from uc_intg_nanoleaf.client import NanoleafClient
from uc_intg_nanoleaf.config import NanoleafConfig
from uc_intg_nanoleaf.remote import NanoleafRemote
from uc_intg_nanoleaf.setup import NanoleafSetup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)8s | %(name)s | %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

_LOG = logging.getLogger(__name__)

loop = asyncio.get_event_loop()
api: Optional[ucapi.IntegrationAPI] = None
nanoleaf_client: Optional[NanoleafClient] = None
nanoleaf_config: Optional[NanoleafConfig] = None
remote: Optional[NanoleafRemote] = None

async def on_setup_complete():
    """Callback executed when driver setup is complete."""
    global remote, nanoleaf_client, api
    _LOG.info("Setup complete. Creating entities...")

    if not api or not nanoleaf_client:
        _LOG.error("Cannot create entities: API or client not initialized.")
        await api.set_device_state(ucapi.DeviceStates.ERROR)
        return

    try:
        if not nanoleaf_config.is_configured():
            _LOG.error("Nanoleaf client is not configured after setup")
            await api.set_device_state(ucapi.DeviceStates.ERROR)
            return

        discovered_devices = nanoleaf_config.devices
        _LOG.info(f"Creating entities for {len(discovered_devices)} discovered devices")
        
        for device_id, device_info in discovered_devices.items():
            _LOG.debug(f"Device {device_id}: {device_info.get('name')} ({device_info.get('device_type')}) - SKU: {device_info.get('sku')}")

        remote = NanoleafRemote(api, nanoleaf_client, nanoleaf_config)
        api.available_entities.add(remote.entity)
        _LOG.info(f"Added remote entity: {remote.entity.id}")
        
        _LOG.info("Remote entity created successfully. Setting state to CONNECTED.")
        await api.set_device_state(ucapi.DeviceStates.CONNECTED)
        
    except Exception as e:
        _LOG.error(f"Error creating entities: {e}", exc_info=True)
        await api.set_device_state(ucapi.DeviceStates.ERROR)

async def on_r2_connect():
    """Handle Remote connection."""
    _LOG.info("Remote connected.")
    
    if api and nanoleaf_config and nanoleaf_config.is_configured():
        if nanoleaf_client:
            # Test connection to at least one device
            devices = nanoleaf_config.devices
            connection_ok = False
            
            for device_id, device_config in devices.items():
                ip_address = device_config.get("ip_address")
                auth_token = device_config.get("auth_token")
                
                if ip_address and auth_token:
                    from uc_intg_nanoleaf.client import NanoleafDevice
                    device = NanoleafDevice(ip_address, auth_token)
                    
                    if await nanoleaf_client.test_connection(device):
                        connection_ok = True
                        break
            
            if connection_ok:
                _LOG.info("Nanoleaf connection verified. Setting state to CONNECTED.")
                await api.set_device_state(ucapi.DeviceStates.CONNECTED)
            else:
                _LOG.warning("Nanoleaf connection failed. Setting state to ERROR.")
                await api.set_device_state(ucapi.DeviceStates.ERROR)
        else:
            _LOG.warning("Nanoleaf client not initialized.")
            await api.set_device_state(ucapi.DeviceStates.ERROR)
    else:
        _LOG.info("Integration not configured yet.")

async def on_disconnect():
    """Handle Remote disconnection."""
    _LOG.info("Remote disconnected.")

async def on_subscribe_entities(entity_ids: list[str]):
    """Handle entity subscription."""
    _LOG.info(f"Entities subscribed: {entity_ids}. Pushing initial state.")
    
    if remote and nanoleaf_client and nanoleaf_config.is_configured():
        _LOG.info("Ensuring remote entity has configured Nanoleaf client...")
        
        # Test connection to at least one device
        devices = nanoleaf_config.devices
        connection_ok = False
        
        for device_id, device_config in devices.items():
            ip_address = device_config.get("ip_address")
            auth_token = device_config.get("auth_token")
            
            if ip_address and auth_token:
                from uc_intg_nanoleaf.client import NanoleafDevice
                device = NanoleafDevice(ip_address, auth_token)
                
                if await nanoleaf_client.test_connection(device):
                    connection_ok = True
                    break
        
        _LOG.info(f"Nanoleaf client connection test: {'OK' if connection_ok else 'FAILED'}")
        
        if not connection_ok:
            _LOG.error("Nanoleaf client connection failed during entity subscription")
            await api.set_device_state(ucapi.DeviceStates.ERROR)
            return
    
    if remote and remote.entity.id in entity_ids:
        _LOG.info("Remote entity subscribed - pushing initial state and starting monitoring")
        
        await remote.push_initial_state()
        
        _LOG.info("Remote entity fully initialized and ready for commands")

async def on_unsubscribe_entities(entity_ids: list[str]):
    """Handle entity unsubscription from Remote."""
    _LOG.info(f"Remote unsubscribed from entities: {entity_ids}")
    
    if remote and remote.entity.id in entity_ids:
        _LOG.info("Remote entity unsubscribed - stopping monitoring if active")

async def init_integration():
    """Initialize the integration objects and API."""
    global api, nanoleaf_client, nanoleaf_config
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    driver_json_path = os.path.join(project_root, "driver.json")
    
    if not os.path.exists(driver_json_path):
        driver_json_path = "driver.json"
        if not os.path.exists(driver_json_path):
            _LOG.error(f"Cannot find driver.json at {driver_json_path}")
            raise FileNotFoundError("driver.json not found")
    
    _LOG.info(f"Using driver.json from: {driver_json_path}")

    api = ucapi.IntegrationAPI(loop)

    config_path = os.path.join(api.config_dir_path, "config.json")
    _LOG.info(f"Using config file: {config_path}")
    nanoleaf_config = NanoleafConfig(config_path)
    
    nanoleaf_client = NanoleafClient()

    setup_handler = NanoleafSetup(nanoleaf_config, nanoleaf_client, on_setup_complete)
    
    await api.init(driver_json_path, setup_handler.setup_handler)
    
    api.add_listener(ucapi.Events.CONNECT, on_r2_connect)
    api.add_listener(ucapi.Events.DISCONNECT, on_disconnect)
    api.add_listener(ucapi.Events.SUBSCRIBE_ENTITIES, on_subscribe_entities)
    api.add_listener(ucapi.Events.UNSUBSCRIBE_ENTITIES, on_unsubscribe_entities)
    
    _LOG.info("Integration API initialized successfully")
    
async def main():
    """Main entry point."""
    _LOG.info("Starting Nanoleaf Integration Driver")
    
    try:
        await init_integration()
        
        if nanoleaf_config and nanoleaf_config.is_configured():
            _LOG.info("Integration is already configured")
            
            devices = nanoleaf_config.devices
            if devices:
                _LOG.info(f"Found {len(devices)} configured devices")
                
                # Test connection to at least one device
                connection_ok = False
                for device_id, device_config in devices.items():
                    ip_address = device_config.get("ip_address")
                    auth_token = device_config.get("auth_token")
                    
                    if ip_address and auth_token:
                        from uc_intg_nanoleaf.client import NanoleafDevice
                        device = NanoleafDevice(ip_address, auth_token)
                        
                        if await nanoleaf_client.test_connection(device):
                            connection_ok = True
                            _LOG.info(f"Successfully connected to device at {ip_address}")
                            break
                
                if connection_ok:
                    _LOG.info("Nanoleaf connection successful")
                    await on_setup_complete()
                else:
                    _LOG.error("Cannot connect to any configured Nanoleaf devices")
                    await api.set_device_state(ucapi.DeviceStates.ERROR)
            else:
                _LOG.warning("No devices found in configuration")
                await api.set_device_state(ucapi.DeviceStates.ERROR)
        else:
            _LOG.warning("Integration is not configured. Waiting for setup...")
            await api.set_device_state(ucapi.DeviceStates.ERROR)

        _LOG.info("Integration is running. Press Ctrl+C to stop.")
        
    except Exception as e:
        _LOG.error(f"Failed to start integration: {e}", exc_info=True)
        if api:
            await api.set_device_state(ucapi.DeviceStates.ERROR)
        raise
    
def shutdown_handler(signum, frame):
    """Handle termination signals for graceful shutdown."""
    _LOG.warning(f"Received signal {signum}. Shutting down...")
    
    async def cleanup():
        try:
            if nanoleaf_client:
                _LOG.info("Closing Nanoleaf client...")
                await nanoleaf_client.disconnect()
            
            _LOG.info("Cancelling remaining tasks...")
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            [task.cancel() for task in tasks]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            _LOG.error(f"Error during cleanup: {e}")
        finally:
            _LOG.info("Stopping event loop...")
            loop.stop()

    loop.create_task(cleanup())

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except (KeyboardInterrupt, asyncio.CancelledError):
        _LOG.info("Driver stopped.")
    except Exception as e:
        _LOG.error(f"Driver failed: {e}", exc_info=True)
    finally:
        if loop and not loop.is_closed():
            _LOG.info("Closing event loop...")
            loop.close()