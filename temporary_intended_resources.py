"""
This script extracts and identifies unique Terraform resources/instances from a Terraform state file.
It specifically looks for resource names containing the keywords: "demo", "test", "temp", "tmp", and "example".

### Purpose:
- Helps users quickly identify temporary or test resources in a Terraform state file.
- Provides summary statistics on the number of matching resources found.
- Can be useful for identifying ephemeral resources that should be monitored or cleaned up.

### Usage:
- Run the script with a Terraform state file as an argument:
  ```
  python extract_resources.py <terraform.tfstate> [-D]
  ```
  - The `-D` flag is optional and includes resource attributes in the output.

### Terraform Cloud Integration:
- The resulting workspace may be a good candidate for Terraform Cloud's Ephemeral Workspaces.
- More details on Ephemeral Workspaces: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/ephemeral

"""
import json
import sys
import pandas as pd

def extract_resources(state_file_path, display_attributes=False):
    """
    Extracts and identifies unique Terraform resources/instances with "demo", "test", "temp", or "tmp" in their name
    from a Terraform state file.

    :param state_file_path: Path to the Terraform state file (JSON format)
    :param display_attributes: Boolean flag to determine if attributes should be displayed
    :return: A DataFrame with extracted unique resources
    """
    try:
        # Load the Terraform state file
        with open(state_file_path, "r", encoding="utf-8") as file:
            terraform_state = json.load(file)

        # Initialize a list to store extracted resources
        filtered_resources = []
        keywords = ["demo", "test", "temp", "tmp", "example"]

        # Iterate through resources in the Terraform state file
        for resource in terraform_state.get("resources", []):
            for instance in resource.get("instances", []):
                # Extract instance name if available
                attributes = instance.get("attributes", {})
                name = attributes.get("name", "Unknown")
                
                # Check if the name contains any of the keywords
                if any(keyword in name.lower() for keyword in keywords):
                    resource_info = {
                        "Resource Type": resource.get("type", "Unknown"),
                        "Resource Name": name,
                    }
                    if display_attributes:
                        resource_info["Attributes"] = attributes
                    
                    filtered_resources.append(resource_info)

        # Convert extracted data into a DataFrame
        resource_df = pd.DataFrame(filtered_resources)

        if resource_df.empty:
            print("\n🔹 No matching resources found in the Terraform state file.")
            return None

        # Identify unique resources based on resource type and name
        unique_resource_df = resource_df.drop_duplicates(subset=["Resource Type", "Resource Name"], keep="first")
        
        # Identify unique resource types and their counts
        unique_resource_types_count = unique_resource_df["Resource Type"].value_counts().to_dict()
        unique_resource_types = len(unique_resource_types_count)

        # Print summary of extracted data
        print("\n🔹 Resource Extraction Summary:")
        print(f"📌 Keywords used for filtering: {', '.join(keywords)}")
        print("--------------------------------------------------")
        print(f"📌 Total Matching Instances Found: {len(resource_df)}")
        print(f"📌 Total Unique Matching Instances: {len(unique_resource_df)}")
        print(f"📌 Total Unique Resource Types: {unique_resource_types}")
        print("📌 Unique Resource Type Counts:")
        for resource_type, count in unique_resource_types_count.items():
            print(f"   - {resource_type}: {count}")
        print("--------------------------------------------------\n")
        
        # Print extracted unique resources in a clean format
        print("✅ Unique Matching Resources:")
        if display_attributes:
            print(unique_resource_df.to_string(index=False))
        else:
            print(unique_resource_df[["Resource Type", "Resource Name"]].to_string(index=False))

        return unique_resource_df

    except FileNotFoundError:
        print(f"❌ Error: The file '{state_file_path}' was not found. Please check the file path and try again.")
    except json.JSONDecodeError:
        print(f"❌ Error: The file '{state_file_path}' is not a valid JSON file. Ensure it contains properly formatted JSON.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure correct command-line arguments are provided
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python extract_resources.py <terraform.tfstate> [-D]")
        sys.exit(1)
    
    state_file_path = sys.argv[1]
    display_attributes = "-D" in sys.argv
    extract_resources(state_file_path, display_attributes)
