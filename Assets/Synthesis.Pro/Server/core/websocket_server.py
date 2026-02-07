"""
Synthesis.Pro WebSocket Server
Real-time bidirectional communication between Unity and AI

Features:
- WebSocket server for Unity command execution
- Command routing and validation
- Result delivery
- Connection management
- Integration with RAG engine
- MCP protocol support (future)

Architecture:
    Unity Editor (C#) <--WebSocket--> Python Server <--> RAG Engine
                                            |
                                            +--> OpenAI API
                                            +--> Knowledge Base
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Set, Callable, Optional
from datetime import datetime
import sys
import os
import shutil
from pathlib import Path

# Add directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))  # core/ directory
sys.path.insert(0, str(Path(__file__).parent.parent))  # Server/ directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Synthesis.Pro/ directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))  # RAG/core/ directory

from rag_engine_lite import SynthesisRAG  # NEW: Lightweight RAG (BM25S + transformers)
from conversation_tracker import ConversationTracker
from database_manager import DatabaseManager
from rag_integration.rag_onboarding import RAGOnboardingSystem
from context_systems.console_monitor import ConsoleMonitor


class SynthesisWebSocketServer:
    """
    WebSocket server for Synthesis.Pro

    Handles real-time communication between Unity and Python AI systems.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize WebSocket server

        Args:
            host: Host to bind to (default: localhost for security)
            port: Port to listen on (default: 8765)
        """
        self.host = host
        self.port = port

        # Active connections
        self.connections: Set[websockets.WebSocketServerProtocol] = set()

        # Command handlers
        self.command_handlers: Dict[str, Callable] = {}

        # Statistics
        self.stats = {
            'connections_total': 0,
            'commands_processed': 0,
            'commands_failed': 0,
            'uptime_start': datetime.now()
        }

        # RAG engine (initialized on first use)
        self.rag: Optional[SynthesisRAG] = None
        self.conversation_tracker: Optional[ConversationTracker] = None
        self.rag_onboarding: Optional[RAGOnboardingSystem] = None
        self.console_monitor: Optional[ConsoleMonitor] = None

        # Setup logging
        self.logger = logging.getLogger("SynthesisWebSocket")
        self._setup_logging()

        # Register default command handlers
        self._register_default_handlers()

    def _setup_logging(self):
        """Configure logging"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _register_default_handlers(self):
        """Register built-in command handlers"""
        self.register_handler("ping", self._handle_ping)
        self.register_handler("get_capabilities", self._handle_get_capabilities)
        self.register_handler("get_stats", self._handle_get_stats)
        self.register_handler("chat", self._handle_chat)
        self.register_handler("search_knowledge", self._handle_search_knowledge)
        self.register_handler("backup_private_db", self._handle_backup_private_db)
        self.register_handler("clear_private_db", self._handle_clear_private_db)
        self.register_handler("restore_private_db", self._handle_restore_private_db)
        self.register_handler("list_backups", self._handle_list_backups)
        self.register_handler("audit_public_db", self._handle_audit_public_db)
        self.register_handler("check_db_updates", self._handle_check_db_updates)
        self.register_handler("update_public_db", self._handle_update_public_db)
        self.register_handler("console_log", self._handle_console_log)

    def register_handler(self, command_type: str, handler: Callable):
        """
        Register a command handler

        Args:
            command_type: Type of command to handle
            handler: Async function to handle the command
        """
        self.command_handlers[command_type] = handler
        self.logger.info(f"Registered handler for: {command_type}")

    async def start(self):
        """Start the WebSocket server"""
        self.logger.info(f"🚀 Starting Synthesis.Pro WebSocket Server")
        self.logger.info(f"📡 Listening on ws://{self.host}:{self.port}")
        self.logger.info(f"🔒 Security: localhost-only binding")

        # Initialize RAG engine
        await self._initialize_rag()

        # Start server
        async with websockets.serve(self._handle_connection, self.host, self.port):
            self.logger.info(f"✅ Server ready! Waiting for Unity connections...")
            await asyncio.Future()  # Run forever

    async def _initialize_rag(self):
        """Initialize RAG engine and conversation tracker"""
        try:
            self.logger.info("Initializing RAG engine...")

            # Check and setup public database and embeddings model
            db_manager = DatabaseManager()

            # Setup database
            if not db_manager.check_setup():
                self.logger.info("Public database not found - running first-time setup...")
                success = db_manager.setup_database()
                if not success:
                    self.logger.warning("Could not download public database")
                    self.logger.warning("Public database will be created as you use Synthesis.Pro")

            # Setup embeddings model
            if not db_manager.check_model_setup():
                self.logger.info("Embeddings model not found - downloading...")
                success = db_manager.setup_model()
                if not success:
                    self.logger.warning("Could not download embeddings model")
                    self.logger.warning("Semantic search will not be available")

            # Check for updates (non-blocking)
            if db_manager.check_setup() or db_manager.check_model_setup():
                updates = db_manager.check_for_updates()
                if updates.get('database') or updates.get('model'):
                    update_list = []
                    if updates.get('database'):
                        update_list.append(f"database ({updates['database']})")
                    if updates.get('model'):
                        update_list.append(f"model ({updates['model']})")
                    self.logger.info(f"Updates available: {', '.join(update_list)}")
                    self.logger.info("Run 'python database_manager.py --update' to update")

            # Create RAG with dual databases
            self.rag = SynthesisRAG(
                database="synthesis_knowledge.db",
                private_database="synthesis_private.db"
            )

            # Create conversation tracker
            self.conversation_tracker = ConversationTracker(self.rag)

            # Create RAG onboarding system for natural AI interactions
            self.rag_onboarding = RAGOnboardingSystem(
                rag_engine=self.rag,
                user_id="unity_session",
                presentation_style="natural"
            )

            # Create console monitor for real-time error capture
            self.console_monitor = ConsoleMonitor(self.rag)

            self.logger.info("✅ RAG engine initialized (dual database mode)")
            self.logger.info("✅ RAG onboarding system ready (natural mode)")
            self.logger.info("✅ Console monitor active (capturing errors & patterns)")
        except Exception as e:
            import traceback
            self.logger.error(f"Failed to initialize RAG: {e}")
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            self.logger.warning("Server will run without RAG features")

    async def _handle_connection(self, websocket: websockets.WebSocketServerProtocol):
        """
        Handle a new WebSocket connection

        Args:
            websocket: WebSocket connection
        """
        # Register connection
        self.connections.add(websocket)
        self.stats['connections_total'] += 1

        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.logger.info(f"🔌 Unity connected: {client_info} (total: {len(self.connections)})")

        try:
            # Send welcome message
            await self._send_message(websocket, {
                "type": "connection",
                "status": "connected",
                "message": "Welcome to Synthesis.Pro!",
                "server_version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            })

            # Handle messages
            async for message in websocket:
                await self._handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"🔌 Unity disconnected: {client_info}")

        except Exception as e:
            self.logger.error(f"Connection error: {e}")

        finally:
            # Unregister connection
            self.connections.remove(websocket)
            self.logger.info(f"📊 Active connections: {len(self.connections)}")

    async def _handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """
        Handle incoming message from Unity

        Args:
            websocket: Client connection
            message: JSON message string
        """
        try:
            # Parse JSON
            data = json.loads(message)

            # Extract command info
            command_id = data.get('id', 'unknown')
            command_type = data.get('type', 'unknown')
            parameters = data.get('parameters', {})

            self.logger.info(f"📥 Command received: {command_type} (ID: {command_id})")

            # Find handler
            if command_type not in self.command_handlers:
                await self._send_error(websocket, command_id, f"Unknown command: {command_type}")
                self.stats['commands_failed'] += 1
                return

            # Execute handler
            handler = self.command_handlers[command_type]
            result = await handler(command_id, parameters)

            # Send result
            await self._send_message(websocket, result)
            self.stats['commands_processed'] += 1

            self.logger.info(f"✅ Command completed: {command_type}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON from client: {e}")
            self.logger.error(f"Raw message: {message[:200]}...")
            await self._send_error(websocket, "unknown", "Invalid JSON format")
            self.stats['commands_failed'] += 1

        except Exception as e:
            import traceback
            self.logger.error(f"Error handling message: {e}")
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            error_id = data.get('id', 'unknown') if isinstance(data, dict) else 'unknown'
            await self._send_error(websocket, error_id, str(e))
            self.stats['commands_failed'] += 1

    async def _send_message(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """
        Send message to Unity

        Args:
            websocket: Client connection
            data: Data to send (will be JSON encoded)
        """
        try:
            message = json.dumps(data)
            await websocket.send(message)
        except Exception as e:
            import traceback
            self.logger.error(f"Failed to send message to client: {e}")
            self.logger.error(f"Message data: {str(data)[:200]}...")
            self.logger.error(f"Stack trace: {traceback.format_exc()}")

    async def _send_error(self, websocket: websockets.WebSocketServerProtocol, command_id: str, error_message: str):
        """
        Send error response

        Args:
            websocket: Client connection
            command_id: Command ID that failed
            error_message: Error description
        """
        await self._send_message(websocket, {
            "commandId": command_id,
            "success": False,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })

    # ========== Command Handlers ==========

    async def _handle_ping(self, command_id: str, parameters: dict) -> dict:
        """Handle ping command"""
        return {
            "commandId": command_id,
            "success": True,
            "message": "Pong! Server is alive!",
            "data": {
                "server_time": datetime.now().isoformat(),
                "active_connections": len(self.connections),
                "uptime_seconds": (datetime.now() - self.stats['uptime_start']).total_seconds()
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_get_capabilities(self, command_id: str, parameters: dict) -> dict:
        """Handle get capabilities command"""
        return {
            "commandId": command_id,
            "success": True,
            "message": "Server capabilities",
            "data": {
                "version": "1.0.0",
                "name": "Synthesis.Pro WebSocket Server",
                "features": [
                    "Real-time communication",
                    "Dual database RAG",
                    "Conversation tracking",
                    "Knowledge search",
                    "AI chat"
                ],
                "registered_commands": list(self.command_handlers.keys()),
                "rag_enabled": self.rag is not None,
                "conversation_tracking": self.conversation_tracker is not None
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_get_stats(self, command_id: str, parameters: dict) -> dict:
        """Handle get stats command"""
        uptime = (datetime.now() - self.stats['uptime_start']).total_seconds()

        return {
            "commandId": command_id,
            "success": True,
            "message": "Server statistics",
            "data": {
                "connections_current": len(self.connections),
                "connections_total": self.stats['connections_total'],
                "commands_processed": self.stats['commands_processed'],
                "commands_failed": self.stats['commands_failed'],
                "uptime_seconds": uptime,
                "uptime_formatted": self._format_uptime(uptime)
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_chat(self, command_id: str, parameters: dict) -> dict:
        """
        Handle chat command (AI conversation)

        Parameters:
            message: User's message
            context: Optional context string
        """
        if not self.rag or not self.conversation_tracker:
            return {
                "commandId": command_id,
                "success": False,
                "message": "RAG engine not available",
                "timestamp": datetime.now().isoformat()
            }

        message = parameters.get('message', '')
        context = parameters.get('context', '')

        if not message:
            return {
                "commandId": command_id,
                "success": False,
                "message": "Missing 'message' parameter",
                "timestamp": datetime.now().isoformat()
            }

        try:
            # Use RAG onboarding system for natural context delivery
            context_data = None
            if self.rag_onboarding:
                context_data = self.rag_onboarding.process_user_message(message)

            # Gather relevant context naturally
            helpful_context = []
            if context_data and context_data.get('has_context'):
                helpful_context.append(context_data.get('context', ''))

            # Search knowledge base for additional context
            search_results = self.rag.search(message, top_k=3, private=True)

            # Format context naturally (not as "search results")
            context_preview = ""
            if helpful_context:
                context_preview = "\n\n".join(helpful_context)
            elif search_results:
                # Show relevant knowledge naturally
                context_preview = "From previous work:\n" + "\n".join(
                    [f"• {r.get('content', '')[:200]}..." for r in search_results[:2]]
                )

            # TODO: Call AI model with context (Phase 3)
            # For now, acknowledge message with natural context
            if context_preview:
                response = f"Message received: {message}\n\n{context_preview}"
            else:
                response = f"Message received: {message}\n(Clean slate - no prior context for this topic)"

            # Track conversation
            self.conversation_tracker.add_exchange(
                user_message=message,
                assistant_message=response,
                context=context
            )

            return {
                "commandId": command_id,
                "success": True,
                "message": "Chat response",
                "data": {
                    "response": response,
                    "has_context": bool(context_preview),
                    "context_items": len(search_results)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Chat failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_search_knowledge(self, command_id: str, parameters: dict) -> dict:
        """
        Handle knowledge search command

        Parameters:
            query: Search query
            top_k: Number of results (default: 10)
            private: Search private database (default: true)
        """
        if not self.rag:
            return {
                "commandId": command_id,
                "success": False,
                "message": "RAG engine not available",
                "timestamp": datetime.now().isoformat()
            }

        query = parameters.get('query', '')
        top_k = parameters.get('top_k', 10)
        private = parameters.get('private', True)

        if not query:
            return {
                "commandId": command_id,
                "success": False,
                "message": "Missing 'query' parameter",
                "timestamp": datetime.now().isoformat()
            }

        try:
            results = self.rag.search(query, top_k=top_k, private=private)

            return {
                "commandId": command_id,
                "success": True,
                "message": f"Found {len(results)} results",
                "data": {
                    "results": results,
                    "count": len(results),
                    "query": query
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Search failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_backup_private_db(self, command_id: str, parameters: dict) -> dict:
        """
        Handle private database backup command

        Creates a timestamped backup of the private database.
        """
        if not self.rag:
            return {
                "commandId": command_id,
                "success": False,
                "message": "RAG engine not available",
                "timestamp": datetime.now().isoformat()
            }

        try:
            # Get private database path
            private_db_path = Path(self.rag.private_database)

            if not private_db_path.exists():
                return {
                    "commandId": command_id,
                    "success": False,
                    "message": "Private database does not exist yet",
                    "timestamp": datetime.now().isoformat()
                }

            # Create backups directory
            backup_dir = private_db_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)

            # Generate timestamped backup filename
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"synthesis_private_backup_{timestamp_str}.db"
            backup_path = backup_dir / backup_filename

            # Copy database to backup
            shutil.copy2(private_db_path, backup_path)

            # Get backup info
            backup_size = backup_path.stat().st_size

            self.logger.info(f"✅ Private database backed up: {backup_filename}")

            return {
                "commandId": command_id,
                "success": True,
                "message": f"Private database backed up successfully",
                "data": {
                    "backup_file": backup_filename,
                    "backup_path": str(backup_path),
                    "backup_size": backup_size,
                    "timestamp": timestamp_str
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Backup error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Backup failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_clear_private_db(self, command_id: str, parameters: dict) -> dict:
        """
        Handle private database clear command

        Deletes the private database file. This is IRREVERSIBLE unless backed up!
        """
        if not self.rag:
            return {
                "commandId": command_id,
                "success": False,
                "message": "RAG engine not available",
                "timestamp": datetime.now().isoformat()
            }

        # Safety check: require explicit confirmation
        confirmation = parameters.get('confirm', False)
        if not confirmation:
            return {
                "commandId": command_id,
                "success": False,
                "message": "Confirmation required. Set 'confirm': true to proceed.",
                "timestamp": datetime.now().isoformat()
            }

        try:
            # Get private database path
            private_db_path = Path(self.rag.private_database)

            if not private_db_path.exists():
                return {
                    "commandId": command_id,
                    "success": True,
                    "message": "Private database does not exist (already clear)",
                    "timestamp": datetime.now().isoformat()
                }

            # Delete the database file
            private_db_path.unlink()

            self.logger.warning(f"⚠️ Private database cleared!")

            return {
                "commandId": command_id,
                "success": True,
                "message": "Private database cleared successfully",
                "data": {
                    "cleared_path": str(private_db_path)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Clear error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Clear failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_restore_private_db(self, command_id: str, parameters: dict) -> dict:
        """
        Handle private database restore command

        Restores private database from a backup file.

        Parameters:
            backup_file: Name of backup file to restore from
        """
        if not self.rag:
            return {
                "commandId": command_id,
                "success": False,
                "message": "RAG engine not available",
                "timestamp": datetime.now().isoformat()
            }

        backup_filename = parameters.get('backup_file', '')
        if not backup_filename:
            return {
                "commandId": command_id,
                "success": False,
                "message": "Missing 'backup_file' parameter",
                "timestamp": datetime.now().isoformat()
            }

        try:
            # Get paths
            private_db_path = Path(self.rag.private_database)
            backup_dir = private_db_path.parent / "backups"
            backup_path = backup_dir / backup_filename

            # Validate backup exists
            if not backup_path.exists():
                return {
                    "commandId": command_id,
                    "success": False,
                    "message": f"Backup file not found: {backup_filename}",
                    "timestamp": datetime.now().isoformat()
                }

            # Create backup of current database before overwriting (safety)
            if private_db_path.exists():
                safety_backup = private_db_path.parent / "backups" / f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(private_db_path, safety_backup)
                self.logger.info(f"Created safety backup before restore: {safety_backup.name}")

            # Restore from backup
            shutil.copy2(backup_path, private_db_path)

            self.logger.info(f"✅ Private database restored from: {backup_filename}")

            return {
                "commandId": command_id,
                "success": True,
                "message": f"Private database restored successfully",
                "data": {
                    "restored_from": backup_filename,
                    "restored_path": str(private_db_path)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Restore error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Restore failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_list_backups(self, command_id: str, parameters: dict) -> dict:
        """
        Handle list backups command

        Returns a list of available backup files.
        """
        if not self.rag:
            return {
                "commandId": command_id,
                "success": False,
                "message": "RAG engine not available",
                "timestamp": datetime.now().isoformat()
            }

        try:
            # Get backup directory
            private_db_path = Path(self.rag.private_database)
            backup_dir = private_db_path.parent / "backups"

            if not backup_dir.exists():
                return {
                    "commandId": command_id,
                    "success": True,
                    "message": "No backups found",
                    "data": {
                        "backups": []
                    },
                    "timestamp": datetime.now().isoformat()
                }

            # List all .db files in backup directory
            backups = []
            for backup_file in sorted(backup_dir.glob("*.db"), reverse=True):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": str(backup_file)
                })

            return {
                "commandId": command_id,
                "success": True,
                "message": f"Found {len(backups)} backup(s)",
                "data": {
                    "backups": backups,
                    "count": len(backups)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"List backups error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"List backups failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_audit_public_db(self, command_id: str, parameters: dict) -> dict:
        """
        Handle public database audit command

        Scans the public database for potentially sensitive content that
        should not be shared publicly.

        Returns audit results with flagged entries.
        """
        if not self.rag:
            return {
                "commandId": command_id,
                "success": False,
                "message": "RAG engine not available",
                "timestamp": datetime.now().isoformat()
            }

        try:
            # Run audit
            audit_results = self.rag.audit_public_database()

            # Log results
            if audit_results["passed"]:
                self.logger.info(f"Public database audit PASSED: {audit_results['total_documents']} documents scanned")
            else:
                self.logger.warning(f"Public database audit FAILED: {audit_results['flagged_count']} suspicious entries found")

            return {
                "commandId": command_id,
                "success": True,
                "message": f"Audit complete: {audit_results['flagged_count']} potential issues found",
                "data": audit_results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Audit error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Audit failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_check_db_updates(self, command_id: str, parameters: dict) -> dict:
        """
        Check if database or model updates are available

        Returns information about the current and latest versions.
        """
        try:
            db_manager = DatabaseManager()

            # Get current versions
            db_info = db_manager.version_info.get('database', {})
            model_info = db_manager.version_info.get('model', {})
            current_updated = db_manager.version_info.get('updated', 'unknown')

            # Check for updates
            updates = db_manager.check_for_updates()

            update_list = []
            if updates.get('database'):
                update_list.append(f"database ({updates['database']})")
            if updates.get('model'):
                update_list.append(f"model ({updates['model']})")

            if update_list:
                message = f"Updates available: {', '.join(update_list)}"
                update_available = True
            else:
                message = "Everything is up to date"
                update_available = False

            return {
                "commandId": command_id,
                "success": True,
                "message": message,
                "data": {
                    "database": {
                        "current_version": db_info.get('version', 'unknown'),
                        "latest_version": updates.get('database', db_info.get('version', 'unknown')),
                        "update_available": bool(updates.get('database'))
                    },
                    "model": {
                        "current_version": model_info.get('version', 'unknown'),
                        "latest_version": updates.get('model', model_info.get('version', 'unknown')),
                        "update_available": bool(updates.get('model'))
                    },
                    "last_updated": current_updated
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Update check error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Update check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_update_public_db(self, command_id: str, parameters: dict) -> dict:
        """
        Update database and model to latest versions

        Downloads and installs updates for both the Unity documentation database
        and the embeddings model.
        """
        try:
            db_manager = DatabaseManager()

            # Check if update is available
            updates = db_manager.check_for_updates()
            if not updates.get('database') and not updates.get('model'):
                return {
                    "commandId": command_id,
                    "success": True,
                    "message": "Everything is already up to date",
                    "timestamp": datetime.now().isoformat()
                }

            # Perform update
            update_list = []
            if updates.get('database'):
                update_list.append(f"database ({updates['database']})")
            if updates.get('model'):
                update_list.append(f"model ({updates['model']})")

            self.logger.info(f"Downloading updates: {', '.join(update_list)}")
            success = db_manager.update_all()

            if success:
                # Reinitialize RAG with updated database/model
                await self._initialize_rag()

                return {
                    "commandId": command_id,
                    "success": True,
                    "message": f"Updated: {', '.join(update_list)}",
                    "data": {
                        "database": db_manager.version_info.get('database', {}),
                        "model": db_manager.version_info.get('model', {})
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "commandId": command_id,
                    "success": False,
                    "message": "Update failed",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Update error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Update failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_console_log(self, command_id: str, parameters: dict) -> dict:
        """
        Handle console log entries from Unity

        Captures errors, warnings, and important logs to RAG memory
        for learning and pattern detection.
        """
        try:
            if not self.console_monitor:
                return {
                    "commandId": command_id,
                    "success": False,
                    "message": "Console monitor not initialized",
                    "timestamp": datetime.now().isoformat()
                }

            # Extract console entries from parameters
            entries = parameters.get('entries', [])
            if not entries:
                return {
                    "commandId": command_id,
                    "success": True,
                    "message": "No entries to process",
                    "timestamp": datetime.now().isoformat()
                }

            # Capture entries
            stats = self.console_monitor.capture_batch(entries)

            # Log if we captured anything interesting
            if stats['captured'] > 0:
                self.logger.info(f"📝 Captured {stats['captured']} console entries to memory")
                if stats.get('errors', 0) > 0:
                    self.logger.warning(f"⚠️  {stats['errors']} error(s) captured")

            return {
                "commandId": command_id,
                "success": True,
                "message": f"Processed {stats['total']} entries, captured {stats['captured']}",
                "data": stats,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Console log handler error: {e}")
            return {
                "commandId": command_id,
                "success": False,
                "message": f"Failed to process console logs: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"


async def main():
    """Main entry point"""
    # Create and start server
    server = SynthesisWebSocketServer(host="localhost", port=8765)

    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        print(f"📊 Final stats:")
        print(f"   Total connections: {server.stats['connections_total']}")
        print(f"   Commands processed: {server.stats['commands_processed']}")
        print(f"   Commands failed: {server.stats['commands_failed']}")


if __name__ == "__main__":
    print("=" * 60)
    print("[>>] Synthesis.Pro WebSocket Server")
    print("=" * 60)
    asyncio.run(main())
