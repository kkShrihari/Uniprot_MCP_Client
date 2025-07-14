import zipfile
import json

with zipfile.ZipFile("Profetch.dxt", "r") as z:
    with z.open("manifest.json") as f:
        data = f.read().decode("utf-8")
        print(data)
        manifest = json.loads(data)
        print("\nKeys in manifest.json:", manifest.keys())
