@AGENTS.md

# Nature Capital Real Estate サイト — Claude Code 用追記

ルートの規約は @AGENTS.md を参照。以下は Claude Code 固有の補足。

## 作業フロー
1. セッション開始時に `PROGRESS.md` の末尾「次回最初に読むファイル」と `PLAN.md` を読む
2. タスクを受けたら `PLAN.md` を更新する(チェックボックス形式)
3. ユーザーへの確認は **1 回に 1 問、選択式(AskUserQuestion)** で聞く。おすすめを先頭に置く
4. 変更後はローカルサーバで表示を確認してから報告する
5. コミット・push はユーザーに確認してから行う
6. セッション終了時に `PROGRESS.md` の末尾に「やったこと」と「次回最初に読むファイル」を追記する
