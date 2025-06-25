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
    
    html_content += """            </tbody>
        </table>
    </div>

    <script>
        function updateSelection() {
            const stableCheckboxes = document.querySelectorAll('.stable-checkbox');
            const selectedCount = document.querySelectorAll('.stable-checkbox:checked').length;
            const totalStableCount = stableCheckboxes.length;
            const downloadBtn = document.getElementById('download-btn');
            
            // Enable/disable download button based on selection
            downloadBtn.disabled = selectedCount === 0;
            
            document.getElementById('selected-count').textContent = selectedCount;
            
            // Update row styling
            stableCheckboxes.forEach(checkbox => {
                const row = checkbox.closest('tr');
                if (checkbox.checked) {
                    row.classList.add('selected');
                } else {
                    row.classList.remove('selected');
                }
            });
            
            // Update select-all checkbox
            const selectAllCheckbox = document.getElementById('select-all');
            if (selectedCount === 0) {
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = false;
            } else if (selectedCount === totalStableCount) {
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = true;
            } else {
                selectAllCheckbox.indeterminate = true;
            }
        }
        
        function toggleAllStable(checkbox) {
            const stableCheckboxes = document.querySelectorAll('.stable-checkbox');
            stableCheckboxes.forEach(rowCheckbox => {
                rowCheckbox.checked = checkbox.checked;
            });
            updateSelection();
        }
        
        function selectAllStable() {
            const stableCheckboxes = document.querySelectorAll('.stable-checkbox');
            stableCheckboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
            updateSelection();
        }
        
        function deselectAll() {
            const allCheckboxes = document.querySelectorAll('.row-checkbox');
            allCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            updateSelection();
        }
        
        function showSelected() {
            const selectedCheckboxes = document.querySelectorAll('.stable-checkbox:checked');
            const selectedTypes = Array.from(selectedCheckboxes).map(cb => cb.dataset.type);
            
            if (selectedTypes.length === 0) {
                alert('No stable types selected');
                return;
            }
            
            const message = 'Selected stable types:\\n' + selectedTypes.join('\\n');
            alert(message);
        }
        
        async function downloadZip() {
            const downloadBtn = document.getElementById('download-btn');
            if (downloadBtn.disabled) {
                return;
            }
            
            const selectedCheckboxes = document.querySelectorAll('.stable-checkbox:checked');
            const selectedTypes = Array.from(selectedCheckboxes).map(cb => cb.dataset.type);
            
            if (selectedTypes.length === 0) {
                alert('No stable types selected. Please select at least one type to download.');
                return;
            }
            
            try {
                const zip = new JSZip();
                
                // Create the content for the text file
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const content = `Selected GridWorks ASL Types
Generated on: ${new Date().toLocaleString()}
Total selected: ${selectedTypes.length}

Types:
${selectedTypes.join('\\n')}`;
                
                // Add the text file to the zip
                zip.file('selected_types.txt', content);
                
                // Generate and download the zip file
                const blob = await zip.generateAsync({type: 'blob'});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `gridworks-selected-types-${timestamp}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                console.log(`Downloaded zip with ${selectedTypes.length} selected types`);
            } catch (error) {
                console.error('Error creating zip file:', error);
                alert('Error creating zip file. Please try again.');
            }
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            updateSelection();
        });
    </script>
</body>
</html>"""
    
    return html_content

def main():
    """Main function to generate and save the HTML file"""
    html_content = generate_html()
    
    # Write to file
    output_file = "types_table.html"
    with open(output_file, 'w') as file:
        file.write(html_content)
    
    print(f"Generated {output_file} successfully!")
    print(f"Open {output_file} in your web browser to view the types table.")

if __name__ == "__main__":
    main() 