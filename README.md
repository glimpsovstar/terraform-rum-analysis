# terraform-rum-analysis
This repository is intended to be used as a template for creating new Terraform modules or just for writing general Terraform code

## Terraform Resource Extractor (`terraform_resource_extractor.py`)
The `terraform_resource_extractor.py` script is a **Terraform state analysis tool** that extracts, counts, and aggregates **managed resources** from a Terraform state (`.tfstate`) file. It helps Terraform users inspect **resource instances, unique resource types, and provider details** in a structured format.

### 🛠 Features
- **Extract managed resources** from a Terraform state file.
- **Count total resource instances** (including those created with `count` or `for_each`).
- **List unique resource types** (e.g., `aws_instance`, `aws_s3_bucket`).
- **Aggregate and summarize resources** to provide insights.
- **Supports debugging mode** to compare instance counts with `jq`.

---

### 📦 Installation Requirements
This script requires **Python 3.x** and the `pandas` library. Install the dependencies using:

```bash
pip install pandas

## Terraform Resource Extractor (`terraform_resource_extractor.py`)

The `terraform_resource_extractor.py` script is a **Terraform state analysis tool** that extracts, counts, and aggregates **managed resources** from a Terraform state (`.tfstate`) file. It helps Terraform users inspect **resource instances, unique resource types, and provider details** in a structured format.

---

### 📦 Installation Requirements

This script requires **Python 3.x** and the `pandas` library. Install the dependencies using:

```bash
pip install pandas
```

---

## 🚀 Usage

Run the script using Python and specify the Terraform state file (`.tfstate`) you want to analyze.

---

### 1️⃣ Extract & Display Managed Resources (Default Mode)

```bash
python terraform_resource_extractor.py -f terraform.tfstate
```

🔹 **Outputs a structured list** of all managed resources, including:

- **Module** (Terraform module where the resource is defined)
- **Resource Type** (e.g., `aws_instance`, `google_compute_instance`)
- **Resource Name** (Terraform name of the resource)
- **Provider** (Cloud provider)
- **Instance Count** (Number of instances)

---

### 2️⃣ 🔹 **Recommended Mode: Show Aggregated Resource Summary (**\`\`**)**

```bash
python terraform_resource_extractor.py -f terraform.tfstate -A
```

✅ **Recommended for most users** as it provides **high-level insights**.\
🔹 **Outputs summary statistics**, including:

- **Total instances**
- **Total unique resources**
- **Unique resource types**
- **Most common resource types & names**

#### Example Output:

```
📊 Aggregate Information:
🔹 Total number of resource instances: 47
🔹 Total number of unique resources: 12
🔹 Total number of unique resource types: 5

🔹 Unique Resource Types:
aws_instance          23
aws_s3_bucket         12
aws_security_group     8
...

🔹 Unique Resource Names:
web_server            10
db_instance            5
...
```

---

### 3️⃣ Count Total Resource Instances (`-n`)

```bash
python terraform_resource_extractor.py -f terraform.tfstate -n
```

🔹 **Outputs only the total number** of resource instances across all types.

#### Example Output:

```
Total number of resource instances: 47
```

---

### 4️⃣ Enable Debug Mode (`-d`)

```bash
python terraform_resource_extractor.py -f terraform.tfstate -n -d
```

🔹 **Compares Python output with ****\`\`**** expected values**, ensuring accuracy.

#### Example Output:

```
🔍 DEBUG: Expected jq output (from Python simulation): 47
🔍 DEBUG: Total resource instances counted (flattened): 47
```

---

### 5️⃣ Save Extracted Data to a CSV File

```bash
python terraform_resource_extractor.py -f terraform.tfstate -o output.csv
```

🔹 Saves the extracted resource list to a **CSV file** for further analysis.

---

### 6️⃣ Group Resources by Module & Type (`-G`)

```bash
python terraform_resource_extractor.py -f terraform.tfstate -G
```

🔹 **Outputs a grouped view** of resources, organized by:

- **Module**
- **Resource Type**
- **Resource Name**
- **Provider**

#### Example Output:

```
📊 Grouped Resource Information:
Module         Resource Type        Resource Name     Provider              Instance Count
------------------------------------------------------------------------------------------------
root           aws_instance         web_server       aws                   3
module.db      aws_rds_instance     database         aws                   2
module.network aws_vpc              vpc_main         aws                   1
...
```

---

## 📝 Example: Comparing with jq

The script's **total instance count** should match the following `jq` command:

```bash
cat terraform.tfstate | jq '[ .resources[] | select(.mode == "managed") | select(.type == "terraform_data" or .type == "null_resource" | not) | .instances | flatten[] ] | length'
```

Use the `-d` flag to **validate Terraform state parsing**.

---

## 💡 When to Use This Script?

✅ **Understanding Terraform resource structure** in a large state file.\
✅ **Verifying instance counts** before applying changes.\
✅ **Detecting duplicate or unnecessary resources**.\
✅ **Comparing Terraform infrastructure** across deployments.\
✅ **Exporting Terraform resource inventory for audits and reporting.**


