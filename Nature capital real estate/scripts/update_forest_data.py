#!/usr/bin/env python3
"""Sync public CKAN metadata only; large GIS files stay at their official source."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

API = 'https://www.geospatial.jp/ckan/api/3/action/package_show?id=layer'
SOURCE = 'https://www.geospatial.jp/ckan/dataset/layer'
OUTPUT = Path(__file__).resolve().parents[1] / 'docs/forest-data/catalog.json'
PREFECTURES = '北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県'.split()

def safe_url(value):
    if not isinstance(value, str):
        raise ValueError('Missing resource URL')
    parts = urlsplit(value)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
        raise ValueError('Resource URL must be public HTTPS')
    return value

def plain(value):
    return html.unescape(re.sub(r'<[^>]*>', '', str(value or ''))).strip()

def normalize(payload):
    if payload.get('success') is not True:
        raise ValueError('CKAN returned an unsuccessful response')
    data = payload['result']
    if data.get('name') != 'layer' or data.get('private') is not False or data.get('state') != 'active':
        raise ValueError('Dataset is not the expected active public dataset')
    if data.get('organization', {}).get('name') != 'rinya':
        raise ValueError('Unexpected publisher')
    resources = data.get('resources')
    if not isinstance(resources, list) or not resources or data.get('num_resources') != len(resources):
        raise ValueError('Empty or incomplete resource collection')
    entries, ids = [], set()
    for row in resources:
        rid = row.get('id')
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError('Missing or duplicate resource ID')
        ids.add(rid)
        name = plain(row.get('name'))
        url = safe_url(row.get('url'))
        match = re.search(r'fr_layer_(\d{2})_', name) or re.search(r'fr_layer_(\d{2})_', url)
        pref = PREFECTURES[int(match[1])-1] if match and 1 <= int(match[1]) <= 47 else None
        fmt = plain(row.get('format')).lower()
        kind = 'download' if pref else 'tile' if all(t in url for t in ('{z}', '{x}', '{y}')) else 'style' if name == 'style.json' else 'document'
        entries.append(dict(id=rid, name=name or rid, url=url, format=fmt,
                            description=plain(row.get('description')), prefecture=pref, kind=kind,
                            modified=row.get('last_modified') or row.get('metadata_modified'), size=row.get('size'),
                            page=f'{SOURCE}/resource/{rid}'))
    # Never infer the license from CKAN's legacy label: the linked terms take precedence.
    return dict(source=SOURCE, api=API, title=plain(data['title']),
                publisher=plain(data['organization']['title']), notes=plain(data.get('notes')),
                source_modified=data['metadata_modified'], license_label=plain(data.get('license_title')),
                resources=entries)

def fetch():
    for attempt in range(3):
        try:
            req = Request(API, headers={'User-Agent': 'NatureCapital-ForestData/1.0', 'Accept': 'application/json'})
            with urlopen(req, timeout=45) as response:
                raw = response.read(10_000_001)
                if len(raw) > 10_000_000:
                    raise ValueError('Unexpectedly large response')
                return json.loads(raw)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

def update(payload, output=OUTPUT, now=None):
    data = normalize(payload)  # Validate everything before touching the last good snapshot.
    fingerprint = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    old = json.loads(output.read_text()) if output.exists() else {}
    checked = now or datetime.now(timezone.utc).isoformat(timespec='seconds')
    changed = fingerprint != old.get('fingerprint')
    data.update(schema_version=1, checked_at=checked, fingerprint=fingerprint,
                changed_at=checked if changed else old['changed_at'])
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    os.replace(temporary, output)
    print(f'{len(data["resources"])} resources; content_changed={changed}; checked_at={checked}')
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='Use an already fetched CKAN response for initial import/testing')
    args = parser.parse_args()
    update(json.loads(args.input.read_text()) if args.input else fetch())
