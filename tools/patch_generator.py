#!/usr/bin/env python3
import ast
import json
import sys
from typing import Any, Dict, List


class PatchGenerator:
    def __init__(self):
        self.patches = []

    def add_import(self, file_path: str, module: str) -> Dict[str, Any]:
        """Add import statement to Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Check if import already exists
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == module:
                    return {"status": "already_exists", "file": file_path}

            # Generate patch
            patch = {
                "action": "add_import",
                "file": file_path,
                "module": module,
                "diff": f"+from {module} import *\n",
                "status": "generated",
            }
            self.patches.append(patch)
            return patch

        except Exception as e:
            return {"status": "error", "file": file_path, "error": str(e)}

    def increase_timeout(self, file_path: str, factor: float) -> Dict[str, Any]:
        """Increase timeout values in test files"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple regex-based timeout increase
            import re

            timeout_pattern = r"(\d+(?:\.\d+)?)\s*[*]\s*timeout"
            matches = re.findall(timeout_pattern, content)

            if not matches:
                return {"status": "no_timeout_found", "file": file_path}

            # Generate patch
            patch = {
                "action": "increase_timeout",
                "file": file_path,
                "factor": factor,
                "matches": matches,
                "diff": f"# Timeout increased by factor {factor}\n",
                "status": "generated",
            }
            self.patches.append(patch)
            return patch

        except Exception as e:
            return {"status": "error", "file": file_path, "error": str(e)}

    def get_patches(self) -> List[Dict[str, Any]]:
        return self.patches

    def clear_patches(self):
        self.patches = []


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/patch_generator.py <action> <file> [params...]")
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else ""

    generator = PatchGenerator()

    if action == "add_import":
        module = sys.argv[3] if len(sys.argv) > 3 else "duri_common.settings"
        result = generator.add_import(file_path, module)
    elif action == "increase_timeout":
        factor = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
        result = generator.increase_timeout(file_path, factor)
    else:
        result = {"status": "unknown_action", "action": action}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
