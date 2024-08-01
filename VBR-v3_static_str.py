# Define valid versions and modules
valid_versions = {'2.2.2.3', '2.2.3.3', '2.3.3.0', '2.3.5.3', '2.3.7.6'}

# Define functions for different versions and families using dictionaries
functions_v2_3_5_3 = [
    'get_permissions_api',
    'get_roles_api',
    'get_users_api',
    'add_user_api',
    'update_user_api',
    'get_external_authentication_servers_api'
]

functions_v2_3_7_6 = [
    'add_role_ap_i',
    'update_role_ap_i',
    'get_permissions_ap_i',
    'delete_role_ap_i',
    'get_roles_ap_i',
    'get_users_ap_i',
    'add_user_ap_i',
    'update_user_ap_i',
    'delete_user_ap_i',
    'get_external_authentication_setting_ap_i',
    'manage_external_authentication_setting_ap_i',
    'get_external_authentication_servers_ap_i',
    'add_and_update_a_a_attribute_ap_i',
    'delete_a_a_attribute_ap_i',
    'get_a_a_attribute_ap_i'
]

modules = {
    '2.3.5.3': {
        'user_and_roles': functions_v2_3_5_3
    },
    '2.3.7.6': {
        'user_and_roles': functions_v2_3_7_6
    }
}

# Function to validate if the provided version is among the known versions
def validate_version(version):
    if version not in valid_versions:
        print(f"Unknown API version, known versions are: {', '.join(valid_versions)}")
        return False
    return True

# Function to attempt to import a module dynamically based on the family name and version
def try_import_module(version, family):
    if version in modules:
        module_dict = modules[version]
        if family in module_dict:
            return module_dict[family]  # Return the dictionary of functions
        else:
            raise ImportError(f"Family '{family}' not found in version '{version}'.")
    else:
        raise ImportError(f"Version '{version}' not found.")

# Function to filter methods to include only those containing the hint in their name
def filter_methods_by_hint(methods_dict, hint):
    # Initialize an empty list to hold methods that match the hint
    matching_methods = []

    # Iterate over each method name in the methods dictionary
    for method in methods_dict:
        # Check if the hint is present in the method name
        if hint in method:
            # If it is, add the method name to the list of matching methods
            matching_methods.append(method)

    # Return the list of methods that matched the hint
    return matching_methods

# Function to check if a specific function exists in the methods dictionary
def call_function(version, family, hint):
    if validate_version(version):
        try:
            methods_dict = try_import_module(version, family)
            methods = filter_methods_by_hint(methods_dict, hint)

            if methods:
                return methods[0]  # Return the matched function name
            else:
                print(f"No matching function for hint '{hint}' in version '{version}'.")
                return None
        except ImportError as e:
            print(f"ImportError: {e}")
            return None

# Example usage
function_called = call_function('2.3.5.3', 'user_and_roles', 'get_users')
print(function_called)  # Expected output: add_user_ap_i
