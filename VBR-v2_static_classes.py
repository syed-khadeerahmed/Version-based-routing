import inspect

# Define valid versions and modules
valid_versions = {'2.2.2.3', '2.2.3.3', '2.3.3.0', '2.3.5.3', '2.3.7.6'}
modules = {
    'v2_3_5_3': {
        'user_and_roles': 'UserAndRoles_v2_3_5_3'
    },
    'v2_3_7_6': {
        'user_and_roles': 'UserAndRoles_v2_3_7_6'
    }
}

# Example classes to simulate module classes
class UserAndRoles_v2_3_5_3:
    def get_permissions_api(self): pass
    def get_roles_api(self): pass
    def get_users_api(self): pass
    def add_user_api(self): pass
    def update_user_api(self): pass
    def get_external_authentication_servers_api(self): pass

class UserAndRoles_v2_3_7_6:
    def __init__(self, session, object_factory, request_validator): pass
    def add_role_ap_i(self): pass
    def update_role_ap_i(self): pass
    def get_permissions_ap_i(self): pass
    def delete_role_ap_i(self): pass
    def get_roles_ap_i(self): pass
    def get_users_ap_i(self): pass
    def add_user_ap_i(self): pass
    def update_user_ap_i(self): pass
    def delete_user_ap_i(self): pass
    def get_external_authentication_setting_ap_i(self): pass
    def manage_external_authentication_setting_ap_i(self): pass
    def get_external_authentication_servers_ap_i(self): pass
    def add_and_update_a_a_attribute_ap_i(self): pass
    def delete_a_a_attribute_ap_i(self): pass
    def get_a_a_attribute_ap_i(self): pass

# Register example classes in globals() dictionary
globals()['UserAndRoles_v2_3_5_3'] = UserAndRoles_v2_3_5_3
globals()['UserAndRoles_v2_3_7_6'] = UserAndRoles_v2_3_7_6

# Function to list all methods of a given class
def list_defined_methods(cls_obj):
    methods = []
    for name, obj in inspect.getmembers(cls_obj, inspect.isfunction):
        if obj.__module__ == cls_obj.__module__:
            methods.append(name)
    return methods

# Function to convert version from '2.3.5.3' to 'v2_3_5_3'
def format_version(version):
    return 'v{}'.format(version.replace(".", "_"))

# Function to validate if the provided version is among the known versions
def validate_version(version):
    if version not in valid_versions:
        print(f"Unknown API version, known versions are: {', '.join(valid_versions)}")
        return False
    return True

# Function to find the closest matching family name from available modules
def find_closest_family(module_dict, family):
    return module_dict.get(family, None)

# Function to attempt to import a module dynamically based on the family name and version
def try_import_module(version, family):
    formatted_version = format_version(version)
    if formatted_version in modules:
        module_dict = modules[formatted_version]
        family_name = find_closest_family(module_dict, family)
        if family_name:
            return globals()[family_name]
        else:
            raise ImportError(f"Module for family '{family}' not found in version '{version}'.")
    else:
        raise ImportError(f"Module for version '{version}' not found.")

# Function to filter methods to include only those containing the hint in their name
def filter_methods_by_hint(methods, hint):
    return [method for method in methods if hint in method]

# Function to check if a specific function exists in the first class found in the module
def call_function(version, family, hint):
    if validate_version(version):
        try:
            cls_obj = try_import_module(version, family)
            methods = list_defined_methods(cls_obj)
            matching_methods = filter_methods_by_hint(methods, hint)

            if matching_methods:
                return matching_methods[0]  # Return the matched function name
            else:
                print(f"No matching function for hint '{hint}' in version '{version}'.")
                return None
        except ImportError as e:
            print(f"ImportError: {e}")
            return None

# Example usage
function_called = call_function('2.3.7.6', 'user_and_roles', 'add_user')
print(function_called)
