# CalcDaytimeStreamlit

日の出🌅・日の入り🌇・日中の長さ🌞を計算して可視化する Streamlit アプリです。

## 概要

このリポジトリは、もともと Mercury Cloud 向けに作成したアプリを、Streamlit で実行できるように移行したものです。  
`PyEphem` による天文計算と `matplotlib` のグラフ表示で、指定した緯度・経度における年間の日照情報を確認できます。

サンプルアプリのURLは次のとおりです。

https://calcdaytime.streamlit.app

![image](assets/SampleAppImage.jpg)

## 主な機能

- 緯度・経度を入力して日の出/日の入り時刻を計算
- 指定地点のタイムゾーンを自動判定（`timezonefinder`）
- 年間の日の出/日の入り時刻の推移をグラフ表示
- 年間の日中長（昼の長さ）をグラフ表示
- 当日の情報と、最早/最遅・夏至/冬至のサマリを表示
- URL クエリパラメータ（`lat`, `lon`）による地点指定

## セットアップ

1. 依存パッケージをインストールします。

```bash
pip install -r requirements.txt
```

2. Streamlit アプリを起動します。

```bash
streamlit run streamlit_app.py
```

起動後、通常は `http://localhost:8501` でアクセスできます。

## 使い方

- デフォルト座標は横浜（`lat=35.4500`, `lon=139.6500`）です。
- サイドバーの入力欄で緯度・経度を変更できます。
- URL にクエリを付けることで、地点を直接指定できます。

例:

- 東京: `http://localhost:8501/?lat=35.6812&lon=139.7671`
- 札幌: `http://localhost:8501/?lat=43.0642&lon=141.3469`
- グリニッジ天文台: `http://localhost:8501/?lat=51.4769&lon=-0.0005`

## 🗺位置

### デフォルト

#### 横浜（神奈川）@国立天文台

https://calcdaytime.streamlit.app

### カスタム位置

#### 🗾国内

| 地域     | リンク                                                                  |
| ------ | -------------------------------------------------------------------- |
| 東京     | <https://calcdaytime.streamlit.app?lat=35.6812&lon=139.7671> |
| 札幌     | <https://calcdaytime.streamlit.app?lat=43.0642&lon=141.3469> |
| 沖縄（那覇） | <https://calcdaytime.streamlit.app?lat=26.2124&lon=127.6809> |

#### 🌏海外

| 地域         | リンク                                                                   |
| ---------- | --------------------------------------------------------------------- |
| グリニッジ天文台   | <https://calcdaytime.streamlit.app?lat=51.4769&lon=-0.0005>   |
| ワシントンDC    | <https://calcdaytime.streamlit.app?lat=38.9072&lon=-77.0369>  |
| メルボルン      | <https://calcdaytime.streamlit.app?lat=-37.8136&lon=144.9631> |
| チクラーヨ（ペルー） | <https://calcdaytime.streamlit.app?lat=-6.7714&lon=-79.8411>  |

## ファイル構成

- [streamlit_app.py](streamlit_app.py): Streamlit アプリ本体
- [requirements.txt](requirements.txt): Streamlit 版の依存パッケージ
- [mercury/sample.ipynb](mercury/sample.ipynb): Mercury 版の元ノートブック
- [mercury/requirements.txt](mercury/requirements.txt): Mercury 版の依存パッケージ

## 使用ライブラリ

- [Streamlit](https://streamlit.io/)
- [PyEphem](https://rhodesmill.org/pyephem/)
- [timezonefinder](https://github.com/jannikmi/timezonefinder)
- [matplotlib](https://matplotlib.org/)
- [pytz](https://pythonhosted.org/pytz/)

## 参考

- https://rhodesmill.org/pyephem/
- https://streamlit.io/
- https://eco.mtk.nao.ac.jp/koyomi/dni/dni15.html
