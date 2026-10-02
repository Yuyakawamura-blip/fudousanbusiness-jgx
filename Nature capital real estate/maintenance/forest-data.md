# Forest open-data LP

Route: `docs/forest-data/` → GitHub Pages `/fudousanbusiness-jgx/forest-data/`.
The home page links to it in a dedicated section and footer. Existing auth.js is retained.

## Source and synchronization

- Official catalog: https://www.geospatial.jp/ckan/dataset/layer
- CKAN action API: https://www.geospatial.jp/ckan/api/3/action/package_show?id=layer
- Publisher checked: organization `rinya` (林野庁).
- `scripts/update_forest_data.py` uses Python's standard library and writes `docs/forest-data/catalog.json` atomically after validation.
- It synchronizes the title, notes, dates, all resource names, formats, URLs, descriptions and resource detail links. The UI includes new non-prefecture resources under documents as well; removed resources disappear on successful refresh.
- Large archives are not mirrored. Downloads and map tiles use the original provider. A file replaced at the same URL is therefore read from the provider even if metadata has not changed (subject to provider caching).
- The per-prefecture mapping is from the official `fr_layer_A_2025` filename convention and JIS prefecture codes. Unknown names remain accessible under documents and are not guessed.
- The image thumbnail and visit counters are deliberately excluded.

## Scheduled execution and publication

`.github/workflows/deploy-pages.yml` runs daily at **06:17 JST (21:17 UTC)**, on matching main pushes, or via workflow_dispatch. Schedule execution can be delayed by GitHub. On every successful run it:

1. runs updater contract tests;
2. fetches the catalog (45 second timeout, 3 attempts);
3. saves a catalog commit with last successful check time;
4. uploads the same `docs` tree and deploys Pages in the same workflow.

This avoids relying on another workflow being triggered by a GITHUB_TOKEN push. The daily timestamp commit also keeps the public repository active for GitHub's 60-day scheduled workflow inactivity policy. The job needs `contents: write`, `pages: write`, `id-token: write`; repository rules must permit its main-branch write. No personal tokens or other secrets are needed.

Failed requests, API errors, empty/incomplete responses, wrong publishers, private datasets, duplicate IDs and unsafe resource URLs fail before snapshot replacement. A failed job does not publish and keeps the previous deployment. A page more than 72 hours past its last successful check displays a stale-data notice. Check Actions run failures and rerun the workflow after recovery. Do not represent a stale snapshot as current.

## Dates and scope

`checked_at`: successful fetch, displayed in Japan time.
`source_modified`: CKAN's published date (timezone-unspecified string; not silently converted).
`changed_at`: last detected metadata-content change; first import is its initial baseline.
Actual forest information age is the GIS attribute `データ時点`, not any of these page dates.

This is the forest planning target area layer, not all forest cover, owner boundaries, species/volume estimates or the separate forest-resource mesh. Its terms require attribution, PDL1.0 and disclosure of editing. The catalog's legacy license label says 政府標準利用規約; linked individual terms explicitly specify PDL1.0, which the LP follows.

Raster bounds and zoom limits (5–16), and legend colors follow the 2026-03-23 data dictionary. The official style.json currently starts at 12 although the dictionary describes vector levels 13–16; the LP supplies the unmodified style URL without overriding its vector zoom settings. If the provider changes schema, tile type, palette or coverage, review the map adapter. Explanatory editorial copy is dated 2026-09-06 and is not auto-rewritten; current source notes and terms links are always shown separately.

## Validation

- `python3 -m unittest discover -s tests -p test_forest_data.py`
- `python3 scripts/update_forest_data.py`
- `node --check docs/forest-data/forest-data.js`
- Validate the deployed JSON's fingerprint/check time and route after publication.

Leaflet 1.9.4 is vendored with its BSD license; only a raster overlay is rendered. The source archives and styles remain unmodified. The vinext starter's `npm test` does not exercise the static `docs` site.
