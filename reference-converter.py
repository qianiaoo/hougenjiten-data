#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""方言変換 参考实现（纯规则・零 LLM）。
两层：① grammar-rules.csv 的有序正则  ② vocab-merged.csv 的词汇替换。
生产环境应移植为 JS 在前端跑——那样连服务器成本都是 0。
"""
import csv, re, sys, collections

def load_rules(path='dict/grammar-rules.csv'):
    by = collections.defaultdict(list)
    for r in csv.DictReader(open(path)):
        if not r['pattern']: continue
        pat = r['pattern']
        if pat.endswith('$'):
            pat = pat[:-1] + r'(?=[。、，！？!?\s]|$)'   # 日语句末：允许标点在后
        key = ('_protect_' + r['dialect']) if r['type'] == 'protect' else r['dialect']
        by[key].append((int(r['order']), pat, r['replace'], r['type'], r['confidence']))
    for d in by: by[d].sort(key=lambda x: x[0])
    return by

def load_vocab(path='dict/vocab-merged.csv', dialect_filter=None):
    """标准语→方言 的反向索引：用 gloss_ja 里形如「〜のこと」的解释做粗匹配。
    这一层默认关闭——自动反向映射噪音大，见 README §4。"""
    out = collections.defaultdict(dict)
    for r in csv.DictReader(open(path)):
        g = r['gloss_ja']
        m = re.match(r'^([ぁ-んァ-ヴー一-龥]{2,8})(のこと|。|$)', g)
        if m: out[r['dialect']][m.group(1)] = r['word']
    return out

def convert(text, dialect, rules, vocab=None, trace=False):
    log = []
    # ① 保护：不该被规则碰的固定表现，先替换为哨兵
    guards = [(pat, f'\x00{i}\x00') for i, (pat, *_ ) in
              enumerate((r for r in rules.get('_protect_' + dialect, [])), 1)]
    saved = []
    for i, (order, pat, rep, typ, conf) in enumerate(rules.get('_protect_' + dialect, []), 1):
        def _keep(m, i=i):
            saved.append((i, m.group(0))); return f'\x00{i}\x00'
        text = re.sub(pat, _keep, text)
    for order, pat, rep, typ, conf in rules.get(dialect, []):
        try:
            new = re.sub(pat, rep, text)
        except re.error:
            continue
        if new != text:
            log.append(f'  [{order:>3} {typ:9} {conf:6}] {pat} → {rep}')
            text = new
    if vocab:
        for std, dia in sorted(vocab.get(dialect, {}).items(), key=lambda x: -len(x[0])):
            if std in text:
                text = text.replace(std, dia); log.append(f'  [vocab] {std} → {dia}')
    # ② 还原被保护的片段
    for i, orig in saved:
        text = text.replace(f'\x00{i}\x00', orig, 1)
    return (text, log) if trace else text

if __name__ == '__main__':
    rules = load_rules()
    DIALECTS = ['関西', '大阪', '京都', '博多', '広島', '名古屋', '三河',
                '津軽', '仙台', '秋田', '鹿児島', '沖縄']
    tests = ['これは本だ。', '明日は行かない。', 'とても面白いだろう。', '疲れたから今日は帰る。',
             '本当にありがとう。', 'ご飯を食べているところです。', '東京に行く。', '捨てるしかない。']
    # 「ない」が動詞否定ではない語 —— 壊れてはいけない
    GUARD = ['それははかない夢だ。', '情けない話だ。', 'だらしないところがある。',
             'とんでもない。', '捨てるしかない。', '危ない。', 'もったいない。']
    KEEP = ['はかない', '情けない', 'だらしない', 'とんでもない', 'しかない', '危ない', 'もったいない']

    if '--test' in sys.argv:
        bad = 0
        for d in DIALECTS:
            for t in GUARD:
                o = convert(t, d, rules)
                for w in KEEP:
                    if w in t and w not in o:
                        print(f'FAIL {d}: {t} -> {o}'); bad += 1
        print(f'誤変換回帰テスト: {"PASS ✅" if bad == 0 else f"FAIL {bad} 件"}'
              f'  （{len(DIALECTS)} 方言 × {len(GUARD)} 文）')
        sys.exit(1 if bad else 0)

    only = [a for a in sys.argv[1:] if not a.startswith('-')]
    for d in (only or DIALECTS):
        n = len(rules.get(d, []))
        print(f'\n===== {d}（規則 {n} 条）=====')
        for t in tests:
            o = convert(t, d, rules)
            print(('  ' if o != t else '× ') + f'{t}\n     → {o}')
