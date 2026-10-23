@AGENTS.md

# Nature Capital Real Estate サイト — Claude Code 用追記

規約は @AGENTS.md を参照。以下は Claude Code 固有の補足。パスはどれもサイトのフォルダ `Nature capital real estate/` からの相対パス。

## 作業フロー
1. セッション開始時に `PROGRESS.md` の末尾「次回最初に読むファイル」と `PLAN.md` を読む。デザインの作業なら `maintenance/design.md` も読む。並行作業(worktree のレーン)なら、先に `WORKLANES.md` の手順に従う
2. タスクを受けたら `PLAN.md` を更新する(チェックボックス形式)。`[ ]` の項目にはレーンのタグ `<!-- lane: <ID> -->` か `<!-- lane: none -->` を付け、push したら `worklane.py add` で表に行を足す(`WORKLANES.md` の 6。レーンの外で足した項目も同じ)
3. ユーザーへの確認は **1 回に 1 問、選択式(AskUserQuestion)** で聞く。おすすめを先頭に置く
4. 変更後はローカルサーバで表示を確認してから報告する
5. コミット・push はユーザーに確認してから行う
6. セッション終了時に `PROGRESS.md` の末尾に「やったこと」と「次回最初に読むファイル」を追記する

## 権限の設定
`.claude/settings.json` はリポジトリ直下とサイトのフォルダの 2 か所にある。Claude Code はセッションを始めたフォルダの設定を読むので、リポジトリ直下から始めても、`Nature-Capital-Real-Estate-LP.code-workspace` でサイトのフォルダを開いても、同じ禁止事項が効くようにしている。片方を変えたら、もう片方も同じように変える(`archive/` のパスの書き方だけが違う)。
