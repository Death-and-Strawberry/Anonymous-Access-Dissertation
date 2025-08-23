import socks
import socket
import asyncio
import logging
from stem import Signal
from stem.control import Controller
from .config import settings

logger = logging.getLogger(__name__)

class TorClient:
    def __init__(self):
        self._setup_proxy()
    
    def _setup_proxy(self):
        """Configure SOCKS proxy for Tor"""
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", settings.tor_socks_port)
        socket.socket = socks.socksocket
    
    async def new_circuit(self) -> bool:
        """Create a new Tor circuit"""
        try:
            def _create_circuit():
                with Controller.from_port(port=settings.tor_control_port) as controller:
                    controller.authenticate(password=settings.tor_control_password)
                    controller.signal(Signal.NEWNYM)
                    return True
            
            result = await asyncio.get_event_loop().run_in_executor(None, _create_circuit)
            logger.info("New Tor circuit created")
            return result
        except Exception as e:
            logger.error(f"Failed to create new circuit: {e}")
            return False
    
    async def check_ip(self) -> str:
        """Check current IP through Tor"""
        import requests
        
        def _check_ip():
            self._setup_proxy()
            response = requests.get('https://httpbin.org/ip', timeout=30)
            return response.json()['origin']
        
        return await asyncio.get_event_loop().run_in_executor(None, _check_ip)

# Global instance
tor_client = TorClient()