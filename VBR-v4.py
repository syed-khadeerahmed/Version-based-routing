import importlib
import inspect

def list_defined_methods(cls_obj):
    methods = []
    members = inspect.getmembers(cls_obj, inspect.isfunction)
    for name, obj in members:
        if obj.__module__ == cls_obj.__module__:
            methods.append(name)
    return methods

def call_function(version, family, hint):
    try:
        # Construct module path
        module_path = f"dnacentersdk.api.{version}.{family}"
        print(f"Trying to import: {module_path}")

        # Import module dynamically
        module = importlib.import_module(module_path)
        print(f"Successfully imported {module_path}")

        # Check if the function exists in the UserandRoles class
        user_and_roles_class = getattr(module, 'UserandRoles', None)
        if user_and_roles_class:
            methods = list_defined_methods(user_and_roles_class)
            matching_methods = [m for m in methods if hint in m]
            if matching_methods:
                print(f"Yes, function '{matching_methods[0]}' is available.")
            else:
                print(f"No matching function for hint '{hint}' in version '{version}'.")
        else:
            print("UserandRoles class not found.")
    except ImportError as e:
        print(f"ImportError: {e}")

def inspect_family_file(version, family,class_name):
    module_path = f"dnacentersdk.api.{version}.{family}"
    try:
        module = importlib.import_module(module_path)
        classes = [cls for cls in dir(module) if isinstance(getattr(module, cls), type)]
        
        for cls_name in classes:
            if cls_name == class_name:
                cls_obj = getattr(module, cls_name)
                print(f"Methods in class {cls_name}:")
                methods = list_defined_methods(cls_obj)
                for method in methods:
                    print(f"- {method}")
                    
    except ImportError as e:
        print(f"ImportError: {e}")

# Example usage
inspect_family_file('v2_3_5_3', 'user_and_roles', "UserandRoles")
call_function('v2_3_5_3', 'user_and_roles', 'add_use')
