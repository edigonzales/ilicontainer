#!/usr/bin/env python3
"""Summarize actual observations; never infer an unmeasured performance gain."""
import argparse
import hashlib
from datetime import datetime, timezone
from collections import defaultdict
import json
from pathlib import Path
import statistics
import struct
import zlib

def physical_storage(path):
    """Benchmark-only byte accounting; does not decode transfers or provide a legacy reader."""
    sections, keys, values = defaultdict(int), defaultdict(int), defaultdict(int)
    shared = 0
    with path.open('rb') as f:
        magic, version, features = struct.unpack('>8sii', f.read(16))
        if not ((magic == b'ILICONT1' and version in (1, 2, 3)) or (magic == b'IBXCONT1' and version == 4)) or features:
            raise ValueError('Unknown accounting layout')
        footer = 64 if version >= 3 else 40
        end = path.stat().st_size - footer
        while f.tell() < end:
            offset = f.tell()
            kind, length, crc = struct.unpack('>iqI', f.read(16))
            if length < 0 or offset + 16 + length > end: raise ValueError('Invalid frame')
            sections[kind] += 16 + length
            if kind not in (6, 7):
                f.seek(length, 1)
                continue
            payload = f.read(length)
            if zlib.crc32(payload) != crc: raise ValueError('Bad page CRC')
            pos = 0
            def integer():
                nonlocal pos
                value, = struct.unpack_from('>i', payload, pos); pos += 4
                return value
            count = integer()
            shared += 20
            previous = b''
            for _ in range(count):
                prefix = integer() if version >= 3 else 0
                n = integer()
                key_cost = 8 if version >= 3 else 4
                if n == -1:
                    overflow, = struct.unpack_from('>q', payload, pos)
                    ref_size = 16 if version >= 3 else 8
                    pos += ref_size; key_cost += ref_size
                    saved = f.tell(); f.seek(overflow)
                    typ, size, checksum = struct.unpack('>iqI', f.read(16))
                    suffix = f.read(size); f.seek(saved)
                    if typ != 11 or zlib.crc32(suffix) != checksum: raise ValueError('Invalid overflow')
                else:
                    if n < 0 or pos + n > len(payload): raise ValueError('Bad key length')
                    suffix = payload[pos:pos+n]; pos += n; key_cost += n
                key = previous[:prefix] + suffix
                category = ('leaf:' if kind == 6 else 'branch:') + chr(key[0])
                keys[category] += key_cost
                previous = key
                n = integer()
                size = (16 if version >= 3 else 8) if n == -1 else n
                if size < 0 or pos + size > len(payload): raise ValueError('Bad value length')
                pos += size; values[category] += 4 + size
            if pos != len(payload): raise ValueError('Trailing page bytes')
    if sum(sections.values()) + 16 + footer != path.stat().st_size: raise ValueError('Byte accounting mismatch')
    return dict(sectionBytes=dict(sections), keyBytes=dict(keys), valueBytes=dict(values),
                sharedIndexPageBytes=shared, headerFooterBytes=16+footer, fileBytes=path.stat().st_size)


p = argparse.ArgumentParser(description=__doc__)
p.add_argument('input', type=Path)
p.add_argument('output', type=Path)
p.add_argument('--expected-cases', type=int, default=52)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)
reports = []
lines = ['# Format-3-Vergleich', '', 'Laufzeiten sind Mediane der protokollierten Wiederholungen. Öffnen und Abfragen werden getrennt gemessen. `delay=-1` bezeichnet lokale Zugriffe. Cachezustände beziehen sich auf den Anwendungscache, nicht den Betriebssystemcache.', '', '| Datensatz / Variante | Vollständig | Core Bytes | mit Index Bytes | Erstellung ms | Roundtrip geprüft |', '|---|---:|---:|---:|---:|---:|']
counts = {}
input_digests, query_windows = {}, {}
for path in sorted(a.input.glob('*/*/results.json')):
    data = json.loads(path.read_text())
    dataset, variant = path.parent.parent.name, path.parent.name
    rows = data['rows']
    data['dataset'], data['variant'] = dataset, variant
    data['complete'] = (path.parent / 'complete').exists()
    data['additionalControls'] = []
    for r in rows:
        if r['operation'] in ('create', 'index', 'directory', 'export'): r['repeat'] = 0
    primary = {r['operation']: r for r in rows if r['operation'] in ('create', 'index', 'directory', 'export')}
    for repeat in (1, 2):
        control_path = path.parent / 'controls' / f'repeat-{repeat}'
        if not (control_path / 'complete').exists(): continue
        control = json.loads((control_path / 'results.json').read_text())
        if control['librarySha256'] != data['librarySha256']:
            raise ValueError(f'Controls use another library: {control_path}')
        for r in control['rows']:
            r['repeat'] = repeat
            if r['operation'] == 'create' and r['inputSha256'] != primary['create']['inputSha256']:
                raise ValueError(f'Controls use another input: {control_path}')
            if 'fileBytes' in r and r['fileBytes'] != primary[r['operation']]['fileBytes']:
                raise ValueError(f'Controls produced another file size: {control_path}')
        data['additionalControls'].append(control)
        rows.extend(control['rows'])
    data['controlsComplete'] = len(data['additionalControls']) == 2
    if data['complete']:
        parameters = data['parameters']
        expected = {(delay, repeat, cache) for delay in parameters['delays']
                    for repeat in range(parameters['repeats']) for cache in ('cold', 'warm')}
        queries = defaultdict(list)
        for row in rows:
            if row['operation'] == 'query': queries[row['query']].append(row)
        required = {'tid', 'fid'} if parameters.get('directoryOnly') else {'tid', 'fid', 'class'} | {f'bbox-{i}' for i in range(len(data['windows']))}
        if parameters['reference'] and parameters['encoding'] == 'iom': required.remove('fid')
        if set(queries) != required: raise ValueError(f'Missing query family: {path}')
        for query, samples in queries.items():
            actual = {(r['delayMillis'], r['repeat'], r['cache']) for r in samples}
            if actual != expected or len(samples) != len(expected):
                raise ValueError(f'Incomplete repetitions: {path}/{query}')
    data['physicalStorage'] = physical_storage(path.parent / 'data.ibx')
    reports.append(data)
    create = next(r for r in rows if r['operation'] == 'create')
    digest = create['inputSha256']
    if dataset in input_digests and input_digests[dataset] != digest:
        raise ValueError(f'Input changed between variants: {dataset}')
    input_digests[dataset] = digest
    if dataset in query_windows and query_windows[dataset] != data['windows']:
        raise ValueError(f'Query windows changed between variants: {dataset}')
    query_windows[dataset] = data['windows']
    index = next(r for r in rows if r['operation'] in ('index', 'directory'))
    proof = next((r['count'] for r in rows if r['operation'] == 'roundtrip'), 'offen')
    lines.append(f'| {dataset}/{variant} | {data["complete"]} | {create["fileBytes"]} | {index["fileBytes"]} | {statistics.median(r["millis"] for r in rows if r["operation"] == "create"):.2f} | {proof} |')
    for r in rows:
        if r['operation'] != 'query': continue
        key = (dataset, r['query'])
        if key in counts and counts[key] != r['count']:
            raise ValueError(f'Inconsistent result count: {dataset}/{variant}/{r["query"]}')
        counts[key] = r['count']
lines += ['', '## Erstellung und Gegenkontrollen', '',
          'Erstellung, Indexaufbau und Export umfassen nach Abschluss der Gegenkontrollen je drei Beobachtungen; davor sind ihre Mediane vorläufig. Vollscans umfassen drei Wiederholungen. Heapwerte sind Pool-Spitzen, kein RSS. Temporärer Speicher ist abgetastet.', '',
          '| Datensatz / Variante | Spatial-Index ms | Export ms | Vollscan ms | Erstellung Heap Bytes | Temporärer Speicher Bytes |',
          '|---|---:|---:|---:|---:|---:|']
for data in reports:
    by_op = defaultdict(list)
    for row in data['rows']: by_op[row['operation']].append(row)
    creation = by_op['create'][0]
    median_ms = lambda op: f"{statistics.median(r['millis'] for r in by_op[op]):.2f}" if by_op[op] else 'n/a'
    lines.append(f'| {data["dataset"]}/{data["variant"]} | {median_ms("index")} | {median_ms("export")} | {median_ms("scan")} | {statistics.median(r["heapPeakPoolSumBytes"] for r in by_op["create"]):g} | {statistics.median(r["temporaryPeakSampledBytes"] for r in by_op["create"]):g} |')

lines += ['', '## Zwanzig reproduzierbare räumliche Fenster', '',
          'Je Fenster zuerst der Median der drei Wiederholungen, anschliessend der Median über die 20 Fenster. HTTP ohne künstliche Verzögerung, kalter Anwendungscache. Öffnen ist nicht enthalten.', '',
          '| Datensatz / Variante | ms | Requests | Chunks | Übertragene Bytes | Zusätzliche Zwischenraumbytes |',
          '|---|---:|---:|---:|---:|---:|']
for data in reports:
    windows = defaultdict(list)
    for row in data['rows']:
        query = row.get('query', '')
        if row['operation'] == 'query' and query.startswith('bbox-') and int(query[5:]) >= 3 and row['delayMillis'] == 0 and row['cache'] == 'cold':
            windows[query].append(row)
    if len(windows) != 20: continue
    value = lambda field: statistics.median(statistics.median(r['millis'] if field == 'millis' else r['metrics'].get(field, 0) for r in rows) for rows in windows.values())
    lines.append(f'| {data["dataset"]}/{data["variant"]} | {value("millis"):.2f} | {value("requests"):g} | {value("chunksRead"):g} | {value("bytesRead"):g} | {value("additionalRangeBytes"):g} |')

lines += ['', '## Selektiver Zugriff', '', '| Datensatz / Variante | Query | Delay ms | Cache | ms | Requests | Bytes | Chunks |', '|---|---|---:|---|---:|---:|---:|---:|']
for data in reports:
    groups = defaultdict(list)
    for r in data['rows']:
        if r['operation'] == 'query': groups[(r['query'], r['delayMillis'], r['cache'])].append(r)
    for (query, delay, cache), rows in sorted(groups.items()):
        # Keep the report readable; all 20 seeded windows remain in JSON.
        if query.startswith('bbox-') and int(query[5:]) > 2: continue
        med = lambda field: statistics.median(r['metrics'][field] for r in rows)
        lines.append(f'| {data["dataset"]}/{data["variant"]} | {query} | {delay} | {cache} | {statistics.median(r["millis"] for r in rows):.2f} | {med("requests"):g} | {med("bytesRead"):g} | {med("chunksRead"):g} |')
lines += ['', '## Veränderung gegenüber der Referenz', '', '| Datensatz / Variante | Indexierte Dateigrösse Δ % | TID kalt, HTTP 80 ms: Zeit Δ % | Requests inklusive Öffnen |', '|---|---:|---:|---:|']
references = {(d['dataset'], d['parameters']['encoding']): d for d in reports if d['parameters']['reference']}
for d in reports:
    ref = references.get((d['dataset'], d['parameters']['encoding']))
    if ref is None or d is ref: continue
    current = [r for r in d['rows'] if r.get('query') == 'tid' and r.get('delayMillis') == 80 and r.get('cache') == 'cold']
    baseline = [r for r in ref['rows'] if r.get('query') == 'tid' and r.get('delayMillis') == 80 and r.get('cache') == 'cold']
    if not current or not baseline: continue
    def total(rows, field):
        repeats = defaultdict(float)
        for r in rows: repeats[r['repeat']] += r['metrics'][field] if field == 'requests' else r[field]
        return statistics.median(repeats.values())
    size_delta = (d['physicalStorage']['fileBytes'] / ref['physicalStorage']['fileBytes'] - 1) * 100
    time_delta = (total(current, 'millis') / total(baseline, 'millis') - 1) * 100
    lines.append(f'| {d["dataset"]}/{d["variant"]} | {size_delta:+.2f} | {time_delta:+.2f} | {total(current, "requests"):g} vs. {total(baseline, "requests"):g} |')
lines += ['', '## Physische Verzeichnisse', '', '| Datensatz / Variante | B+-Baum-Seiten Bytes | Seitenrahmen Bytes | TID-Schlüssel Bytes | TID-Werte Bytes | FID-Schlüssel Bytes | FID-Werte Bytes |', '|---|---:|---:|---:|---:|---:|---:|']
for d in reports:
    st = d['physicalStorage']
    lines.append(f'| {d["dataset"]}/{d["variant"]} | {st["sectionBytes"].get(6, 0) + st["sectionBytes"].get(7, 0)} | {st["sharedIndexPageBytes"]} | {st["keyBytes"].get("leaf:O", 0)} | {st["valueBytes"].get("leaf:O", 0)} | {st["keyBytes"].get("leaf:F", 0)} | {st["valueBytes"].get("leaf:F", 0)} |')

overview = ['', '## Kompakter Vergleich: Referenz → Hilbert + STR, 256 KiB', '',
            'Diese Übersicht enthält nur vollständig gemessene Paare. Die mittlere zentrale Bounding Box ist `bbox-1`; Zugriffe sind kalt über HTTP ohne künstliche Verzögerung, ohne Öffnen.', '',
            '| Datensatz / Profil | Dateigrösse Bytes | BBox Requests | BBox Chunks |',
            '|---|---:|---:|---:|']
for d in reports:
    encoding = d['parameters']['encoding']
    if d['variant'] != f'hilbert-str-{encoding}-262144' or not d['complete']: continue
    ref = references.get((d['dataset'], encoding))
    if ref is None or not ref['complete']: continue
    def metric(report, field):
        rows = [r for r in report['rows'] if r['operation'] == 'query' and r.get('query') == 'bbox-1' and r.get('delayMillis') == 0 and r.get('cache') == 'cold']
        return f"{statistics.median(r['metrics'][field] for r in rows):g}"
    overview.append(f'| {d["dataset"]}/{encoding} | {ref["physicalStorage"]["fileBytes"]} → {d["physicalStorage"]["fileBytes"]} | {metric(ref, "requests")} → {metric(d, "requests")} | {metric(ref, "chunksRead")} → {metric(d, "chunksRead")} |')
overview += ['', '## Vollständiges Variantenraster', '', 'Beim synthetischen Millionenbestand wird kein Spatial Index ergänzt; die zweite Grössenangabe entspricht deshalb dem Core. Der Aufbau der obligatorischen B+-Baum-Verzeichnisse ist in der Erstellungszeit enthalten.', '']
lines[4:4] = overview

completed = sum(d['complete'] for d in reports)
controls_completed = sum(d['controlsComplete'] for d in reports)
fully_complete = completed == a.expected_cases and controls_completed == a.expected_cases
lines.insert(2, f'**Status: Abfragematrix {completed}/{a.expected_cases}; dreifache Gegenkontrollen {controls_completed}/{a.expected_cases}.** ' + ('Die vollständige Vergleichsmatrix ist abgeschlossen.' if fully_complete else 'Zwischenstand; die Abnahme der vollständigen Vergleichsmatrix ist noch offen.'))
lines.insert(3, '')
run = dict(completedCases=completed, expectedCases=a.expected_cases, controlsCompletedCases=controls_completed, complete=fully_complete,
           generatedAtUtc=datetime.now(timezone.utc).isoformat(),
           fixedParameters=dict(compression='zstd', compressionLevel=3, numericEncoding='lexical',
                                seed=20260917, cacheBytes=33554432, prefetchMaxGap=4096,
                                prefetchMaxBytes=1048576, maxHeapBytes=402653184))
if (a.input / 'build.json').exists(): run['build'] = json.loads((a.input / 'build.json').read_text())
if (a.input / 'production-proof.json').exists(): run['productionProof'] = json.loads((a.input / 'production-proof.json').read_text())
run['workerSha256'] = {name: hashlib.sha256((a.input / name).read_bytes()).hexdigest() for name in ('worker.jar', 'directory-worker.jar', 'controls-worker.jar') if (a.input / name).exists()}
(a.output / 'run.json').write_text(json.dumps(run, indent=2) + '\n')
(a.output / 'results.json').write_text(json.dumps(reports, separators=(',', ':')) + '\n')
(a.output / 'README.md').write_text('\n'.join(lines) + '\n')
