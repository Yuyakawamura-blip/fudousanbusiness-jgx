# Nature Capital Real Estate サイト — Agent Instructions

> AI コーディングエージェント(Claude Code / Codex 等)向けの指示書。規約の更新はこのファイルのみで行い、`CLAUDE.md` は本ファイルを import して Claude 固有の補足だけを持つ。

## Project
森林・里山の相続・管理・出口整理を扱う「ネイチャーキャピタル・リアルエステイト」の Web サイト。日本GXグループの事業。
**ビルド無しの静的 HTML / CSS / JS**。`docs/` 配下だけが GitHub Pages で公開される。

- 公開 URL: https://yuyakawamura-blip.github.io/fudousanbusiness-jgx/
- デザインの元: Figma `voPyGfM8U5sFDuvgGXEyzK`(ページとフレームの対応は `maintenance/figma.md`)
- サイト階層図: `LP_HIERARCHY.drawio`

## 対象者
- **主役: 山林所有者**(相続・遠方管理・売却/活用)。トップと主要導線はこの人向けに書く
- 副: 林業事業体(森林経営計画作成支援ツール)/ 企業・参加者・一般の方(森林を知る・オープンデータ)
- 読み手に高齢の方が多い前提で、文字の大きさ・行間・分かりやすい言葉を優先する

## 構成
| パス | 内容 |
| --- | --- |
| `docs/index.html` + `docs/home.css` | トップ |
| `docs/about/` `docs/concerns/` `docs/services/` | 私たちについて / お悩みから探す / サービス一覧 |
| `docs/services/satoyama-real-estate/` | 山林所有者向けサービス |
| `docs/services/forest-planning-tool/` | 林業事業体向けツール |
| `docs/forest/` `docs/forest-guide/` `docs/forest/sustainable-forestry/`(`en/` あり) | 森林を知る系 |
| `docs/forest-data/` | 森林オープンデータ(地図・カタログ。`catalog.json` は毎日自動更新) |
| `docs/partners/` | 企業・個人の方向け(企業の森づくり / 自然資本・クレジット / 体験・ボランティア / 山林の取得・活用) |
| `docs/styles.css` | 全ページ共通 CSS |
| `docs/nav.js` | スマホ幅(720px 以下)のメニューボタンを全ページのヘッダーに追加する |
| `docs/auth.js` | 全ページのパスワードゲート(クライアント側のみ。本当の保護ではない) |
| `docs/404.html` | 存在しない URL 用。GitHub Pages はどの階層でもこのファイルを返すので `<base href="/fudousanbusiness-jgx/">` でリンクの基準を固定している |
| `archive/` | 公開対象外の旧ページ |
| `maintenance/` | 運用メモ(デザインの決まり `design.md` / Figma / 森林データ / ローカル確認用の nginx 設定) |

## Commands
- ローカル確認: `docker compose up -d`(このフォルダで実行、停止は `docker compose down`)→ http://localhost:8000/ 。`/fudousanbusiness-jgx/` 配下は公開時と同じパス(404 ページ確認用)、`/__preview/` 配下はパスワード画面なし(撮影用)
- Docker が無いとき: `python3 -m http.server 8000 -d docs`(同じポートなので Docker と同時には使えない)
- 森林データ更新のテスト: `python3 -m unittest discover -s tests -p 'test_forest_data.py'`
- `tests/rendered-html.test.mjs` は旧ビルド(`dist/`)用で、現行サイトの確認には使わない

## Conventions
- **見た目と画面構成の決まりは `maintenance/design.md`**。ページを作る・直すときは先に読む
- **ヘッダー / フッターは各 HTML に直書き**。ナビやフッターを変えたら全ページ(各 index.html 12 ファイル + `docs/404.html`)を同じように直す。ヘッダーナビは対象者別: 山林をお持ちの方 / 林業事業体の方 / 企業・個人の方 / 森林を知る / 私たちについて / 無料相談
- リンク・画像は**相対パス**。ページの階層(`../` / `../../` / `../../../`)に合わせる
- ヘッダーとフッターの相談リンクは「**無料相談**」(英語版は Free consultation)。本文の相談ボタンは所有者向けページで「無料相談を申し込む」、事業者・企業向けページで「お問い合わせをする」。外部リンクには CSS で ↗ が付くので本文に矢印を書かない。リンク先は共通の Google フォーム(`target="_blank" rel="noopener noreferrer"`)
- 山林所有者向けサービスの名前は「**さとやま不動産**」(説明が要る所では「山林・里山の管理と出口整理」を添える)。サービスの並びは所有者向け → 林業事業体向け → 企業・個人の方の順
- セクションの小見出しラベル(`.label` など)は日本語で書く(英語版ページとブランド名「NATURE CAPITAL REAL ESTATE」を除く)。見出しは `word-break: auto-phrase` で文節改行するので、1 文節が列幅を超えない大きさにする
- ページタイトルは「ページ名 | ネイチャーキャピタル・リアルエステイト」(英語版は「… | Nature Capital Real Estate」)
- 文字色は背景とのコントラスト比 4.5 以上にする(小見出しラベルは #4f6a57)
- 「ご相談の流れと費用」は共通部品 `.flow-fees`(styles.css)。トップとさとやま不動産で同じ 3 段階(無料 / 無料 / 事前にお見積り)を保つ
- ロゴは `docs/assets/nature-capital-mark.svg`
- 各ページの `<head>` にはファビコンと共有用(OGP)のメタタグがある。新しいページを作るときも同じ一式を入れる(og:url は公開 URL の絶対パス、共有画像は `docs/assets/og-image.jpg`)。独自ドメインに移すときは og:url / og:image を書き換える
- 新しい画像は **WebP・1 枚 300KB 目安**、ファイル名は英小文字のケバブケース。`alt` を必ず書く
- レイアウトはデスクトップとスマホ幅(720px 以下)の両方で確認する
- 自然資本価値・売却・認証の結果を約束する表現を書かない(既存の注意書きの方針に合わせる)
- コミットは日本語で「何をしたか」を 50 文字以内・prefix なし

## Deploy
- 変更は **`develop` ブランチに push する**(`main` に直接 push しない)。`main` への反映(マージ / PR)はユーザーが決める。`catalog.json` の自動コミットは `main` にだけ入るので、`develop` には必要に応じて `origin/main` を取り込む
- `main` への push で `.github/workflows/deploy-pages.yml`(リポジトリ直下)が `docs/` を公開する
- ワークフローが毎日 `catalog.json` をコミットするので、**push 前に必ず `git pull --rebase`**
- リポジトリ直下には別プロジェクト(`jcredit-creation-system/` `jgx-hp/` など)もある。このサイトのファイル以外をコミットに含めない

## Don'ts
- `docs/` の外に公開したいファイルを置かない(公開されない)
- `archive/` のファイルを編集しない
- `git push --force` / `git reset --hard` をしない
- Google フォームの URL やプライバシーポリシーのリンクを勝手に変えない
