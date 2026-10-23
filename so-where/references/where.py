#!/usr/bin/env python3
"""Where: a local, evidence-backed operational map. Python 3.9+, standard library only."""
import argparse
import copy
import fcntl
import html
import json
import mimetypes
import os
import re
import secrets
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

KINDS = {'service', 'repository', 'host', 'document'}
STATES = {'draft', 'curated', 'retired'}
RELATIONS = {'runs_on', 'built_from', 'documents', 'depends_on', 'related_to', 'supersedes'}
RUNTIME = {'address', 'host', 'deployment', 'repo', 'subdirectory', 'revision', 'root', 'entrypoint', 'environment'}
FIELDS = {'id', 'title', 'summary', 'why', 'owner', 'kind', 'state', 'locations', 'runtime',
          'tags', 'evidence', 'uncertainties', 'verified_at', 'review_after_days', 'relations', 'history'}


def now():
    return datetime.now(timezone.utc)


def stamp():
    return now().isoformat(timespec='seconds')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parse_time(value):
    require(isinstance(value, str), 'Timestamp must be a string')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(dt.tzinfo is not None, 'Timestamp needs a timezone')
    return dt


def string(value):
    return isinstance(value, str) and bool(value.strip())


def valid_uri(value):
    return string(value) and urlparse(value).scheme.lower() in {'https', 'http', 'file', 'obsidian', 'ssh'}


def validate(data, at=None):
    at = at or now()
    require(isinstance(data, dict), 'Manifest must be an object')
    require(set(data) == {'schema_version', 'demo', 'revision', 'records', 'events'}, 'Unexpected manifest fields')
    require(data['schema_version'] == 1 and type(data['demo']) is bool, 'Unsupported schema or demo flag')
    require(type(data['revision']) is int and data['revision'] >= 0, 'Invalid revision')
    require(isinstance(data['records'], list) and isinstance(data['events'], list), 'Records/events must be lists')
    ids = set()
    for r in data['records']:
        require(isinstance(r, dict) and set(r) == FIELDS, 'Record fields do not match contract')
        rid = r['id']
        require(isinstance(rid, str) and re.fullmatch(r'k-[0-9a-f]{6}', rid), 'Invalid record id')
        require(rid not in ids, 'Duplicate id: ' + rid)
        ids.add(rid)
        for key in ('title', 'summary', 'why', 'owner'):
            require(string(r[key]), rid + ': missing ' + key)
        require(r['kind'] in KINDS and r['state'] in STATES, rid + ': invalid kind/state')
        for key in ('locations', 'tags', 'evidence', 'uncertainties', 'relations', 'history'):
            require(isinstance(r[key], list), rid + ': ' + key + ' must be a list')
        for key in ('tags', 'uncertainties'):
            require(all(string(s) for s in r[key]), rid + ': invalid ' + key)
        require(type(r['review_after_days']) is int and 1 <= r['review_after_days'] <= 3650, rid + ': invalid review period')
        for loc in r['locations']:
            require(isinstance(loc, dict) and set(loc) == {'label', 'uri'} and string(loc['label']) and valid_uri(loc['uri']), rid + ': invalid location')
        require(len({loc['uri'] for loc in r['locations']}) == len(r['locations']), rid + ': duplicate location')
        require(isinstance(r['runtime'], dict) and set(r['runtime']) <= RUNTIME, rid + ': invalid runtime fields')
        require(all(string(v) for v in r['runtime'].values()), rid + ': empty runtime value; omit unknown fields')
        for e in r['evidence']:
            require(isinstance(e, dict) and set(e) <= {'scope', 'observed_at', 'ref', 'summary', 'deployment', 'sample'}, rid + ': invalid evidence fields')
            require(e.get('scope') in {'route', 'source', 'runtime', 'identity'} and string(e.get('summary')) and string(e.get('ref')), rid + ': incomplete evidence')
            require(parse_time(e.get('observed_at')) <= at, rid + ': evidence is dated in the future')
            require(type(e.get('sample')) is bool, rid + ': evidence needs sample boolean')
            require(data['demo'] or not e['sample'], rid + ': sample evidence cannot enter a real map')
        if r['verified_at'] is not None:
            require(parse_time(r['verified_at']) <= at, rid + ': verification is dated in the future')
        if r['state'] == 'draft':
            require(r['verified_at'] is None, rid + ': draft must not be marked verified')
        if r['state'] == 'curated':
            verified = promotable(r, at, allow_stale=True)
            require(parse_time(r['verified_at']) == verified, rid + ': verification does not match evidence')
        for rel in r['relations']:
            require(isinstance(rel, dict) and set(rel) == {'type', 'to'} and rel['type'] in RELATIONS, rid + ': invalid relationship')
    for r in data['records']:
        for rel in r['relations']:
            require(rel['to'] in ids and rel['to'] != r['id'], r['id'] + ': dangling or self relationship')
    return data


def promotable(r, at=None, allow_stale=False):
    at = at or now()
    require(not r['uncertainties'], 'Resolve uncertainties before promotion')
    require(r['locations'], 'Add a primary location before promotion')
    scopes = {'identity'}
    if r['kind'] == 'service':
        require(set(r['runtime']) == RUNTIME, 'Service serving chain is incomplete')
        scopes = {'route', 'source', 'runtime'}
    times = []
    for scope in scopes:
        evidence = [e for e in r['evidence'] if e['scope'] == scope and
                    (r['kind'] != 'service' or e.get('deployment') == r['runtime']['deployment'])]
        require(evidence, 'Missing ' + scope + ' evidence for the current subject/deployment')
        times.append(max(parse_time(e['observed_at']) for e in evidence))
    oldest = min(times)
    require(oldest <= at, 'Future evidence is not verification')
    require(allow_stale or at <= oldest + timedelta(days=r['review_after_days']), 'Evidence is stale; inspect the source again')
    return oldest


def freshness(r, at=None):
    at = at or now()
    if r['state'] != 'curated':
        return r['state'].capitalize()
    due = parse_time(r['verified_at']) + timedelta(days=r['review_after_days'])
    return 'Stale' if at > due else 'Current'


def read(root):
    return validate(json.loads((root / 'registry.json').read_text()))


def atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextmanager
def locked(root):
    root.mkdir(parents=True, exist_ok=True)
    with (root / '.where.lock').open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def save(root, data):
    validate(data)
    path = root / 'registry.json'
    if path.exists():
        atomic(root / 'registry.json.bak', path.read_text())
    atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def default_record(raw):
    r = {'id': 'k-' + secrets.token_hex(3), 'title': '', 'kind': 'document', 'summary': '',
         'why': '', 'owner': '', 'state': 'draft', 'locations': [], 'runtime': {}, 'tags': [],
         'evidence': [], 'uncertainties': [], 'verified_at': None, 'review_after_days': 14,
         'relations': [], 'history': []}
    r.update(copy.deepcopy(raw))
    r.update(state='draft', verified_at=None, history=[])
    return r


def mutate(data, action, payload):
    data = copy.deepcopy(data)
    reason = payload.get('reason', '')
    if action == 'capture':
        r = default_record(payload['record'])
        data['records'].append(r)
    else:
        r = next((r for r in data['records'] if r['id'] == payload.get('id')), None)
        require(r is not None, 'Unknown record id')
        before = copy.deepcopy(r)
        if action == 'promote':
            require(r['state'] == 'draft', 'Only drafts can be promoted; amend a curated record to re-verify it')
            r['verified_at'] = promotable(r).isoformat()
            r['state'] = 'curated'
        elif action == 'amend':
            require(string(reason), 'Amendment needs a reason')
            new = default_record(payload['record'])
            require(new['id'] == r['id'], 'Amendment must retain the id')
            new['history'] = r['history']
            r.clear()
            r.update(new)
        elif action == 'link':
            rel = {'type': payload['type'], 'to': payload['to']}
            require(rel not in r['relations'], 'Relationship already exists')
            r['relations'].append(rel)
        elif action == 'relocate':
            require(string(reason), 'Relocation needs a reason')
            loc = next((l for l in r['locations'] if l['uri'] == payload['old']), None)
            require(loc is not None, 'Old URI not found; no pointer was changed')
            require(valid_uri(payload['new']), 'New location needs a supported URI')
            loc['uri'] = payload['new']
            r.update(state='draft', verified_at=None)
            r['uncertainties'].append('Verify relocated reference: ' + payload['new'])
        elif action == 'retire':
            require(string(reason), 'Retirement needs a reason')
            r['state'] = 'retired'
        else:
            raise ValueError('Unknown operation')
        before.pop('history', None)
        r['history'].append({'action': action, 'at': stamp(), 'reason': reason, 'before': before})
    data['revision'] += 1
    data['events'].append({'at': stamp(), 'action': action, 'id': r['id'], 'reason': reason})
    validate(data)
    return data, r['id']


def md_text(value):
    return str(value).replace('\n', ' ').replace('|', '\\|')


def evidence_link(ref):
    parsed = urlparse(ref)
    if parsed.scheme:
        return ref if valid_uri(ref) else ''
    path = Path(ref)
    return ref if not path.is_absolute() and '..' not in path.parts else ''


def build(root, data=None, at=None):
    data = data or read(root)
    at = at or now()
    validate(data)
    enriched = copy.deepcopy(data)
    for r in enriched['records']:
        r['freshness'] = freshness(r, at)
    enriched['built_at'] = at.isoformat(timespec='seconds')
    template = Path(__file__).with_name('dashboard.html').read_text()
    embedded = json.dumps(enriched, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    atomic(root / 'index.html', template.replace('__WHERE_DATA__', embedded))
    titles = {r['id']: r['title'] for r in data['records']}
    intro = 'Fictional sample inventory.' if data['demo'] else 'Curated inventory; verify stale claims before acting.'
    lines = ['# Where', '', 'A daily map of what runs where and why.', '', intro,
             '', 'Generated from `registry.json`; edit the manifest or use the helper.', '',
             '## Needs attention', '']
    attention = [r for r in data['records'] if freshness(r, at) in {'Stale', 'Draft'}]
    lines += [f"- [ ] {r['title']} — {freshness(r, at)} — `{r['id']}`" for r in attention] or ['No records need attention.']
    lines += ['', '## Map', '', '| Subject | State | Why | Primary location |', '| --- | --- | --- | --- |']
    vault = root / 'obsidian'
    vault.mkdir(exist_ok=True)
    home = ['# Where', '', intro, '', 'Generated view. Edit registry.json; rebuild after changes.', '']
    for r in data['records']:
        primary = r['locations'][0]['uri'] if r['locations'] else 'Unknown'
        lines.append(f"| [{md_text(r['title'])}](obsidian/{r['id']}.md) | {freshness(r, at)} | {md_text(r['why'])} | {md_text(primary)} |")
        home.append(f"- [[{r['id']}|{r['title']}]] — {freshness(r, at)}")
        note = ['---', 'id: ' + r['id'], 'title: ' + json.dumps(r['title']),
                'state: ' + r['state'], 'tags: ' + json.dumps(['where'] + r['tags']), '---', '',
                '# ' + r['title'], '', r['summary'], '', intro, '', '**Why:** ' + r['why'], '',
                '**Owner:** ' + r['owner'], '', '**Knowledge state:** ' + freshness(r, at), '',
                '**Observed:** ' + str(r['verified_at'] or 'Not verified'), '', '## Locations', '']
        note += [f"- {l['label']}: {l['uri']}" for l in r['locations']]
        note += ['', '## Serving chain', '']
        note += [f'- {key}: `{value}`' for key, value in r['runtime'].items()] or ['No runtime claim.']
        note += ['', '## Connected records', '']
        note += [f"- {rel['type']}: [[{rel['to']}|{titles[rel['to']]}]]" for rel in r['relations']] or ['No connections yet.']
        incoming = [(s, rel) for s in data['records'] for rel in s['relations'] if rel['to'] == r['id']]
        note += [f"- Incoming {rel['type']}: [[{s['id']}|{s['title']}]]" for s, rel in incoming]
        note += ['', '## Evidence', '']
        for e in r['evidence']:
            ref = evidence_link(e['ref'])
            # Export is one level deeper than the canonical registry.
            target = '../' + ref if ref and not urlparse(ref).scheme else ref
            link = f"[source](<{target}>)" if target else '`' + e['ref'] + '`'
            note.append(f"- {e['scope']} · {e['observed_at']} · {e['summary']} · {link}")
        note += ['', '## Open questions', ''] + (['- ' + q for q in r['uncertainties']] or ['None recorded.'])
        note += ['', '## History', '', '```json', json.dumps(r['history'], indent=2), '```', '']
        atomic(vault / (r['id'] + '.md'), '\n'.join(note))
    atomic(vault / 'Where.md', '\n'.join(home) + '\n')
    atomic(root / 'START.md', '\n'.join(lines) + '\n')


def serve(root, port):
    csrf = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, code, content, mime='application/json'):
            body = content.encode() if isinstance(content, str) else content
            self.send_response(code)
            self.send_header('Content-Type', mime + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def trusted(self):
            expected = f'127.0.0.1:{self.server.server_port}'
            require(self.headers.get('Host') == expected, 'Use the printed loopback URL')
            origin = self.headers.get('Origin')
            require(origin is None or origin == 'http://' + expected, 'Cross-origin access refused')

        def do_GET(self):
            try:
                self.trusted()
                path = unquote(urlparse(self.path).path)
                if path == '/api/registry':
                    self.respond(200, json.dumps({'registry': read(root), 'csrf': csrf}))
                    return
                name = 'index.html' if path == '/' else path.lstrip('/')
                allowed = name in {'index.html', 'START.md', 'registry.json', 'README.md', 'DESIGN.md'}
                allowed = allowed or bool(re.fullmatch(r'obsidian/(k-[a-f0-9]{6}|Where)\.md', name))
                allowed = allowed or (name.startswith('evidence/') and name.endswith('.md'))
                target = (root / name).resolve()
                require(allowed and root.resolve() in target.parents and target.is_file(), 'File not available')
                mime = 'text/plain' if name.endswith('.md') else mimetypes.guess_type(name)[0] or 'text/plain'
                self.respond(200, target.read_bytes(), mime)
            except (ValueError, OSError) as e:
                self.respond(404, json.dumps({'error': str(e)}))

        def do_POST(self):
            try:
                self.trusted()
                require(secrets.compare_digest(self.headers.get('X-Where-Token', ''), csrf), 'Invalid session token')
                require(self.headers.get('Content-Type') == 'application/json', 'JSON required')
                size = int(self.headers.get('Content-Length', '0'))
                require(0 < size <= 262144, 'Request must be between 1 byte and 256 KiB')
                payload = json.loads(self.rfile.read(size))
                require(isinstance(payload, dict), 'JSON body must be an object')
                action = self.path.removeprefix('/api/')
                require(action in {'capture', 'amend', 'promote', 'link', 'relocate', 'retire'}, 'Unknown operation')
                with locked(root):
                    data = read(root)
                    if payload.pop('expected_revision', None) != data['revision']:
                        self.respond(409, json.dumps({'error': 'Map changed; refresh before saving'}))
                        return
                    changed, rid = mutate(data, action, payload)
                    save(root, changed)
                    build(root, changed)
                self.respond(200, json.dumps({'registry': changed, 'id': rid}))
            except (ValueError, KeyError, TypeError, OSError) as e:
                self.respond(400, json.dumps({'error': str(e)}))

    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'Where: http://127.0.0.1:{server.server_port} — Ctrl-C to stop', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path.cwd(), help='Map directory containing registry.json')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('init', help='Create an empty real map, refusing overwrite')
    sub.add_parser('check', help='Validate structure and curated evidence coverage')
    sub.add_parser('build', help='Generate HTML, START.md, and linked Obsidian pages')
    s = sub.add_parser('serve', help='Open a loopback-only editable map')
    s.add_argument('--port', type=int, default=8765)
    for command in ('capture', 'amend'):
        s = sub.add_parser(command)
        s.add_argument('--file', required=True, type=Path, help='Record JSON')
        if command == 'amend':
            s.add_argument('id')
            s.add_argument('--reason', required=True)
    for command in ('promote', 'retire', 'link', 'relocate'):
        s = sub.add_parser(command)
        s.add_argument('id')
        if command in {'retire', 'relocate'}:
            s.add_argument('--reason', required=True)
        if command == 'link':
            s.add_argument('--type', required=True, choices=sorted(RELATIONS))
            s.add_argument('--to', required=True)
        if command == 'relocate':
            s.add_argument('--old', required=True)
            s.add_argument('--new', required=True)
    args = p.parse_args()
    root = args.root.resolve()
    try:
        with locked(root):
            if args.command == 'init':
                require(not (root / 'registry.json').exists(), 'Map already exists; refusing overwrite')
                data = {'schema_version': 1, 'demo': False, 'revision': 0, 'records': [], 'events': []}
                save(root, data)
                build(root, data)
            else:
                data = read(root)
                if args.command in {'build', 'serve'}:
                    build(root, data)
                elif args.command != 'check':
                    payload = vars(args).copy()
                    if args.command in {'capture', 'amend'}:
                        payload['record'] = json.loads(args.file.read_text())
                    data, rid = mutate(data, args.command, payload)
                    save(root, data)
                    build(root, data)
                    print(rid)
        if args.command == 'serve':
            serve(root, args.port)
        else:
            print(f"OK: {args.command}; {len(data['records'])} records; revision {data['revision']}")
    except (ValueError, KeyError, TypeError, OSError) as e:
        print('Where: ' + str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
