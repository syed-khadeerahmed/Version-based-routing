import importlib  
import inspect    
import pkgutil    
import difflib    

class VersionBasedRouting:
    class VersionError(Exception):
        """Exception raised for invalid DNA Center API versions."""
        pass

    def list_defined_methods(self, cls_obj):
        """
        Lists all methods of a given class.
        
        Parameters:
        cls_obj (type): The class object whose methods are to be listed.
        
        Returns:
        List[str]: A list of method names.
        """
        methods = []  # Initialize an empty list to store method names

        # Get all members (functions, classes, etc.) of the class
        members = inspect.getmembers(cls_obj)

        # Iterate through each member
        for name, obj in members:
            # Check if the member is a function and belongs to the class's module
            if inspect.isfunction(obj) and obj.__module__ == cls_obj.__module__:
                methods.append(name)  # Add the method name to the list

        return methods  # Return the list of method names

    def format_version(self, version):
        """
        Converts version from '2.3.5.3' to 'v2_3_5_3'.
        
        Parameters:
        version (str): The version string in 'X.Y.Z.W' format.
        
        Returns:
        str: The formatted version string.
        """
        formatted_version = 'v' + version.replace('.', '_')  # Replace dots with underscores and prefix with 'v'
        return formatted_version

    def validate_version(self, version):
        """
        Validates if the provided version is among the known versions.
        
        Parameters:
        version (str): The version string to be validated.
        
        Raises:
        VersionError: If the version is not among the known versions.
        """
        valid_versions = ['2.2.2.3', '2.2.3.3', '2.3.3.0', '2.3.5.3', '2.3.7.6']  # List of known versions

        # Check if the provided version is in the list of valid versions
        if version not in valid_versions:
            raise self.VersionError(
                'Unknown API version, known versions are: '
                '2.2.2.3, 2.2.3.3, 2.3.3.0, 2.3.5.3, and 2.3.7.6'
            )

    def find_closest_family(self, module, family):
        """
        Finds the closest matching family name from available modules.
        
        Parameters:
        module (module): The base module for the API version.
        family (str): The family name to find close matches for.
        
        Returns:
        str or None: The closest matching family name or None if no match is found.
        """
        available_families = []  # Initialize an empty list for available family names

        # Iterate over all submodules in the module's path
        for _, name, _ in pkgutil.iter_modules(module.__path__):
            available_families.append(name)  # Add each submodule name to the list

        # Find close matches for the given family name
        closest_matches = difflib.get_close_matches(family, available_families)
        print(available_families)
        print()
        # Return the closest match if found, otherwise return None
        if closest_matches:
            return closest_matches[0]
        
        return None

    def try_import_module(self, version, family):
        """
        Attempts to import a module dynamically based on the family name and version.
        
        Parameters:
        version (str): The API version to import.
        family (str): The family name for the submodule.
        
        Returns:
        module: The imported submodule.
        
        Raises:
        ImportError: If the module or submodule cannot be imported.
        """
        formatted_version = self.format_version(version)  # Format the version string
        module_path = f"dnacentersdk.api.{formatted_version}"  # Construct the module path

        try:
            # Import the base module for the version
            base_module = importlib.import_module(module_path)
            
            # Find the closest matching family name
            family_name = self.find_closest_family(base_module, family)
            
            if family_name:
                # Construct the path for the submodule and import it
                submodule_path = f"{module_path}.{family_name}"
                submodule = importlib.import_module(submodule_path)
                return submodule
            else:
                raise ImportError(f"Module for family '{family}' not found in version '{version}'.")
        except ImportError as e:
            raise ImportError(f"Module for version '{version}' not found: {e}")

    def inspect_family_file(self, version, family):
        """
        Inspects the family file and lists available classes and their methods.
        
        Parameters:
        version (str): The API version.
        family (str): The family name of the module to inspect.
        """
        try:
            # Validate the API version
            self.validate_version(version)
            
            # Import the relevant module dynamically
            module = self.try_import_module(version, family)
            print(f"Successfully imported {module.__name__}")

            # Get all members of the module
            members = inspect.getmembers(module)
            
            # Initialize an empty list for class names
            class_names = []
            
            # Iterate through each member
            for name, obj in members:
                # Check if the member is a class and belongs to the current module
                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                    class_names.append(name)

            if class_names:
                # Use the first class as default if any classes are found
                default_class_name = class_names[0]
                cls_obj = getattr(module, default_class_name)
                print(f"Methods in class {default_class_name}:")
                
                # List all defined methods in the class
                methods = self.list_defined_methods(cls_obj)
                for method in methods:
                    print(f"- {method}")
            else:
                print(f"No classes found in module '{module.__name__}'.")

        except ImportError as e:
            print(f"ImportError: {e}")
        except self.VersionError as e:
            print(e)

class DNACConnector:
    def __init__(self, version, family_hint, function_hint):
        """
        Initializes the DNACConnector with version, family hint, and function hint.
        
        Parameters:
        version (str): The API version.
        family_hint (str): The family hint to locate the relevant submodule.
        function_hint (str): The function hint to locate the relevant method.
        """
        self.version = version
        self.family_hint = family_hint
        self.function_hint = function_hint
        self.version_based_routing = VersionBasedRouting()
        self.dnac = self.connect_to_dnac()  # Establish connection

    def connect_to_dnac(self):
        """
        Creates a mock connection to the DNAC (replace with actual implementation).
        
        Returns:
        function: A mock function to simulate the DNAC API execution.
        """
        def _exec(family, function, op_modifies, params):
            print(f"Executing {function} in family {family}")
            return {"status": "success"}
        
        return _exec

    def get_user(self):
        """
        Retrieve users from Cisco Catalyst Center.
        
        Returns:
        dict: The response from the DNAC API.
        """
        try:
            # Import the relevant module dynamically
            module = self.version_based_routing.try_import_module(self.version, self.family_hint)
            print(f"Successfully imported {module.__name__}")

            # Find the family class
            members = inspect.getmembers(module)
            family_class_name = None
            
            for name, obj in members:
                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                    family_class_name = name
                    break
            
            family_class = getattr(module, family_class_name, None) if family_class_name else None

            if family_class:
                # List all defined methods in the class
                methods = self.version_based_routing.list_defined_methods(family_class)
                
                # Match the function hint with available methods
                matching_methods = [method for method in methods if self.function_hint in method]

                if matching_methods:
                    # Print the matched function name
                    print(f"Matched function: {matching_methods[0]}")
                    # Use the dynamic values in the execution
                    response = self.dnac(
                        family=self.family_hint,
                        function=matching_methods[0],
                        op_modifies=True,
                        params={"invoke_source": "external"},
                    )
                    # print(matching_methods[0])
                    return response
                else:
                    print(f"No matching function for hint '{self.function_hint}' in version '{self.version}'.")
            else:
                print(f"Class for family '{self.family_hint}' not found.")
        except ImportError as e:
            print(f"ImportError: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize the DNAC connector with version, family hint, and function hint
    connector = DNACConnector(version='2.3.7.6', family_hint='user role', function_hint='add_user')

    # Create an instance of VersionBasedRouting
    functions = VersionBasedRouting()

    # Inspect the family file
    functions.inspect_family_file('2.3.7.6', 'user role')

    # Retrieve user information
    response = connector.get_user()
    print(response)
