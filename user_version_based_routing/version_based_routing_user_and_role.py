#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
__author__ = ("Ajith Andrew J, Syed khadeer Ahmed")

import importlib
import inspect
import pkgutil
import difflib

import re, time
from ansible_collections.cisco.dnac.plugins.module_utils.dnac import (
    DnacBase,
    validate_list_of_dicts,
    validate_str,
    validate_list
)
from ansible.module_utils.basic import AnsibleModule


class User(DnacBase):
    """Class containing member attributes for user workflow_manager module"""

    def __init__(self, module):
        super().__init__(module)
        self.result["response"] = []
        self.supported_states = ["merged", "deleted"]
        self.payload = module.params
        self.log(self.payload)
        self.keymap = {}


    # Below function used to validate input over the ansible validation
    def validate_input_yml(self):

        self.log('Validating the Playbook Yaml File..', "INFO")

        if not self.config:
            self.status = "success"
            self.msg = "Configuration is not available in the playbook for validation"
            self.log(self.msg, "ERROR")
            return self
        
        userlist = self.payload.get("config")
        userlist = self.camel_to_snake_case(userlist)
        user_details = dict(first_name = dict(required = False, type = 'str'),
                    last_name = dict(required = False, type = 'str'),
                    email = dict(required = False, type = 'str'),
                    password = dict(required = False, type = 'str'),
                    username = dict(required = True, type = 'str'),
                    role_list = dict(required = False, type = 'list', elements='str'),
                    )
        valid_param, invalid_param = validate_list_of_dicts(userlist, user_details)

        if invalid_param:
            self.msg("Invalid param found in playbook: '{0}' "
                            .format(", ".join(invalid_param)))
            self.log(self.msg, "ERROR")
            self.status = "failed"
            return self

        self.validated_config = valid_param
        self.msg = "Successfully validated playbook config params:{0}".format(str(valid_param[0]))
        self.log(self.msg, "INFO")
        self.status = "success"
        return self

    def valid_user_config_parameters(self, user_config):

        errormsg = []

        if user_config.get("first_name"):
            param_spec = dict(type = "str", length_max = 255)
            validate_str(user_config["first_name"], param_spec, "first_name",
                            errormsg)

        if user_config.get("last_name"):
            param_spec = dict(type = "str", length_max = 255)
            validate_str(user_config["last_name"], param_spec, "last_name",
                            errormsg)

        if user_config.get("email"):
            email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
            if not email_regex.match(user_config["email"]):
                errormsg.append("email: Invalid email format for email: '{0}'".format(user_config["email"]))

        if user_config.get("password"):
            password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
            if not password_regex.match(user_config["password"]):
                errormsg.append("password: Password does not meet complexity requirements for password: '{0}'".format(user_config["password"]))

        if user_config.get("username"):
            param_spec = dict(type = "str", length_max = 255)
            validate_str(user_config["username"], param_spec, "username",
                            errormsg)

        if user_config.get("role_list"):
            param_spec = dict(type = "list", elements="str")
            validate_list(user_config["role_list"], param_spec, "role_list",
                            errormsg)

        if len(errormsg) > 0:
            self.msg = "Invalid parameters in playbook config: '{0}' "\
                     .format(str("\n".join(errormsg)))
            self.log(self.msg, "ERROR")
            self.status = "failed"
            return self

        self.msg = "Successfully validated config params:{0}".format(str(user_config))
        self.log(self.msg, "INFO")
        self.status = "success"
        return self

    def get_want(self, user_config):

        
        for key,value in user_config.items():
            self.want[key] = value
        self.log("Desired State (want): {0}".format(str(self.want)), "INFO")
        return self

    def get_have(self, input_config):

        user_exists = False
        role_exists = False
        current_user_config = None
        current_role_config = None
        # check if given user config exists, if exists store current user info
        (user_exists, role_exists, current_user_config, current_role_config) = self.get_current_config(input_config)

        if not user_exists:
            self.log("The provided user '{0}' is not present in the Cisco Catalyst Center. User_exists = {1}".format(str(input_config.get("username")), str(user_exists)), "INFO")
        self.log("Current user config details (have): {0}".format(str(current_user_config)), "DEBUG")

        if user_exists:
            self.have["username"] = current_user_config.get("username")
            self.have["user_exists"] = user_exists
            self.have["current_user_config"] = current_user_config
            self.have["current_role_config"] = current_role_config
        else:
            self.have["user_exists"] = user_exists
        if role_exists:
            self.have["current_role_config"] = current_role_config

        self.log("Current State (have): {0}".format(str(self.have)), "INFO")
        return self

    def get_diff_merged(self, config):

        config_updated = False
        config_created = False
        task_response = None
        # check if the given user config exists and/or needs to be updated/created.

        if self.have.get("user_exists"):
            #update the user
            self.valid_user_config_parameters(config).check_return_status()
            (consolidated_data, update_required_param) = self.user_requires_update(self.have["current_user_config"], self.have["current_role_config"])

            if not consolidated_data:
                # user does not need update
                self.msg = "user does not need any update"
                self.log(self.msg, "INFO")
                responses = {}
                responses["users_updates"] = {"response": config}
                self.result['msg'] = self.msg
                self.result["response"].append(responses)
                self.result["skipped"] = True
                return self
            user_in_have = self.have["current_user_config"]
            update_param = update_required_param
            update_param["user_id"] = user_in_have.get("user_id")
            self.log('Final user data to update {}'.format(str(update_param)),
                  "INFO")
            task_response = self.update_user(update_param)
            task_res = str(task_response)
            self.log('Task respoonse {}'.format(str(task_res)),"INFO")
            config_updated = True

        else:
            # Create the user
            self.valid_user_config_parameters(config).check_return_status()
            self.log('Creating user with config {}'.format(str(config)), "INFO")
            user_params = self.want

            try:
                user_details = {}

                for key, value in user_params.items():
                    if value is not None:
                        if key != "role_list":
                            user_details[key] = value
                        else:
                            current_role= self.have.get("current_role_config")
                            user_details[key] = []
                            for role_name in user_params['role_list']:
                                role_id = current_role.get(role_name)
                                if role_id:
                                    user_details[key].append(role_id)
                                else:
                                    self.log("Role ID for {0} not found in current_role_config".format(str(role_name)))

                user_params = user_details
            except Exception as e:
                user_name = user_params['username']
                self.log("""The user '{0}' does not need additional filtering for 'None' values \
                         in the 'user_params' dictionary.""".format(user_name), "INFO")

            task_response = self.create_user(user_params)
            self.log('Task response {}'.format(str(task_response)), "INFO")
            config_created = True

        responses = {}
            
        if config_updated:
            responses["users_operation"] = {"response": task_response}
            self.msg = responses
            self.result['response'] = self.msg
            self.status = "success"
            self.log(self.msg, "INFO")

        if config_created:
            responses["users_operation"] = {"response": task_response}
            self.msg = responses
            self.result['response'] = self.msg
            self.status = "success"
            self.log(self.msg, "INFO")

        return self

    def list_defined_methods(self, cls_obj):
        """Lists all methods of a given class."""
        methods = []
        
        # Iterate over all members of the class
        for name, obj in inspect.getmembers(cls_obj, inspect.isfunction):
            # Check if the function is defined in the class's module
            if obj.__module__ == cls_obj.__module__:
                # If it is, add the method name to the methods list
                methods.append(name)
        
        return methods

    def format_version(self, version):
        """Converts version from '2.3.5.3' to 'v2_3_5_3'."""
        return 'v{}'.format(version.replace(".", "_"))

    def validate_version(self, version):
        """Validates if the provided version is among the known versions."""
        valid_versions = {'2.2.2.3', '2.2.3.3', '2.3.3.0', '2.3.5.3', '2.3.7.6'}
        if version not in valid_versions:
            self.log("'Unknown API version, known versions are: '2.2.2.3, 2.2.3.3, 2.3.3.0, 2.3.5.3, and 2.3.7.6'")

    def find_closest_family(self, module, family):
        """Finds the closest matching family name from available modules."""
        available_families = self.get_available_families(module)
        closest_matches = difflib.get_close_matches(family, available_families)
        return closest_matches[0] if closest_matches else None

    def get_available_families(self, module):
        """Gets the names of all modules available in the given module's directory."""
        available_families = []
        for _, name, _ in pkgutil.iter_modules(module.__path__):
            available_families.append(name)
        return available_families

    def try_import_module(self, version, family):
        """Attempts to import a module dynamically based on the family name and version."""
        formatted_version = self.format_version(version)
        module_path = "dnacentersdk.api.{}".format(formatted_version)

        try:
            base_module = importlib.import_module(module_path)
            family_name = self.find_closest_family(base_module, family)
            if family_name:
                submodule_path = "{}.{}".format(module_path, family_name)
                return importlib.import_module(submodule_path)
            else:
                raise ImportError("Module for family '{}' not found in version '{}'.".format(family, version))
        except ImportError as e:
            raise ImportError("Module for version '{}' not found: {}.".format(version, e))

    def filter_methods_by_hint(self,methods, hint):
        """Filters methods to include only those containing the hint in their name."""
        matching_methods = []
        
        # Iterate over each method name in the methods list
        for method in methods:
            # Check if the hint is a substring of the method name
            if hint in method:
                # If it is, add the method name to the matching_methods list
                matching_methods.append(method)
        
        return matching_methods

    def call_function(self, version, family, hint):
        """Checks if a specific function exists in the first class found in the module."""
        try:
            self.validate_version(version)
            module = self.try_import_module(version, family)
            self.log("Successfully imported {}".format(module.__name__))

            # Use the expanded function to get class names
            class_names = self.get_class_names(module)
            if class_names:
                family_class = getattr(module, class_names[0])
                methods = self.list_defined_methods(family_class)
                matching_methods = self.filter_methods_by_hint(methods, hint)

                if matching_methods:
                    self.log("Yes, function '{}' is available.".format(matching_methods[0]))
                    return matching_methods[0]  # Return the matched function name
                else:
                    self.log("No matching function for hint '{}' in version '{}'.".format(hint, version))
                    return None
            else:
                self.log("No classes found in module '{}'.".format(module.__name__))
                return None
        except ImportError as e:
            self.log("ImportError: {}.".format(e))
            return None

    def get_class_names(self, module):
        """Gets the names of all classes defined in the given module."""
        class_names = []
        
        # Iterate over all members of the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if the class is defined in the given module
            if obj.__module__ == module.__name__:
                class_names.append(name)
        
        return class_names


    def get_current_config(self, input_config):

        user_exists = False
        role_exists = False
        current_user_configuration = {}
        current_role_configuration = {}
        response_user = None
        response_role = None
        input_param = {}

        if input_config.get("username") is not None and input_config.get("username") != "":
            input_param["username"] = input_config["username"]

        if input_config.get("role_list") and all(item for item in input_config.get("role_list")):
            input_param["role_list"] = input_config["role_list"]

        if not input_param:
            self.log("Required param username or role_list is not in playbook config", "ERROR")
            return (user_exists, current_user_configuration, current_role_configuration)
        
        function_get_user = "get_user"
        version = self.payload.get("dnac_version")
        VBR_funtion_get_user = self.call_function(version, 'user_and_roles', function_get_user)
        self.log(f"VBR_funtion : {VBR_funtion_get_user}")

        function_get_role = "get_role"
        version = self.payload.get("dnac_version")
        VBR_funtion_get_role = self.call_function(version, 'user_and_roles', function_get_role)
        self.log(f"VBR_funtion : {VBR_funtion_get_role}")

        try:

            response_user = self.dnac._exec(
                family="user_and_roles",
                function= VBR_funtion_get_user,
                op_modifies=True,
                params={**input_param, 'invoke_source': 'external', 'auth_source': 'internal'},
            )

            response_role = self.dnac._exec(
                family="user_and_roles",
                function=VBR_funtion_get_role,
                op_modifies=True,
            )

        except Exception as e:
            self.log("The provided user '{0}' is either invalid or not present in the Cisco Catalyst Center."\
                     .format(str(input_param) + str(e)), "WARNING")

        if response_user and response_role:
            response_user = self.camel_to_snake_case(response_user)
            response_role = self.camel_to_snake_case(response_role)
            current_user_configuration = {}
            current_role_configuration = {}
            self.log("Received API response from 'get_users_api': {0}".format(str(response_user)), "DEBUG")
            self.log("Received API response from 'get_roles_api': {0}".format(str(response_role)), "DEBUG")

            users = response_user.get("response", {}).get("users", [])
            roles = response_role.get("response", {}).get("roles", [])

            for user in users:
                if user.get("username") == input_config.get("username"):
                    current_user_configuration = user
                    user_exists = True

            if input_config.get("role_list") != None:
              for role in roles:
                  if role.get("name") in input_config.get("role_list"):
                      current_role_configuration[role.get("name")] = role.get("role_id")
                      role_exists = True

        return (user_exists, role_exists, current_user_configuration, current_role_configuration)

    def create_user(self, user_params):
        function_add_user = "add_user"
        version = self.payload.get("dnac_version")
        VBR_funtion_add_user = self.call_function(version, 'user_and_roles', function_add_user)
        self.log(f"VBR_funtion : {VBR_funtion_add_user}")

        user_info_params= self.snake_to_camel_case(user_params)
        self.log("Create user with user_info_params: {0}".format(str(user_info_params)), "DEBUG")
        response = self.dnac._exec(
            family="user_and_roles",
            function=VBR_funtion_add_user,
            op_modifies=True,
            params=user_info_params,
        )
        self.log("Received API response from 'create_user': {0}".format(str(response)), "DEBUG")
        return response
    
    def user_requires_update(self, current_user, current_role):

        update_required = False
        update_user_param = {}

        if current_user.get('first_name') != self.want.get('first_name'):
            update_user_param['first_name'] = self.want['first_name']
            update_required = True
        elif 'first_name' not in update_user_param:
            update_user_param['first_name'] = current_user['first_name']
        
        if current_user.get('last_name') != self.want.get('last_name'):
            update_user_param['last_name'] = self.want['last_name']
            update_required = True
        elif 'last_name' not in update_user_param:
            update_user_param['last_name'] = current_user['last_name']
        
        if current_user.get('email') != self.want.get('email'):
            update_user_param['email'] = self.want['email']
            update_required = True
        elif 'email' not in update_user_param:
            update_user_param['email'] = current_user['email']
        
        if current_user.get('username') != self.want.get('username'):
            update_user_param['username'] = self.want['username']
            update_required = True
        elif 'username' not in update_user_param:
            update_user_param['username'] = current_user['username']
        
        if current_user.get('role_list')[0] != current_role[self.want.get("role_list")[0]]:
            role_id = current_role[self.want.get("role_list")[0]]
            update_user_param['role_list'] = [role_id]
            update_required = True
        elif 'role_list' not in update_user_param:
            update_user_param['role_list'] = [current_role[self.want.get("role_list")[0]]]

        return (update_required,update_user_param)

    def update_user(self, user_params):

        function_update_user = "update_user"
        version = self.payload.get("dnac_version")
        VBR_funtion_update_user = self.call_function(version, 'user_and_roles', function_update_user)
        self.log(f"VBR_funtion : {VBR_funtion_update_user}")

        user_info_params= self.snake_to_camel_case(user_params)
        self.log("Update user with user_info_params: {0}".format(str(user_info_params)), "DEBUG")
        response = self.dnac._exec(
            family="user_and_roles",
            function=VBR_funtion_update_user,
            op_modifies=True,
            params=user_info_params,
        )
        self.log("Received API response from 'update_user': {0}".format(str(response)), "DEBUG")
        return response

    def verify_diff_merged(self, config):

        self.get_have(config)
        self.log("Current State (have): {0}".format(str(self.have)), "INFO")
        self.log("Desired State (want): {0}".format(str(self.want)), "INFO")

        # Code to validate ccc config for merged state
        user_exist = self.have.get("user_exists")
        user_name = self.want.get("username")

        if user_exist:
            self.status = "success"
            self.msg = "The requested user '{0}' is present in the Cisco Catalyst Center and its creation has been verified.".format(user_name)
            self.log(self.msg, "INFO")

        (require_update, updated_user_info) = self.user_requires_update(self.have["current_user_config"], self.have["current_role_config"])

        if not require_update:
            self.log("The update for user '{0}' has been successfully verified. The updated info - {1}".format(user_name, updated_user_info), "INFO")
            self. status = "success"
            return self

        self.log("""The playbook input for user '{0}' does not align with the Cisco Catalyst Center, indicating that the merge task
                 may not have executed successfully.""".format(user_name), "INFO")

        return self
    
    def snake_to_camel_case(self, data):
            """
            This function converts keys from snake case to camel case in a given dictionary.
            
            Parameters:
            - data: type Dict: A dictionary with keys in snake case.

            Returns:
            A new dictionary with keys converted to camel case.
            """
            def to_camel_case(snake_str):
                components = snake_str.split('_')
                return components[0] + ''.join(x.title() for x in components[1:])

            if isinstance(data, dict):
                camel_case_data = {}
                for key, value in data.items():
                    new_key = to_camel_case(key)

                    if isinstance(value, dict):
                        camel_case_data[new_key] = self.snake_to_camel_case(value)
                    elif isinstance(value, list):
                        camel_case_data[new_key] = [self.snake_to_camel_case(item) if isinstance(item, dict) else item for item in value]
                    else:
                        camel_case_data[new_key] = value

                return camel_case_data
            elif isinstance(data, list):
                return [self.snake_to_camel_case(item) if isinstance(item, dict) else item for item in data]
            else:
                return data


def main():
    """ main entry point for module execution
    """
    # Basic Ansible type check or assign default.
    user_details = {'dnac_host': {'required': True, 'type': 'str'},
                    'dnac_port': {'type': 'str', 'default': '443'},
                    'dnac_username': {'type': 'str', 'default': 'admin'},
                    'dnac_password': {'type': 'str', 'no_log': True},
                    'dnac_verify': {'type': 'bool', 'default': 'True'},
                    'dnac_version': {'type': 'str', 'default': '2.2.3.3'},
                    'dnac_debug': {'type': 'bool', 'default': False},
                    'dnac_log': {'type': 'bool', 'default': False},
                    'dnac_log_level': {'type': 'str', 'default': 'WARNING'},
                    "dnac_log_file_path": {"type": 'str', "default": 'dnac.log'},
                    'config_verify': {'type': 'bool', "default": False},
                    "dnac_log_append": {"type": 'bool', "default": True},
                    'dnac_api_task_timeout': {'type': 'int', "default": 1200},
                    'dnac_task_poll_interval': {'type': 'int', "default": 2},
                    'config': {'required': True, 'type': 'list', 'elements': 'dict'},
                    'validate_response_schema': {'type': 'bool', 'default': True},
                    'state': {'default': 'merged', 'choices': ['merged', 'deleted']}
                }

    module = AnsibleModule(
        argument_spec=user_details,
        supports_check_mode=True
    )

    ccc_user = User(module)
    state = ccc_user.params.get("state")

    if state not in ccc_user.supported_states:
        ccc_user.status = "invalid"
        ccc_user.msg = "State {0} is invalid".format(state)
        ccc_user.check_return_status()

    ccc_user.validate_input_yml().check_return_status()
    config_verify = ccc_user.params.get("config_verify")

    for config in ccc_user.validated_config:
        ccc_user.reset_values()
        ccc_user.get_want(config).check_return_status()
        ccc_user.get_have(config).check_return_status()
        ccc_user.get_diff_state_apply[state](config).check_return_status()
        
        if config_verify:
            time.sleep(5)
            ccc_user.verify_diff_state_apply[state](config).check_return_status()

    module.exit_json(**ccc_user.result)

if __name__ == '__main__':
    main()