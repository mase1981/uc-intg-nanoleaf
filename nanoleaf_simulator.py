#!/usr/bin/env python3
"""
Nanoleaf device simulator for testing integration.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import logging
import socket
from datetime import datetime
from typing import Dict, Any

from aiohttp import web, ClientSession
from zeroconf import ServiceInfo, Zeroconf
from zeroconf.asyncio import AsyncZeroconf

logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)


class NanoleafSimulator:
    """Simulates a Nanoleaf device for testing."""
    
    def __init__(self, device_name: str = "Test Nanoleaf", device_model: str = "NL29", port: int = 16021):
        self.device_name = device_name
        self.device_model = device_model
        self.port = port
        self.host = self._get_local_ip()
        
        # Device state
        self.auth_tokens = set()
        self.pairing_mode = False
        self.pairing_start_time = None
        
        # FIXED: Create device-specific info based on model and name
        self.device_info = self._create_device_info()
        
        # Web server
        self.app = None
        self.runner = None
        self.site = None
        
        # mDNS
        self.zeroconf = None
        self.service_info = None

    def _create_device_info(self) -> Dict[str, Any]:
        """Create device-specific information based on model and name."""
        
        # Base device info template
        base_info = {
            "name": self.device_name,
            "serialNo": f"S{self.device_model}001",
            "manufacturer": "Nanoleaf",
            "firmwareVersion": "3.3.0",
            "model": self.device_model,
            "state": {
                "on": {"value": True},
                "brightness": {"value": 80, "max": 100, "min": 1},
                "hue": {"value": 120, "max": 360, "min": 0},
                "sat": {"value": 75, "max": 100, "min": 0},
                "ct": {"value": 4000, "max": 6500, "min": 1200},
                "colorMode": "effect"
            }
        }
        
        # Model-specific configurations
        if self.device_model == "NL22":  # Light Panels
            base_info.update({
                "effects": {
                    "select": "Northern Lights",
                    "effectsList": [
                        "Color Burst", "Flames", "Forest", "Inner Peace", 
                        "Northern Lights", "Romantic", "Snowfall", "Fireworks",
                        "Lightning", "Paint Splatter"
                    ]
                },
                "panelLayout": {
                    "layout": {
                        "numPanels": 6,
                        "sideLength": 150,
                        "positionData": [
                            {"panelId": 101, "x": 0, "y": 0, "o": 0, "shapeType": 0},
                            {"panelId": 102, "x": 150, "y": 0, "o": 60, "shapeType": 0},
                            {"panelId": 103, "x": 300, "y": 0, "o": 0, "shapeType": 0},
                            {"panelId": 104, "x": 0, "y": 130, "o": 60, "shapeType": 0},
                            {"panelId": 105, "x": 150, "y": 130, "o": 0, "shapeType": 0},
                            {"panelId": 106, "x": 300, "y": 130, "o": 60, "shapeType": 0}
                        ]
                    },
                    "globalOrientation": {"value": 0, "max": 360, "min": 0}
                }
            })
        
        elif self.device_model == "NL29":  # Canvas
            base_info.update({
                "effects": {
                    "select": "Meteor Shower",
                    "effectsList": [
                        "Color Burst", "Falling Whites", "Fireworks", "Flames",
                        "Forest", "Inner Peace", "Meteor Shower", "Nemo",
                        "Northern Lights", "Paint Splatter", "Pulse Pop Beats",
                        "Radial Sound Bar", "Rhythmic Northern Lights", "Romantic",
                        "Sound Bar", "Streaking Notes"
                    ]
                },
                "panelLayout": {
                    "layout": {
                        "numPanels": 9,
                        "sideLength": 100,
                        "positionData": [
                            {"panelId": 201, "x": 0, "y": 0, "o": 0, "shapeType": 2},
                            {"panelId": 202, "x": 100, "y": 0, "o": 0, "shapeType": 2},
                            {"panelId": 203, "x": 200, "y": 0, "o": 0, "shapeType": 2},
                            {"panelId": 204, "x": 0, "y": 100, "o": 0, "shapeType": 2},
                            {"panelId": 205, "x": 100, "y": 100, "o": 0, "shapeType": 2},
                            {"panelId": 206, "x": 200, "y": 100, "o": 0, "shapeType": 2},
                            {"panelId": 207, "x": 0, "y": 200, "o": 0, "shapeType": 2},
                            {"panelId": 208, "x": 100, "y": 200, "o": 0, "shapeType": 2},
                            {"panelId": 209, "x": 200, "y": 200, "o": 0, "shapeType": 2}
                        ]
                    },
                    "globalOrientation": {"value": 0, "max": 360, "min": 0}
                }
            })
        
        elif self.device_model == "NL52":  # Shapes
            base_info.update({
                "effects": {
                    "select": "Aurora",
                    "effectsList": [
                        "Aurora", "Color Burst", "Flames", "Forest", "Inner Peace",
                        "Lightning", "Northern Lights", "Paint Splatter", "Romantic",
                        "Snowfall", "Kaleidoscope", "Prism", "Spectrum Cycle"
                    ]
                },
                "panelLayout": {
                    "layout": {
                        "numPanels": 12,
                        "sideLength": 67,
                        "positionData": [
                            {"panelId": 301, "x": 0, "y": 0, "o": 0, "shapeType": 7},
                            {"panelId": 302, "x": 67, "y": 0, "o": 0, "shapeType": 7},
                            {"panelId": 303, "x": 134, "y": 0, "o": 0, "shapeType": 7},
                            {"panelId": 304, "x": 201, "y": 0, "o": 0, "shapeType": 7},
                            {"panelId": 305, "x": 0, "y": 67, "o": 0, "shapeType": 7},
                            {"panelId": 306, "x": 67, "y": 67, "o": 0, "shapeType": 7},
                            {"panelId": 307, "x": 134, "y": 67, "o": 0, "shapeType": 7},
                            {"panelId": 308, "x": 201, "y": 67, "o": 0, "shapeType": 7},
                            {"panelId": 309, "x": 0, "y": 134, "o": 0, "shapeType": 7},
                            {"panelId": 310, "x": 67, "y": 134, "o": 0, "shapeType": 7},
                            {"panelId": 311, "x": 134, "y": 134, "o": 0, "shapeType": 7},
                            {"panelId": 312, "x": 201, "y": 134, "o": 0, "shapeType": 7}
                        ]
                    },
                    "globalOrientation": {"value": 0, "max": 360, "min": 0}
                }
            })
        
        return base_info

    def _get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            # Connect to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

    async def start(self):
        """Start the simulator."""
        _LOG.info(f"🚀 Starting Nanoleaf simulator: {self.device_name}")
        _LOG.info(f"📍 Device will be available at: http://{self.host}:{self.port}")
        
        # Start web server
        await self._start_web_server()
        
        # Start mDNS
        await self._start_mdns()
        
        _LOG.info(f"✅ Simulator ready! Device IP: {self.host}:{self.port}")
        _LOG.info(f"🔧 To pair: POST to http://{self.host}:{self.port}/api/v1/new")
        _LOG.info(f"📋 Device automatically in pairing mode for testing")

    async def stop(self):
        """Stop the simulator."""
        _LOG.info("Stopping Nanoleaf simulator...")
        
        if self.zeroconf:
            await self.zeroconf.async_unregister_service(self.service_info)
            await self.zeroconf.async_close()
        
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

    async def _start_web_server(self):
        """Start the HTTP API server."""
        self.app = web.Application()
        
        # API routes
        self.app.router.add_post("/api/v1/new", self._handle_pairing)
        self.app.router.add_get("/api/v1/{auth_token}", self._handle_get_info)
        self.app.router.add_put("/api/v1/{auth_token}/state", self._handle_set_state)
        self.app.router.add_put("/api/v1/{auth_token}/effects", self._handle_set_effects)
        self.app.router.add_put("/api/v1/{auth_token}/identify", self._handle_identify)
        self.app.router.add_get("/api/v1/", self._handle_unauthorized)
        
        # Start server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await self.site.start()

    async def _start_mdns(self):
        """Start mDNS advertisement."""
        try:
            self.zeroconf = AsyncZeroconf()
            
            # Create service info
            service_name = f"{self.device_name.replace(' ', '-')}._nanoleafapi._tcp.local."
            
            self.service_info = ServiceInfo(
                "_nanoleafapi._tcp.local.",
                service_name,
                addresses=[socket.inet_aton(self.host)],
                port=self.port,
                properties={
                    b"md": self.device_model.encode(),
                    b"srcvers": b"3.3.0",
                    b"id": f"AA:BB:CC:DD:EE:F{self.port - 16020}".encode()  # Unique ID per port
                },
                server=f"{socket.gethostname()}.local."
            )
            
            await self.zeroconf.async_register_service(self.service_info)
            _LOG.info(f"📡 mDNS service registered: {service_name}")
            
        except Exception as e:
            _LOG.error(f"Failed to start mDNS: {e}")

    async def _handle_unauthorized(self, request):
        """Handle unauthorized API access."""
        return web.Response(status=401, text="Unauthorized")

    async def _handle_pairing(self, request):
        """Handle pairing request."""
        _LOG.info(f"🔗 Pairing request received for {self.device_name}")
        
        # Simulate pairing mode requirement (but always allow for testing)
        auth_token = f"test_token_{self.port}_{len(self.auth_tokens) + 1}_{datetime.now().strftime('%H%M%S')}"
        self.auth_tokens.add(auth_token)
        
        _LOG.info(f"✅ Pairing successful! Auth token: {auth_token}")
        
        return web.json_response({"auth_token": auth_token})

    async def _handle_get_info(self, request):
        """Handle device info request."""
        auth_token = request.match_info['auth_token']
        
        if auth_token not in self.auth_tokens:
            return web.Response(status=401, text="Unauthorized")
        
        _LOG.info(f"📋 Device info requested for {self.device_name} with token: {auth_token[:10]}...")
        return web.json_response(self.device_info)

    async def _handle_set_state(self, request):
        """Handle state change request."""
        auth_token = request.match_info['auth_token']
        
        if auth_token not in self.auth_tokens:
            return web.Response(status=401, text="Unauthorized")
        
        try:
            data = await request.json()
            _LOG.info(f"🎛️ State change on {self.device_name}: {data}")
            
            # Update device state
            if "on" in data:
                self.device_info["state"]["on"]["value"] = data["on"]["value"]
            if "brightness" in data:
                self.device_info["state"]["brightness"]["value"] = data["brightness"]["value"]
            if "hue" in data:
                self.device_info["state"]["hue"]["value"] = data["hue"]["value"]
            if "sat" in data:
                self.device_info["state"]["sat"]["value"] = data["sat"]["value"]
            if "ct" in data:
                self.device_info["state"]["ct"]["value"] = data["ct"]["value"]
            
            return web.Response(status=204)
            
        except Exception as e:
            _LOG.error(f"Error handling state change: {e}")
            return web.Response(status=400, text="Bad Request")

    async def _handle_set_effects(self, request):
        """Handle effects request."""
        auth_token = request.match_info['auth_token']
        
        if auth_token not in self.auth_tokens:
            return web.Response(status=401, text="Unauthorized")
        
        try:
            data = await request.json()
            _LOG.info(f"🎨 Effects change on {self.device_name}: {data}")
            
            if "select" in data:
                effect_name = data["select"]
                if effect_name in self.device_info["effects"]["effectsList"]:
                    self.device_info["effects"]["select"] = effect_name
                    _LOG.info(f"✅ Effect changed to: {effect_name}")
                else:
                    _LOG.warning(f"⚠️ Unknown effect: {effect_name}")
            
            return web.Response(status=204)
            
        except Exception as e:
            _LOG.error(f"Error handling effects change: {e}")
            return web.Response(status=400, text="Bad Request")

    async def _handle_identify(self, request):
        """Handle identify request."""
        auth_token = request.match_info['auth_token']
        
        if auth_token not in self.auth_tokens:
            return web.Response(status=401, text="Unauthorized")
        
        _LOG.info(f"🔍 IDENTIFY: {self.device_name} is flashing! (simulated)")
        return web.Response(status=204)


async def main():
    """Run multiple device simulators for testing."""
    simulators = []
    
    # Create multiple test devices with proper model/name combinations
    devices = [
        {"name": "Living Room Panels", "model": "NL22", "port": 16021},
        {"name": "Bedroom Canvas", "model": "NL29", "port": 16022},
        {"name": "Office Shapes", "model": "NL52", "port": 16023},
    ]
    
    try:
        # Start all simulators
        for device in devices:
            simulator = NanoleafSimulator(
                device_name=device["name"],
                device_model=device["model"],
                port=device["port"]
            )
            simulators.append(simulator)
            await simulator.start()
            await asyncio.sleep(1)  # Stagger startup
        
        _LOG.info("🎉 All simulators started successfully!")
        _LOG.info("💡 Test your integration now - devices should be discoverable")
        _LOG.info("📄 Press Ctrl+C to stop simulators")
        _LOG.info("")
        _LOG.info("🔧 Device Summary:")
        _LOG.info("  • Living Room Panels (NL22) - 6 triangular panels - port 16021")
        _LOG.info("  • Bedroom Canvas (NL29) - 9 square panels - port 16022") 
        _LOG.info("  • Office Shapes (NL52) - 12 hexagonal panels - port 16023")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        _LOG.info("⏹️ Stopping simulators...")
        
        # Stop all simulators
        for simulator in simulators:
            await simulator.stop()
        
        _LOG.info("✅ All simulators stopped")


if __name__ == "__main__":
    asyncio.run(main())