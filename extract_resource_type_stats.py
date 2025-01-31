import json
import sys
import pandas as pd
import argparse

def extract_resource_instances(state_file_path, resource_type, detailed_output=False):
    """
    Extracts and identifies unique instances of a specified Terraform resource type from a state file.

    :param state_file_path: Path to the Terraform state file (JSON format)
    :param resource_type: The resource type to search for (e.g., 'azuread_group_member')
    :param detailed_output: Boolean flag to output full instance details
    :return: A DataFrame with extracted unique resource instances
    """
    try:
        # Load the Terraform state file
        with open(state_file_path, "r", encoding="utf-8") as file:
            terraform_state = json.load(file)

        # Initialize an empty list to store resource details
        resource_instances = []

        # Iterate over resources in the Terraform state file
        for resource in terraform_state.get("resources", []):
            if resource.get("type") == resource_type:
                for instance in resource.get("instances", []):
                    # Extract relevant attributes dynamically
                    attributes = instance.get("attributes", {})
                    resource_instances.append(attributes)

        # Convert extracted data into a DataFrame
        resource_instances_df = pd.DataFrame(resource_instances)

        if resource_instances_df.empty:
            print(f"\n🔹 No `{resource_type}` instances found in the Terraform state file.")
            return None

        # Identify unique resource instances
        unique_resource_instances_df = resource_instances_df.drop_duplicates()

        # Print summary of results
        print(f"\n🔹 {resource_type} Extraction Summary:")
        print("--------------------------------------------------")
        print(f"📌 Total `{resource_type}` Instances Found: {len(resource_instances_df)}")
        print(f"📌 Total Unique `{resource_type}` Instances: {len(unique_resource_instances_df)}")
        print("--------------------------------------------------\n")
        
        # Print extracted unique instances in a clean format if detailed output is enabled
        if detailed_output:
            print(f"✅ Unique {resource_type} Instances:")
            print(unique_resource_instances_df.to_string(index=False))

        return unique_resource_instances_df

    except FileNotFoundError:
        print(f"❌ Error: The file '{state_file_path}' was not found. Please check the file path and try again.")
    except json.JSONDecodeError:
        print(f"❌ Error: The file '{state_file_path}' is not a valid JSON file. Ensure it contains properly formatted JSON.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Argument parser to handle command-line inputs
    parser = argparse.ArgumentParser(description="Extract specific Terraform resource instances from a state file.")
    
    # Adding required arguments for file and resource type
    parser.add_argument("-f", "--file", required=True, help="Path to the Terraform state file")
    parser.add_argument("-r", "--resource", required=True, help="Resource type to extract")
    
    # Optional argument to enable detailed output
    parser.add_argument("-D", "--detailed", action="store_true", help="Output detailed instance information")
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Execute extraction function
    extract_resource_instances(args.file, args.resource, args.detailed)
