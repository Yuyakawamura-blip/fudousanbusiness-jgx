# Figma Design Source

File: https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK

The homepage design is the source for `docs/index.html` and `docs/home.css`.
The ten other current pages were exported as editable text, frames, vectors,
and discrete image assets on 2026-10-07. Archived pages are excluded.

| Route | Local source | Figma frame |
| --- | --- | --- |
| `/` | `docs/index.html`, `docs/home.css` | [2:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=2-2) |
| `/about/` | `docs/about/index.html` | [21:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=21-2) |
| `/concerns/` | `docs/concerns/index.html` | [21:143](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=21-143) |
| `/forest/` | `docs/forest/index.html` | [8:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=8-2) |
| `/services/` | `docs/services/index.html` | [10:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=10-2) |
| `/services/forest-planning-tool/` | `docs/services/forest-planning-tool/index.html` | [11:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=11-2) |
| `/services/satoyama-real-estate/` | `docs/services/satoyama-real-estate/index.html` | [12:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=12-2) |
| `/forest-guide/` | `docs/forest-guide/index.html` | [14:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=14-2) |
| `/forest/sustainable-forestry/` | `docs/forest/sustainable-forestry/index.html` | [15:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=15-2) |
| `/forest/sustainable-forestry/en/` | `docs/forest/sustainable-forestry/en/index.html` | [16:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=16-2) |
| `/forest-data/` | `docs/forest-data/index.html`, its CSS and JS | [17:2](https://www.figma.com/design/voPyGfM8U5sFDuvgGXEyzK?node-id=17-2) |

## Update Workflow

1. Edit the existing screen in this file, retaining its frame ID where practical.
2. Provide its node-specific Figma URL and request implementation.
3. Read the current Figma design context and screenshot; adapt it to the static HTML/CSS site.
4. Preserve functional navigation, forms, data tools, and any unrelated local edits.
5. Verify desktop/mobile rendering, asset loading, and local links.
6. Commit and publish when requested; then verify GitHub Pages separately.

Figma edits do not automatically update the repository or the public website.
Maps, filters, and other dynamic controls are editable design snapshots in Figma;
their behavior remains implemented in the website's JavaScript.

## Export Organization Status

All ten lower-level pages were added successfully. About and Concerns have their
own Figma pages and share a footer instance. The other eight screens remain on
the original `Page 1`, alongside the unchanged homepage design.

A `Site Footer` component set (node `20:55`) contains Japanese standard,
English standard, and Japanese compact variants. Further page organization and
component reuse stopped at the Figma Starter MCP tool-call limit.

## Homepage Assets

The hero and concept photos match the existing local images byte for byte.
The Figma logo bitmap and map/compass SVGs are stored under `docs/assets/` as
`figma-home-mark.png`, `figma-home-map.svg`, and `figma-home-compass.svg`.
No temporary Figma asset URL is used by the website.
