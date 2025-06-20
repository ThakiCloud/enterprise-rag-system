"""
CLI interface for the Enterprise RAG System
"""
import asyncio
import sys
import time
from pathlib import Path
from typing import Optional

from .core.dependencies import get_knowledge_base, get_rag_agent, get_reasoning_agent, get_research_team
from .knowledge.manager import process_url, get_knowledge_base_info, cleanup_old_files


class RAGCLI:
    """Command Line Interface for Enterprise RAG System"""
    
    def __init__(self):
        self.knowledge_base = get_knowledge_base()
        self.rag_agent = get_rag_agent()
        self.reasoning_agent = get_reasoning_agent()
        self.research_team = get_research_team()
        self.current_session_id = f"cli_session_{int(time.time())}"
        
    def print_banner(self):
        """Print CLI banner"""
        print("=" * 60)
        print("🤖 Enterprise RAG System - CLI Interface")
        print("=" * 60)
        print("Commands:")
        print("  /help          - Show this help message")
        print("  /info          - Show knowledge base information")
        print("  /url <url>     - Add URL content to knowledge base")
        print("  /reasoning     - Toggle advanced reasoning mode")
        print("  /session       - Show current session info")
        print("  /cleanup       - Clean up old uploaded files")
        print("  /quit or /exit - Exit the CLI")
        print("=" * 60)
        print()
    
    def show_info(self):
        """Show knowledge base information"""
        info = get_knowledge_base_info(self.knowledge_base)
        print("\n📊 Knowledge Base Information:")
        print("-" * 30)
        for key, value in info.items():
            print(f"{key}: {value}")
        print()
    
    async def add_url(self, url: str):
        """Add URL content to knowledge base"""
        try:
            print(f"🔗 Processing URL: {url}")
            result = await process_url(url, self.knowledge_base)
            print(f"✅ {result['message']}")
            if 'sources_added' in result:
                print(f"📄 Sources added: {result['sources_added']}")
        except Exception as e:
            print(f"❌ Error processing URL: {str(e)}")
    
    def cleanup_files(self):
        """Clean up old files"""
        print("🧹 Cleaning up old files...")
        result = cleanup_old_files()
        print(f"✅ {result['message']}")
    
    def show_session_info(self):
        """Show current session information"""
        print(f"\n🔧 Session Information:")
        print(f"Session ID: {self.current_session_id}")
        print(f"RAG Agent: {'✅ Active' if self.rag_agent else '❌ Not initialized'}")
        print(f"Reasoning Agent: {'✅ Active' if self.reasoning_agent else '❌ Not initialized'}")
        print(f"Research Team: {'✅ Active' if self.research_team else '❌ Not initialized'}")
        print()
    
    async def process_query(self, question: str, use_reasoning: bool = False):
        """Process a user query"""
        try:
            if use_reasoning:
                agent = self.research_team if self.research_team else self.reasoning_agent
                print("🧠 Using advanced reasoning...")
            else:
                agent = self.rag_agent
                print("🔍 Using standard RAG...")
            
            if not agent:
                print("❌ Agent not available")
                return
            
            # Set session ID
            agent.session_id = self.current_session_id
            
            print("⏳ Processing your query...")
            response = agent.run(question)
            
            print("\n" + "=" * 60)
            print("📝 Response:")
            print("-" * 60)
            print(response.content)
            
            # Show sources if available
            if hasattr(response, 'sources') and response.sources:
                print(f"\n📚 Sources ({len(response.sources)}):")
                for i, source in enumerate(response.sources, 1):
                    source_info = source.get('uri', source.get('content', 'Unknown source'))
                    print(f"  {i}. {source_info}")
            
            # Show reasoning steps if available
            if hasattr(response, 'reasoning') and response.reasoning:
                reasoning_steps = response.reasoning if isinstance(response.reasoning, list) else [response.reasoning]
                print(f"\n🧠 Reasoning Steps:")
                for i, step in enumerate(reasoning_steps, 1):
                    print(f"  {i}. {step}")
            
            print("=" * 60)
            print()
            
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
    
    async def run(self):
        """Run the CLI interface"""
        self.print_banner()
        
        use_reasoning = False
        
        while True:
            try:
                # Get user input
                prompt = "🤖 RAG" + (" + Reasoning" if use_reasoning else "") + " > "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    command_parts = user_input[1:].split(' ', 1)
                    command = command_parts[0].lower()
                    args = command_parts[1] if len(command_parts) > 1 else ""
                    
                    if command in ['help', 'h']:
                        self.print_banner()
                    elif command in ['info', 'i']:
                        self.show_info()
                    elif command in ['url', 'u']:
                        if args:
                            await self.add_url(args)
                        else:
                            print("❌ Please provide a URL. Usage: /url <url>")
                    elif command in ['reasoning', 'r']:
                        use_reasoning = not use_reasoning
                        status = "enabled" if use_reasoning else "disabled"
                        print(f"🧠 Advanced reasoning {status}")
                    elif command in ['session', 's']:
                        self.show_session_info()
                    elif command in ['cleanup', 'c']:
                        self.cleanup_files()
                    elif command in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    else:
                        print(f"❌ Unknown command: {command}. Type /help for available commands.")
                else:
                    # Process as a query
                    await self.process_query(user_input, use_reasoning)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")


async def run_cli():
    """Main CLI entry point"""
    cli = RAGCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(run_cli()) 