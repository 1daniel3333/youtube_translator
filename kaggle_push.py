import os
import json
import sys
from kaggle.api.kaggle_api_extended import KaggleApi

# Set these variables
KAGGLE_NOTEBOOK_ID = os.environ.get('KAGGLE_NOTEBOOK_ID')  # e.g. 'username/notebook-slug'
PYTHON_SCRIPT_PATH = 'Youtube_Translation.py'
KAGGLE_JSON_PATH = os.path.expanduser('~/.kaggle/kaggle.json')

# Ensure kaggle.json exists
if not os.path.exists(KAGGLE_JSON_PATH):
    kaggle_json_env = os.environ.get('KAGGLE_JSON')
    if kaggle_json_env:
        os.makedirs(os.path.dirname(KAGGLE_JSON_PATH), exist_ok=True)
        with open(KAGGLE_JSON_PATH, 'w') as f:
            f.write(kaggle_json_env)
        os.chmod(KAGGLE_JSON_PATH, 0o600)
    else:
        print('kaggle.json not found. Please set KAGGLE_JSON env variable or place kaggle.json in ~/.kaggle/')
        sys.exit(1)

api = KaggleApi()
api.authenticate()

# Download the existing notebook metadata
notebook = api.kernels_pull(KAGGLE_NOTEBOOK_ID, path='kaggle_notebook', metadata=True)
notebook_dir = 'kaggle_notebook/'
notebook_metadata_path = os.path.join(notebook_dir, 'kernel-metadata.json')
notebook_code_path = os.path.join(notebook_dir, 'script.py')

# Replace the code with the latest script
with open(PYTHON_SCRIPT_PATH, 'r', encoding='utf-8') as src, open(notebook_code_path, 'w', encoding='utf-8') as dst:
    dst.write(src.read())

# Push the updated notebook
api.kernels_push(notebook_dir)
print('Kaggle notebook updated successfully.') 