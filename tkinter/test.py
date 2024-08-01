import os

def run_script(script_name, project_path, folder_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    # Make sure the script is executable
    os.system(f"chmod +x {script_path}")
    
    # Construct the command
    command = f"{script_path} {project_path} {folder_name}"
    
    # Execute the command
    result = os.system(command)
    
    # Check the result 
    if result == 0:
        print(f"{script_name} executed successfully.")
    else:
        print(f"Error executing {script_name} with exit code: {result}")

if __name__ == "__main__":
    project_path = "/home/amiche/Pictures/outputs_test/josue/images"
    
    # Dynamically extract project_path and folder_name
    project_path, folder_name = os.path.split(os.path.dirname(project_path))
    
    # If the output_path is simply "/home/amiche/Pictures/test/meubles"
    # project_path, folder_name = os.path.split(output_path)
    
    print(f"Project Path: {project_path}")
    print(f"Folder Name: {folder_name}")
    run_script("colmap_demo.sh", project_path, folder_name)