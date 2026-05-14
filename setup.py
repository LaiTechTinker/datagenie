import os

# Root project folder
ROOT_DIR = "backend"

# Folder structure and files
structure = {
    "api": [
        "__init__.py",
        "auth.py",
        "automl.py",
        "datasets.py",
        "reports.py",
        "visualizations.py",
    ],
    "models": [
        "__init__.py",
        "dataset.py",
        "job.py",
        "report.py",
        "user.py",
    ],
    "services": [
        "__init__.py",
        "auth_service.py",
        "automl_service.py",
        "dataset_service.py",
        "report_service.py",
        "viz_service.py",
    ],
    "sockets": [
        "__init__.py",
        "training.py",
    ],
    "utils": [
        "__init__.py",
        "decorators.py",
        "errors.py",
        "jwt_utils.py",
        "parsers.py",
    ]
}

# Root-level files
root_files = [
    ".env.example",
    ".gitignore",
    "app.py",
    "config.py",
    "extensions.py",
    "README.md",
    "requirements.txt",
]

def create_project():
    # Create root directory
    os.makedirs(ROOT_DIR, exist_ok=True)

    # Create folders and files
    for folder, files in structure.items():
        folder_path = os.path.join(ROOT_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)

        for file in files:
            file_path = os.path.join(folder_path, file)

            # Create empty file
            with open(file_path, "w") as f:
                pass

    # Create root files
    for file in root_files:
        file_path = os.path.join(ROOT_DIR, file)

        with open(file_path, "w") as f:
            pass

    print(" Backend project structure created successfully!")

if __name__ == "__main__":
    create_project()