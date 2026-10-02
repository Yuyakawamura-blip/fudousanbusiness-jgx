# 森林オープンデータLP：資料確認メモ

確認日：2026-09-06

林野庁の指定ページ本文と、本文から直接案内された関連資料（外部サイトの標準仕様書を含む）を取得し、LPに関係するデータ仕様・公開方法・利用条件を重点確認した。全報告書の全図表や、リンク先からさらに分岐するサイト全体を精査したという意味ではない。PDF本文の抽出結果は一時領域に保持し、原本を当サイトに再配布しない。

## 実装に反映した点

- 区域レイヤと航空レーザ森林資源解析、全国森林資源メッシュは異なるデータ。今回の地図は指定された区域レイヤに限定。
- データは2024年度に収集した原典を加工。実際の時点は属性「データ時点」を確認。地図の境界は所有権・所有界・面積の証明にならない。
- 配布一覧では説明のZIP表記と実ファイルの7z表記が異なるため、実リソースの形式を採用。現在は47都道府県の7zと規約・タイル・QLR等で計56リソース。
- データ定義書の座標系はGeoPackageがJGD2011/EPSG:6668、タイルがEPSG:3857。ラスタはズーム5–16。ベクトルの定義書は13–16だが現行style.jsonは12–16の設定があり、接続案内では公式style.jsonをそのまま利用する。
- CKANの汎用ライセンス欄は旧表記。個別重要情報が指定するPDL1.0へのリンク、林野庁への出典、重ね合わせ・表示濃度の加工を記載。
- 航空レーザは一般公開分と申請提供分を区別。申請提供を一般向け自由ダウンロードとして案内しない。
- 森林資源解析・オープンデータ標準は森林GISフォーラムが運用。クラウド標準は公開データの一覧ではなく情報連携の仕様。
- 個人情報ガイドラインとクラウドのセキュリティ資料は、所有者情報の第三者提供とデータ連携の前提を扱う。本LPでは個人情報の結合・所有者照会を行わない。
- スマート林業実践マニュアルは人材育成・合意形成・課題に応じた技術選定を重視。区域データだけで経営計画や現地調査が完成するとの表現を避ける。

## 直接リンク資料の取得・本文確認用一覧

- [航空レーザ測量について(外部リンク:国土地理院)](https://www.gsi.go.jp/kankyochiri/Laser_index.html) — HTML取得済み
- [森林資源データ解析・管理標準仕様書 Ver3.0(外部リンク:日本森林技術協会)(PDF：4,697KB)](https://fgis.jp/wordpress/wp-content/uploads/2025/08/%E6%A3%AE%E6%9E%97%E8%B3%87%E6%BA%90%E3%83%87%E3%83%BC%E3%82%BF%E8%A7%A3%E6%9E%90%E3%83%BB%E7%AE%A1%E7%90%86%E6%A8%99%E6%BA%96%E4%BB%95%E6%A7%98%E6%9B%B8Ver3_0_2025%E5%B9%B47%E6%9C%88%E7%89%88fin.pdf) — PDF本文抽出済み
- [森林情報に関するオープンデータ標準仕様書【航空レーザ森林資源解析データ編】Ver2.0(外部リンク:日本森林技術協会)(PDF：6,222KB)](https://fgis.jp/wordpress/wp-content/uploads/2025/08/%E6%A3%AE%E6%9E%97%E6%83%85%E5%A0%B1%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E3%82%AA%E3%83%BC%E3%83%97%E3%83%B3%E3%83%87%E3%83%BC%E3%82%BF%E6%A8%99%E6%BA%96%E4%BB%95%E6%A7%98%E6%9B%B8Ver2_0_2025%E5%B9%B47%E6%9C%88%E7%89%88fin.pdf) — PDF本文抽出済み
- [高精度な森林情報の整備・活用のためのリモートセンシング技術やその利用方法等に関する手引き(平成30年3月)(PDF : 8,417KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-20.pdf) — PDF本文抽出済み
- [航空機LiDARデータを使った地位指数分布図の作成の手引き（令和4年3月）(PDF : 4,479KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-85.pdf) — PDF本文抽出済み
- [令和2年度レーザ計測による森林資源データの解析・管理の標準化事業報告書(外部リンク:日本森林技術協会)(PDF：48,930KB）](http://www.jafta.or.jp/pdf/sinrinshigen-hyoujunka/0_R2_shinrinshigenhyoujunka_report.pdf) — PDF本文抽出済み
- [令和3年度レーザ計測による森林資源データの解析・管理の標準化事業報告書(外部リンク:日本森林技術協会)(PDF：12,127KB）](http://www.jafta.or.jp/pdf/sinrinshigen-hyoujunka/0_R3_shinrinshigenhyoujunka_report.pdf) — PDF本文抽出済み
- [令和3年度リモートセンシング技術等を用いた森林の機能別調査の手法に関する調査事業報告書(令和4年3月)(PDF : 3,696KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-15.pdf) — PDF本文抽出済み
- [令和6年度森林資源調査手法の複合利用に関する評価検証委託事業報告書(PDF : 9,216KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-84.pdf) — PDF本文抽出済み
- [令和7年度森林資源調査手法複合利用評価検証委託事業(令和8年3月)(PDF : 21,727KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-86.pdf) — PDF本文抽出済み
- [令和6年度飛散予測の高度化に向けた航空レーザ計測・解析委託事業（栃木県東部）分割1(PDF : 28,936KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-88.pdf) — PDF本文抽出済み
- [令和6年度飛散予測の高度化に向けた航空レーザ計測・解析委託事業（栃木県東部）分割2(PDF : 19,362KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-89.pdf) — PDF本文抽出済み
- [令和6年度飛散予測の高度化に向けた航空レーザ計測・解析事業（群馬県東部）(PDF : 29,177KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-90.pdf) — PDF本文抽出済み
- [(PDF : 1,752KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-80.pdf) — PDF本文抽出済み
- [外部リンク：国土地理院)](https://www.gsi.go.jp/KOUKYOU/index.html) — HTML取得済み
- [令和4年度森林情報オープン化推進対策事業報告書(令和5年3月)(PDF : 9,246KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-2.pdf) — PDF本文抽出済み
- [令和5年度森林情報オープン化推進対策委託事業報告書(令和6年3月)(PDF : 11,924KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-8.pdf) — PDF本文抽出済み
- [令和6年度森林情報プラットフォーム化推進委託事業報告書(令和7年3月)(PDF : 10,840KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-83.pdf) — PDF本文抽出済み
- [令和7年度全国統合データ整備・公開委託事業(令和8年3月)(PDF : 2,499KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-91.pdf) — PDF本文抽出済み
- [令和7年度保安林情報のオープンデータ化予備調査委託事業(令和8年3月)(PDF : 1,827KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-87.pdf) — PDF本文抽出済み
- [(PDF : 776KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-81.pdf) — PDF本文抽出済み
- [(PDF : 1,917KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-82.pdf) — PDF本文抽出済み
- [森林クラウドシステムに係る標準仕様書ver.6.1(令和4年3月)(外部リンク：日本森林技術協会HP)(PDF:6,958KB)](https://fgis.jp/wordpress/wp-content/uploads/2022/07/%E6%A3%AE%E6%9E%97%E3%82%AF%E3%83%A9%E3%82%A6%E3%83%89%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%81%AB%E4%BF%82%E3%82%8B%E6%A8%99%E6%BA%96%E4%BB%95%E6%A7%98%E6%9B%B8Ver6_1.pdf) — PDF本文抽出済み
- [森林クラウドシステムに関わる情報セキュリティガイドラインVer6.0(令和3年3月)(外部リンク:日本森林技術協会)(PDF:2,241KB)](https://fgis.jp/wordpress/wp-content/uploads/2021/09/%E6%A3%AE%E6%9E%97%E3%82%AF%E3%83%A9%E3%82%A6%E3%83%89%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%81%AB%E9%96%A2%E3%82%8F%E3%82%8B%E6%83%85%E5%A0%B1%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E3%82%AC%E3%82%A4%E3%83%89%E3%83%A9%E3%82%A4%E3%83%B3Ver6.0.pdf) — PDF本文抽出済み
- [スマート林業実践マニュアル(総集編)(PDF : 7,383KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-1.pdf) — PDF本文抽出済み
- [平成30年度スマート林業構築普及展開事業事例集(PDF : 2,832KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-3.pdf) — PDF本文抽出済み
- [令和元年度スマート林業構築普及展開事業事例集(PDF : 4,201KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-33.pdf) — PDF本文抽出済み
- [平成30年度報告書(PDF : 9,020KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-28.pdf) — PDF本文抽出済み
- [令和元年度報告書(PDF : 15,601KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-36.pdf) — PDF本文抽出済み
- [令和 2年度報告書(PDF : 17,338KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-55.pdf) — PDF本文抽出済み
- [令和 3年度報告書(本体)(PDF : 26,829KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-73.pdf) — PDF本文抽出済み
- [令和 3年度報告書(地域協議会資料)(PDF : 27,218KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-74.pdf) — PDF本文抽出済み
- [令和 4年度報告書(一式)(PDF : 22,885KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-4.pdf) — PDF本文抽出済み
- [(PDF : 5,290KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-5.pdf) — PDF本文抽出済み
- [(PDF : 9,056KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-6.pdf) — PDF本文抽出済み
- [(PDF : 8,947KB)](https://www.rinya.maff.go.jp/j/keikaku/smartforest/attach/pdf/smart_forestry-7.pdf) — PDF本文抽出済み
- [ICT林業生産管理システム標準仕様書案 Ver1.0(アプリ編)(外部リンク:日本森林技術協会)(PDF：1,225KB)](http://www.jafta.or.jp/pdf/ICTseisankanri-hyoujunka/1_R3_ICTseisankanri_hyoujunsiyousho_app.pdf) — PDF本文抽出済み
- [付表(外部リンク:日本森林技術協会)(PDF:148KB)](https://www.jafta.or.jp/pdf/ICTseisankanri-hyoujunka/1_R3_ICTseisankanri_hyoujunsiyousho_app_appendix.pdf) — PDF本文抽出済み
- [ICT林業生産管理システム標準仕様書案 Ver1.0(機械管理編)(外部リンク:日本森林技術協会)(PDF：1,493KB)](http://www.jafta.or.jp/pdf/ICTseisankanri-hyoujunka/2_R3_ICTseisankanri_hyoujunsiyousho_kikaikanri.pdf) — PDF本文抽出済み
- [付表(外部リンク:日本森林技術協会)(PDF:84KB)](https://www.jafta.or.jp/pdf/ICTseisankanri-hyoujunka/2_R3_ICTseisankanri_hyoujunsiyousho_kikaikanri_appendix.pdf) — PDF本文抽出済み
- [ICT生産管理システムの標準化事業報告書(令和2年度)(外部リンク:日本森林技術協会)(PDF：8,244KB)](http://www.jafta.or.jp/pdf/ICTseisankanri-hyoujunka/0_R2_ICTseisankanrihyoujunka_report.pdf) — PDF本文抽出済み
- [ICT生産管理システムの標準化事業報告書(令和3年度)(外部リンク:日本森林技術協会)(PDF：6,349KB)](http://www.jafta.or.jp/pdf/ICTseisankanri-hyoujunka/0_R3_ICTseisankanrihyoujunka_report.pdf) — PDF本文抽出済み
- [公共データ利用規約（第1.0版）](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0) — HTML取得済み
- [森林計画対象森林レイヤの利用規約](https://www.geospatial.jp/ckan/dataset/aa0bc6ed-f5ac-4f05-89c6-0c7034503303/resource/248232db-b42b-4e34-8f47-5bfb37bd1b59/download/forest_planning_target_forest_layer_terms_of_use.pdf) — PDF本文抽出済み
- [公共データ利用規約（第１.0版）に関する重要情報](https://www.geospatial.jp/ckan/dataset/aa0bc6ed-f5ac-4f05-89c6-0c7034503303/resource/699da07c-08aa-4fc8-887e-6585d55dfaf5/download/important_notes_on_public_data_usage_layer_terms_v1.0.pdf) — PDF本文抽出済み
- [データ定義書（令和８年３月23日版、林野庁森林整備部計画課）](https://www.geospatial.jp/ckan/dataset/aa0bc6ed-f5ac-4f05-89c6-0c7034503303/resource/5e031fcf-ed9a-4594-892a-4129feccea0c/download/data_dictionary_20260323.pdf) — PDF本文抽出済み

## その他の確認先

- [林野庁の指定ページ](https://www.rinya.maff.go.jp/j/keikaku/smartforest/smart_forestry.html)
- [森林計画対象森林レイヤ](https://www.geospatial.jp/ckan/dataset/layer)（APIで全リソースを取得）
- [森林情報WEB-GIS](https://webgis-rashinban-mori.com/)（配信入口を確認。アプリ内の全レイヤの品質検証は対象外）
- [地理院タイル一覧](https://maps.gsi.go.jp/development/ichiran.html)
- [Leaflet API](https://leafletjs.com/reference.html)
- [GitHubの定期実行](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
