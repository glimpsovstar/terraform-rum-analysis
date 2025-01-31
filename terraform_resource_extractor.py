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
    """
    try:
        with open(state_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"❌ Error: File '{state_file}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: File '{state_file}' is not a valid JSON file.")
        exit(1)

def extract_resources(state_data, exclude_tfe_vault=False, only_tfe_vault=False, debug=False):
    """
    Extracts managed resources from the Terraform state file.
    
    Args:
        state_data (dict): Parsed Terraform state JSON.
        exclude_tfe_vault (bool): Whether to exclude HashiCorp-related resources (tfe_, vault_).
        only_tfe_vault (bool): Whether to include only HashiCorp-related resources.
        debug (bool): Whether to print debug information.
    
    Returns:
        pd.DataFrame: A DataFrame containing extracted resource information.
        int: The total count of HashiCorp-related resources.
    """
    resources = []
    total_instances_debug = 0
    hashi_instances = 0

    for resource in state_data.get("resources", []):
        if resource.get("mode") == "managed" and resource.get("type") not in ["terraform_data", "null_resource"]:
            is_hashi_resource = resource["type"].startswith("tfe_") or resource["type"].startswith("vault_")
            
            if exclude_tfe_vault and is_hashi_resource:
                continue
            
            if only_tfe_vault and not is_hashi_resource:
                continue
            
            if is_hashi_resource:
                hashi_instances += len(resource.get("instances", []))
            
            instances = resource.get("instances", [])
            total_instances_debug += len(instances)

            for instance in instances:
                resources.append({
                    "Module": resource.get("module", "root"),
                    "Resource Type": resource["type"],
                    "Resource Name": resource["name"],
                    "Provider": resource.get("provider", "unknown"),
                    "Instance Count": 1
                })

    if debug:
        print(f"🔍 DEBUG: Total resource instances counted (flattened): {total_instances_debug}")

    return pd.DataFrame(resources), hashi_instances

def count_instances(resource_df):
    """
    Returns the total count of resource instances.
    
    Args:
        resource_df (pd.DataFrame): DataFrame of extracted resources.

    Returns:
        int: Total number of resource instances.
    """
    return len(resource_df)

def aggregate_resources(resource_df, hashi_instances, exclude_tfe_vault):
    """
    Outputs aggregate statistics about the extracted resources.
    
    Args:
        resource_df (pd.DataFrame): DataFrame of extracted resources.
        hashi_instances (int): The total count of HashiCorp-related resources.
        exclude_tfe_vault (bool): Whether to exclude HashiCorp-related resources.
    """
    total_instances = count_instances(resource_df)
    total_resources = resource_df["Resource Name"].nunique()
    unique_types = resource_df["Resource Type"].nunique()

    print("\n📊 Aggregate Information:")
    print(f"🔹 Total number of resource instances: {total_instances}")
    print(f"🔹 Total number of unique resources: {total_resources}")
    print(f"🔹 Total number of unique resource types: {unique_types}")
    if not exclude_tfe_vault:
        print(f"🔹 Total number of HashiCorp related resource instances: {hashi_instances}")
    
    print("\n🔹 Unique Resource Types:")
    filtered_types = resource_df["Resource Type"].loc[~resource_df["Resource Type"].str.startswith(("tfe_", "vault_"))] if exclude_tfe_vault else resource_df["Resource Type"]
    print(filtered_types.value_counts().to_string())
    
    print("\n🔹 Unique Resource Names:")
    filtered_names = resource_df["Resource Name"].loc[~resource_df["Resource Type"].str.startswith(("tfe_", "vault_"))] if exclude_tfe_vault else resource_df["Resource Name"]
    print(filtered_names.value_counts().to_string())

def compare_with_jq(state_data, debug=False):
    """
    Compares Python script output with the expected jq output.
    
    Args:
        state_data (dict): Parsed Terraform state JSON.
        debug (bool): Whether to print debug information.
    """
    bash_count = sum(len(resource.get("instances", [])) for resource in state_data.get("resources", [])
                     if resource.get("mode") == "managed" and resource.get("type") not in ["terraform_data", "null_resource"])
    
    if debug:
        print(f"🔍 DEBUG: Expected jq output (from Python simulation): {bash_count}")

def main():
    """
    Main function to parse command-line arguments and execute the appropriate mode.
    """
    parser = argparse.ArgumentParser(description="Extract and analyze managed resources from a Terraform state file.")
    parser.add_argument("-f", "--file", required=True, help="The Terraform state file to analyze.")
    parser.add_argument("-n", "--number", action="store_true", help="Only output the number of resource instances.")
    parser.add_argument("-A", "--aggregate", action="store_true", help="Output aggregate information about resources.")
    parser.add_argument("-H", "--hide-tfe-vault", action="store_true", help="Exclude 'tfe_' and 'vault_' resources from results.")
    parser.add_argument("-Ho", "--only-tfe-vault", action="store_true", help="Only show 'tfe_' and 'vault_' resources.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode to show extra information.")
    
    args = parser.parse_args()
    state_data = load_state_file(args.file)
    
    compare_with_jq(state_data, args.debug)
    resource_df, hashi_instances = extract_resources(state_data, args.hide_tfe_vault, args.only_tfe_vault, args.debug)

    if resource_df.empty:
        print("⚠ No managed resources found in the Terraform state file.")
        exit(0)

    if args.number:
        print(f"Total number of resource instances: {count_instances(resource_df)}")
        exit(0)

    if args.aggregate:
        aggregate_resources(resource_df, hashi_instances, args.hide_tfe_vault)
        exit(0)

    print("\n📊 Extracted Managed Resources:")
    print(resource_df.to_string(index=False))

if __name__ == "__main__":
    main()
