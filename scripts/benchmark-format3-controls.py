#!/usr/bin/env python3
"""Add two isolated creation/index/export observations to each completed query case."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('format3_benchmark', ROOT / 'scripts/benchmark-format3.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--report', type=Path, help='Refresh the Markdown/JSON report after each case')
    parser.add_argument('--case', help='Optional dataset/variant filter for a smoke run')
    parser.add_argument('--reference', type=Path, default=ROOT / 'benchmark-data/format3-reference')
    args = parser.parse_args()
    base = args.input.resolve()
    manifest = json.loads((args.reference / 'manifest.json').read_text())
    reference = args.reference / 'distribution'
    for name, digest in manifest['files'].items():
        if bench.digest(reference / name) != digest: raise RuntimeError(f'Reference changed: {name}')
    distribution = base / 'distribution'
    for name, digest in json.loads((base / 'build.json').read_text())['libraries'].items():
        if bench.digest(distribution / name) != digest: raise RuntimeError(f'Format-3 library changed: {name}')
    worker = base / 'controls-worker.jar'
    bench.worker_jar(next((ROOT / 'build/install/ibx/lib').glob('ibx-*.jar')), worker)
    java = str(Path(os.environ.get('JAVA_HOME', '/Users/stefan/.sdkman/candidates/java/21.0.7-tem')) / 'bin/java')
    for source in sorted(base.glob('*/*/config.json')):
        case = source.parent
        if args.case and str(case.relative_to(base)) != args.case: continue
        if not (case / 'complete').exists(): raise RuntimeError(f'Query case not complete: {case}')
        original = json.loads(source.read_text())
        for repeat in (1, 2):
            output = case / 'controls' / f'repeat-{repeat}'
            output.mkdir(parents=True, exist_ok=True)
            config = dict(original, output=str(output), controlsOnly=True)
            config_file = output / 'config.json'
            if (output / 'complete').exists():
                if json.loads(config_file.read_text()) != config: raise RuntimeError(f'Changed controls: {output}')
                continue
            config_file.write_text(json.dumps(config, indent=2))
            libraries = reference if config['reference'] else distribution
            print(f'controls {case.relative_to(base)} repeat {repeat + 1}', flush=True)
            with (output / 'worker.log').open('w') as log:
                subprocess.run([java, '-Xmx384m', '-cp', str(worker) + os.pathsep + str(libraries / 'lib/*'),
                                'ch.interlis.ibx.benchmark.OptimizationBenchmark', str(config_file)],
                               cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
            # The extra observation is a measurement artifact, not another benchmark input.
            (output / 'data.ibx').unlink()
        if args.report:
            subprocess.run(['python3', str(ROOT / 'scripts/report-format3.py'), str(base), str(args.report)], check=True)


if __name__ == '__main__': main()
