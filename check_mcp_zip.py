import zipfile
import json

def check_zip(zip_path):
    required_manifest_keys = {
        "name",
        "version",
        "description",
        "entry",
        "toolkit_version",
        "dxt_version",
        "author",
        "server"
    }
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        namelist = z.namelist()
        
        # 1. Check manifest.json at root
        manifest_candidates = [f for f in namelist if f.lower() == 'manifest.json' or f.lower().endswith('/manifest.json')]
        if not manifest_candidates:
            print("❌ manifest.json not found in the ZIP root or subfolders.")
            return False
        if 'manifest.json' not in namelist:
            print("⚠️ Warning: manifest.json is not at the root of the ZIP.")
            # but continue checking anyway

        # 2. Check no extra root folder wrapping files:
        # Check if all files have a common root folder
        roots = set(f.split('/')[0] for f in namelist if f.strip())
        if len(roots) == 1:
            root_folder = next(iter(roots))
            root_contents = [f for f in namelist if f.startswith(root_folder + '/')]
            if len(root_contents) == len(namelist):
                print(f"⚠️ Warning: all files are inside a root folder '{root_folder}'. Expected manifest.json at root.")
        else:
            print("✅ No extra root folder wrapping all files detected.")
        
        # 3. Read and validate manifest.json
        manifest_file = 'manifest.json' if 'manifest.json' in namelist else manifest_candidates[0]
        with z.open(manifest_file) as mf:
            data_bytes = mf.read()
            
            # Check UTF-8 encoding without BOM
            try:
                text = data_bytes.decode('utf-8-sig')  # utf-8-sig removes BOM if present
                if data_bytes.startswith(b'\xef\xbb\xbf'):
                    print("⚠️ manifest.json has BOM, recommended to remove it.")
                else:
                    print("✅ manifest.json is UTF-8 encoded without BOM.")
            except UnicodeDecodeError as e:
                print(f"❌ manifest.json is not UTF-8 encoded: {e}")
                return False

            # Validate JSON
            try:
                manifest_json = json.loads(text)
            except json.JSONDecodeError as e:
                print(f"❌ manifest.json contains invalid JSON: {e}")
                return False

            # Check required keys
            keys = set(manifest_json.keys())
            missing_keys = required_manifest_keys - keys
            if missing_keys:
                print(f"❌ manifest.json is missing required keys: {missing_keys}")
                return False
            else:
                print("✅ manifest.json contains all required keys.")

            # 4. Check that entry file exists
            entry_path = manifest_json.get("entry")
            if entry_path not in namelist:
                print(f"❌ Entry path '{entry_path}' from manifest.json not found inside ZIP.")
                return False
            else:
                print(f"✅ Entry path '{entry_path}' found in ZIP.")

    print("🎉 All checks passed successfully!")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python check_mcp_zip.py your_extension.zip")
    else:
        zip_file = sys.argv[1]
        check_zip(zip_file)
