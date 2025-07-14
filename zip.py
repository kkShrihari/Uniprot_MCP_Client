import zipfile
import os

output_zip = "Profetch.dxt"
with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write("manifest.json", arcname="manifest.json")
    for foldername, _, filenames in os.walk("Profetch"):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, ".")
                z.write(filepath, arcname)

print("✅ Created Profetch.dxt")
