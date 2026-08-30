# hougenjiten-data

日本全国の方言辞書データ。[hougenjiten.com](https://hougenjiten.com) が使っている語彙・文法規則の一次データを、
**CC BY-SA 4.0** で公開しています。

Wikipedia 日本語版の方言記事と JMdict/EDICT から作った派生物のため、
CC BY-SA の継承（Share-Alike）条項にしたがって同じ条件で公開しています。
出典を表示すれば、誰でも自由に利用・改変・再配布できます。

---

## 収録内容

| ファイル | 行数 | 内容 |
| --- | --- | --- |
| `dict/vocab-merged.csv` | 5,023 | 方言語彙。122 の方言記事から抽出（Wikipedia 4,487 ＋ JMdict 536） |
| `dict/grammar-rules.csv` | 575 | 変換用の文法規則 323 条 ＋ 誤変換防止（protect）252 条 / 12 方言 |
| `dict/wikipedia-articles.txt` | 263 | 抽出元となった Wikipedia 記事名と記事サイズ |
| `dict/kawaii.csv` | 39 | 「かわいい方言・面白い方言」の分類と解説文 |
| `dict/differentiators.json` | 12 地域 | 隣接方言との違いの解説文 |
| `dict/exclude.csv` | 39 | サイト側で扱わないキーワード（NSFW・単字助詞・他社ブランド語） |
| `reference-converter.py` | — | 変換アルゴリズムの参考実装（Python・依存ゼロ） |

キーワード調査データ（検索ボリューム等）は CC BY-SA ソースの派生物ではないため含めていません。

---

## `grammar-rules.csv` の形式

```csv
dialect,order,type,pattern,replace,note,confidence
関西,16,copula,だ$,や,断定の助動詞 だ→や,high
関西,34,negation,([かがさたなばまら])ない,\1へん,五段動詞の未然形+へん,high
関西,1,protect,しかない,,〜しかない は動詞否定ではない,high
```

| 列 | 説明 |
| --- | --- |
| `dialect` | 関西 / 大阪 / 京都 / 博多 / 広島 / 名古屋 / 三河 / 津軽 / 仙台 / 秋田 / 鹿児島 / 沖縄 |
| `order` | 適用順。昇順に当てる。同じ値は同一段階（大阪の五段否定 9 条が該当） |
| `type` | `protect` / `copula` / `negation` / `aspect` / `particle` / `lexical` / `phonology` |
| `pattern` | 標準語に対する正規表現。`$` で終わる場合は `(?=[。、，！？!?\s]|$)` に展開して使う |
| `replace` | 置換文字列。`\1` は捕獲グループ |
| `confidence` | `high` 507 / `medium` 62 / `low` 6。**medium と low の 68 条は日本語母語話者による検証が済んでいません** |

### 適用アルゴリズム（3 段階・順序厳守）

```
① PROTECT  type=protect のパターンに一致する箇所を番兵へ退避する
② APPLY    残りの規則を order 昇順に適用する
③ RESTORE  番兵を元の文字列へ戻す
```

**① を省くと壊れます。** `([かがさたなばまら])ない → \1へん` は五段動詞の否定を狙った規則ですが、
`しかない` `はかない` `情けない` の「ない」は動詞否定ではありません。

| 入力 | PROTECT なし | 正しい |
| --- | --- | --- |
| 捨てるしかない | ほかすしかへん ❌ | ほかすしかない |
| それははかない夢だ | それははけへん夢や ❌ | それははかない夢や |
| 情けない話だ | 情けへん話や ❌ | 情けない話や |

誤変換は未変換よりずっと悪い、というのがこのデータ設計の前提です。

---

## `vocab-merged.csv` の形式

```csv
source,dialect,word,kanji,gloss_ja,gloss_en,section
Wikipedia,広島弁,たいぎい,,面倒くさい,,た行
JMdict,近畿,あかん,明かん,,useless; no good; cannot; must,
```

`dialect` 列は**抽出元の Wikipedia 記事名**です（方言名そのものとは限りません）。
たとえば `近畿` `近畿方言` `大阪弁 (前田勇)` はいずれも関西の語彙ですが、別々の記事名として
入っています。抽出元の記事名と記事サイズの一覧は `dict/wikipedia-articles.txt` にあります。

なお、記事名をサイト上の地域ページへ束ねる対応表は本リポジトリには含まれません
（本サイトの構成そのものであり、CC BY-SA ソースの派生物ではないため）。
記事名は概ね方言名なので、利用目的に合わせて各自で束ねてください。

Wikipedia の表から機械抽出しているため、`gloss_ja` にウィキ記法（`||`、`align="..."`）が
残っている行があります。利用する際は各セルを `||` で分割し、日本語の断片を拾ってください。

---

## 出典

このデータは以下の派生物です。

- **Wikipedia 日本語版** の方言関連記事 263 件 — [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ja)
  記事名の一覧は `dict/wikipedia-articles.txt` にあります。
- **JMdict/EDICT** — [Electronic Dictionary Research and Development Group](https://www.edrdg.org/)（EDRDG）,
  [CC BY-SA 4.0](https://www.edrdg.org/edrdg/licence.html)

## ライセンス

[Creative Commons 表示 - 継承 4.0 国際（CC BY-SA 4.0）](https://creativecommons.org/licenses/by-sa/4.0/deed.ja)

再配布・改変は自由ですが、出典の表示と、同じライセンスでの公開が必要です。
詳細は [`LICENSE`](LICENSE) をご覧ください。

## 注意

方言には市町村・世代による差が大きく、このデータがすべての話者にあてはまるわけではありません。
特に `confidence` が `medium` / `low` の規則は未検証です。
誤りを見つけたら Issue でお知らせください。
