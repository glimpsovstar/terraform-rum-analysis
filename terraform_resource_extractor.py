"""
Terraform Resource Extractor
============================
This script extracts and analyzes managed resources from a Terraform state file.

🛠 Required Python Modules:
   - json
   - argparse
   - pandas (install using `pip install pandas` if not already installed)

💡 Usage Examples:
   1️⃣ **Extract and display managed resources (default mode)**:
      python terraform_resource_extractor.py -f terraform.tfstate

   2️⃣ **Count total resource instances (like jq script)**:
      python terraform_resource_extractor.py -f terraform.tfstate -n

   3️⃣ **Show aggregated resource details**:
      python terraform_resource_extractor.py -f terraform.tfstate -A

   4️⃣ **Enable debug mode to compare with jq output**:
      python terraform_resource_extractor.py -f terraform.tfstate -n -d
"""

import json
import argparse
import pandas as pd

def load_state_file(state_file):
    """
    Loads and parses the Terraform state file.

    Args:
        state_file (str): Path to the Terraform state JSON file.

    Returns:
        dict: Parsed JSON data from the Terraform state file.

    Exits:
        - If the file is not found.
        - If the file is not a valid JSON.
    """
    try:
        with open(state_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"❌ Error: File '{state_file}' not found. Please provide a valid Terraform state file.")
        exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: File '{state_file}' is not a valid JSON file. Ensure it is a valid Terraform state file.")
        exit(1)

def extract_resources(state_data, debug=False):
    """
    Extracts managed resources from the Terraform state file and ensures instance count is accurate.

    Args:
        state_data (dict): Parsed Terraform state JSON.
        debug (bool): Whether to print debug information.

    Returns:
        pd.DataFrame: A DataFrame containing extracted resource information.
    """
    resources = []
    total_instances_debug = 0  # Debug counter for total instances

    for resource in state_data.get("resources", []):
        if resource.get("mode") == "managed" and resource.get("type") not in ["terraform_data", "null_resource"]:
            instances = resource.get("instances", [])
            total_instances_debug += len(instances)

            for instance in instances:
                resources.append({
                    "Module": resource.get("module", "root"),  # Terraform module (default: "root")
                    "Resource Type": resource["type"],  # e.g., aws_instance, aws_s3_bucket
                    "Resource Name": resource["name"],  # Terraform resource name
                    "Provider": resource.get("provider", "unknown"),  # Cloud provider type
                    "Instance Count": 1  # Each row represents a single instance
                })

    if debug:
        print(f"🔍 DEBUG: Total resource instances counted (flattened): {total_instances_debug}")

    return pd.DataFrame(resources)

def count_instances(resource_df):
    """
    Returns the total count of resource instances.

    Args:
        resource_df (pd.DataFrame): DataFrame of extracted resources.

    Returns:
        int: Total number of resource instances.
    """
    return len(resource_df)

def aggregate_resources(resource_df):
    """
    Outputs aggregate statistics about the extracted resources.

    Args:
        resource_df (pd.DataFrame): DataFrame of extracted resources.

    Prints:
        - Total number of resource instances
        - Total number of unique resources
        - Unique resource types and names with their counts
    """
    total_instances = count_instances(resource_df)
    total_resources = resource_df["Resource Name"].nunique()
    unique_types = resource_df["Resource Type"].nunique()

    print("\n📊 Aggregate Information:")
    print(f"🔹 Total number of resource instances: {total_instances}")
    print(f"🔹 Total number of unique resources: {total_resources}")
    print(f"🔹 Total number of unique resource types: {unique_types}")

    print("\n🔹 Unique Resource Types:")
    print(resource_df["Resource Type"].value_counts().to_string())

    print("\n🔹 Unique Resource Names:")
    print(resource_df["Resource Name"].value_counts().to_string())

def compare_with_jq(state_data, debug=False):
    """
    Compares Python script output with the expected jq output.

    Args:
        state_data (dict): Parsed Terraform state JSON.
        debug (bool): Whether to print debug information.

    Prints:
        - Expected total instance count (as jq would compute it).
    """
    bash_count = sum(len(resource.get("instances", [])) for resource in state_data.get("resources", [])
                     if resource.get("mode") == "managed" and resource.get("type") not in ["terraform_data", "null_resource"])
    
    if debug:
        print(f"🔍 DEBUG: Expected jq output (from Python simulation): {bash_count}")

def main():
    """
    Main function to parse command-line arguments and execute the appropriate mode.

    Modes:
        - Default: Extract and display managed resources.
        - -n: Count total resource instances.
        - -A: Show aggregate resource information.
        - -d: Enable debug mode.
    """
    parser = argparse.ArgumentParser(description="Terraform Resource Extractor - Extract and analyze managed resources from a Terraform state file.")
    parser.add_argument("-f", "--file", required=True, help="The Terraform state file to analyze.")
    parser.add_argument("-n", "--number", action="store_true", help="Only output the number of resource instances.")
    parser.add_argument("-A", "--aggregate", action="store_true", help="Output aggregate information about resources.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode to show extra information.")

    args = parser.parse_args()
    state_data = load_state_file(args.file)

    compare_with_jq(state_data, args.debug)
    resource_df = extract_resources(state_data, args.debug)

    if resource_df.empty:
        print("⚠ No managed resources found in the Terraform state file.")
        exit(0)

    if args.number:
        print(f"Total number of resource instances: {count_instances(resource_df)}")
        exit(0)

    if args.aggregate:
        aggregate_resources(resource_df)
        exit(0)

    # Default Output: Show extracted managed resources with column descriptions
    print("\n📊 Extracted Managed Resources:")
    print("\n🔹 Column Descriptions:")
    print("   - Module: Terraform module where the resource is defined.")
    print("   - Resource Type: Type of the Terraform resource (e.g., aws_instance, aws_s3_bucket).")
    print("   - Resource Name: Logical name given to the resource in Terraform.")
    print("   - Provider: Cloud provider responsible for this resource.")
    print("   - Instance Count: Number of instances of this resource.")

    print("\n🔹 Resource List:")
    print(resource_df.to_string(index=False))

if __name__ == "__main__":
    main()
