#!/usr/bin/env python3
"""
MCP Workflows Project Scaffolder

This script creates a new MCP Workflows project from the current template.
Usage: python scaffold.py <project_name> [destination_dir]

Example:
    python scaffold.py my-new-project
    python scaffold.py my-new-project /path/to/projects
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


class ProjectScaffolder:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.exclude_files: set[str] = {
            ".git",
            ".venv_workflows",
            "__pycache__",
            ".pytest_cache",
            ".coverage",
            "htmlcov",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
            "Thumbs.db",
            ".mypy_cache",
            ".ruff_cache",
            "node_modules",
            ".env",
            ".env.local",
            ".env.*.local",
            "secrets",
            "*.key",
            "*.pem",
            "*.crt",
            "*.p12",
            "build",
            "dist",
            "*.egg-info",
            ".tox",
            ".nox",
            "coverage.xml",
            "*.cover",
            "*.log",
            "logs",
            "*.tmp",
            "*.bak",
            "*.backup"
        }
        self.exclude_dirs: set[str] = {
            ".git",
            ".venv_workflows",
            "__pycache__",
            ".pytest_cache",
            "htmlcov",
            ".mypy_cache",
            ".ruff_cache",
            "node_modules",
            "build",
            "dist",
            "*.egg-info",
            ".tox",
            ".nox"
        }

    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from copying."""
        path_str = str(path)

        # Check exact matches
        if path.name in self.exclude_files:
            return True

        # Check directory patterns
        for exclude_dir in self.exclude_dirs:
            if exclude_dir in path_str:
                return True

        # Check if it's a hidden file/directory (except .vscode, .gitignore)
        return path.name.startswith(".") and path.name not in [".vscode", ".gitignore"]

    def copy_template(self, dest_dir: Path) -> None:
        """Copy template files to destination directory."""
        print(f"📁 Copying template to {dest_dir}")

        for src_path in self.template_dir.rglob("*"):
            if self.should_exclude(src_path):
                continue

            # Calculate relative path from template directory
            rel_path = src_path.relative_to(self.template_dir)

            # Skip if it's the scaffold script itself
            if rel_path.name == "scaffold.py":
                continue

            dest_path = dest_dir / rel_path

            try:
                if src_path.is_file():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    print(f"  ✅ {rel_path}")
                elif src_path.is_dir():
                    dest_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"  ❌ Failed to copy {rel_path}: {e}")

    def customize_project(self, dest_dir: Path, project_name: str) -> None:
        """Customize the copied project with the new project name."""
        print(f"🔧 Customizing project: {project_name}")

        # Convert project name to package name (snake_case)
        package_name = project_name.lower().replace("-", "_").replace(" ", "_")

        # Files to customize
        files_to_update = [
            dest_dir / "pyproject.toml",
            dest_dir / "README.md",
            dest_dir / "src" / "mcp_workflows" / "__init__.py",
            dest_dir / "Makefile"
        ]

        for file_path in files_to_update:
            if file_path.exists():
                try:
                    content = file_path.read_text()

                    # Replace project name
                    content = content.replace("MCP Workflows", project_name.title())
                    content = content.replace("mcp-workflows", project_name.lower())
                    content = content.replace("mcp_workflows", package_name)

                    file_path.write_text(content)
                    print(f"  ✅ Updated {file_path.relative_to(dest_dir)}")
                except Exception as e:
                    print(f"  ❌ Failed to update {file_path}: {e}")

        # Rename package directory
        old_package_dir = dest_dir / "src" / "mcp_workflows"
        new_package_dir = dest_dir / "src" / package_name

        if old_package_dir.exists() and old_package_dir != new_package_dir:
            try:
                shutil.move(str(old_package_dir), str(new_package_dir))
                print(f"  ✅ Renamed package directory to {package_name}")
            except Exception as e:
                print(f"  ❌ Failed to rename package directory: {e}")

    def setup_project(self, dest_dir: Path) -> None:
        """Set up the new project (git init, venv, install deps)."""
        print("🚀 Setting up project...")

        # Initialize git
        try:
            subprocess.run(["git", "init"], cwd=dest_dir, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=dest_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit: Project scaffolded from MCP Workflows template"],
                         cwd=dest_dir, check=True, capture_output=True)
            print("  ✅ Git repository initialized and committed")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Git setup failed: {e}")

        # Create virtual environment
        venv_dir = dest_dir / ".venv"
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, capture_output=True)
            print("  ✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Virtual environment creation failed: {e}")
            return

        # Install dependencies
        pip_path = venv_dir / "bin" / "pip"
        if pip_path.exists():
            try:
                subprocess.run([str(pip_path), "install", "-e", ".[dev]"], cwd=dest_dir, check=True, capture_output=True)
                print("  ✅ Dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️  Dependency installation failed: {e}")

    def scaffold(self, project_name: str, dest_dir: Path | None) -> Path:
        """Main scaffolding method."""
        if dest_dir is None:
            dest_dir = Path.cwd() / project_name
        else:
            dest_dir = dest_dir / project_name

        print(f"🏗️  Scaffolding new MCP Workflows project: {project_name}")
        print(f"📍 Destination: {dest_dir}")

        if dest_dir.exists():
            response = input(f"Directory {dest_dir} already exists. Overwrite? (y/N): ")
            if response.lower() != "y":
                print("❌ Scaffolding cancelled")
                return dest_dir
            shutil.rmtree(dest_dir)

        # Create destination directory
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy template
        self.copy_template(dest_dir)

        # Customize project
        self.customize_project(dest_dir, project_name)

        # Setup project
        self.setup_project(dest_dir)

        print("\n✅ Project scaffolding complete!")
        print(f"📂 Project location: {dest_dir}")
        print("🚀 To get started:")
        print(f"   cd {dest_dir}")
        print("   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate")
        print("   make test")
        print("   make run")

        return dest_dir


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new MCP Workflows project")
    parser.add_argument("project_name", help="Name of the new project")
    parser.add_argument("destination", nargs="?", help="Destination directory (default: current directory)")

    args = parser.parse_args()

    # Get template directory (directory containing this script)
    template_dir = Path(__file__).parent

    # Create scaffolder
    scaffolder = ProjectScaffolder(template_dir)

    # Determine destination
    dest_dir = Path(args.destination) if args.destination else None

    # Scaffold project
    try:
        result_dir = scaffolder.scaffold(args.project_name, dest_dir)
        print(f"\n🎉 Success! Project '{args.project_name}' created at {result_dir}")
    except Exception as e:
        print(f"❌ Scaffolding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
