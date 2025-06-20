import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call
import io
from contextlib import redirect_stdout, redirect_stderr

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.cli import RAGCLI, run_cli


class TestRAGCLI:
    """Test suite for the RAG CLI interface"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies"""
        with patch.multiple(
            'app.cli',
            get_knowledge_base=MagicMock(),
            get_rag_agent=MagicMock(),
            get_reasoning_agent=MagicMock(),
            get_research_team=MagicMock(),
        ) as mocks:
            yield mocks
    
    @pytest.fixture
    def cli_instance(self, mock_dependencies):
        """Create a CLI instance with mocked dependencies"""
        return RAGCLI()
    
    def test_cli_initialization(self, cli_instance):
        """Test CLI initializes correctly"""
        assert cli_instance is not None
        assert hasattr(cli_instance, 'knowledge_base')
        assert hasattr(cli_instance, 'rag_agent')
        assert hasattr(cli_instance, 'reasoning_agent')
        assert hasattr(cli_instance, 'research_team')
        assert cli_instance.current_session_id.startswith('cli_session_')
    
    def test_print_banner(self, cli_instance):
        """Test banner printing works"""
        with redirect_stdout(io.StringIO()) as captured:
            cli_instance.print_banner()
            output = captured.getvalue()
        
        assert "Enterprise RAG System - CLI Interface" in output
        assert "/help" in output
        assert "/info" in output
        assert "/url" in output
        assert "/quit" in output
    
    @patch('app.cli.get_knowledge_base_info')
    def test_show_info(self, mock_get_info, cli_instance):
        """Test knowledge base info display"""
        mock_get_info.return_value = {
            "Total Documents": 5,
            "Status": "Active",
            "Vector DB": "LanceDB"
        }
        
        with redirect_stdout(io.StringIO()) as captured:
            cli_instance.show_info()
            output = captured.getvalue()
        
        assert "Knowledge Base Information" in output
        assert "Total Documents: 5" in output
        assert "Status: Active" in output
        mock_get_info.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.cli.process_url')
    async def test_add_url_success(self, mock_process_url, cli_instance):
        """Test successful URL addition"""
        mock_process_url.return_value = {
            "message": "URL processed successfully",
            "sources_added": 3
        }
        
        with redirect_stdout(io.StringIO()) as captured:
            await cli_instance.add_url("https://example.com")
            output = captured.getvalue()
        
        assert "Processing URL: https://example.com" in output
        assert "URL processed successfully" in output
        assert "Sources added: 3" in output
        mock_process_url.assert_called_once_with("https://example.com", cli_instance.knowledge_base)
    
    @pytest.mark.asyncio
    @patch('app.cli.process_url')
    async def test_add_url_error(self, mock_process_url, cli_instance):
        """Test URL addition error handling"""
        mock_process_url.side_effect = Exception("URL processing failed")
        
        with redirect_stdout(io.StringIO()) as captured:
            await cli_instance.add_url("https://invalid-url.com")
            output = captured.getvalue()
        
        assert "Processing URL: https://invalid-url.com" in output
        assert "Error processing URL: URL processing failed" in output
    
    @patch('app.cli.cleanup_old_files')
    def test_cleanup_files(self, mock_cleanup, cli_instance):
        """Test file cleanup functionality"""
        mock_cleanup.return_value = {"message": "Cleanup completed successfully"}
        
        with redirect_stdout(io.StringIO()) as captured:
            cli_instance.cleanup_files()
            output = captured.getvalue()
        
        assert "Cleaning up old files..." in output
        assert "Cleanup completed successfully" in output
        mock_cleanup.assert_called_once()
    
    def test_show_session_info(self, cli_instance):
        """Test session information display"""
        with redirect_stdout(io.StringIO()) as captured:
            cli_instance.show_session_info()
            output = captured.getvalue()
        
        assert "Session Information" in output
        assert cli_instance.current_session_id in output
        assert "RAG Agent" in output
        assert "Reasoning Agent" in output
        assert "Research Team" in output
    
    @pytest.mark.asyncio
    async def test_process_query_rag_mode(self, cli_instance):
        """Test query processing in RAG mode"""
        cli_instance.rag_agent = MagicMock()
        cli_instance.rag_agent.run.return_value = MagicMock(
            content="This is a RAG response",
            sources=[{"uri": "test_source.pdf"}]
        )
        
        with redirect_stdout(io.StringIO()) as captured:
            await cli_instance.process_query("What is AI?", use_reasoning=False)
            output = captured.getvalue()
        
        assert "Using standard RAG..." in output
        assert "This is a RAG response" in output
        assert "test_source.pdf" in output
        cli_instance.rag_agent.run.assert_called_once_with("What is AI?")
    
    @pytest.mark.asyncio
    async def test_process_query_reasoning_mode(self, cli_instance):
        """Test query processing in reasoning mode"""
        cli_instance.research_team = MagicMock()
        cli_instance.research_team.run.return_value = MagicMock(
            content="This is a reasoning response",
            reasoning=["Step 1: Analysis", "Step 2: Conclusion"]
        )
        
        with redirect_stdout(io.StringIO()) as captured:
            await cli_instance.process_query("Complex question?", use_reasoning=True)
            output = captured.getvalue()
        
        assert "Using advanced reasoning..." in output
        assert "This is a reasoning response" in output
        assert "Step 1: Analysis" in output
        assert "Step 2: Conclusion" in output
        cli_instance.research_team.run.assert_called_once_with("Complex question?")
    
    @pytest.mark.asyncio
    async def test_process_query_no_agent(self, cli_instance):
        """Test query processing when agent is not available"""
        cli_instance.rag_agent = None
        
        with redirect_stdout(io.StringIO()) as captured:
            await cli_instance.process_query("Test query", use_reasoning=False)
            output = captured.getvalue()
        
        assert "Agent not available" in output
    
    @pytest.mark.asyncio
    async def test_process_query_error_handling(self, cli_instance):
        """Test query processing error handling"""
        cli_instance.rag_agent = MagicMock()
        cli_instance.rag_agent.run.side_effect = Exception("Agent error")
        
        with redirect_stdout(io.StringIO()) as captured:
            await cli_instance.process_query("Test query", use_reasoning=False)
            output = captured.getvalue()
        
        assert "Error processing query: Agent error" in output


class TestCLICommands:
    """Test CLI command parsing and execution"""
    
    @pytest.fixture
    def mock_cli(self):
        """Mock CLI instance for testing commands"""
        with patch('app.cli.RAGCLI') as mock_cli_class:
            mock_instance = MagicMock()
            mock_cli_class.return_value = mock_instance
            yield mock_instance
    
    @pytest.mark.asyncio
    async def test_help_command(self, mock_cli):
        """Test help command functionality"""
        mock_cli.print_banner = MagicMock()
        mock_cli.run = AsyncMock()
        
        # Test that help command calls print_banner
        with patch('builtins.input', side_effect=['/help', '/quit']):
            with patch('builtins.print'):
                await mock_cli.run()
        
        # Verify run was called
        mock_cli.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_info_command(self, mock_cli):
        """Test info command functionality"""
        mock_cli.show_info = MagicMock()
        mock_cli.run = AsyncMock()
        
        with patch('builtins.input', side_effect=['/info', '/quit']):
            with patch('builtins.print'):
                await mock_cli.run()
        
        mock_cli.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_url_command_with_args(self, mock_cli):
        """Test URL command with arguments"""
        mock_cli.add_url = AsyncMock()
        mock_cli.run = AsyncMock()
        
        with patch('builtins.input', side_effect=['/url https://example.com', '/quit']):
            with patch('builtins.print'):
                await mock_cli.run()
        
        mock_cli.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_url_command_without_args(self, mock_cli):
        """Test URL command without arguments"""
        mock_cli.run = AsyncMock()
        
        with patch('builtins.input', side_effect=['/url', '/quit']):
            with patch('builtins.print') as mock_print:
                await mock_cli.run()
        
        # Check that run was called
        mock_cli.run.assert_called_once()


@pytest.mark.asyncio
async def test_run_cli_function():
    """Test the main run_cli function"""
    with patch('app.cli.RAGCLI') as mock_cli_class:
        mock_instance = MagicMock()
        mock_instance.run = AsyncMock()
        mock_cli_class.return_value = mock_instance
        
        await run_cli()
        
        mock_cli_class.assert_called_once()
        mock_instance.run.assert_called_once()


class TestCLIIntegration:
    """Integration tests for CLI functionality"""
    
    @pytest.mark.asyncio
    @patch('app.cli.get_knowledge_base')
    @patch('app.cli.get_rag_agent')
    @patch('app.cli.get_reasoning_agent')
    @patch('app.cli.get_research_team')
    async def test_full_cli_workflow(self, mock_research_team, mock_reasoning_agent, 
                                   mock_rag_agent, mock_knowledge_base):
        """Test a complete CLI workflow"""
        # Setup mocks
        mock_kb = MagicMock()
        mock_knowledge_base.return_value = mock_kb
        
        mock_agent = MagicMock()
        mock_agent.run.return_value = MagicMock(content="Test response")
        mock_rag_agent.return_value = mock_agent
        
        cli = RAGCLI()
        
        # Test initialization
        assert cli.knowledge_base == mock_kb
        assert cli.rag_agent == mock_agent
        
        # Test query processing
        with redirect_stdout(io.StringIO()) as captured:
            await cli.process_query("Test question")
            output = captured.getvalue()
        
        assert "Test response" in output
        mock_agent.run.assert_called_once_with("Test question")
    
    def test_cli_session_id_format(self):
        """Test that session ID is properly formatted"""
        cli = RAGCLI()
        assert cli.current_session_id.startswith('cli_session_')
        assert len(cli.current_session_id.split('_')) == 3  # cli_session_timestamp
    
    @pytest.mark.asyncio
    @patch('app.cli.get_knowledge_base')
    @patch('app.cli.get_rag_agent')
    @patch('app.cli.get_reasoning_agent')
    @patch('app.cli.get_research_team')
    async def test_keyboard_interrupt_handling(self, mock_research_team, mock_reasoning_agent, 
                                               mock_rag_agent, mock_knowledge_base):
        """Test graceful handling of KeyboardInterrupt"""
        cli = RAGCLI()
        
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with redirect_stdout(io.StringIO()) as captured:
                await cli.run()
                output = captured.getvalue()
            
            assert "Goodbye!" in output
    
    @pytest.mark.asyncio
    @patch('app.cli.get_knowledge_base')
    @patch('app.cli.get_rag_agent')
    @patch('app.cli.get_reasoning_agent')
    @patch('app.cli.get_research_team')
    async def test_eof_error_handling(self, mock_research_team, mock_reasoning_agent, 
                                      mock_rag_agent, mock_knowledge_base):
        """Test graceful handling of EOFError"""
        cli = RAGCLI()
        
        with patch('builtins.input', side_effect=EOFError):
            with redirect_stdout(io.StringIO()) as captured:
                await cli.run()
                output = captured.getvalue()
            
            assert "Goodbye!" in output 