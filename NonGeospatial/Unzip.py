import glob
import os
import zipfile
import shutil
input_zip_path = r"\path\to.zip"
 
def add_filetype_to_list(folder, file_type, list_of_files):
    # print(f"Globbing files in folder {folder}, format: {file_type}")
    folder_list_of_files = glob.glob('{}/*.{}'.format(folder, file_type))
    # print(f"found {len(folder_list_of_files)} files")

    if len(folder_list_of_files) > 0:
        for ffile in folder_list_of_files:
            list_of_files.append(ffile)

    return list_of_files

def extract_zip(input_zip_file, output_directory):
    def _additional_zips():
        internal_zip_files = []
        folders_to_search = [os.path.join(output_directory, o) for o in os.listdir(output_directory)
                             if os.path.isdir(os.path.join(output_directory, o))]
        folders_to_search.append(output_directory)

        for fldr in folders_to_search:
            add_filetype_to_list(fldr, 'zip', internal_zip_files)

        # Decompress them
        for zip_path in internal_zip_files:
            zip_ref = zipfile.ZipFile(zip_path, 'r')
            extract_folder = os.path.dirname(zip_path)
            zip_ref.extractall(extract_folder)
            zip_ref.close()


    def gdb_not_in_gdb():
        is_gdb_content = []
        add_filetype_to_list(output_directory, 'gdbtable', is_gdb_content)
        if len(is_gdb_content) > 0:
            dest_dir = os.path.join(output_directory, 'temp.gdb')
            os.mkdir(dest_dir)

            # Iterate through files in the source directory
            for item in os.listdir(output_directory):
                source_path = os.path.join(output_directory, item)
                dest_path = os.path.join(dest_dir, item)
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, dest_path)  # copy2 preserves metadata

    # If the input file is not a zip format, then it is already decompressed
    if not input_zip_file.endswith(".zip"):
        shutil.copy2(input_zip_file, output_directory)
        return

    # Unzip the initial zip file
    zip_ref = zipfile.ZipFile(input_zip_file, 'r')
    zip_ref.extractall(output_directory)
    zip_ref.close()

    # Also locate any other zip files, that were within the original zip
    _additional_zips()

    # check for case where we now have a gdb's contents, but not inside a GDB
    gdb_not_in_gdb()

    return


# Walk through incoming folder and extract any zip files found
for root, dirs, files in os.walk(input_zip_path):
    for file in files:
        if file.endswith('.zip'):
            zip_path = os.path.join(root, file)
            extract_zip(zip_path, root)
            print(f"Unzipped: {file}")
 
print("Done.")
 
