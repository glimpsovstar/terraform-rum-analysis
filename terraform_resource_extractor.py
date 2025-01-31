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

   5️⃣ **Exclude HashiCorp-related resources (tfe_, vault_)**:
      python terraform_resource_extractor.py -f terraform.tfstate -H

   6️⃣ **Only show HashiCorp-related resources (tfe_, vault_)**:
      python terraform_resource_extractor.py -f terraform.tfstate -Ho

   7️⃣ **Group resources by module, type, name, and provider**:
      python terraform_resource_extractor.py -f terraform.tfstate -G

   8️⃣ **Output results to a CSV file**:
      python terraform_resource_extractor.py -f terraform.tfstate -o output.csv
"""

import json
import argparse
import pandas as pd

def load_state_file(state_file):
    """
    Loads and parses the Terraform state file.
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

def save_to_csv(resource_df, output_file):
    """
    Saves extracted resources to a CSV file.
    """
    output_file = output_file if output_file.endswith(".csv") else output_file + ".csv"
    resource_df.to_csv(output_file, index=False)
    print(f"✅ Results saved to {output_file}")

def extract_resources(state_data, exclude_tfe_vault=False, only_tfe_vault=False, debug=False):
    """
    Extracts managed resources from the Terraform state file.
    """
    resources = []
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
            
            for instance in resource.get("instances", []):
                resources.append({
                    "Module": resource.get("module", "root"),
                    "Resource Type": resource["type"],
                    "Resource Name": resource["name"],
                    "Provider": resource.get("provider", "unknown"),
                    "Instance Count": 1
                })
    
    return pd.DataFrame(resources), hashi_instances

def aggregate_resources(resource_df, hashi_instances, is_hashi_only, is_excluding_hashi):
    """
    Outputs aggregate statistics about the extracted resources.
    """
    total_instances = len(resource_df)
    total_resources = resource_df["Resource Name"].nunique()
    unique_types = resource_df["Resource Type"].nunique()

    print("\n📊 Aggregate Information:")
    if is_hashi_only:
        print(f"🔹 Total HashiCorp related resource instances: {hashi_instances}")
    else:
        print(f"🔹 Total number of resource instances: {total_instances}")
        if not is_excluding_hashi:
            print(f"🔹 Total HashiCorp related resource instances: {hashi_instances}")
    print(f"🔹 Total number of unique resources: {total_resources}")
    print(f"🔹 Total number of unique resource types: {unique_types}")
    
    print("\n🔹 Unique Resource Types:")
    print(resource_df["Resource Type"].value_counts().to_string())
    
    print("\n🔹 Unique Resource Names:")
    print(resource_df["Resource Name"].value_counts().to_string())

def group_resources(resource_df):
    """
    Groups resources by module, type, name, and provider and prints grouped results.
    """
    grouped_df = resource_df.groupby(["Module", "Resource Type", "Resource Name", "Provider"]).sum()
    print("\n📊 Grouped Resource Information:")
    print(grouped_df.to_string())

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
    parser.add_argument("-G", "--group", action="store_true", help="Group resources by module, type, name, and provider.")
    parser.add_argument("-o", "--output", help="Output results to a specified .csv file.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode to show extra information.")
    
    args = parser.parse_args()
    state_data = load_state_file(args.file)
    
    compare_with_jq(state_data, args.debug)
    resource_df, hashi_instances = extract_resources(state_data, args.hide_tfe_vault, args.only_tfe_vault, args.debug)

    if resource_df.empty:
        print("⚠ No managed resources found in the Terraform state file.")
        exit(0)

    # Store results for optional CSV output
    final_df = resource_df.copy()

    if args.number:
        print(f"Total number of resource instances: {len(resource_df)}")
        exit(0)

    if args.aggregate:
        aggregate_resources(resource_df, hashi_instances, args.only_tfe_vault, args.hide_tfe_vault)
        exit(0)
    
    if args.group:
        grouped_df = group_resources(resource_df)
        final_df = grouped_df.reset_index()  # Ensure it's properly formatted for CSV
    
    if args.output:
        save_to_csv(final_df, args.output)
    
    print("\n📊 Extracted Managed Resources:")
    print(resource_df.to_string(index=False))

if __name__ == "__main__":
    main()
