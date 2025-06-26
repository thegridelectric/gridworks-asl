#!/usr/bin/env python3
"""
Script to generate an HTML table of types from registry.yaml
"""

import yaml
import os

def load_registry():
    """Load the registry.yaml file"""
    registry_path = "type_definitions/registry.yaml"
    with open(registry_path, 'r') as file:
        return yaml.safe_load(file)

def type_name_to_python_file(type_name):
    """Convert type name to Python file name"""
    # Convert dots to underscores and add .py extension
    return type_name.replace('.', '_') + '.py'

def get_named_type_content(type_name):
    """Get the content of a named type Python file"""
    python_file = type_name_to_python_file(type_name)
    file_path = f"src/gwasl/named_types/{python_file}"
    
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"# Type {type_name} - Python file not found: {python_file}"

def get_file_content(file_path):
    """Get the content of a file"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"# File not found: {file_path}"

def find_dependencies(python_content):
    """Find all gwasl imports in Python content"""
    import re
    dependencies = set()
    
    # Find all gwasl imports
    gwasl_imports = re.findall(r'from gwasl\.([^\s]+)', python_content)
    for import_path in gwasl_imports:
        dependencies.add(import_path)
    
    return dependencies

def get_all_dependencies(selected_types):
    """Get all dependencies for selected types"""
    all_dependencies = set()
    
    for type_name in selected_types:
        # Get the named type content
        python_file = type_name_to_python_file(type_name)
        file_path = f"src/gwasl/named_types/{python_file}"
        
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                dependencies = find_dependencies(content)
                all_dependencies.update(dependencies)
        except FileNotFoundError:
            continue
    
    return all_dependencies

def get_dependency_files(dependencies):
    """Get all files needed for dependencies"""
    files = {}
    
    for dep in dependencies:
        if dep == 'property_format':
            # Single file
            files[f'gwasl/{dep}.py'] = get_file_content(f'src/gwasl/{dep}.py')
        elif dep.startswith('enums.'):
            # Enum file
            enum_name = dep.split('.')[1]
            files[f'gwasl/enums/{enum_name}.py'] = get_file_content(f'src/gwasl/enums/{enum_name}.py')
            # Also include __init__.py
            files[f'gwasl/enums/__init__.py'] = get_file_content(f'src/gwasl/enums/__init__.py')
        elif dep.startswith('type_helpers.'):
            # Type helper file
            helper_name = dep.split('.')[1]
            files[f'gwasl/type_helpers/{helper_name}.py'] = get_file_content(f'src/gwasl/type_helpers/{helper_name}.py')
            # Also include __init__.py
            files[f'gwasl/type_helpers/__init__.py'] = get_file_content(f'src/gwasl/type_helpers/__init__.py')
        elif dep.startswith('named_types.'):
            # Another named type file
            type_name = dep.split('.')[1]
            files[f'gwasl/named_types/{type_name}.py'] = get_file_content(f'src/gwasl/named_types/{type_name}.py')
    
    return files

def generate_html():
    """Generate HTML table of types"""
    registry = load_registry()
    
    # Extract types
    types = registry.get('types', {})
    type_names = list(types.keys())
    
    # Sort types alphabetically
    type_names.sort()
    
    # Count stable types
    stable_types = [name for name in type_names if types[name].get('stable', False)]
    
    # Get Python file contents for all types
    python_files = {}
    for type_name in type_names:
        python_files[type_name] = get_named_type_content(type_name)
    
    # Get all possible dependencies for all types
    all_dependencies = get_all_dependencies(type_names)
    dependency_files = get_dependency_files(all_dependencies)
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GridWorks ASL Types</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        .stats {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .controls {{
            display: flex;
            justify-content: flex-end;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .selection-info {{
            color: #666;
            font-size: 0.9em;
        }}
        .button {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        .button:hover {{
            background-color: #0056b3;
        }}
        .button.secondary {{
            background-color: #6c757d;
        }}
        .button.secondary:hover {{
            background-color: #545b62;
        }}
        .button.success {{
            background-color: #28a745;
        }}
        .button.success:hover {{
            background-color: #1e7e34;
        }}
        .button:disabled {{
            background-color: #6c757d !important;
            cursor: not-allowed;
            opacity: 0.6;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
            position: sticky;
            top: 0;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        tr.selected {{
            background-color: #e3f2fd !important;
        }}
        tr.unstable {{
            opacity: 0.6;
        }}
        .checkbox {{
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        .checkbox:disabled {{
            cursor: not-allowed;
            opacity: 0.5;
        }}
        .type-name {{
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: #007bff;
        }}
        .version {{
            background-color: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
            font-weight: 500;
        }}
        .stable-true {{
            color: #28a745;
            font-weight: 600;
        }}
        .stable-false {{
            color: #dc3545;
            font-weight: 600;
        }}
        .description {{
            color: #6c757d;
            font-size: 0.95em;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 40px;">GridWorks ASL Types</h2>
        
        <table>
            <thead>
                <tr>
                    <th><input type="checkbox" id="select-all" class="checkbox" onchange="toggleAllStable(this)"></th>
                    <th>Type Name</th>
                    <th>Current Version</th>
                    <th>Stable</th>
                    <th>Description</th>
                    <th style="text-align: right;"><button class="button" style="width: 120px;" onclick="downloadZip()" id="download-btn">Download ZIP</button></th>
                </tr>
            </thead>
            <tbody>
"""
    
    for type_name in type_names:
        type_data = types[type_name]
        current_version = type_data.get('current_version', 'N/A')
        stable = type_data.get('stable', False)
        description = type_data.get('description', 'No description available')
        
        stable_class = "stable-true" if stable else "stable-false"
        stable_text = "True" if stable else "False"
        
        # Add row class and checkbox attributes based on stability
        row_class = "unstable" if not stable else ""
        checkbox_disabled = "disabled" if not stable else ""
        checkbox_class = "checkbox row-checkbox" + (" stable-checkbox" if stable else "")
        
        html_content += f"""                <tr class="{row_class}">
                    <td><input type="checkbox" class="{checkbox_class}" data-type="{type_name}" {checkbox_disabled} onchange="updateSelection()"></td>
                    <td><span class="type-name">{type_name}</span></td>
                    <td><span class="version">{current_version}</span></td>
                    <td><span class="{stable_class}">{stable_text}</span></td>
                    <td class="description">{description}</td>
                    <td></td>
                </tr>
"""
    
    # Convert Python files to JavaScript object
    python_files_js = "{\n"
    for type_name, content in python_files.items():
        # Escape the content for JavaScript
        escaped_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        python_files_js += f'    "{type_name}": "{escaped_content}",\n'
    python_files_js = python_files_js.rstrip(',\n') + "\n}"
    
    # Convert dependency files to JavaScript object
    dependency_files_js = "{\n"
    for file_path, content in dependency_files.items():
        # Escape the content for JavaScript
        escaped_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        dependency_files_js += f'    "{file_path}": "{escaped_content}",\n'
    dependency_files_js = dependency_files_js.rstrip(',\n') + "\n}"
    
    html_content += f"""            </tbody>
        </table>
    </div>

    <script>
        // Embedded Python file contents
        const pythonFiles = {python_files_js};
        
        // Embedded dependency file contents
        const dependencyFiles = {dependency_files_js};
        
        function updateSelection() {{
            const stableCheckboxes = document.querySelectorAll('.stable-checkbox');
            const selectedCount = document.querySelectorAll('.stable-checkbox:checked').length;
            const totalStableCount = stableCheckboxes.length;
            const downloadBtn = document.getElementById('download-btn');
            
            // Enable/disable download button based on selection
            downloadBtn.disabled = selectedCount === 0;
            
            document.getElementById('selected-count').textContent = selectedCount;
            
            // Update row styling
            stableCheckboxes.forEach(checkbox => {{
                const row = checkbox.closest('tr');
                if (checkbox.checked) {{
                    row.classList.add('selected');
                }} else {{
                    row.classList.remove('selected');
                }}
            }});
            
            // Update select-all checkbox
            const selectAllCheckbox = document.getElementById('select-all');
            if (selectedCount === 0) {{
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = false;
            }} else if (selectedCount === totalStableCount) {{
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = true;
            }} else {{
                selectAllCheckbox.indeterminate = true;
            }}
        }}
        
        function toggleAllStable(checkbox) {{
            const stableCheckboxes = document.querySelectorAll('.stable-checkbox');
            stableCheckboxes.forEach(rowCheckbox => {{
                rowCheckbox.checked = checkbox.checked;
            }});
            updateSelection();
        }}
        
        function selectAllStable() {{
            const stableCheckboxes = document.querySelectorAll('.stable-checkbox');
            stableCheckboxes.forEach(checkbox => {{
                checkbox.checked = true;
            }});
            updateSelection();
        }}
        
        function deselectAll() {{
            const allCheckboxes = document.querySelectorAll('.row-checkbox');
            allCheckboxes.forEach(checkbox => {{
                checkbox.checked = false;
            }});
            updateSelection();
        }}
        
        function showSelected() {{
            const selectedCheckboxes = document.querySelectorAll('.stable-checkbox:checked');
            const selectedTypes = Array.from(selectedCheckboxes).map(cb => cb.dataset.type);
            
            if (selectedTypes.length === 0) {{
                alert('No stable types selected');
                return;
            }}
            
            const message = 'Selected stable types:\\n' + selectedTypes.join('\\n');
            alert(message);
        }}
        
        function getDependenciesForTypes(selectedTypes) {{
            const dependencies = new Set();
            
            for (const typeName of selectedTypes) {{
                const content = pythonFiles[typeName] || '';
                const gwaslImports = content.match(/from gwasl\\.([^\\s]+)/g) || [];
                
                for (const importStatement of gwaslImports) {{
                    const match = importStatement.match(/from gwasl\\.([^\\s]+)/);
                    if (match) {{
                        dependencies.add(match[1]);
                    }}
                }}
            }}
            
            return Array.from(dependencies);
        }}
        
        async function downloadZip() {{
            const downloadBtn = document.getElementById('download-btn');
            if (downloadBtn.disabled) {{
                return;
            }}
            
            const selectedCheckboxes = document.querySelectorAll('.stable-checkbox:checked');
            const selectedTypes = Array.from(selectedCheckboxes).map(cb => cb.dataset.type);
            
            if (selectedTypes.length === 0) {{
                alert('No stable types selected. Please select at least one type to download.');
                return;
            }}
            
            try {{
                const zip = new JSZip();
                
                // Create gwasl/named_types directory and add Python files
                const gwaslFolder = zip.folder('gwasl');
                const namedTypesFolder = gwaslFolder.folder('named_types');
                
                // For each selected type, add its Python file
                for (const typeName of selectedTypes) {{
                    const pythonFileName = typeName.replace(/\./g, '_') + '.py';
                    
                    // Get the Python file content from the embedded data
                    const fileContent = pythonFiles[typeName] || `# Type ${{typeName}} - Python file not found: ${{pythonFileName}}
# This file should contain the Python implementation for the ${{typeName}} type.
# Please check the src/gwasl/named_types/ directory for the correct implementation.`;
                    
                    namedTypesFolder.file(pythonFileName, fileContent);
                }}
                
                // Get dependencies for selected types
                const dependencies = getDependenciesForTypes(selectedTypes);
                
                // Add dependency files
                for (const dep of dependencies) {{
                    if (dep === 'property_format') {{
                        const content = dependencyFiles['gwasl/property_format.py'] || `# File not found: gwasl/property_format.py`;
                        zip.file('gwasl/property_format.py', content);
                    }} else if (dep.startsWith('enums.')) {{
                        const enumName = dep.split('.')[1];
                        const enumContent = dependencyFiles[`gwasl/enums/${{enumName}}.py`] || `# File not found: gwasl/enums/${{enumName}}.py`;
                        zip.file(`gwasl/enums/${{enumName}}.py`, enumContent);
                        
                        // Also add __init__.py
                        const initContent = dependencyFiles['gwasl/enums/__init__.py'] || `# File not found: gwasl/enums/__init__.py`;
                        zip.file('gwasl/enums/__init__.py', initContent);
                    }} else if (dep.startsWith('type_helpers.')) {{
                        const helperName = dep.split('.')[1];
                        const helperContent = dependencyFiles[`gwasl/type_helpers/${{helperName}}.py`] || `# File not found: gwasl/type_helpers/${{helperName}}.py`;
                        zip.file(`gwasl/type_helpers/${{helperName}}.py`, helperContent);
                        
                        // Also add __init__.py
                        const initContent = dependencyFiles['gwasl/type_helpers/__init__.py'] || `# File not found: gwasl/type_helpers/__init__.py`;
                        zip.file('gwasl/type_helpers/__init__.py', initContent);
                    }} else if (dep.startsWith('named_types.')) {{
                        const typeName = dep.split('.')[1];
                        const typeContent = dependencyFiles[`gwasl/named_types/${{{{typeName}}}}.py`] || `# File not found: gwasl/named_types/${{{{typeName}}}}.py`;
                        namedTypesFolder.file(`${{{{typeName}}}}.py`, typeContent);
                    }}
                }}
                
                // Generate and download the zip file
                const blob = await zip.generateAsync({{type: 'blob'}});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `gridworks-selected-types-${{new Date().toISOString().replace(/[:.]/g, '-')}}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                console.log(`Downloaded zip with ${{selectedTypes.length}} selected types and their dependencies`);
            }} catch (error) {{
                console.error('Error creating zip file:', error);
                alert('Error creating zip file. Please try again.');
            }}
        }}
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {{
            updateSelection();
        }});
    </script>
</body>
</html>"""
    
    return html_content

def main():
    """Main function to generate and save the HTML file"""
    html_content = generate_html()
    
    # Write to file
    output_file = "ui/types_table.html"
    with open(output_file, 'w') as file:
        file.write(html_content)
    
    print(f"Generated {output_file} successfully!")
    print(f"Open {output_file} in your web browser to view the types table.")

if __name__ == "__main__":
    main() 