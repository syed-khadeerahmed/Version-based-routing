import importlib
import inspect

def list_defined_methods(cls_obj):
    methods = []
    members = inspect.getmembers(cls_obj, inspect.isfunction)
    for name, obj in members:
        if obj.__module__ == cls_obj.__module__:
            methods.append(name)
    return methods

# Mapping of versions to function names
function_map = {
    'v2_3_7_6': {'get_role': 'get_roles_ap_i', 'get_users': 'get_users_ap_i'},
    'v2_3_5_3': {'get_role': 'get_roles_api'},
    # Add more versions and functions as needed
}

def call_function(version, family, hint):
    try:
        # Get the function name based on the version and hint
        function_name = function_map.get(version, {}).get(hint)
        
        if not function_name:
            print(f"No matching function for hint '{hint}' in version '{version}'.")
            return

        # Construct module path
        module_path = f"dnacentersdk.api.{version}.{family}"
        print(f"Trying to import: {module_path}")

        # Import module dynamically
        module = importlib.import_module(module_path)
        print(f"Successfully imported {module_path}")

        # Check if the function exists in the UserandRoles class
        user_and_roles_class = getattr(module, 'UserandRoles', None)
        if user_and_roles_class and function_name in list_defined_methods(user_and_roles_class):
            print(f"Yes, {function_name} is available.")
        else:
            print(f"Function {function_name} not found in {family}.")
    except ImportError as e:
        print(f"ImportError: {e}")

def inspect_family_file(version, family):
    module_path = f"dnacentersdk.api.{version}.{family}"
    try:
        module = importlib.import_module(module_path)
        classes = [cls for cls in dir(module) if isinstance(getattr(module, cls), type)]
        
        for cls_name in classes:
            if cls_name == 'UserandRoles':
                cls_obj = getattr(module, cls_name)
                print(f"Methods in class {cls_name}:")
                methods = list_defined_methods(cls_obj)
                for method in methods:
                    print(f"- {method}")
                    
    except ImportError as e:
        print(f"ImportError: {e}")

# Example usage
call_function('v2_3_7_6', 'user_and_roles', 'add_role')
inspect_family_file('v2_3_7_6', 'user_and_roles')
