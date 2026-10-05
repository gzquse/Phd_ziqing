#!/usr/bin/env python3
"""Gate an STE-edited chapter against its original: citations, labels, refs, equations,
figures, tables, algorithms, listings and prose numbers must survive."""
import re, sys, collections
def strip_comments(s): return re.sub(r'(?<!\\)%.*', '', s)
def env_blocks(s, name):
    return re.findall(r'\\begin\{'+name+r'\*?\}.*?\\end\{'+name+r'\*?\}', s, re.S)
def norm(b): return re.sub(r'\s+', ' ', b).strip()
def analyse(path):
    s = strip_comments(open(path, encoding='utf8').read())
    d = {}
    d['cites'] = collections.Counter(k.strip() for m in re.findall(r'\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}', s) for k in m.split(','))
    d['labels'] = set(re.findall(r'\\label\{([^}]*)\}', s))
    d['refs'] = set(k.strip() for m in re.findall(r'\\(?:[cC]ref|labelcref|crefrange|ref|eqref)\{([^}]*)\}', s) for k in m.split(','))
    d['equations'] = collections.Counter(norm(b) for n in ('equation','align','gather','multline') for b in env_blocks(s, n))
    d['tikz'] = collections.Counter(norm(b) for b in env_blocks(s, 'tikzpicture') + env_blocks(s, 'quantikz'))
    d['tables'] = collections.Counter(norm(b) for n in ('tabular','tabularx','longtable') for b in env_blocks(s, n))
    d['algos'] = collections.Counter(norm(b) for b in env_blocks(s, 'algorithm'))
    d['listings'] = collections.Counter(norm(b) for b in env_blocks(s, 'lstlisting'))
    d['figures'] = len(env_blocks(s, 'figure'))
    # prose numbers: outside tikz/tables/listings/equations
    prose = s
    for n in ('tikzpicture','quantikz','tabular','tabularx','longtable','lstlisting','equation','align','algorithm'):
        prose = re.sub(r'\\begin\{'+n+r'\*?\}.*?\\end\{'+n+r'\*?\}', ' ', prose, flags=re.S)
    prose = re.sub(r'\\(?:label|ref|cref|Cref|labelcref|crefrange|cite|input|includegraphics)\{[^}]*\}', ' ', prose)
    d['numbers'] = collections.Counter(re.findall(r'(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][-+]?\d+)?(?![\w])', prose))
    d['words'] = len(re.findall(r"[A-Za-z][A-Za-z'-]+", re.sub(r'\\[A-Za-z]+', ' ', prose)))
    body = re.sub(r'\\caption\{(?:[^{}]|\{[^{}]*\})*\}', ' ', prose)
    d['body'] = len(re.findall(r"[A-Za-z][A-Za-z'-]+", re.sub(r'\\[A-Za-z]+', ' ', body)))
    d['chapter'] = re.search(r'\\chapter\{[^\n]*', s)
    d['auth'] = re.search(r'\\authorshipstatement\{.*?\}\n', s, re.S)
    d['aidecl'] = re.search(r'\\aideclaration\{.*?\}\n', s, re.S)
    return d, s
def main(orig, new):
    a, sa = analyse(orig); b, sb = analyse(new); ok = True
    def fail(msg): 
        nonlocal ok; ok = False; print('FAIL', msg)
    if a['cites'] != b['cites']:
        diff = (a['cites'] - b['cites']), (b['cites'] - a['cites']); fail(f"citations differ: missing={dict(diff[0])} extra={dict(diff[1])}")
    if a['labels'] - b['labels']: fail(f"labels missing: {a['labels']-b['labels']}")
    newlabels = b['labels'] - a['labels']
    if a['refs'] - b['refs']: fail(f"ref targets missing: {a['refs']-b['refs']}")
    for key in ('equations','tikz','tables','algos','listings'):
        missing = a[key] - b[key]
        if missing: fail(f"{key}: {sum(missing.values())} block(s) changed or missing; first: {list(missing)[0][:120]!r}")
    if b['figures'] < a['figures']: fail(f"figure count fell {a['figures']} -> {b['figures']}")
    missing_nums = a['numbers'] - b['numbers']
    if missing_nums: fail(f"prose numbers missing/reduced: {dict(missing_nums)}")
    for key in ('chapter','auth','aidecl'):
        if a[key] and (not b[key] or norm(a[key].group(0)) != norm(b[key].group(0))): fail(f"{key} block changed")
    if '\\aideclaration' in sb and '\\aideclaration' not in sa: fail("new file uses \\aideclaration, which the author removed from the class")
    # brace balance
    if sb.count('{') != sb.count('}'): fail(f"brace imbalance {sb.count('{')} vs {sb.count('}')}")
    ratio = b['words'] / max(1, a['words']); bratio = b['body'] / max(1, a['body'])
    print(f"words {a['words']} -> {b['words']} ({ratio:.2f}x); body w/o captions {a['body']} -> {b['body']} ({bratio:.2f}x); figures {a['figures']} -> {b['figures']}; new labels {sorted(newlabels)}")
    if bratio > 1.0: fail("edited body text (excluding captions) is longer than the original")
    if ratio > 1.05: fail("edited chapter is more than 5% longer than the original including captions")
    print('PASS' if ok else 'REJECTED', new)
    return ok
if __name__ == '__main__':
    sys.exit(0 if main(sys.argv[1], sys.argv[2]) else 1)
