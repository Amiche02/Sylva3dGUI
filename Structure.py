import os
import json

def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    structure = {}
    for dirpath, dirnames, filenames in os.walk(rootdir):
        folder = os.path.relpath(dirpath, rootdir)
        subdir = structure
        if folder != ".":
            for part in folder.split(os.sep):
                subdir = subdir.setdefault(part, {})
        for dirname in dirnames:
            subdir[dirname] = {}
        for filename in filenames:
            subdir[filename] = None
    return structure

def main():
    project_root = input("Enter the root directory of your project: ")
    directory_structure = get_directory_structure(project_root)
    with open("project_structure.json", "w") as outfile:
        json.dump(directory_structure, outfile, indent=4)
    print(f"Project structure has been saved to project_structure.json")

if __name__ == "__main__":
    main()
