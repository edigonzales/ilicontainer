"""Assemble tested CLI/plugin distributions, matching library sources and provenance."""

import hashlib, json, pathlib, shutil, subprocess, zipfile

root = pathlib.Path(__file__).resolve().parents[1]
out = root / "build/release"
out.mkdir(parents=True, exist_ok=True)
lib = next((root / "build/install/ibx/lib").glob("iox-ibx-*.jar"))
source = next((root / "build/release-dependencies").glob("*sources.jar"))


def manifest(p):
    with zipfile.ZipFile(p) as z:
        return dict(
            line.split(": ", 1)
            for line in z.read("META-INF/MANIFEST.MF").decode().splitlines()
            if ": " in line
        )


a, b = manifest(lib), manifest(source)
assert a["Source-Commit"] == b["Source-Commit"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


info = dict(
    formatVersion=5,
    commit=subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip(),
    ioxIbx=dict(
        version=a["Implementation-Version"],
        commit=a["Source-Commit"],
        binarySha256=sha(lib),
        sourceSha256=sha(source),
    ),
    runtimeJars={
        p.name: sha(p) for p in sorted((root / "build/install/ibx/lib").glob("*.jar"))
    },
)
for p in list((root / "build/distributions").glob("*.zip")) + list(
    (root / "build").glob("ibx-qgis-0.6.0.zip")
):
    shutil.copy2(p, out / p.name)
with zipfile.ZipFile(out / "ibx-format5-sources.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
        .decode()
        .split("\0")
    ):
        if name and (root / name).is_file():
            z.write(root / name, name)
    with zipfile.ZipFile(source) as dep:
        for name in dep.namelist():
            if not name.endswith("/"):
                z.writestr("dependencies/iox-ibx/" + name, dep.read(name))
    z.write(source, "dependencies/" + source.name)
    z.writestr("provenance.json", json.dumps(info, indent=2))
(out / "provenance.json").write_text(json.dumps(info, indent=2) + "\n")
(out / "SHA256SUMS").write_text(
    "".join(
        sha(p) + "  " + p.name + "\n"
        for p in sorted(out.iterdir())
        if p.is_file() and p.name != "SHA256SUMS"
    )
)
print(out)
