# TWIX: Reconstructing Structured Data from Templatized Documents

[![Paper](https://img.shields.io/badge/Paper-arXiv-red)](https://arxiv.org/abs/2501.06659)

TWIX is a tool for automatically extracting strucutred data from templatized documents that are programmatically generated by populating fields in a visual template. TWIX reverse-engineers the underlying template, and then perform data extraction.  

1. A Python package for running production pipelines from the Python code
2. By default, TWIX offers end-to-end APIs that enable direct extraction of structured data from PDFs without requiring labels  
3. TWIX allows users to interactively modify the predicted template to improve data extraction
4. TWIX is 700x faster, 5,000x cheaper, and 25% more accurate than GPT-4 Vision for extracting information from a large document collection with 817 pages  

![TWIX Figure](docs/assets/readme_example.jpg)



# 🚀 Getting Started

If you want to use TWIX as a Python package:

## Prerequisites
- Python 3.10 or later
- OpenAI API key

1. Clone the repository

```bash
git clone https://github.com/yiminl18/TWIX.git
```

2. Install packages. 

```bash
pip install -e . 
```

3. Set OpenAI API key as environment variable

[You can refer to this document](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)


# TWIX API Reference

This document provides an overview of the available APIs in the TWIX Python package. Each API is described with its functionality, parameters, and return values.

---

## **API List**

```python
__all__ = [
    "predict_field",
    "predict_template",
    "extract_data",
    "extract_phrase",
    "transform",
    "remove_template_node",
    "modify_template_node",
    "add_fields",
    "remove_fields"
]
```

Below is a detailed description of each API:

---

### **1. extract_phrase**

Extracts phrases from PDFs by using OCR tools.

- **Parameters:**
  - `data_files` (list): Stores a list of paths to documents that are created using the same template.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.
  - `page_limit` (int, optional): Specifies how many pages to extract. By default, it extracts all pages of a document.
- **Returns:**
  - `list`: A list of phrases. The raw extracted phrases and their bounding box are also written in the result folder.

---

### **2. predict_field**

Predicts a list of fields from documents. Fields refer to phrases in table headers or keywords in key-value pairs.

- **Parameters:**
  - `data_files` (list): Stores a list of paths to documents that are created using the same template.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.
- **Returns:**
  - `list`: A list of predicted phrases. TWIX also writes the results in the local result folder, naming the file as `twix_key.txt`.

---

### **3. predict_template**

Predicts the template from documents. A template is defined as a tree (refer to the paper for details) and stored as a JSON. Each tree node (JSON object) corresponds to the abstract of a data block, storing the type and fields of the node.

- **Parameters:**
  - `data_files` (list): Stores a list of paths to documents that are created using the same template.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.
- **Returns:**
  - `list`: The template as a list of nodes, stored locally in the result folder, naming the file as `template.json`.

---

### **4. extract_data**

Extracts data based on a template.

- **Parameters:**
  - `data_files` (list): Stores a list of paths to documents that are created using the same template.
  - `template` (list, optional): The template output from `predict_template`. If not specified, TWIX will look in the local result folder to read the predicted template.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.
- **Returns:**
  - `dict`: A dictionary of extraction results, where the key is the file path, and the value is the extraction object of that file. Each extraction object is a list of data blocks containing either table blocks or key-value blocks. Results will be written locally in the result folder, naming the file as `extracted.json`.

---

### **5. transform**

Provides an end-to-end API to directly extract data from PDFs.

- **Parameters:**
  - `data_files` (list): Stores a list of paths to documents that are created using the same template.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.
- **Returns:**
  - `fields` (list): A list of strings representing the predicted fields.
  - `template` (list): The template as a list of nodes, stored locally in the result folder, naming the file as `template.json`.
  - `extraction_object` (dict): A dictionary of extraction results, where the key is the file path, and the value is the extraction object of that file. Each extraction object is a list of data blocks containing either table blocks or key-value blocks. Results will be written locally in the result folder, naming the file as `extracted.json`.

---

### **6. add_fields**

Allows users to add fields to the predicted fields.

- **Parameters:**
  - `added_fields` (list): A list of fields to add based on the predicted fields.
  - `data_files` (list, optional): Stores a list of paths to documents that are created using the same template. At least one of `data_files` or `result_folder` must be specified.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.

---

### **7. remove_fields**

Allows users to delete fields from the predicted fields.

- **Parameters:**
  - `removed_fields` (list): A list of fields to delete based on the predicted fields.
  - `data_files` (list, optional): Stores a list of paths to documents that are created using the same template. At least one of `data_files` or `result_folder` must be specified.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.

---

### **8. remove_template_node**

Allows users to remove nodes in the predicted template.

- **Parameters:**
  - `node_ids` (list): A list of node IDs. Each node ID is an integer.
  - `data_files` (list, optional): Stores a list of paths to documents that are created using the same template. At least one of `data_files` or `result_folder` must be specified.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.

---

### **9. modify_template_node**

Allows users to update nodes in the predicted template.

- **Parameters:**
  - `node_id` (int): The integer node ID to update.
  - `type` (str): The type of the node to update, either `"kv"` or `"table"`.
  - `fields` (list): A list of fields (strings) to update.
  - `data_files` (list, optional): Stores a list of paths to documents that are created using the same template. At least one of `data_files` or `result_folder` must be specified.
  - `result_folder` (str, optional): The path to store results. If not specified, TWIX will automatically create a folder under `root/tests/out/file_name/`.

---

