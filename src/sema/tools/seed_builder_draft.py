"""
Sema Seed Builder - Generates self-contained sema/ directories for repositories
"""
import shutil
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional
from jinja2 import Template


class SeedBuilder:
    """Generates self-contained sema directories for repositories."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize the seed builder.
        
        Args:
            registry_path: Path to the registry directory. If None, uses default location.
        """
        if registry_path is None:
            # Default: src/sema/registry
            registry_path = Path(__file__).parent.parent / "registry"
        
        self.registry_path = registry_path
        self.templates_path = Path(__file__).parent.parent / "templates"
        
        # Load the registry to validate selections
        self.registry = self._load_registry()
        
        # Track what we're building
        self.selected_types: List[str] = []
        self.selected_enums: List[str] = []
        self.resolved_types: Set[str] = set()
        self.resolved_enums: Set[str] = set()
    
    def _load_registry(self) -> dict:
        """Load the registry.yaml file."""
        registry_file = self.registry_path.parent.parent.parent / "type_definitions" / "registry.yaml"
        
        with open(registry_file, 'r') as f:
            return yaml.safe_load(f)
    
    def generate_seed(
        self,
        selected_types: List[str],
        selected_enums: List[str],
        package_name: str,
        repo_name: str,
        output_path: Path,
        include_old_versions: bool = True,
        include_tests: bool = True
    ) -> Path:
        """
        Generate a complete sema/ directory.
        
        Args:
            selected_types: List of type names (e.g., ["power.watts", "channel.readings"])
            selected_enums: List of enum names (e.g., ["actor.class"])
            package_name: Python package name (e.g., "gbo")
            repo_name: Repository name (e.g., "gridworks-backoffice")
            output_path: Where to create the sema/ directory
            include_old_versions: Whether to include old versions for migration
            include_tests: Whether to include basic tests
            
        Returns:
            Path to the generated sema/ directory
        """
        self.selected_types = selected_types
        self.selected_enums = selected_enums
        self.package_name = package_name
        # Resolve dependencies
        self._resolve_dependencies()
        
        # Create directory structure
        sema_path = output_path / "sema"
        (sema_path / "types").mkdir(parents=True, exist_ok=True)
        (sema_path / "enums").mkdir(parents=True, exist_ok=True)
        
        if include_old_versions:
            (sema_path / "types" / "old_versions").mkdir(exist_ok=True)
        
        if include_tests:
            (sema_path / "tests").mkdir(exist_ok=True)
        
        # Copy selected types and enums
        self._copy_types(sema_path / "types")
        self._copy_enums(sema_path / "enums")
        
        # Copy property_format.py
        self._copy_property_format(sema_path)
        
        # Generate codec.py from template
        self._generate_codec(package_name, repo_name, sema_path)
        
        # Generate __init__.py files
        self._generate_init_files(package_name, sema_path)
        
        # Generate basic tests if requested
        if include_tests:
            self._generate_tests(package_name, sema_path / "tests")
        
        # Generate README
        self._generate_readme(repo_name, sema_path)
        
        return sema_path
    
    def _resolve_dependencies(self):
        """
        Resolve all dependencies for selected types and enums.
        Adds any required enums/types that the selected ones depend on.
        """
        # Start with selected items
        self.resolved_types = set(self.selected_types)
        self.resolved_enums = set(self.selected_enums)
        
        # Keep resolving until no new dependencies found
        changed = True
        while changed:
            changed = False
            
            # Check each type for dependencies
            for type_name in list(self.resolved_types):
                if type_name in self.registry.get('types', {}):
                    type_info = self.registry['types'][type_name]
                    
                    # Get dependencies from the current version
                    if 'versions' in type_info:
                        current_version = type_info.get('current_version')
                        if current_version and current_version in type_info['versions']:
                            deps = type_info['versions'][current_version].get('dependencies', {})
                            for dep in deps.get('direct', []):
                                # Parse dependency (format: "enum.name:version" or "type.name:version")
                                dep_name = dep.split(':')[0]
                                
                                # Determine if it's an enum or type
                                if dep_name in self.registry.get('enums', {}):
                                    if dep_name not in self.resolved_enums:
                                        self.resolved_enums.add(dep_name)
                                        changed = True
                                elif dep_name in self.registry.get('types', {}):
                                    if dep_name not in self.resolved_types:
                                        self.resolved_types.add(dep_name)
                                        changed = True
    
    def _copy_types(self, types_dir: Path):
        """Copy selected type files to the output directory,  rewriting imports."""
        for type_name in self.resolved_types:
            # Convert dot notation to file path
            # e.g., "power.watts" -> "power_watts.py"
            file_name = type_name.replace(".", "_") + ".py"
            
            source = self.registry_path / "types" / file_name
            if source.exists():
                content = source.read_text()
                # Rewrite imports from sema.runtime to target package
                content = self._rewrite_imports(content, self.package_name)
                dest = types_dir / file_name
                shutil.copy2(source, dest)
                print(f"  Copied type: {type_name}")
            else:
                print(f"  Warning: Type file not found: {source}")

    def _rewrite_imports(self, content: str, package_name: str) -> str:
        """Rewrite imports to use the target package name."""
        import re
        
        # Replace imports from sema.runtime.types
        content = re.sub(
            r'from sema\.registry\.types\.(\w+) import',
            fr'from {package_name}.sema.types.\1 import',
            content
        )
        
        # Replace imports from sema.runtime.enums
        content = re.sub(
            r'from sema\.registry\.enums\.(\w+) import',
            fr'from {package_name}.sema.enums.\1 import',
            content
        )
        
        # Replace imports from sema.runtime (for semaType base class)
        content = re.sub(
            r'from sema\.registry import semaType',
            fr'from {package_name}.sema.codec import semaType',
            content
        )

    def _copy_enums(self, enums_dir: Path):
        """Copy selected enum files to the output directory."""
        for enum_name in self.resolved_enums:
            # Convert dot notation to file path
            file_name = enum_name.replace(".", "_") + ".py"
            
            source = self.registry_path / "enums" / file_name
            if source.exists():
                dest = enums_dir / file_name
                shutil.copy2(source, dest)
                print(f"  Copied enum: {enum_name}")
            else:
                print(f"  Warning: Enum file not found: {source}")
    
    def _copy_property_format(self, sema_path: Path):
        """Copy property_format.py from registry."""
        source = self.registry_path / "property_format.py"
        if source.exists():
            dest = sema_path / "property_format.py"
            shutil.copy2(source, dest)
            print("  Copied property_format.py")
        else:
            print(f"  Warning: property_format.py not found at {source}")
    
    def _generate_codec(self, package_name: str, repo_name: str, sema_path: Path):
        """Generate codec.py from template."""
        template_path = self.templates_path / "codec.py.jinja2"
        
        if not template_path.exists():
            print(f"  Warning: Template not found: {template_path}")
            return
        
        with open(template_path) as f:
            template = Template(f.read())
        
        code = template.render(
            package_name=package_name,
            repo_name=repo_name,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            type_count=len(self.resolved_types)
        )
        
        output_file = sema_path / "codec.py"
        output_file.write_text(code)
        print("  Generated codec.py")
    
    def _generate_init_files(self, package_name: str, sema_path: Path):
        """Generate __init__.py files for all directories."""
        
        # Main sema/__init__.py
        main_init = self._generate_main_init(package_name)
        (sema_path / "__init__.py").write_text(main_init)
        
        # types/__init__.py
        types_init = self._generate_types_init(package_name)
        (sema_path / "types" / "__init__.py").write_text(types_init)
        
        # enums/__init__.py
        enums_init = self._generate_enums_init(package_name)
        (sema_path / "enums" / "__init__.py").write_text(enums_init)
        
        # old_versions/__init__.py (if it exists)
        old_versions_dir = sema_path / "types" / "old_versions"
        if old_versions_dir.exists():
            old_versions_init = '"""Old versions for migration."""\n\n__all__ = []\n'
            (old_versions_dir / "__init__.py").write_text(old_versions_init)
        
        print("  Generated __init__.py files")
    
    def _generate_main_init(self, package_name: str) -> str:
        """Generate the main sema/__init__.py file."""
        # Convert type names to class names
        type_classes = []
        for type_name in sorted(self.resolved_types):
            # e.g., "power.watts" -> "PowerWatts"
            class_name = ''.join(word.capitalize() for word in type_name.split('.'))
            type_classes.append((type_name, class_name))
        
        # Convert enum names to class names  
        enum_classes = []
        for enum_name in sorted(self.resolved_enums):
            # e.g., "actor.class" -> "ActorClass"
            class_name = ''.join(word.capitalize() for word in enum_name.split('.'))
            enum_classes.append((enum_name, class_name))
        
        lines = ['"""sema (Application Shared Language) for this repository."""\n']
        lines.append(f"from {package_name}.sema.codec import semaType, semaCodec, semaError, get_current_types\n")
        
        if type_classes:
            lines.append("\n# Types")
            for type_name, class_name in type_classes:
                module_name = type_name.replace(".", "_")
                lines.append(f"from {package_name}.sema.types.{module_name} import {class_name}")
        
        if enum_classes:
            lines.append("\n# Enums")
            for enum_name, class_name in enum_classes:
                module_name = enum_name.replace(".", "_")
                lines.append(f"from {package_name}.sema.enums.{module_name} import {class_name}")
        
        lines.append("\n__all__ = [")
        lines.append('    # Core')
        lines.append('    "semaType",')
        lines.append('    "semaCodec",')
        lines.append('    "semaError",')
        lines.append('    "get_current_types",')
        
        if type_classes:
            lines.append('    # Types')
            for _, class_name in type_classes:
                lines.append(f'    "{class_name}",')
        
        if enum_classes:
            lines.append('    # Enums')
            for _, class_name in enum_classes:
                lines.append(f'    "{class_name}",')
        
        lines.append("]\n")
        
        return '\n'.join(lines)
    
    def _generate_types_init(self, package_name: str) -> str:
        """Generate types/__init__.py file."""
        lines = ['"""sema Types for this repository."""\n']
        
        type_classes = []
        for type_name in sorted(self.resolved_types):
            class_name = ''.join(word.capitalize() for word in type_name.split('.'))
            module_name = type_name.replace(".", "_")
            lines.append(f"from {package_name}.sema.types.{module_name} import {class_name}")
            type_classes.append(class_name)
        
        lines.append("\n__all__ = [")
        for class_name in type_classes:
            lines.append(f'    "{class_name}",')
        lines.append("]\n")
        
        return '\n'.join(lines)
    
    def _generate_enums_init(self, package_name: str) -> str:
        """Generate enums/__init__.py file."""
        lines = ['"""sema Enums for this repository."""\n']
        
        enum_classes = []
        for enum_name in sorted(self.resolved_enums):
            class_name = ''.join(word.capitalize() for word in enum_name.split('.'))
            module_name = enum_name.replace(".", "_")
            lines.append(f"from {package_name}.sema.enums.{module_name} import {class_name}")
            enum_classes.append(class_name)
        
        lines.append("\n__all__ = [")
        for class_name in enum_classes:
            lines.append(f'    "{class_name}",')
        lines.append("]\n")
        
        return '\n'.join(lines)
    
    def _generate_tests(self, package_name: str, tests_dir: Path):
        """Generate basic test file."""
        test_content = f'''"""Basic tests to verify sema codec functionality."""

import pytest
from {package_name}.sema import semaCodec, semaType

def test_codec_initialization():
    """Test that codec initializes with discovered types."""
    codec = semaCodec()
    assert len(codec.registry) > 0

def test_round_trip():
    """Test encoding and decoding works."""
    codec = semaCodec()
    
    # This would need to be customized based on selected types
    # For now, just verify the codec exists
    assert codec is not None
'''
        (tests_dir / "test_codec.py").write_text(test_content)
        print("  Generated test file")
    
    def _generate_readme(self, repo_name: str, sema_path: Path):
        """Generate a README for the sema directory."""
        readme_content = f"""# sema for {repo_name}

This directory contains the sema (Application Shared Language) types and codec for {repo_name}.

## Generated

- Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Types included: {len(self.resolved_types)}
- Enums included: {len(self.resolved_enums)}

## Structure

- `codec.py` - Serialization/deserialization codec
- `property_format.py` - Field validators
- `types/` - Message type definitions
- `enums/` - Enumeration definitions
- `tests/` - Basic functionality tests

## Usage

```python
from {repo_name.replace('-', '_')}.sema import semaCodec

codec = semaCodec()
# Use codec.from_dict() and codec.to_bytes() for serialization
```

## Source

Generated from the GridWorks sema Registry: https://github.com/thegridelectric/gridworks-sema
"""
        (sema_path / "README.md").write_text(readme_content)
        print("  Generated README.md")


# Example usage
if __name__ == "__main__":
    builder = SeedBuilder()
    
    output = Path("./test_output")
    output.mkdir(exist_ok=True)
    
    builder.generate_seed(
        selected_types=["power.watts", "channel.readings"],
        selected_enums=["actor.class"],
        package_name="gbo",
        repo_name="gridworks-backoffice",
        output_path=output
    )
    
    print(f"\nGenerated sema directory at: {output / 'sema'}")

