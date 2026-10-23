---
name: lane
description: WORKLANES.md の次のレーンを取り、worktree で作業し、push の前でユーザーの承認を待ち、片付けまで行う。1 回の実行で 1 レーン。
disable-model-invocation: true
---

# /lane — レーンを 1 つ取って仕上げる

`WORKLANES.md` の手順を 1 レーン分、決まった順に行う。手順の中身と理由は `WORKLANES.md` と `maintenance/design.md` §A にあり、このファイルは順番だけを持つ。両者が食い違うときは `WORKLANES.md` に従い、食い違いをユーザーに伝える。

パスはサイトのフォルダ `/Users/gh/Documents/GitHub/fudousanbusiness-jgx/Nature capital real estate`(以下 `SITE`)からの相対。

## 1. 読む
- `SITE/PROGRESS.md` の末尾の「次回最初に読むファイル」、`SITE/PLAN.md`、`SITE/WORKLANES.md` の「使い方」と「レーンでの作業の決まり」
- デザインの作業なら `SITE/maintenance/design.md` も

## 2. レーンを取る
- このセッションの名前を 1 回だけ作り、以降も同じものを使う: `claude-<月日>-<時分>-<16 進 4 桁>`(例 `claude-1023-1612-a3f9`)。モデル名だけでは、どのセッションのレーンか見分けられないため
- `python3 "SITE/scripts/worklane.py" --who <名前>` を実行し、終了コードを読む
  - **3**: 取れるレーンがない。表示された一覧をユーザーに伝えて終わる。表から手で選ばない
  - **0**: 表示された Set up のコマンドを順に実行し(worktree と確認用のコンテナ)、`Work in:` のフォルダで作業する
  - **それ以外**: 出力をそのまま伝えて止まる

## 3. 作業する
- メインのチェックアウトでは作業しない。確認用サーバは表示されたポートを使い、8000 は使わない
- 変更の前に、問題・計画・確かめ方を説明し、ユーザーの了承を待つ
- ユーザーに決めてもらうことは 1 回に 1 問、AskUserQuestion で聞き、おすすめを先頭に置く
- 今は答えが出ない人の判断や物を待つことになったら、`worklane.py mark <ID> b --note <待っているもの>` にして終わる
- 途中でやめるときは `worklane.py mark <ID> o` に戻し、worktree の扱いをユーザーに伝える
- 作業のコミットは、確かめ終えてからユーザーに確認して行う。`PLAN.md` と `PROGRESS.md` はまだ直さない

## 4. push の前で止まる
作業のコミットを終えたら、コミットの一覧(`git log --oneline origin/develop..HEAD`)と確かめた結果をまとめ、AskUserQuestion で 1 問聞く: 「develop に取り込んで push してよいか」。おすすめは確認の結果で決める(失敗・未確認が残るなら「まだ push しない」を先頭に)。

## 5. 承認されたら仕上げる(`WORKLANES.md` の 3 と 5)
worktree の中で、この順に行う。どれかが失敗したら、そこで止まって伝える。
1. `git pull --rebase origin develop`
2. `python3 scripts/check_links.py`
3. `PLAN.md` のチェックと `PROGRESS.md` の追記(「やったこと」と「次回最初に読むファイル」)を 1 コミット
4. `git push origin HEAD:develop`
5. worktree の外から `python3 "SITE/scripts/worklane.py" finish <ID>`。終了コード 1 なら、表示された理由を直してからもう一度実行する。自分で `rm` や `git branch -D` を使わない

## 6. 終える
やったことを短く伝え、次のレーンに進むなら `/clear` のあとに `/lane` を実行するよう伝える。このセッションのまま次のレーンを取らない(前のレーンの文脈が残り、毎回の読み込みが重くなるため)。
