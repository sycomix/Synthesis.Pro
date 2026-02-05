"""
RAG Bridge - Python side of Unity-Python RAG integration
Receives commands from Unity via JSON files and executes RAG operations
"""
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "RAG"))

from rag_engine import SynthesisRAG
from context_preview import ContextPreview
from context_detector import ContextDetector
from curiosity_trigger import CuriosityTrigger


class RAGBridgeServer:
    """Handles RAG commands from Unity"""

    def __init__(self):
        # Database paths
        server_dir = Path(__file__).parent
        self.public_db = server_dir / "synthesis_public.db"
        self.private_db = server_dir / "synthesis_private.db"

        # Initialize RAG engines
        self.public_rag = None
        self.private_rag = None

        # Initialize services
        self.context_preview = None
        self.context_detector = None
        self.curiosity_trigger = None

        # Session state
        self.current_session_id = None

    def initialize(self):
        """Initialize RAG engines and services"""
        try:
            # Initialize public RAG if database exists
            if self.public_db.exists():
                self.public_rag = SynthesisRAG(str(self.public_db))

            # Initialize private RAG if database exists
            if self.private_db.exists():
                self.private_rag = SynthesisRAG(str(self.private_db))

            # Use public RAG for services (can search both DBs)
            if self.public_rag:
                self.context_preview = ContextPreview(self.public_rag)
                self.context_detector = ContextDetector(self.public_rag)
                self.curiosity_trigger = CuriosityTrigger(self.public_rag)

            return True

        except Exception as e:
            print(f"[RAG Bridge] Initialization error: {e}")
            return False

    def start_session(self, session_id: str = None) -> dict:
        """Start new RAG session with context preview"""
        self.current_session_id = session_id or "default"

        preview = None
        if self.context_preview:
            preview = self.context_preview.generate_preview()

        return {
            "success": True,
            "session_id": self.current_session_id,
            "preview": preview,
            "message": "Session started"
        }

    def process_user_message(self, message: str) -> dict:
        """Process user message and return relevant context if available"""
        if not self.context_detector:
            return {"success": False, "message": "Context detector not initialized"}

        result = self.context_detector.detect_context_need(message)

        return {
            "success": True,
            "has_context": result.get('has_context', False),
            "confidence": result.get('confidence', 0.0),
            "context": result.get('context', ''),
            "message": "Message processed"
        }

    def process_ai_response(self, ai_response: str, user_message: str,
                           enable_collective_learning: bool = False) -> dict:
        """Process AI response for uncertainty detection"""
        if not self.curiosity_trigger:
            return {"success": False, "message": "Curiosity trigger not initialized"}

        # Detect uncertainty
        uncertainty = self.curiosity_trigger.detect_uncertainty(ai_response)

        # Offer context if uncertain
        context_offer = None
        if uncertainty['is_uncertain']:
            context_offer = self.curiosity_trigger.offer_context(ai_response, user_message)

        result = {
            "success": True,
            "is_uncertain": uncertainty['is_uncertain'],
            "uncertainty_type": uncertainty.get('uncertainty_type'),
            "topic": uncertainty.get('topic'),
            "message": "AI response processed"
        }

        if context_offer:
            result["context_offer"] = context_offer.get('suggestion', '')
            result["has_context"] = True
        else:
            result["has_context"] = False

        # TODO: Implement collective learning contribution when enabled
        if enable_collective_learning:
            result["collective_learning"] = "Not yet implemented"

        return result

    def end_session(self) -> dict:
        """End current RAG session"""
        session_id = self.current_session_id
        self.current_session_id = None

        return {
            "success": True,
            "session_id": session_id,
            "message": "Session ended"
        }

    def execute_command(self, command_data: dict) -> dict:
        """Execute a command from Unity"""
        command = command_data.get('command')

        if command == 'start_session':
            session_id = command_data.get('session_id')
            return self.start_session(session_id)

        elif command == 'process_user_message':
            message = command_data.get('message')
            if not message:
                return {"success": False, "message": "Missing 'message' parameter"}
            return self.process_user_message(message)

        elif command == 'process_ai_response':
            ai_response = command_data.get('ai_response')
            user_message = command_data.get('user_message', '')
            enable_cl = command_data.get('enable_collective_learning', False)

            if not ai_response:
                return {"success": False, "message": "Missing 'ai_response' parameter"}

            return self.process_ai_response(ai_response, user_message, enable_cl)

        elif command == 'end_session':
            return self.end_session()

        else:
            return {"success": False, "message": f"Unknown command: {command}"}


def main():
    """Main entry point for RAG bridge"""
    if len(sys.argv) < 2:
        print("Usage: rag_bridge.py <input_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # Read input command
        with open(input_file, 'r') as f:
            command_data = json.load(f)

        output_file = command_data.get('output_file')

        if not output_file:
            print("Error: No output_file specified in command data")
            sys.exit(1)

        # Initialize bridge
        bridge = RAGBridgeServer()

        if not bridge.initialize():
            result = {"success": False, "message": "Failed to initialize RAG bridge"}
        else:
            # Execute command
            result = bridge.execute_command(command_data)

        # Write result to output file
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        sys.exit(0)

    except Exception as e:
        error_result = {
            "success": False,
            "message": f"Bridge error: {str(e)}"
        }

        # Try to write error to output file
        try:
            output_file = command_data.get('output_file')
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(error_result, f, indent=2)
        except:
            pass

        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
