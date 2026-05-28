#!/usr/bin/python3
"""
migasfree-agent - Multi-protocol TCP Tunnel Agent (SSH, VNC, RDP, etc.)

This agent establishes secure WebSocket connections to relay servers,
enabling remote access to local services through mTLS authentication.
"""

import asyncio
import inspect
import json
import logging
import os
import shlex
import socket
import ssl
import subprocess
import sys
import time
import uuid
from contextlib import suppress
from dataclasses import dataclass, field  # stdlib 3.7+; backport: pip install dataclasses
from typing import Any, Dict, Optional, Set
from urllib.parse import urlparse

import requests
import requests.adapters
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_SERVICES = {
    'ssh': 22,
    'vnc': 5900,
    'rdp': 3389,
    'exec': 0,
}  # exec doesn't need a port
RECONNECT_DELAY = 5
# Allowed commands for execution (whitelist for security)
ALLOWED_COMMANDS = ['migasfree']
PORT_CHECK_TIMEOUT = 0.5
BUFFER_SIZE = 8192
WEBSOCKET_CONFIG = {
    'ping_interval': 20,
    'ping_timeout': 60,
    'close_timeout': 10,
    'max_size': 10**7,
}


class StrictSSLCompatAdapter(requests.adapters.HTTPAdapter):
    """Custom HTTPAdapter that disables strict SSL verification in modern Python versions (e.g., Python 3.13+)."""

    def init_poolmanager(self, connections: int, maxsize: int, block: bool = False, **kwargs: Any) -> Any:
        context = ssl.create_default_context()
        if hasattr(ssl, 'VERIFY_X509_STRICT'):
            context.verify_flags &= ~ssl.VERIFY_X509_STRICT
        if hasattr(ssl, 'VERIFY_X509_PARTIAL_CHAIN'):
            context.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN
        kwargs['ssl_context'] = context
        return super().init_poolmanager(connections, maxsize, block=block, **kwargs)

    def proxy_manager_for(self, proxy: str, **kwargs: Any) -> Any:
        context = ssl.create_default_context()
        if hasattr(ssl, 'VERIFY_X509_STRICT'):
            context.verify_flags &= ~ssl.VERIFY_X509_STRICT
        if hasattr(ssl, 'VERIFY_X509_PARTIAL_CHAIN'):
            context.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN
        kwargs['ssl_context'] = context
        return super().proxy_manager_for(proxy, **kwargs)


@dataclass
class TunnelInfo:
    """Stores information about an active tunnel."""

    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    service: str
    port: int
    start_time: float
    client_cn: Optional[str] = None


@dataclass
class SSLConfig:
    """SSL/mTLS configuration."""

    fqdn: str
    key_file: str
    cert_file: str
    ca_file: str
    context: ssl.SSLContext = field(init=False)

    def __post_init__(self) -> None:
        self.context = self._create_context()

    def _create_context(self) -> ssl.SSLContext:
        """Creates and configures SSL context."""
        # Force TLSv1.2 or higher for maximum compatibility with HAProxy mTLS
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if hasattr(ssl, 'TLSVersion'):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        else:
            # Fallback for Python 3.6 which lacks TLSVersion attribute
            ctx.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        ctx.check_hostname = False  # We verify via mTLS certificates
        ctx.verify_mode = ssl.CERT_REQUIRED
        if hasattr(ssl, 'VERIFY_X509_STRICT'):
            ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        if hasattr(ssl, 'VERIFY_X509_PARTIAL_CHAIN'):
            ctx.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN

        try:
            ctx.load_verify_locations(cafile=self.ca_file)
        except Exception as e:
            logger.error(f'Failed to load CA certificate: {e}')

        try:
            ctx.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)
        except Exception as e:
            logger.warning(f'Failed to load mTLS certificate: {e}')

        return ctx


class MultiProtocolAgent:
    """
    Agent that creates TCP tunnels through WebSocket connections.

    Supports multiple protocols (SSH, VNC, RDP, etc.) by forwarding
    local ports through a secure relay server.
    """

    def __init__(
        self,
        manager_url: str,
        ssl_config: SSLConfig,
        agent_id: Optional[int] = None,
        project: Optional[str] = None,
        services: Optional[Dict[str, int]] = None,
    ):
        self.manager_url = manager_url.rstrip('/')
        self.ssl_config = ssl_config
        self.server_url: Optional[str] = None
        self.agent_id = agent_id if agent_id is not None else str(uuid.uuid4())
        self.project = project or 'Unknown'
        self.hostname = socket.gethostname()
        self.services = services or DEFAULT_SERVICES.copy()
        self.tcp_tunnels: Dict[str, TunnelInfo] = {}
        self.websocket: Optional[Any] = None  # websockets.WebSocketClientProtocol (no stubs)
        self.session = requests.Session()
        adapter = StrictSSLCompatAdapter()
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self.background_tasks: Set[asyncio.Task] = set()

    def _is_port_open(self, port: int) -> bool:
        """Checks if a port is open on localhost."""
        with suppress(OSError), socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(PORT_CHECK_TIMEOUT)
            return sock.connect_ex(('127.0.0.1', port)) == 0
        return False

    def _get_system_info(self) -> dict:
        """Gets system information and active services."""
        active_services = []

        for name, port in self.services.items():
            if self._is_port_open(port):
                active_services.append(name)

        return {
            'services': active_services,
        }

    def _format_duration(self, seconds: float) -> str:
        """Formats duration in HH:MM:SS format."""
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f'{int(hours):02}:{int(minutes):02}:{int(secs):02}'

    async def _register(self) -> None:
        """Registers the agent with the server via WebSocket."""
        message = {
            'type': 'register_agent',
            'id': self.agent_id,
            'name': f'{self.hostname} [CID-{self.agent_id}]',
            'services': self._get_system_info()['services'],
            'mode': 'tcp_tunnel',
        }
        assert self.websocket is not None
        await self.websocket.send(json.dumps(message))
        logger.info(f'Agent registered: {self.agent_id}')

    async def _heartbeat_loop(self) -> None:
        """Periodically registers the agent to keep status active in Redis."""
        try:
            while self.websocket is not None and not self.websocket.closed:
                await asyncio.sleep(60)
                if self.websocket is not None and not self.websocket.closed:
                    logger.debug('Sending periodic heartbeat registration')
                    await self._register()
        except asyncio.CancelledError:
            logger.debug('Heartbeat loop cancelled')
        except Exception as e:
            logger.error(f'Error in heartbeat loop: {e}')

    async def _handle_tcp_tunnel(
        self,
        tunnel_id: str,
        service: str = 'ssh',
        client_cn: Optional[str] = None,
    ) -> None:
        """Handles a TCP tunnel to any local service."""
        if service not in self.services:
            logger.error(f"Service '{service}' not available.")
            return

        port = self.services[service]
        logger.info(f'Starting tunnel {service.upper()}: {tunnel_id} -> port {port} (Client: {client_cn})')

        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', port)
            self.tcp_tunnels[tunnel_id] = TunnelInfo(
                reader=reader,
                writer=writer,
                service=service,
                port=port,
                start_time=time.time(),
                client_cn=client_cn,
            )
            task = asyncio.create_task(self._forward_service_to_ws(tunnel_id, reader, service))
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
        except OSError as e:
            logger.error(f'Error connecting to local service {service}: {e}')
            await self._close_tcp_tunnel(tunnel_id)

    async def _forward_service_to_ws(
        self,
        tunnel_id: str,
        reader: asyncio.StreamReader,
        service: str,
    ) -> None:
        """Forwards data from local service to WebSocket."""
        try:
            while tunnel_id in self.tcp_tunnels:
                data = await reader.read(BUFFER_SIZE)
                if not data:
                    break
                message = {
                    'type': 'tunnel_data',
                    'tunnel_id': tunnel_id,
                    'origin': 'agent',
                    'data': data.hex(),
                }
                assert self.websocket is not None
                await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f'Error reading service {service}: {e}')
        finally:
            await self._close_tcp_tunnel(tunnel_id)

    async def _write_tcp_tunnel(self, tunnel_id: str, data_hex: str) -> None:
        """Writes data to an existing tunnel."""
        if tunnel_id not in self.tcp_tunnels:
            return

        try:
            data = bytes.fromhex(data_hex)
            writer = self.tcp_tunnels[tunnel_id].writer
            writer.write(data)
            await writer.drain()
        except Exception as e:
            logger.error(f'Error writing to tunnel: {e}')
            await self._close_tcp_tunnel(tunnel_id)

    async def _close_tcp_tunnel(self, tunnel_id: str) -> None:
        """Closes a tunnel and cleans up resources."""
        if tunnel_id not in self.tcp_tunnels:
            return

        tunnel = self.tcp_tunnels.pop(tunnel_id)

        with suppress(Exception):
            tunnel.writer.close()
            # wait_closed() is only supported in Python 3.7+
            if hasattr(tunnel.writer, 'wait_closed'):
                await tunnel.writer.wait_closed()

        duration_str = self._format_duration(time.time() - tunnel.start_time)
        client_str = f' (Client: {tunnel.client_cn})' if tunnel.client_cn else ''
        logger.info(f'Tunnel closed {tunnel.service.upper()}: {tunnel_id} (Duration: {duration_str}){client_str}')

        if self.websocket:
            with suppress(Exception):
                await self.websocket.send(json.dumps({'type': 'tunnel_closed', 'tunnel_id': tunnel_id}))

    async def _handle_messages(self) -> None:
        """Processes incoming WebSocket messages."""
        handlers = {
            'start_tcp_tunnel': self._handle_start_tunnel,
            'tunnel_data': self._handle_tunnel_data,
            'close_tcp_tunnel': self._handle_close_tunnel,
            'execute_command': self._handle_execute_command,
        }
        # Handlers that should run in background (non-blocking)
        background_handlers = {'execute_command'}

        try:
            assert self.websocket is not None
            async for message_raw in self.websocket:
                message = json.loads(message_raw)
                msg_type = message.get('type')
                handler = handlers.get(msg_type)
                if handler:
                    # Execute long-running commands in background to not block other messages
                    if msg_type in background_handlers:
                        task = asyncio.create_task(handler(message))
                        self.background_tasks.add(task)
                        task.add_done_callback(self.background_tasks.discard)
                    else:
                        await handler(message)
        except websockets.ConnectionClosed:
            logger.warning('WebSocket connection closed')
        except Exception as e:
            logger.error(f'WebSocket error: {e}')

    async def _handle_start_tunnel(self, message: dict) -> None:
        """Handles start_tcp_tunnel message."""
        await self._handle_tcp_tunnel(
            str(message.get('tunnel_id', '')),
            str(message.get('service', 'ssh')),
            message.get('client_cn'),
        )

    async def _handle_tunnel_data(self, message: dict) -> None:
        """Handles tunnel_data message."""
        await self._write_tcp_tunnel(
            str(message.get('tunnel_id', '')),
            str(message.get('data', '')),
        )

    async def _handle_close_tunnel(self, message: dict) -> None:
        """Handles close_tcp_tunnel message."""
        await self._close_tcp_tunnel(str(message.get('tunnel_id', '')))

    async def _handle_execute_command(self, message: dict) -> None:
        """Handles remote command execution."""
        command = message.get('command', '')
        exec_id = message.get('exec_id')
        client_cn = message.get('client_cn', 'unknown')

        if not command or not exec_id:
            logger.error('Invalid execute_command message: missing command or exec_id')
            return

        # Validate command is in whitelist
        try:
            command_parts = shlex.split(command)
        except ValueError as e:
            await self._send_exec_error(exec_id, f'Invalid command syntax: {e}')
            return

        if not command_parts:
            await self._send_exec_error(exec_id, 'Empty command')
            return

        base_command = command_parts[0]
        if base_command not in ALLOWED_COMMANDS:
            error_msg = f'Command "{base_command}" not allowed. Allowed: {", ".join(ALLOWED_COMMANDS)}'
            logger.warning(f'Rejected command from {client_cn}: {command}')
            await self._send_exec_error(exec_id, error_msg)
            return

        logger.info(f'Executing command from {client_cn}: {command}')

        try:
            # Prepare environment with forced color settings
            env = {
                'TERM': 'xterm-256color',
                'FORCE_COLOR': '1',
                'CLICOLOR_FORCE': '1',
                'PYTHONUNBUFFERED': '1',
                **{k: v for k, v in os.environ.items() if isinstance(v, str)},  # Inherit current env
            }

            # Execute command with streaming output (non-interactive)
            # Use create_subprocess_exec to prevent shell injection
            process = await asyncio.create_subprocess_exec(
                *command_parts,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            # Stream stdout and stderr concurrently
            async def stream_output(stream: asyncio.StreamReader, stream_type: str) -> None:
                try:
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        assert self.websocket is not None
                        await self.websocket.send(
                            json.dumps(
                                {
                                    'type': 'exec_output',
                                    'exec_id': exec_id,
                                    'stream': stream_type,
                                    'data': line.decode('utf-8', errors='replace'),
                                }
                            )
                        )
                except Exception as e:
                    logger.error(f'Error streaming {stream_type}: {e}')

            # Wait for both streams and process completion
            assert process.stdout is not None
            assert process.stderr is not None
            await asyncio.gather(
                stream_output(process.stdout, 'stdout'),
                stream_output(process.stderr, 'stderr'),
            )

            exit_code = await process.wait()

            # Send completion message
            assert self.websocket is not None
            await self.websocket.send(
                json.dumps(
                    {
                        'type': 'exec_complete',
                        'exec_id': exec_id,
                        'exit_code': exit_code,
                    }
                )
            )

            logger.info(f'Command completed with exit code {exit_code}: {command}')

        except Exception as e:
            logger.error(f'Error executing command: {e}')
            await self._send_exec_error(exec_id, str(e))

    async def _send_exec_error(self, exec_id: str, error_msg: str) -> None:
        """Sends an execution error message."""
        try:
            assert self.websocket is not None
            await self.websocket.send(
                json.dumps(
                    {
                        'type': 'exec_error',
                        'exec_id': exec_id,
                        'error': error_msg,
                    }
                )
            )
        except Exception as e:
            logger.error(f'Failed to send exec error: {e}')

    async def _fetch_relay_assignment(self) -> Optional[str]:
        """Fetches relay server assignment from manager."""
        logger.info(f'Contacting Manager at {self.manager_url}')

        def do_request() -> requests.Response:
            return self.session.post(
                f'{self.manager_url}/register',
                json={
                    'id': self.agent_id,
                    'name': self.hostname,
                    'services': self._get_system_info()['services'],
                },
                timeout=5,
                cert=(self.ssl_config.cert_file, self.ssl_config.key_file),
                verify=self.ssl_config.ca_file,
            )

        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, do_request)
            resp.raise_for_status()
            return str(resp.json()['relay'])
        except requests.RequestException as e:
            logger.error(f'Manager error: {e}')
            return None

    def _build_connect_kwargs(self, headers: dict) -> dict:
        """Builds WebSocket connection kwargs."""
        kwargs: Dict[str, Any] = dict(WEBSOCKET_CONFIG)

        if self.server_url and self.server_url.startswith('wss://'):
            kwargs['ssl'] = self.ssl_config.context

        return kwargs

    def _connect_websocket(self, connect_kwargs: dict, headers: dict) -> Any:
        """Connects to WebSocket with version compatibility handling."""
        # Clean up potential conflict
        connect_kwargs.pop('additional_headers', None)

        # Determine correct header argument via strict signature inspection
        # (Version checks are unreliable on some distro packages)
        use_additional_headers = False
        try:
            sig = inspect.signature(websockets.connect)
            if 'additional_headers' in sig.parameters:
                use_additional_headers = True
        except Exception:
            # Fallback to version check if inspection fails
            with suppress(Exception):
                if int(websockets.__version__.split('.')[0]) >= 10:
                    use_additional_headers = True

        server_url: str = self.server_url or ''
        if use_additional_headers:
            return websockets.connect(server_url, additional_headers=headers, **connect_kwargs)
        else:
            return websockets.connect(server_url, extra_headers=headers, **connect_kwargs)

    async def connect(self) -> None:
        """Main connection loop with automatic reconnection."""
        while True:
            try:
                if not self.server_url:
                    self.server_url = await self._fetch_relay_assignment()
                    if not self.server_url:
                        await asyncio.sleep(RECONNECT_DELAY)
                        continue

                logger.info(f'Connecting to {self.server_url}')
                headers = {'X-Agent-ID': self.agent_id}
                connect_kwargs = self._build_connect_kwargs(headers)

                async with self._connect_websocket(connect_kwargs, headers) as ws:
                    self.websocket = ws
                    logger.info('Connection established')
                    await self._register()

                    # Start periodic heartbeat task
                    heartbeat_task = asyncio.ensure_future(self._heartbeat_loop())
                    try:
                        await self._handle_messages()
                    finally:
                        heartbeat_task.cancel()
                        with suppress(asyncio.CancelledError):
                            await heartbeat_task

                logger.warning('Disconnected from Relay')
                self.server_url = None

            except Exception as e:
                logger.error(f'Connection error: {e}')
                self.server_url = None
                await asyncio.sleep(RECONNECT_DELAY)


def load_migasfree_config() -> dict:
    """Invokes migasfree CLI to obtain configuration in JSON format without importing client modules."""
    try:
        result = subprocess.run(
            ['migasfree', '--quiet', 'conf', '--json'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        config = json.loads(result.stdout)
        if isinstance(config, dict):
            return config
        raise ValueError('Invalid JSON structure returned by migasfree conf.')
    except Exception as e:
        logger.error(f'Failed to get configuration from migasfree: {e}')
        raise RuntimeError('migasfree command is not available or failed to execute.') from e


def load_migasfree_cid() -> int:
    """Invokes migasfree CLI to obtain the local computer ID (CID)."""
    for cmd in [
        ['migasfree', '--quiet', 'info', 'id'],
        ['sudo', 'migasfree', '--quiet', 'info', 'id'],
    ]:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            return int(result.stdout.strip())
        except Exception as e:
            logger.debug(f'Failed to obtain CID via {cmd}: {e}')

    raise RuntimeError('Failed to obtain CID via migasfree info id.')


async def main() -> None:
    """Main entry point."""
    config = load_migasfree_config()

    server = config.get('server', 'localhost')
    if '://' not in server:
        server = f'{config.get("api_protocol", "https")}://{server}'

    parsed = urlparse(server)
    fqdn = parsed.hostname or 'localhost'
    port = parsed.port
    protocol = parsed.scheme or config.get('api_protocol', 'https')

    port_str = f':{port}' if port else ''
    manager_url = f'{protocol}://{fqdn}{port_str}/manager/v1/private/tunnel'

    ca_file = config.get('ca_file', '')
    cert_file = ''
    key_file = ''
    if ca_file:
        mtls_dir = os.path.dirname(ca_file)
        cert_file = os.path.join(mtls_dir, 'cert.pem')
        key_file = os.path.join(mtls_dir, 'key.pem')

    ssl_config = SSLConfig(
        fqdn=fqdn,
        ca_file=ca_file,
        cert_file=cert_file,
        key_file=key_file,
    )

    agent_id = load_migasfree_cid()
    project = config.get('project', 'migasfree')

    agent = MultiProtocolAgent(
        manager_url=manager_url,
        ssl_config=ssl_config,
        services=DEFAULT_SERVICES,
        agent_id=agent_id,
        project=project,
    )
    await agent.connect()


if __name__ == '__main__':
    try:
        if sys.version_info >= (3, 7):  # noqa: UP036
            asyncio.run(main())
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info('Agent stopped')
