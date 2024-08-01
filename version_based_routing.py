import importlib
import inspect
import pkgutil
import difflib


def list_defined_methods(cls_obj):
    """Lists all methods of a given class."""
    methods = []
    
    # Iterate over all members of the class
    for name, obj in inspect.getmembers(cls_obj, inspect.isfunction):
        print(name, obj)
        # Check if the function is defined in the class's module
        if obj.__module__ == cls_obj.__module__:
            # If it is, add the method name to the methods list
            methods.append(name)
    
    return methods

def format_version(version):
    """Converts version from '2.3.5.3' to 'v2_3_5_3'."""
    return 'v{}'.format(version.replace(".", "_"))

def validate_version(version):
    """Validates if the provided version is among the known versions."""
    valid_versions = {'2.2.2.3', '2.2.3.3', '2.3.3.0', '2.3.5.3', '2.3.7.6'}
    if version not in valid_versions:
        print("'Unknown API version, known versions are: '2.2.2.3, 2.2.3.3, 2.3.3.0, 2.3.5.3, and 2.3.7.6'")

def find_closest_family(module, family):
    """Finds the closest matching family name from available modules."""
    available_families = get_available_families(module)
    closest_matches = difflib.get_close_matches(family, available_families)
    if closest_matches:
        return closest_matches[0]

def get_available_families(module):
    """Gets the names of all modules available in the given module's directory."""
    available_families = []
    for _, name, _ in pkgutil.iter_modules(module.__path__):
        available_families.append(name)
    return available_families

def try_import_module(version, family):
    """Attempts to import a module dynamically based on the family name and version."""
    formatted_version = format_version(version)
    module_path = "dnacentersdk.api.{}".format(formatted_version)

    try:
        base_module = importlib.import_module(module_path)
        family_name = find_closest_family(base_module, family)
        if family_name:
            submodule_path = "{}.{}".format(module_path, family_name)
            return importlib.import_module(submodule_path)
        else:
            raise ImportError("Module for family '{}' not found in version '{}'.".format(family, version))
    except ImportError as e:
        raise ImportError("Module for version '{}' not found: {}.".format(version, e))

def filter_methods_by_hint(methods, hint):
    """Filters methods to include only those containing the hint in their name."""
    matching_methods = []
    
    # Iterate over each method name in the methods list
    for method in methods:
        # Check if the hint is a substring of the method name
        if hint in method:
            # If it is, add the method name to the matching_methods list
            matching_methods.append(method)
    
    return matching_methods

def get_class_names(module):
    """Gets the names of all classes defined in the given module."""
    class_names = []
    
    # Iterate over all members of the module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        # Check if the class is defined in the given module
        if obj.__module__ == module.__name__:
            class_names.append(name)
    
    return class_names

def call_function(version, family, hint):
    """Checks if a specific function exists in the first class found in the module."""
    try:
        validate_version(version)
        module = try_import_module(version, family)
        print("Successfully imported {}".format(module.__name__))

        # Use the expanded function to get class names
        class_names = get_class_names(module)
        if class_names:
            family_class = getattr(module, class_names[0])
            methods = list_defined_methods(family_class)#
            matching_methods = filter_methods_by_hint(methods, hint)

            if matching_methods:
                print("Yes, function '{}' is available.".format(matching_methods[0]))
                return matching_methods[0]  # Return the matched function name
            else:
                print("No matching function for hint '{}' in version '{}'.".format(hint, version))
                return None
        else:
            print("No classes found in module '{}'.".format(module.__name__))
            return None
    except ImportError as e:
        print("ImportError: {}.".format(e))
        return None



function_called = call_function('2.3.5.3', 'user_and role', 'add_user')
print(function_called)  # Expected output: add_user_ap_i