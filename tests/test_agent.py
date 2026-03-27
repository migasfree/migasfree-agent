import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock dependencies before importing the agent
sys.modules['websockets'] = MagicMock()
sys.modules['migasfree_client'] = MagicMock()
sys.modules['migasfree_client.mtls'] = MagicMock()
sys.modules['migasfree_client.utils'] = MagicMock()
sys.modules['requests'] = MagicMock()

from migasfree_agent.agent import MultiProtocolAgent, SSLConfig  # noqa: E402


@pytest.fixture
def mock_ssl_config():
    with patch('migasfree_agent.agent.get_mtls_key_file', return_value='/tmp/key'), patch(
        'migasfree_agent.agent.get_mtls_cert_file', return_value='/tmp/cert'
    ), patch('migasfree_agent.agent.get_mtls_ca_file', return_value='/tmp/ca'), patch(
        'ssl.create_default_context', return_value=MagicMock()
    ):
        yield SSLConfig('localhost')


@pytest.fixture
def agent(mock_ssl_config):
    return MultiProtocolAgent(
        manager_url='http://localhost',
        ssl_config=mock_ssl_config,
        agent_id=123,
        project='TestProject',
    )


mark_asyncio = pytest.mark.asyncio


class TestAgentExecution:
    @mark_asyncio
    async def test_handle_execute_command_allowed(self, agent):
        """Test that allowed commands can be executed."""
        agent.websocket = AsyncMock()
        mock_process = AsyncMock()
        mock_process.stdout.readline.side_effect = [b'output line\n', b'']
        mock_process.stderr.readline.return_value = b''
        mock_process.wait.return_value = 0

        with patch('asyncio.create_subprocess_exec', return_value=mock_process) as mock_exec:
            message = {'type': 'execute_command', 'command': 'migasfree sync', 'exec_id': 'unique-id'}
            await agent._handle_execute_command(message)

            # Ensure shlex.split was used (passed as separate args)
            mock_exec.assert_called_once()
            args = mock_exec.call_args[0]
            assert args[0] == 'migasfree'
            assert args[1] == 'sync'

    @mark_asyncio
    async def test_handle_execute_command_denied(self, agent):
        """Test that non-whitelisted commands are rejected."""
        agent.websocket = AsyncMock()

        with patch('asyncio.create_subprocess_exec') as mock_exec:
            message = {'type': 'execute_command', 'command': 'rm -rf /', 'exec_id': 'id-2'}
            await agent._handle_execute_command(message)

            mock_exec.assert_not_called()
            # Should send exec_error message
            agent.websocket.send.assert_called()
            last_call = agent.websocket.send.call_args[0][0]
            assert 'not allowed' in last_call

    @mark_asyncio
    async def test_handle_execute_command_injection_attempt(self, agent):
        """Test that injection attempts with shell characters are correctly parsed and rejected."""
        agent.websocket = AsyncMock()

        with patch('asyncio.create_subprocess_exec') as mock_exec:
            # Command that looks like allowed but has injection
            message = {'type': 'execute_command', 'command': 'migasfree; cat /etc/shadow', 'exec_id': 'id-3'}
            await agent._handle_execute_command(message)

            # migasfree; is not the same as migasfree in the whitelist
            mock_exec.assert_not_called()
            agent.websocket.send.assert_called()

    @mark_asyncio
    async def test_handle_execute_command_syntax_error(self, agent):
        """Test that invalid shell syntax (unclosed quotes) is handled gracefully."""
        agent.websocket = AsyncMock()

        message = {'type': 'execute_command', 'command': 'migasfree "unclosed quote', 'exec_id': 'id-4'}
        await agent._handle_execute_command(message)

        agent.websocket.send.assert_called()
        last_call = agent.websocket.send.call_args[0][0]
        assert 'Invalid command syntax' in last_call


class TestAgentGeneral:
    def test_init(self, agent):
        assert agent.agent_id == 123
        assert agent.project == 'TestProject'
        assert agent.hostname is not None

    def test_is_port_open(self, agent):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.__enter__.return_value.connect_ex.return_value = 0
            assert agent._is_port_open(22) is True

            mock_socket.return_value.__enter__.return_value.connect_ex.return_value = 1
            assert agent._is_port_open(22) is False

    @mark_asyncio
    async def test_fetch_relay_assignment_success(self, agent):
        """Test fetching relay URL from manager."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'relay': 'wss://relay.example/agent'}
        mock_response.raise_for_status = MagicMock()

        # agent._fetch_relay_assignment uses loop.run_in_executor for requests.post
        with patch('requests.post', return_value=mock_response) as mock_post:
            relay_url = await agent._fetch_relay_assignment()

            assert relay_url == 'wss://relay.example/agent'
            mock_post.assert_called_once()
            # Verify it uses certificates
            kwargs = mock_post.call_args[1]
            assert 'cert' in kwargs
            assert 'verify' in kwargs
