"""Recursive JSON Schema Healer.
100% Python Standard Library.
"""

class RecursiveJsonSchemaHealer:
    """Recursive JSON schema validator and autonomous healer for LLM structured outputs."""

    @classmethod
    def validate_and_heal(cls, schema: dict, data: any, coerce_types: bool = True, add_missing_defaults: bool = True) -> dict:
        modifications = []
        violations = []

        def _heal_node(sub_schema: dict, val: any, path: str):
            s_type = sub_schema.get("type")
            curr_val = val

            if curr_val is None:
                if sub_schema.get("nullable") or s_type == "null":
                    return curr_val
                if "default" in sub_schema and add_missing_defaults:
                    modifications.append(f"Injected default for {path}")
                    return sub_schema["default"]

            # Type checking and coercion
            if s_type == "string" and not isinstance(curr_val, str):
                if coerce_types:
                    modifications.append(f"Coerced {path} to string")
                    curr_val = str(curr_val)
                else:
                    violations.append(f"{path} expected string, got {type(curr_val).__name__}")
            elif s_type == "integer" and (not isinstance(curr_val, int) or isinstance(curr_val, bool)):
                if coerce_types:
                    try:
                        curr_val = int(float(curr_val))
                        modifications.append(f"Coerced {path} to integer")
                    except (ValueError, TypeError):
                        violations.append(f"{path} cannot be coerced to integer")
                else:
                    violations.append(f"{path} expected integer, got {type(curr_val).__name__}")
            elif s_type == "number" and (not isinstance(curr_val, (int, float)) or isinstance(curr_val, bool)):
                if coerce_types:
                    try:
                        curr_val = float(curr_val)
                        modifications.append(f"Coerced {path} to number")
                    except (ValueError, TypeError):
                        violations.append(f"{path} cannot be coerced to number")
                else:
                    violations.append(f"{path} expected number, got {type(curr_val).__name__}")
            elif s_type == "boolean" and not isinstance(curr_val, bool):
                if coerce_types:
                    if isinstance(curr_val, str):
                        curr_val = curr_val.lower() in ("true", "1", "yes")
                    else:
                        curr_val = bool(curr_val)
                    modifications.append(f"Coerced {path} to boolean")
                else:
                    violations.append(f"{path} expected boolean, got {type(curr_val).__name__}")

            # Object recursion
            if s_type == "object" or (isinstance(curr_val, dict) and "properties" in sub_schema):
                if not isinstance(curr_val, dict):
                    curr_val = {}
                    modifications.append(f"Initialized {path} as dict")

                # Check required fields
                for req_key in sub_schema.get("required", []):
                    if req_key not in curr_val or curr_val[req_key] is None:
                        prop_schema = sub_schema.get("properties", {}).get(req_key, {})
                        if "default" in prop_schema and add_missing_defaults:
                            curr_val[req_key] = prop_schema["default"]
                            modifications.append(f"Added default for missing required field: {path}.{req_key}")
                        elif add_missing_defaults:
                            def_type = prop_schema.get("type", "string")
                            dummy = {"string": "", "integer": 0, "number": 0.0, "boolean": False, "array": [], "object": {}}.get(def_type, "")
                            curr_val[req_key] = dummy
                            modifications.append(f"Added empty placeholder for missing required field: {path}.{req_key}")
                        else:
                            violations.append(f"Missing required property {path}.{req_key}")

                # Traverse children
                props = sub_schema.get("properties", {})
                for k, child_schema in props.items():
                    if k in curr_val:
                        curr_val[k] = _heal_node(child_schema, curr_val[k], f"{path}.{k}")

            # Array recursion
            elif s_type == "array" or (isinstance(curr_val, list) and "items" in sub_schema):
                if not isinstance(curr_val, list):
                    curr_val = [curr_val] if curr_val is not None else []
                    modifications.append(f"Wrapped {path} into list")
                item_schema = sub_schema.get("items", {})
                if item_schema:
                    curr_val = [_heal_node(item_schema, item, f"{path}[{idx}]") for idx, item in enumerate(curr_val)]

            return curr_val

        healed = _heal_node(schema, data, "root")
        return {
            "is_valid": len(violations) == 0,
            "healed_data": healed,
            "modifications_applied": modifications,
            "violations": violations
        }
