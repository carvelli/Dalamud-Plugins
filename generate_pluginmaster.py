import json
import os
from os.path import getmtime
from zipfile import ZipFile

plugin_names = ["SliceIsRight"]

def copy_plugins():
    for plugin_name in plugin_names:
        for dirpath, _, filenames in os.walk(f"../{plugin_name}/dist/{plugin_name}"):
            if len(filenames) == 0 or "latest.zip" not in filenames:
                continue
               
            os.makedirs(name=f"dist/{plugin_name}", exist_ok=True)

            with ZipFile(f"{dirpath}/latest.zip", "r") as zin:
                with ZipFile(f"dist/{plugin_name}/latest.zip", "w") as zout:
                    for item in zin.infolist():
                        buffer = zin.read(item.filename)
                        if (item.filename[-10:] != ".deps.json"):
                            zout.writestr(item, buffer)

def extract_manifests():
    manifests = []
    for plugin_name in plugin_names:
        with ZipFile(f"dist/{plugin_name}/latest.zip", "r") as z:
            manifest = json.loads(z.read(f"{plugin_name}.json").decode())
            manifest['InternalName'] = plugin_name
            manifests.append(manifest)

    return manifests

def add_extra_fields(manifests):
    DEFAULTS = {
        "IsHide": False,
        "IsTestingExclusive": False,
        "ApplicableVersion": "any"
    }

    for manifest in manifests:
        download_url = "https://raw.githubusercontent.com/carvelli/Dalamud-Plugins/master/dist/{name}/latest.zip"

        manifest["DownloadLinkInstall"] = manifest["DownloadLinkTesting"] = manifest["DownloadLinkUpdate"] = download_url.format(
            name=manifest["InternalName"]
        )

        for k, v in DEFAULTS.items():
            if k not in manifest:
                manifest[k] = v

def update_last_updated(manifests):
    for manifest in manifests:
        latest = f"../{manifest['InternalName']}/dist/{manifest['InternalName']}/latest.zip"
        modified = int(getmtime(latest))

        if "LastUpdated" not in manifest or modified != int(manifest["LastUpdated"]):
            manifest["LastUpdated"] = str(modified)

def dump_master(manifests):
    with open(f"dist/pluginmaster.json", "w") as f:
        json.dump(manifests, f, indent=4)


if __name__ == "__main__":
    copy_plugins()
    manifests = extract_manifests()

    add_extra_fields(manifests)
    update_last_updated(manifests)

    dump_master(manifests)