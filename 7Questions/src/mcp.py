"""MCP tool definitions for 7D storage."""

from .api import SevenQuestionsAPI
import json


# Global instance
api = SevenQuestionsAPI()


def register_tools() -> list:
    """Return tool definitions for MCP."""
    return [
        {
            "name": "assert_fact",
            "description": "Store a fact as 7D coordinate [Q,O,L,T,N,K,M]",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "q": {"type": ["string", "number"], "description": "Who"},
                    "o": {"type": ["string", "number"], "description": "What"},
                    "l": {"type": ["string", "number"], "description": "Where"},
                    "t": {"type": ["string", "number"], "description": "When"},
                    "n": {"type": ["string", "number"], "description": "How much"},
                    "k": {"type": ["string", "number"], "description": "Which/Kind"},
                    "m": {"type": ["string", "number"], "description": "How (predicate)"},
                    "value": {"description": "The value to store"}
                },
                "required": ["q", "o", "l", "t", "n", "k", "m", "value"]
            }
        },
        {
            "name": "ask",
            "description": "Query points with wildcards (null = any)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "q": {"type": ["string", "number", "null"]},
                    "o": {"type": ["string", "number", "null"]},
                    "l": {"type": ["string", "number", "null"]},
                    "t": {"type": ["string", "number", "null"]},
                    "n": {"type": ["string", "number", "null"]},
                    "k": {"type": ["string", "number", "null"]},
                    "m": {"type": ["string", "number", "null"]}
                }
            }
        },
        {
            "name": "erase",
            "description": "Delete a specific 7D point",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "q": {"type": ["string", "number"]},
                    "o": {"type": ["string", "number"]},
                    "l": {"type": ["string", "number"]},
                    "t": {"type": ["string", "number"]},
                    "n": {"type": ["string", "number"]},
                    "k": {"type": ["string", "number"]},
                    "m": {"type": ["string", "number"]}
                },
                "required": ["q", "o", "l", "t", "n", "k", "m"]
            }
        },
        {
            "name": "show_model",
            "description": "Export entire state"
        },
        {
            "name": "reset",
            "description": "Clear all data"
        }
    ]


def call_tool(name: str, args: dict) -> str:
    """Execute a tool and return JSON result."""
    try:
        if name == "assert_fact":
            result = api.assert_fact(
                args.get("q"), args.get("o"), args.get("l"),
                args.get("t"), args.get("n"), args.get("k"),
                args.get("m"), args.get("value")
            )
        elif name == "ask":
            result = api.ask(
                q=args.get("q"), o=args.get("o"), l=args.get("l"),
                t=args.get("t"), n=args.get("n"), k=args.get("k"),
                m=args.get("m")
            )
        elif name == "erase":
            result = api.erase(
                args.get("q"), args.get("o"), args.get("l"),
                args.get("t"), args.get("n"), args.get("k"),
                args.get("m")
            )
        elif name == "show_model":
            result = api.show_model()
        elif name == "reset":
            result = api.reset()
        else:
            result = {"error": f"Unknown tool: {name}"}
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})
