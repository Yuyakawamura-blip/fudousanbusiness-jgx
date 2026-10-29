# Nature Capital Real Estate サイト — Agent Instructions

> AI コーディングエージェント(Claude Code / Codex 等)向けの指示書。規約の更新はこのファイルのみで行い、`CLAUDE.md` は本ファイルを import して Claude 固有の補足だけを持つ。

## Project
森林・里山の相続・管理・出口整理を扱う「ネイチャーキャピタル・リアルエステイト」の Web サイト。日本GXグループの事業。
**ビルド無しの静的 HTML / CSS / JS**。`docs/` 配下だけが GitHub Pages で公開される。

- 公開 URL: https://yuyakawamura-blip.github.io/fudousanbusiness-jgx/
- デザインの元: Figma `voPyGfM8U5sFDuvgGXEyzK`(ページとフレームの対応は `maintenance/figma.md`)
- サイト階層図: `LP_HIERARCHY.drawio`
- 設計書: `DESIGN.md`(コンセプト・仕様・11 工程の現状・未決定事項)。進め方は `maintenance/ai-product-dev-guide.md`、ベースラインは事業計画書(SharePoint P065)

## 対象者
- **主役: 山林所有者**(相続・遠方管理・売却/活用)。トップと主要導線はこの人向けに書く
- 副: 林業事業体(森林経営計画作成支援ツール)/ 企業・参加者・一般の方(森林を知る・オープンデータ)
- 読み手に高齢の方が多い前提で、文字の大きさ・行間・分かりやすい言葉を優先する

## 構成
| パス | 内容 |
| --- | --- |
| `docs/index.html` + `docs/home.css` + `docs/home-letter.css` / `home-letter.js` | トップ(本文は「手紙 → 相談票」。`home-letter.*` は本文だけに効く) |
| `docs/about/` `docs/concerns/` `docs/services/` | 私たちについて / お悩みから探す / サービス一覧 |
| `docs/services/satoyama-real-estate/` | 山林所有者向けサービス |
| `docs/services/forest-planning-tool/` | 林業事業体向けツール |
| `docs/forest/` `docs/forest-guide/` `docs/forest/sustainable-forestry/`(`en/` あり) | 森林を知る系 |
| `docs/forest-data/` | 森林オープンデータ(地図・カタログ。`catalog.json` は毎日自動更新) |
| `docs/partners/` | 企業・個人の方向け(企業の森づくり / 自然資本・クレジット / 体験・ボランティア / 山林の取得・活用) |
| `docs/styles.css` | 全ページ共通 CSS |
| `docs/nav.js` | スマホ幅(720px 以下)のメニューボタンを全ページのヘッダーに追加する |
| `docs/consult-source.js` | 相談フォームへのリンクに流入元(`?src=`)と押したページを事前入力する。`FORM_ENTRY` が空なら何もしない(`maintenance/consult-source.md`) |
| `docs/consult-sheet.js` | 相談票の印を相談フォームの「ご相談の内容」「山林の所在地」に事前入力する(`maintenance/consult-source.md`) |
| `docs/auth.js` | 全ページのパスワードゲート(クライアント側のみ。本当の保護ではない) |
| `docs/404.html` | 存在しない URL 用。GitHub Pages はどの階層でもこのファイルを返すので `<base href="/fudousanbusiness-jgx/">` でリンクの基準を固定している |
| `archive/` | 公開対象外の旧ページ |
| `maintenance/` | 運用メモ(Figma / 森林データ / 流入元の記録 / 整理メモのひな形 / 公開前チェックリスト / 開発ガイド) |

## Commands
- ローカル確認: `python3 -m http.server 8000 -d docs` → http://localhost:8000/
- 森林データ更新のテスト: `python3 -m unittest discover -s tests -p 'test_forest_data.py'`
- `tests/rendered-html.test.mjs` は旧ビルド(`dist/`)用で、現行サイトの確認には使わない

## 進め方
- `maintenance/ai-product-dev-guide.md` の 11 工程・5 層(戦略 → 要件 → 構造 → 骨格 → 表層)に沿う。見た目より先に目的と流れを決める
- `DESIGN.md` では 事実 / 仮説 / 決定 / 実装済み / 検証済み / 未決定 を書き分ける。決めたら日付と理由を残す
- 報告では「ローカルで確認」「公開(push)」「公開 URL で確認」を分けて書く

## Conventions
- **ヘッダー / フッターは各 HTML に直書き**。ナビやフッターを変えたら全ページ(各 index.html 12 ファイル + `docs/404.html`)を同じように直す。ヘッダーナビは対象者別: 山林をお持ちの方 / 林業事業体の方 / 企業・個人の方 / 森林を知る / 私たちについて / 無料相談
- リンク・画像は**相対パス**。ページの階層(`../` / `../../` / `../../../`)に合わせる
- ヘッダーとフッターの相談リンクは「**無料相談**」(英語版は Free consultation)。本文の相談ボタンは所有者向けページで「無料相談を申し込む」、事業者・企業向けページで「お問い合わせをする」。外部リンクには CSS で ↗ が付くので本文に矢印を書かない。リンク先は共通の Google フォーム(`target="_blank" rel="noopener noreferrer"`)
- 山林所有者向けサービスの名前は「**さとやま不動産**」(説明が要る所では「山林・里山の管理と出口整理」を添える)。サービスの並びは所有者向け → 林業事業体向け → 企業・個人の方の順
- セクションの小見出しラベル(`.label` など)は日本語で書く(英語版ページとブランド名「NATURE CAPITAL REAL ESTATE」を除く)。見出しは `word-break: auto-phrase` で文節改行するので、1 文節が列幅を超えない大きさにする
- ページタイトルは「ページ名 | ネイチャーキャピタル・リアルエステイト」(英語版は「… | Nature Capital Real Estate」)
- 文字色は背景とのコントラスト比 4.5 以上にする(小見出しラベルは #4f6a57)
- 「ご相談の流れと費用」は共通部品 `.flow-fees`(styles.css)。トップとさとやま不動産で同じ 3 段階(無料 / 無料 / 事前にお見積り)を保つ
- ロゴは `docs/assets/nature-capital-mark.svg`
- 各ページの `<head>` にはファビコン・共有用(OGP)のメタタグ・Noto Sans JP の読み込み(preconnect + link。CSS の `@import` は使わない)・`nav.js`・`consult-source.js` がある。`<body>` の直後に「本文へ移動」(`.skip-link` → `<main id="main">`)。新しいページを作るときも同じ一式を入れる(404 は `<base>` があるので本文へ移動は付けない)(og:url は公開 URL の絶対パス、共有画像は `docs/assets/og-image.jpg`)。独自ドメインに移すときは og:url / og:image を書き換える
- 新しい画像は **WebP・1 枚 300KB 目安**、ファイル名は英小文字のケバブケース。`alt` を必ず書く
- レイアウトはデスクトップとスマホ幅(720px 以下)の両方で確認する
- 自然資本価値・売却・認証の結果を約束する表現を書かない(既存の注意書きの方針に合わせる)
- コミットは日本語で「何をしたか」を 50 文字以内・prefix なし

## Deploy
- `main` への push で `.github/workflows/deploy-pages.yml`(リポジトリ直下)が `docs/` を公開する
- ワークフローが毎日 `catalog.json` をコミットするので、**push 前に必ず `git pull --rebase`**
- リポジトリ直下には別プロジェクト(`jcredit-creation-system/` `jgx-hp/` など)もある。このサイトのファイル以外をコミットに含めない

## Don'ts
- `docs/` の外に公開したいファイルを置かない(公開されない)
- `archive/` のファイルを編集しない
- `git push --force` / `git reset --hard` をしない
- Google フォームの URL やプライバシーポリシーのリンクを勝手に変えない
