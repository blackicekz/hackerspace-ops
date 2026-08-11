import ast
import sys
import unittest
from pathlib import Path

LAYERS = ("domain", "application", "adapters", "infrastructure")
ALLOWED_PROJECT_DEPENDENCIES = {
    "domain": {"domain"},
    "application": {"domain", "application"},
    "adapters": {"domain", "application", "adapters"},
    "infrastructure": set(LAYERS),
}
CORE_LAYERS = {"domain", "application"}


class ArchitectureDependenciesTest(unittest.TestCase):
    def test_production_dependencies_point_inward(self) -> None:
        violations: list[str] = []
        for path in Path("src").glob("**/*.py"):
            layer = path.parts[1] if len(path.parts) > 2 else None
            if layer not in LAYERS:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for module in imported_modules(tree, path):
                dependency = project_layer(module)
                if dependency and dependency not in ALLOWED_PROJECT_DEPENDENCIES[layer]:
                    violations.append(f"{path}: {layer} must not import {dependency}")
                elif layer in CORE_LAYERS and is_third_party(module):
                    violations.append(
                        f"{path}: {layer} must not import third-party module {module}"
                    )

        self.assertEqual([], violations, "\n".join(violations))

    def test_relative_imports_are_resolved_before_checking_boundaries(self) -> None:
        tree = ast.parse("from ..infrastructure import settings")

        self.assertEqual(
            ["src.infrastructure"], imported_modules(tree, Path("src/application/use_case.py"))
        )

    def test_core_third_party_imports_are_identified(self) -> None:
        self.assertTrue(is_third_party("vendor_sdk.client"))
        self.assertFalse(is_third_party("datetime"))
        self.assertFalse(is_third_party("src.domain"))


def imported_modules(tree: ast.AST, path: Path) -> list[str]:
    modules: list[str] = []
    package = list(path.with_suffix("").parts[:-1])
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = resolve_import_from(node, package)
            if base == "src":
                modules.extend(f"src.{alias.name}" for alias in node.names)
            elif base:
                modules.append(base)
    return modules


def resolve_import_from(node: ast.ImportFrom, package: list[str]) -> str:
    if node.level == 0:
        return node.module or ""
    keep = len(package) - node.level + 1
    base = package[:keep]
    if node.module:
        base.extend(node.module.split("."))
    return ".".join(base)


def project_layer(module: str) -> str | None:
    parts = module.split(".")
    if len(parts) >= 2 and parts[0] == "src" and parts[1] in LAYERS:
        return parts[1]
    return None


def is_third_party(module: str) -> bool:
    root = module.split(".")[0]
    return root != "src" and root not in sys.stdlib_module_names


if __name__ == "__main__":
    unittest.main()
