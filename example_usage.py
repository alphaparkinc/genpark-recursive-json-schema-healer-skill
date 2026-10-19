"""Example usage for Recursive JSON Schema Healer."""
from client import RecursiveJsonSchemaHealer
import json

schema = {
    "type": "object",
    "required": ["agent_id", "confidence_score", "active"],
    "properties": {
        "agent_id": {"type": "string"},
        "confidence_score": {"type": "number", "default": 0.95},
        "active": {"type": "boolean", "default": True}
    }
}

malformed = {
    "agent_id": 998822,
    "confidence_score": "0.88"
}

res = RecursiveJsonSchemaHealer.validate_and_heal(schema, malformed)
print(json.dumps(res, indent=2))
