import os
import json
import requests
import subprocess

def ingest_project_data(project_id):
    """
    Ingest all files from a project's folder in the Docker container's file system.
    
    Args:
        project_id (str): The project identifier (e.g., "Justin")
    
    Returns:
        dict: Summary of the ingestion process with success and error counts
    """
    container_project_folder = f"/mounted_autohint_configs/{project_id}"
    container_name = "rag-server"

    print(f"Accessing files in container at: {container_project_folder}")
    
    check_dir_cmd = f"docker exec {container_name} bash -c '[ -d {container_project_folder} ] && echo exists || echo not_found'"
    dir_check_result = subprocess.run(check_dir_cmd, shell=True, capture_output=True, text=True)
    
    if "not_found" in dir_check_result.stdout:
        print(f"Error: Project folder {container_project_folder} not found in container")
        return {"success": 0, "error": 0, "status": "folder_not_found"}

    # Check and create collection if needed
    if not collection_exists(project_id):
        create_collection_response = create_collection(project_id)
        if create_collection_response.get("status_code") not in [200, 201]:
            print(f"Warning: Collection creation failed: {create_collection_response}")
            return {"success": 0, "error": 0, "status": "collection_creation_failed"}

    # Get file list
    list_files_cmd = f"docker exec {container_name} find {container_project_folder} -type f -not -path \"*/\\.*\" | sort"
    file_list_result = subprocess.run(list_files_cmd, shell=True, capture_output=True, text=True)

    if file_list_result.returncode != 0:
        print(f"Error listing files in container: {file_list_result.stderr}")
        return {"success": 0, "error": 0, "status": "file_list_error"}

    file_paths = file_list_result.stdout.strip().split('\n')
    success_count = error_count = skipped_count = 0

    for file_path in file_paths:
        if not file_path:
            continue
        filename = os.path.basename(file_path)
        if filename == 'config.yaml' or filename.startswith('.'):
            skipped_count += 1
            print(f"Skipping {filename} (config file or hidden)")
            continue

        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            local_file_path = os.path.join(temp_dir, filename)
            copy_cmd = f"docker cp {container_name}:{file_path} {local_file_path}"
            copy_result = subprocess.run(copy_cmd, shell=True)

            if copy_result.returncode != 0:
                print(f"Error copying {filename} from container")
                error_count += 1
                continue

            if upload_document_to_project(local_file_path, project_id):
                success_count += 1
            else:
                error_count += 1

    summary = {
        "success": success_count,
        "error": error_count,
        "skipped": skipped_count,
        "status": "completed"
    }

    print(f"\nContainer files ingestion complete: {success_count} uploaded, {error_count} errors, {skipped_count} skipped")
    return summary


def collection_exists(name):
    """Check if collection exists before creating it"""
    url = "http://localhost:8082/collections"
    try:
        response = requests.get(url)
        if response.status_code == 200 and response.json().get("collections"):
            return any(col["collection_name"] == name for col in response.json()["collections"])
    except Exception as e:
        print(f"Error checking collections: {e}")
    return False


def create_collection(collection_name):
    """Create a collection for document storage"""
    url = "http://localhost:8082/collections"
    
    # The API expects a direct list of collection names, not a dictionary with a 'collection_names' key
    data = [collection_name]  # Send as an array/list directly
    
    try:
        print(f"Creating collection {collection_name}...")
        response = requests.post(url, json=data)
        return {
            "status_code": response.status_code,
            "response": response.json() if response.content else {}
        }
    except Exception as e:
        print(f"Error creating collection: {e}")
        return {"status_code": 500, "error": str(e)}


def upload_document_to_project(file_path, project_id):
    """Upload a document to a project-specific collection"""
    url = "http://localhost:8082/documents"  # Note: Using port 8082 for ingestion server
    
    filename = os.path.basename(file_path)
    
    # Skip certain files
    if filename.startswith('.') or not os.path.isfile(file_path):
        print(f"Skipping {filename} (not a file or hidden)")
        return False
    
    try:
        with open(file_path, 'rb') as file:
            # Important: In RAG v2, documents are passed as a list
            files = {'documents': (filename, file)}
            
            # # Using the PATCH endpoint to replace files if they already exist
            # data = {
            #     'data': json.dumps({
            #         'collection_name': project_id
            #     })
            # }
            # Custom extraction and split settings
            payload = {
                "collection_name": project_id,
                "extraction_options": {
                    "extract_text": True,
                    "extract_tables": False,
                    "extract_charts": False,
                    "extract_images": False,
                    "extract_method": "pdfium",
                    "text_depth": "page"
                },
                # "split_options": {
                #     "chunk_size": 1024,
                #     "chunk_overlap": 150
                # }
            }

            data = {'data': json.dumps(payload)}
            
            print(f"Uploading {filename} to project/collection {project_id}...")
            response = requests.patch(url, files=files, data=data)
            
            print(f"Status: {response.status_code}")
            if response.content:
                print(f"Response: {response.json()}")
            return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error uploading {filename}: {e}")
        return False

import time
import requests

def wait_for_ingest_ready(timeout=120):
    url = "http://localhost:7670/v1/health/ready"
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                print("✅ nv-ingest is ready.")
                return True
        except Exception:
            pass
        print("⏳ Waiting for nv-ingest to be ready...")
        time.sleep(2)
    print("❌ Timed out waiting for nv-ingest.")
    return False