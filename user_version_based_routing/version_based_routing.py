# Define valid versions and modules
valid_versions = {'2.2.2.3', '2.2.3.3', '2.3.3.0', '2.3.5.3', '2.3.7.6'}

# Define functions for different versions and families using dictionaries
functions_v2_3_5_3 = {
    'get_permissions': 'get_permissions_api',
    'get_roles': 'get_roles_api',
    'get_users': 'get_users_api',
    'add_user': 'add_user_api',
    'update_user': 'update_user_api',
    'get_external_authentication_servers': 'get_external_authentication_servers_api'
}

functions_v2_3_7_6 = {
    'add_role': 'add_role_ap_i',
    'update_role': 'update_role_ap_i',
    'get_permissions': 'get_permissions_ap_i',
    'delete_role': 'delete_role_ap_i',
    'get_roles': 'get_roles_ap_i',
    'get_users': 'get_users_ap_i',
    'add_user': 'add_user_ap_i',
    'update_user': 'update_user_ap_i',
    'delete_user': 'delete_user_ap_i',
    'get_external_authentication_setting': 'get_external_authentication_setting_ap_i',
    'manage_external_authentication_setting': 'manage_external_authentication_setting_ap_i',
    'get_external_authentication_servers': 'get_external_authentication_servers_ap_i',
    'add_and_update_aa_attribute': 'add_and_update_a_a_attribute_ap_i',
    'delete_aa_attribute': 'delete_a_a_attribute_ap_i',
    'get_aa_attribute': 'get_a_a_attribute_ap_i'
}

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


def try_import_module(version, family):
    if version in modules:
        module_dict = modules[version]
        if family in module_dict:
            return module_dict[family]
        else:
            raise ImportError(f"Family '{family}' not found in version '{version}'.")
    else:
        raise ImportError(f"Version '{version}' not found.")


def call_function(version, family, function_key):
    if validate_version(version):
        try:
            methods_dict = try_import_module(version, family)
            if function_key in methods_dict:
                return methods_dict[function_key]
            else:
                print(f"No function found '{function_key}' in version '{version}'.")
                return None
        except ImportError as e:
            print(f"ImportError: {e}")
            return None