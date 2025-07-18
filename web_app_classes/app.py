import os
import sys
import inspect
import importlib.util
from flask import Flask, render_template, request, jsonify
import pandas as pd
import traceback
from pathlib import Path

app = Flask(__name__)

class EndpointManager:
    """
    Class responsible for endpoint management - loading .py files,
    discovering classes and methods, and executing selected methods.
    """
    
    def __init__(self, endpoint_folder="endpoint_files"):
        """
        Initialize the endpoint manager.
        
        Args:
            endpoint_folder (str): Path to the folder with endpoint files
        """
        self.endpoint_folder = endpoint_folder
        self.loaded_modules = {}
        self.available_methods = {}
        self._discover_endpoints()
    
    def _discover_endpoints(self):
        """
        Discovers all .py files in the endpoints folder and extracts
        classes and methods from them. This method is called during initialization.
        """
        if not os.path.exists(self.endpoint_folder):
            print(f"Folder {self.endpoint_folder} does not exist. Creating it.")
            os.makedirs(self.endpoint_folder)
            return
        
        # Iterate through all .py files in the folder
        for filename in os.listdir(self.endpoint_folder):
            if filename.endswith('.py') and not filename.startswith('__'):
                self._load_module(filename)
    
    def _load_module(self, filename):
        """
        Loads a single Python module and extracts classes and methods from it.
        
        Args:
            filename (str): Name of the file to load
        """
        module_name = filename[:-3]  # Remove .py extension
        file_path = os.path.join(self.endpoint_folder, filename)
        
        try:
            # Dynamic module importing
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self.loaded_modules[module_name] = module
            
            # Find all classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if the class is defined in this module (not imported)
                if obj.__module__ == module_name:
                    self._extract_methods_from_class(module_name, name, obj)
                    
        except Exception as e:
            print(f"Error loading module {filename}: {e}")
            traceback.print_exc()
    
    def _extract_methods_from_class(self, module_name, class_name, class_obj):
        """
        Extracts methods from a class, skipping private and special methods.
        
        Args:
            module_name (str): Module name
            class_name (str): Class name
            class_obj: Class object
        """
        for method_name, method_obj in inspect.getmembers(class_obj, inspect.isfunction):
            # Skip private and special methods
            if not method_name.startswith('_'):
                # Check if method returns DataFrame (optional)
                method_key = f"{module_name}.{class_name}.{method_name}"
                self.available_methods[method_key] = {
                    'module': module_name,
                    'class': class_name,
                    'method': method_name,
                    'class_obj': class_obj,
                    'method_obj': method_obj
                }
        
    
    def get_available_methods(self):
        """
        Returns a list of available methods in a format suitable for the interface.
        
        Returns:
            list: List of dictionaries with method information
        """
        methods_list = []
        for method_key, method_info in self.available_methods.items():
            methods_list.append({
                'key': method_key,
                'display_name': f"{method_info['module']} → {method_info['class']} → {method_info['method']}"
            })
        return sorted(methods_list, key=lambda x: x['display_name'])
    
    def execute_method(self, method_key):
        """
        Executes the selected method and returns the result.
        
        Args:
            method_key (str): Key identifying the method to execute
            
        Returns:
            dict: Method execution result or error information
        """
        if method_key not in self.available_methods:
            return {
                'success': False,
                'error': f'Method {method_key} not found'
            }
        
        method_info = self.available_methods[method_key]
        
        try:
            # Create class instance
            class_instance = method_info['class_obj']()
            
            # Execute method
            if method_info.get('is_static', False):
                # Static method
                result = getattr(method_info['class_obj'], method_info['method'])()
            else:
                # Instance method
                result = getattr(class_instance, method_info['method'])()
            
            # Check if result is DataFrame
            if isinstance(result, pd.DataFrame):
                return {
                    'success': True,
                    'data_type': 'dataframe',
                    'data': result.to_dict('records'),  # Convert DataFrame to dictionary
                    'columns': result.columns.tolist(),
                    'shape': result.shape
                }
            else:
                return {
                    'success': True,
                    'data_type': 'other',
                    'data': str(result)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error executing method: {str(e)}',
                'traceback': traceback.format_exc()
            }

# Global endpoint manager instance
endpoint_manager = EndpointManager()

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/api/methods')
def get_methods():
    """API endpoint returning list of available methods"""
    return jsonify(endpoint_manager.get_available_methods())

@app.route('/api/execute', methods=['POST'])
def execute_method():
    """API endpoint for executing selected methods"""
    data = request.get_json()
    method_key = data.get('method_key')
    
    if not method_key:
        return jsonify({
            'success': False,
            'error': 'No method key provided'
        }), 400
    
    result = endpoint_manager.execute_method(method_key)
    return jsonify(result)

@app.route('/api/reload')
def reload_endpoints():
    """API endpoint for reloading endpoints"""
    global endpoint_manager
    endpoint_manager = EndpointManager()
    return jsonify({
        'success': True,
        'message': 'Endpoints have been reloaded',
        'methods_count': len(endpoint_manager.available_methods)
    })

if __name__ == '__main__':
    # Create templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print(f"Found {len(endpoint_manager.available_methods)} methods in endpoints")
    print("Available methods:")
    for method in endpoint_manager.get_available_methods():
        print(f"  - {method['display_name']}")
    
    app.run(debug=True, host='0.0.0.0', port=6789)