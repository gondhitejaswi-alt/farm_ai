"""
Restore your OLD trained models + datasets into this project.

The v10 zip shipped with an EMPTY ml/saved_models/ folder and no CSV files,
so yield predictions fall back to the built-in estimator. This script copies
everything back from your old project (zip file OR extracted folder) WITHOUT
overwriting anything newer.

Usage (Windows/Mac/Linux):
    python restore_old_data.py "C:\\path\\to\\farm_ai_LIVE_v7.zip"
    python restore_old_data.py "C:\\path\\to\\old_extracted_folder"
"""
import os, sys, shutil, zipfile, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
WANT_DIRS = [("ml/saved_models", "ml/saved_models")]
WANT_EXT = (".csv", ".pkl", ".joblib", ".json", ".h5", ".keras", ".npy")
WANT_DATA_DIR = "data"
SKIP_NAMES = {"crop_data.py", "generate_sample.py", "merge_datasets.py", "__init__.py"}


def find_project_root(base):
    """Locate the folder that contains 'agents' and 'ml' (the old farm_ai root)."""
    for dp, dns, _ in os.walk(base):
        if "agents" in dns and ("ml" in dns or "data" in dns):
            return dp
    return None


def copy_tree(src, dst):
    n = 0
    for dp, _, files in os.walk(src):
        rel = os.path.relpath(dp, src)
        for f in files:
            s = os.path.join(dp, f)
            d = os.path.normpath(os.path.join(dst, rel, f))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            if not os.path.exists(d):
                shutil.copy2(s, d)
                n += 1
    return n


def main(arg):
    tmp = None
    if os.path.isfile(arg) and arg.lower().endswith(".zip"):
        tmp = tempfile.mkdtemp(prefix="farm_old_")
        print("Extracting old zip ...")
        with zipfile.ZipFile(arg) as z:
            for i in z.infolist():
                name = i.filename.replace("\\", "/")
                p = os.path.join(tmp, name)
                if name.endswith("/"):
                    os.makedirs(p, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    with open(p, "wb") as f:
                        f.write(z.read(i))
        base = tmp
    elif os.path.isdir(arg):
        base = arg
    else:
        print("Give the path to the old .zip or the old project folder.")
        return 1

    old = find_project_root(base)
    if not old:
        print("Could not find an old farm_ai project (folder with agents/ and ml/) inside:", arg)
        return 1
    print("Old project found at:", old)

    total = 0
    for s, d in WANT_DIRS:
        sp = os.path.join(old, *s.split("/"))
        if os.path.isdir(sp):
            n = copy_tree(sp, os.path.join(ROOT, *d.split("/")))
            print(f"  models  : {n} file(s) copied from {s}")
            total += n
        else:
            print(f"  models  : {s} not found in old project")

    od = os.path.join(old, WANT_DATA_DIR)
    n = 0
    if os.path.isdir(od):
        for f in os.listdir(od):
            sp = os.path.join(od, f)
            if os.path.isfile(sp) and f.lower().endswith(WANT_EXT) and f not in SKIP_NAMES:
                dp = os.path.join(ROOT, "data", f)
                if not os.path.exists(dp):
                    shutil.copy2(sp, dp)
                    n += 1
    print(f"  datasets: {n} file(s) copied from data/")
    total += n

    # Old user history (if the old app ever saved one)
    for rel in ("data/user_data",):
        sp = os.path.join(old, *rel.split("/"))
        if os.path.isdir(sp):
            k = copy_tree(sp, os.path.join(ROOT, *rel.split("/")))
            print(f"  history : {k} file(s) copied from {rel}")
            total += k

    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nDone. Nothing was overwritten." if total else "\nNothing new to copy (already restored or old project had no data).")
    print("Restart the app:  python -m streamlit run dashboard/streamlit_app.py")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
