#!/usr/bin/env python3
"""Explicit, resumable Format-3 comparison. Each worker uses exactly one isolated library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    'dmav': ('benchmark-data/dmav/source.xtf', 'DMAV_Toleranzstufen_V1_1.Toleranzstufen.Toleranzstufe', 'Geometrie'),
    'fixpoints': ('benchmark-data/fixpoints-2542/source.xtf', 'DMAV_FixpunkteAVKategorie3_V1_0.FixpunkteAVKategorie3.LFP3', 'Geometrie'),
    'localities': ('benchmark-data/localities/AMTOVZ_INTERLIS24/OfficialIndexOfLocalities_V1_0.xtf', 'OfficialIndexOfLocalities_V1_0.OfficialIndexOfLocalities.Locality', 'Geometry'),
    'million': ('benchmark-data/format3-million.xtf', 'Tiny.Data.Item', 'point'),
}

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def synthetic(path):
    if path.exists(): return
    fixture = (ROOT / 'src/test/resources/tiny.xtf').read_text()
    with path.open('w') as out:
        out.write(fixture.split('<ili:datasection>')[0])
        out.write('<ili:datasection><Tiny:Data ili:bid="million">')
        for i in range(1_000_000):
            out.write(f'<Tiny:Item ili:tid="p{i}"><Tiny:point><geom:coord><geom:c1>{i % 1000}</geom:c1><geom:c2>{i // 1000}</geom:c2></geom:coord></Tiny:point></Tiny:Item>')
        out.write('</Tiny:Data></ili:datasection></ili:transfer>')


def worker_jar(library, target):
    prefixes = ('ch/interlis/ilicontainer/benchmark/OptimizationBenchmark',
                'ch/interlis/ilicontainer/benchmark/RangeServer')
    with zipfile.ZipFile(library) as src:
        entries = {name: src.read(name) for name in src.namelist()
                   if name.startswith(prefixes) and name.endswith('.class')}
    if target.exists():
        with zipfile.ZipFile(target) as saved:
            actual = {name: saved.read(name) for name in saved.namelist()}
        if actual != entries: raise RuntimeError(f'Saved measurement worker differs: {target}')
        return
    with zipfile.ZipFile(target, 'w') as out:
        for name, data in sorted(entries.items()):
            out.writestr(zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)), data)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', action='append', choices=DATASETS)
    p.add_argument('--output', type=Path, default=ROOT / 'benchmark-data/format3')
    p.add_argument('--reference', type=Path, default=ROOT / 'benchmark-data/format3-reference')
    p.add_argument('--repeats', type=int, default=3)
    p.add_argument('--delays', default='-1,0,20,80', help='-1 means local; others HTTP request delay in ms')
    p.add_argument('--only', help='Variant prefix filter, e.g. reference or hilbert-str')
    a = p.parse_args()
    if a.repeats < 1: p.error("--repeats must be positive")
    if any(int(v) not in (-1, 0, 20, 80) for v in a.delays.split(',')): p.error("--delays supports -1,0,20,80")
    a.output = a.output.resolve(); a.output.mkdir(parents=True, exist_ok=True)
    ref_manifest = json.loads((a.reference / 'manifest.json').read_text())
    ref_dist = a.reference / 'distribution'
    for name, sha in ref_manifest['files'].items():
        if digest(ref_dist / name) != sha: raise RuntimeError(f'Reference changed: {name}')
    dist = a.output / 'distribution'
    if not dist.exists(): shutil.copytree(ROOT / 'build/install/ilicontainer', dist)
    libraries = {str(f.relative_to(dist)): digest(f) for f in sorted((dist / 'lib').glob('*.jar'))}
    if (a.output / 'build.json').exists():
        saved = json.loads((a.output / 'build.json').read_text())
        if saved['libraries'] != libraries: raise RuntimeError('Saved distribution changed; use a fresh output directory')
    (a.output / 'build.json').write_text(json.dumps({'libraries': libraries, 'reference': ref_manifest}, indent=2))
    worker = a.output / 'worker.jar'
    worker_jar(next((dist / 'lib').glob('ilicontainer-*.jar')), worker)
    java = str(Path(os.environ.get('JAVA_HOME', '/Users/stefan/.sdkman/candidates/java/21.0.7-tem')) / 'bin/java')
    variants = [('reference', True, False, 'x', False, 262144),
                ('x-direct', False, False, 'x', False, 262144),
                ('x-prefetch', False, True, 'x', False, 262144),
                ('str', False, True, 'str', False, 262144),
                ('hilbert-str', False, True, 'str', True, 262144)]
    variants += [('hilbert-str', False, True, 'str', True, n) for n in (65536, 1048576, 4194304)]
    for dataset in a.dataset or ['dmav', 'fixpoints', 'localities', 'million']:
        source, cls, attr = DATASETS[dataset]
        source = ROOT / source
        if dataset == 'million': synthetic(source)
        for encoding in ['iom', 'wkb']:
            for name, reference, prefetch, packing, hilbert, chunk in variants:
                if a.only and not name.startswith(a.only): continue
                if dataset == "million" and name not in ("reference", "x-direct"): continue
                output = a.output / dataset / f'{name}-{encoding}-{chunk}'
                output.mkdir(parents=True, exist_ok=True)
                config = dict(input=str(source), output=str(output), **{'class': cls}, attribute=attr,
                              encoding=encoding, chunkSize=chunk, reference=reference, prefetch=prefetch,
                              packing=packing, hilbert=hilbert, repeats=a.repeats,
                              delays=[int(n) for n in a.delays.split(',')], crs='EPSG:2056',
                              windowsFile=str(a.output / dataset / 'windows.json'),
                              modelPaths=['https://models.geo.admin.ch', 'https://models.interlis.ch'] if dataset != 'million' else [],
                              modelFiles=[str(ROOT / 'src/test/resources/Tiny.ili')] if dataset == 'million' else [])
                if dataset == "million": config["directoryOnly"] = True
                config_file = output / 'config.json'
                if (output / 'complete').exists():
                    if json.loads(config_file.read_text()) != config:
                        raise RuntimeError(f'Completed case has different parameters: {output}; use a new output directory')
                    continue
                config_file.write_text(json.dumps(config, indent=2))
                selected_worker = worker
                if dataset == 'million':
                    selected_worker = a.output / 'directory-worker.jar'
                    worker_jar(next((ROOT / 'build/install/ilicontainer/lib').glob('ilicontainer-*.jar')), selected_worker)
                cp = str(selected_worker) + os.pathsep + str((ref_dist if reference else dist) / 'lib/*')
                print(f'{dataset} {output.name}', flush=True)
                with (output / 'worker.log').open('w') as log:
                    subprocess.run([java, '-Xmx384m', '-cp', cp,
                                    'ch.interlis.ilicontainer.benchmark.OptimizationBenchmark', str(config_file)],
                                   cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)

if __name__ == '__main__': main()
