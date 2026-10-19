"""MCP Server for Recursive JSON Schema Healer.
100% Python Standard Library JSON-RPC.
"""
import sys
import json
from client import RecursiveJsonSchemaHealer

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "validate_and_heal",
                                "description": "Validate and automatically repair malformed JSON data against schema",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "schema": {"type": "object", "description": "JSON Schema specification"},
                                        "data": {"type": "object", "description": "Data payload to validate and heal"}
                                    },
                                    "required": ["schema", "data"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                args = req.get("params", {}).get("arguments", {})
                schema = args.get("schema", {})
                data = args.get("data", {})
                res = RecursiveJsonSchemaHealer.validate_and_heal(schema, data)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
