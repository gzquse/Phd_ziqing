#!/usr/bin/env python3
"""build_html.py - build a browsable HTML version of the TTU dissertation.

    python3 tools/build_html.py [--jobs N] [--force] [--skip-figures] [--build-dir DIR]

Pipeline
  1. flatten main.tex (inline every \\input in order, read the title-page metadata);
  2. cut every figure / algorithm2e environment out, compile each one as a standalone
     document with tectonic (same packages and macros as preamble.tex), convert the PDF to
     SVG with pdftocairo and cache by content hash (html/images/manifest.json);
     if a figure refuses to compile twice it is cropped out of main.pdf instead (PNG);
  3. preprocess what pandoc cannot handle (siunitx, text macros, \\code, cleveref, tables,
     longtable, declarations, equation numbers read from main.aux, ...);
  4. run pandoc (--citeproc, IEEE CSL, MathJax 3) with the template in tools/template.html
     written by this script;
  5. post-process the HTML (reference list position, listing captions, chapter kickers,
     lists of figures / tables) and verify the result.

Only thesis/tools/ and thesis/html/ are written to.
"""
import argparse
import hashlib
import html as htmlmod
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent          # thesis/tools
THESIS = HERE.parent                            # thesis/
HTML = THESIS / 'html'
IMAGES = HTML / 'images'
MANIFEST = IMAGES / 'manifest.json'
CSL = HERE / 'ieee.csl'
CSL_URL = 'https://raw.githubusercontent.com/citation-style-language/styles/master/ieee.csl'
BIB = THESIS.parent / 'bib' / 'refs.bib'
if not BIB.exists():
    BIB = THESIS / 'refs.bib'
MAIN_TEX = THESIS / 'main.tex'
MAIN_AUX = THESIS / 'main.aux'
MAIN_PDF = THESIS / 'main.pdf'
PREAMBLE_TEX = THESIS / 'preamble.tex'

MATHJAX_URL = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'


def which(name, fallback):
    return shutil.which(name) or fallback


TECTONIC = which('tectonic', '/opt/homebrew/bin/tectonic')
PANDOC = which('pandoc', '/opt/homebrew/bin/pandoc')
PDFTOCAIRO = which('pdftocairo', '/opt/homebrew/bin/pdftocairo')
PDFTOPPM = which('pdftoppm', '/opt/homebrew/bin/pdftoppm')
PDFTOTEXT = which('pdftotext', '/opt/homebrew/bin/pdftotext')

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print('  warning: ' + msg, file=sys.stderr)


def log(msg):
    print(msg, flush=True)


# --------------------------------------------------------------------------------------
# small LaTeX parsing helpers
# --------------------------------------------------------------------------------------

def match_brace(s, i):
    """s[i] == '{'; return the index of the matching '}'."""
    depth = 0
    j = i
    n = len(s)
    while j < n:
        c = s[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise ValueError('unbalanced braces near: ' + s[i:i + 60])


def match_bracket(s, i):
    """s[i] is just after '['; return the index of the closing ']' at brace depth 0."""
    depth = 0
    j = i
    n = len(s)
    while j < n:
        c = s[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif c == ']' and depth == 0:
            return j
        j += 1
    raise ValueError('unbalanced bracket near: ' + s[i:i + 60])


def replace_cmd(s, name, nargs, fn, allow_opt=False):
    """Replace every \\name[opt]{a1}..{an} by fn(args, opt). Occurrences without the
    expected brace arguments are left untouched."""
    out = []
    pos = 0
    pat = re.compile(r'\\' + re.escape(name) + r'(?![A-Za-z@])')
    while True:
        m = pat.search(s, pos)
        if not m:
            break
        k = m.end()
        opt = None
        while k < len(s) and s[k] in ' \t':
            k += 1
        if allow_opt and k < len(s) and s[k] == '[':
            e = match_bracket(s, k + 1)
            opt = s[k + 1:e]
            k = e + 1
            while k < len(s) and s[k] in ' \t':
                k += 1
        args = []
        ok = True
        for _ in range(nargs):
            while k < len(s) and s[k] in ' \t':
                k += 1
            if k < len(s) and s[k] == '{':
                e = match_brace(s, k)
                args.append(s[k + 1:e])
                k = e + 1
            else:
                ok = False
                break
        if not ok:
            out.append(s[pos:m.end()])
            pos = m.end()
            continue
        out.append(s[pos:m.start()])
        out.append(fn(args, opt))
        pos = k
    out.append(s[pos:])
    return ''.join(out)


def strip_comments(s, tex_faithful=False):
    """Remove % comments. tex_faithful=True also eats the newline and the indentation of
    the next line (what TeX does; needed inside TikZ code). Otherwise whole-line comments
    are dropped and trailing comments are cut but the newline is kept."""
    if tex_faithful:
        out = []
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c == '\\':
                out.append(s[i:i + 2])
                i += 2
                continue
            if c == '%':
                j = s.find('\n', i)
                if j == -1:
                    break
                i = j + 1
                while i < n and s[i] in ' \t':
                    i += 1
                continue
            out.append(c)
            i += 1
        return ''.join(out)
    out = []
    for line in s.split('\n'):
        i = 0
        n = len(line)
        cut = None
        while i < n:
            c = line[i]
            if c == '\\':
                i += 2
                continue
            if c == '%':
                cut = i
                break
            i += 1
        if cut is None:
            out.append(line)
        elif line[:cut].strip() == '':
            continue
        else:
            out.append(line[:cut])
    return '\n'.join(out)


def roman(n):
    vals = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
            (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    out = ''
    for v, r in vals:
        while n >= v:
            out += r
            n -= v
    return out


def roman_to_int(s):
    vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total = 0
    prev = 0
    for ch in reversed(s):
        v = vals.get(ch, 0)
        if v < prev:
            total -= v
        else:
            total += v
            prev = v
    return total


def slug(label):
    return re.sub(r'[^A-Za-z0-9_.-]+', '-', label).strip('-')


# --------------------------------------------------------------------------------------
# main.tex, preamble.tex and main.aux
# --------------------------------------------------------------------------------------

def read(path):
    return Path(path).read_text(encoding='utf-8')


def parse_main(text):
    text_nc = strip_comments(text)
    meta = {}

    def grab(cmd):
        m = re.search(r'\\' + cmd + r'\s*\{', text_nc)
        if not m:
            return ''
        e = match_brace(text_nc, m.end() - 1)
        return text_nc[m.end():e].strip()

    for key, cmd in [('title', 'title'), ('author', 'author'), ('credentials', 'credentials'),
                     ('department', 'department'), ('degree', 'degree'),
                     ('month', 'graduationmonth'), ('year', 'graduationyear'),
                     ('chair', 'committeechair'), ('dean', 'graduatedean')]:
        meta[key] = grab(cmd)
    meta['committee'] = []
    for m in re.finditer(r'\\committeemember\s*\{', text_nc):
        e = match_brace(text_nc, m.end() - 1)
        meta['committee'].append(text_nc[m.end():e].strip())
    meta['doctype'] = 'A Thesis' if re.search(r'\\documentclass\[[^\]]*\bthesis\b', text_nc) else 'A Dissertation'

    body = text_nc.split('\\begin{document}', 1)[1].split('\\end{document}', 1)[0]
    items = []
    for line in body.split('\n'):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'\\input\{([^}]*)\}', line)
        if m:
            items.append(('input', m.group(1)))
            continue
        for marker in ('ttumainmatter', 'ttureferences', 'ttuappendices'):
            if line.startswith('\\' + marker):
                items.append((marker, None))
    return meta, items


def parse_aux(path):
    """label -> dict(type, counter, parent, num, page) from cleveref's @cref entries."""
    labels = {}
    if not path.exists():
        warn('main.aux not found; numbers will be computed by counting')
        return labels
    text = read(path)
    pat = re.compile(r'\\newlabel\{([^}]*)@cref\}\{\{\[([^\]]*)\]\[([^\]]*)\]\[([^\]]*)\]([^}]*)\}'
                     r'\{\[[^\]]*\]\[([^\]]*)\]')
    for m in pat.finditer(text):
        labels[m.group(1)] = dict(type=m.group(2), counter=m.group(3), parent=m.group(4),
                                  num=m.group(5).strip(), page=m.group(6))
    plain = re.compile(r'\\newlabel\{([^}@]*)\}\{\{([^{}]*)\}\{([^{}]*)\}')
    for m in plain.finditer(text):
        if m.group(1) not in labels:
            labels[m.group(1)] = dict(type='?', counter='', parent='', num=m.group(2).strip(),
                                      page=m.group(3))
    return labels


def parse_preamble(text):
    """Return (text_macros, math_macro_lines, theorem_envs, newtheorem_lines)."""
    text = strip_comments(text)
    text_macros = {}
    math_lines = []
    theorem_envs = {}
    newtheorem_lines = []
    for line in text.split('\n'):
        m = re.match(r'\s*\\newcommand\{\\([A-Za-z]+)\}\{([^{}\\]*)\}\s*$', line)
        if m:
            text_macros[m.group(1)] = m.group(2)
            continue
        if re.match(r'\s*\\(newcommand|renewcommand|DeclareMathOperator\*?)\{', line):
            math_lines.append(line.strip())
            continue
        m = re.match(r'\s*\\newtheorem\{([A-Za-z]+)\}(\[[^\]]*\])?\{([^}]*)\}', line)
        if m:
            theorem_envs[m.group(1)] = m.group(3)
            newtheorem_lines.append(line.strip())
            continue
        if re.match(r'\s*\\theoremstyle\{', line):
            newtheorem_lines.append(line.strip())
    return text_macros, math_lines, theorem_envs, newtheorem_lines


def standalone_preamble(preamble_text):
    """Preamble for the standalone figure documents: class-level packages of ttuthesis.cls
    plus preamble.tex minus what needs the full document (theorems, cleveref)."""
    keep = []
    for line in preamble_text.split('\n'):
        if re.search(r'\\(newtheorem|theoremstyle|crefname|Crefname|numberwithin|thetheorem)\b', line):
            continue
        keep.append(line)
    filtered = '\n'.join(keep)
    return r'''\documentclass[border=4pt,varwidth=6in]{standalone}
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
\usepackage[scaled=0.92]{helvet}
\usepackage{courier}
\usepackage{setspace}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{float}
\usepackage[font={singlespacing,normalsize},labelfont=bf,labelsep=period,justification=justified,singlelinecheck=false]{caption}
\usepackage{subcaption}
\usepackage{booktabs,multirow,longtable,threeparttable,array,tabularx}
\usepackage{enumitem}
''' + filtered + r'''
\newcommand{\todo}[1]{{\color{red!70!black}\textbf{[TODO: #1]}}}
\providecommand{\cref}[1]{#1}
\providecommand{\Cref}[1]{#1}
\providecommand{\labelcref}[1]{#1}
\providecommand{\ref}[1]{#1}
\providecommand{\cite}[1]{[#1]}
'''


# --------------------------------------------------------------------------------------
# flattening
# --------------------------------------------------------------------------------------

def flatten(items):
    parts = []
    for kind, arg in items:
        if kind == 'input':
            path = THESIS / (arg if arg.endswith('.tex') else arg + '.tex')
            parts.append('\n' + read(path) + '\n')
        else:
            parts.append('\n\\HtmlMarker{%s}\n' % kind)
    return ''.join(parts)


# --------------------------------------------------------------------------------------
# listings protection
# --------------------------------------------------------------------------------------

def protect_listings(doc):
    bodies = []

    def repl(m):
        bodies.append(m.group(2))
        return m.group(1) + '\n@@LST%d@@\n\\end{lstlisting}' % (len(bodies) - 1)

    doc = re.sub(r'(\\begin\{lstlisting\}(?:\[(?:[^\[\]]|\{[^{}]*\})*\])?)\n(.*?)\\end\{lstlisting\}',
                 repl, doc, flags=re.S)
    return doc, bodies


def restore_listings(doc, bodies):
    for i, b in enumerate(bodies):
        doc = doc.replace('\n@@LST%d@@\n' % i, '\n' + b)
    return doc


# --------------------------------------------------------------------------------------
# cross references (cleveref)
# --------------------------------------------------------------------------------------

CREF_NAMES = {
    'chapter': ('Chapter', 'Chapters'), 'section': ('Section', 'Sections'),
    'subsection': ('Section', 'Sections'), 'subsubsection': ('Section', 'Sections'),
    'paragraph': ('Section', 'Sections'), 'appendix': ('Appendix', 'Appendices'),
    'subappendix': ('Section', 'Sections'), 'subsubappendix': ('Section', 'Sections'),
    'figure': ('Figure', 'Figures'), 'subfigure': ('Figure', 'Figures'),
    'table': ('Table', 'Tables'), 'subtable': ('Table', 'Tables'),
    'equation': ('Equation', 'Equations'), 'algocf': ('Algorithm', 'Algorithms'),
    'algorithm': ('Algorithm', 'Algorithms'), 'lstlisting': ('Listing', 'Listings'),
    'listing': ('Listing', 'Listings'), 'page': ('Page', 'Pages'),
    'theorem': ('Theorem', 'Theorems'), 'lemma': ('Lemma', 'Lemmas'),
    'proposition': ('Proposition', 'Propositions'), 'corollary': ('Corollary', 'Corollaries'),
    'definition': ('Definition', 'Definitions'), 'assumption': ('Assumption', 'Assumptions'),
    'remark': ('Remark', 'Remarks'), 'example': ('Example', 'Examples'),
    'enumi': ('Item', 'Items'), 'enumii': ('Item', 'Items'),
}


class RefResolver:
    def __init__(self, labels, theorem_envs, sub_parent):
        self.labels = labels
        self.names = dict(CREF_NAMES)
        for env, name in theorem_envs.items():
            plural = name + ('s' if not name.endswith('y') else '')
            if name.endswith('y'):
                plural = name[:-1] + 'ies'
            self.names[env] = (name, plural)
        self.sub_parent = sub_parent
        self.unresolved = []

    def info(self, label):
        d = self.labels.get(label)
        if not d:
            self.unresolved.append(label)
            return None
        return d

    def target(self, label):
        return self.sub_parent.get(label, label)

    def fmt_num(self, d):
        return '(%s)' % d['num'] if d['type'] == 'equation' else d['num']

    def link(self, label, text, link):
        if not link:
            return text
        return '\\hyperref[%s]{%s}' % (self.target(label), text)

    @staticmethod
    def _counter(d):
        try:
            return int(d['counter'])
        except ValueError:
            return None

    def _join(self, parts):
        if len(parts) == 1:
            return parts[0]
        if len(parts) == 2:
            return parts[0] + ' and ' + parts[1]
        return ', '.join(parts[:-1]) + ' and ' + parts[-1]

    def resolve(self, labels, cap, link=True, names=True):
        """cleveref-style text for a list of labels."""
        infos = []
        for lab in labels:
            d = self.info(lab)
            if d is None:
                infos.append((lab, None))
            else:
                infos.append((lab, d))
        # group by display name in order of first appearance, sort within group by counter
        groups = []
        for lab, d in infos:
            if d is None:
                groups.append(('??', [(lab, d)]))
                continue
            nm = self.names.get(d['type'], (d['type'].capitalize(), d['type'].capitalize() + 's'))
            for g in groups:
                if g[0] == nm:
                    g[1].append((lab, d))
                    break
            else:
                groups.append((nm, [(lab, d)]))
        out_groups = []
        for nm, members in groups:
            if nm == '??':
                out_groups.append('??')
                continue
            members.sort(key=lambda x: ((x[1]['parent'] or ''), self._counter(x[1]) or 0))
            # compress runs of >=3 consecutive items (same parent, counter+1)
            items = []
            i = 0
            while i < len(members):
                j = i
                while (j + 1 < len(members)
                       and members[j + 1][1]['parent'] == members[j][1]['parent']
                       and self._counter(members[j + 1][1]) is not None
                       and self._counter(members[j][1]) is not None
                       and self._counter(members[j + 1][1]) == self._counter(members[j][1]) + 1):
                    j += 1
                if j - i >= 2:
                    a, b = members[i], members[j]
                    items.append(self.link(a[0], self.fmt_num(a[1]), link) + ' to '
                                 + self.link(b[0], self.fmt_num(b[1]), link))
                    i = j + 1
                else:
                    for k in range(i, j + 1):
                        items.append(self.link(members[k][0], self.fmt_num(members[k][1]), link))
                    i = j + 1
            plural = len(members) > 1
            name = nm[1] if plural else nm[0]
            if not cap:
                name = name  # the class loads cleveref with 'capitalise': always capitalised
            if names:
                if len(members) == 1 and link:
                    lab, d = members[0]
                    out_groups.append('\\hyperref[%s]{%s %s}' % (self.target(lab), name, self.fmt_num(d)))
                else:
                    out_groups.append(name + ' ' + self._join(items))
            else:
                out_groups.append(self._join(items))
        return self._join(out_groups)

    def resolve_range(self, a, b, link=True):
        da, db = self.info(a), self.info(b)
        if da is None or db is None:
            return '??'
        nm = self.names.get(da['type'], (da['type'].capitalize(), da['type'].capitalize() + 's'))
        return '%s %s to %s' % (nm[1], self.link(a, self.fmt_num(da), link), self.link(b, self.fmt_num(db), link))

    def apply(self, doc, link=True):
        def split(arg):
            return [x.strip() for x in arg.split(',') if x.strip()]

        doc = replace_cmd(doc, 'crefrange', 2, lambda a, o: self.resolve_range(a[0].strip(), a[1].strip(), link))
        doc = replace_cmd(doc, 'Crefrange', 2, lambda a, o: self.resolve_range(a[0].strip(), a[1].strip(), link))
        doc = replace_cmd(doc, 'labelcref', 1, lambda a, o: self.resolve(split(a[0]), False, link, names=False))
        doc = replace_cmd(doc, 'Cref', 1, lambda a, o: self.resolve(split(a[0]), True, link))
        doc = replace_cmd(doc, 'cref', 1, lambda a, o: self.resolve(split(a[0]), False, link))
        doc = replace_cmd(doc, 'eqref', 1, lambda a, o: self.resolve(split(a[0]), False, link, names=False))

        def plain_ref(a, o):
            lab = a[0].strip()
            d = self.info(lab)
            if d is None:
                return '??'
            return self.link(lab, d['num'], link)

        doc = replace_cmd(doc, 'ref', 1, plain_ref)
        return doc


# --------------------------------------------------------------------------------------
# float extraction (figures and algorithms -> standalone jobs)
# --------------------------------------------------------------------------------------

class FigJob:
    def __init__(self, name, kind, label, code, caption):
        self.name = name            # image basename without extension
        self.kind = kind            # 'figure' | 'algorithm'
        self.label = label
        self.code = code            # LaTeX between \begin{document} and \end{document}
        self.caption = caption
        self.tex = None
        self.hash = None
        self.method = None          # 'tectonic' | 'fallback' | 'cached'
        self.ext = 'svg'
        self.error = None


def find_spans(block, env):
    spans = []
    for m in re.finditer(r'\\begin\{%s\}' % env, block):
        e = block.find('\\end{%s}' % env, m.end())
        if e == -1:
            break
        spans.append((m.start(), e + len('\\end{%s}' % env)))
    return spans


def inside(pos, spans):
    return any(a <= pos < b for a, b in spans)


def extract_floats(doc, sub_parent):
    """Replace figure and algorithm environments by includegraphics figures; return jobs."""
    jobs = []
    counters = {'figure': 0, 'algorithm': 0}

    def handle(m, env):
        block = m.group(0)
        inner = strip_comments(m.group(2), tex_faithful=True)
        subs = find_spans(inner, 'subfigure')
        # main caption: last \caption outside sub-figures
        cap_text = ''
        cap_span = None
        for cm in re.finditer(r'\\caption(?![A-Za-z])', inner):
            if inside(cm.start(), subs):
                continue
            k = cm.end()
            while k < len(inner) and inner[k] in ' \t':
                k += 1
            if k < len(inner) and inner[k] == '[':
                e = match_bracket(inner, k + 1)
                k = e + 1
                while k < len(inner) and inner[k] in ' \t':
                    k += 1
            if k < len(inner) and inner[k] == '{':
                e = match_brace(inner, k)
                cap_text = inner[k + 1:e]
                cap_span = (cm.start(), e + 1)
        label = None
        lab_span = None
        for lm in re.finditer(r'\\label\{([^}]*)\}', inner):
            if inside(lm.start(), subs):
                continue
            label = lm.group(1).strip()
            lab_span = (lm.start(), lm.end())
            break
        for a, b in subs:
            for lm in re.finditer(r'\\label\{([^}]*)\}', inner[a:b]):
                if label:
                    sub_parent[lm.group(1).strip()] = label
        code = inner
        cuts = [s for s in (cap_span, lab_span) if s]
        for a, b in sorted(cuts, reverse=True):
            code = code[:a] + code[b:]
        counters[env] += 1
        if label:
            name = slug(label)
        else:
            name = '%s-%d' % (env, counters[env])
            warn('%s environment #%d has no label; image named %s' % (env, counters[env], name))
        job = FigJob(name, env, label, code.strip('\n'), cap_text)
        jobs.append(job)
        lab_tex = '\\label{%s}\n' % label if label else ''
        return ('\n\\begin{figure}\n\\centering\n\\includegraphics{@@IMG:%s@@}\n\\caption{%s}\n%s\\end{figure}\n'
                % (name, cap_text, lab_tex))

    doc = re.sub(r'\\begin\{figure\}(\[[^\]]*\])?(.*?)\\end\{figure\}',
                 lambda m: handle(m, 'figure'), doc, flags=re.S)
    doc = re.sub(r'\\begin\{algorithm\}(\[[^\]]*\])?(.*?)\\end\{algorithm\}',
                 lambda m: handle(m, 'algorithm'), doc, flags=re.S)
    return doc, jobs


def job_tex(job, pre, resolver, cite_numbers):
    code = resolver.apply(job.code, link=False)

    def cite(a, o):
        keys = [k.strip() for k in a[0].split(',')]
        nums = [str(cite_numbers.get(k, '?')) for k in keys]
        return '[' + ', '.join(nums) + ']'

    code = replace_cmd(code, 'cite', 1, cite, allow_opt=True)
    if job.kind == 'figure':
        body = '\\begin{figure}[H]\n%s\n\\end{figure}' % code
    else:
        body = '\\begin{algorithm}[H]\n%s\n\\end{algorithm}' % code
    return pre + '\\begin{document}\n' + body + '\n\\end{document}\n'


# --------------------------------------------------------------------------------------
# figure compilation
# --------------------------------------------------------------------------------------

def run(cmd, cwd=None, timeout=600):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, 'timeout'


class PdfPages:
    """Lazy access to the text of main.pdf pages (for the crop fallback)."""

    def __init__(self, pdf):
        self.pdf = pdf
        self._pages = None
        self._offset = None

    def pages(self):
        if self._pages is None:
            rc, _ = run([PDFTOTEXT, '-layout', str(self.pdf), str(BUILD / 'main.txt')])
            self._pages = read(BUILD / 'main.txt').split('\f') if rc == 0 else []
        return self._pages

    def offset(self):
        """pdf page index (1-based) of thesis page 1, minus 1."""
        if self._offset is None:
            self._offset = 0
            for i, t in enumerate(self.pages()):
                if 'CHAPTER I' in t and 'INTRODUCTION' in t:
                    self._offset = i
                    break
        return self._offset

    def find_page(self, needle):
        needle = re.sub(r'\s+', ' ', needle).strip()
        for i, t in enumerate(self.pages()):
            if needle in re.sub(r'\s+', ' ', t):
                return i + 1
        return None


def plain_text(latex):
    s = re.sub(r'\\[A-Za-z]+\*?(\[[^\]]*\])?', ' ', latex)
    s = re.sub(r'[{}~$]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def fallback_crop(job, labels, pdfpages, figs_dir):
    """Crop the figure from main.pdf: locate the page via main.aux, crop from the top of
    the text block to the bottom of the caption, 150 dpi PNG."""
    page = None
    d = labels.get(job.label or '')
    if d and d.get('page', '').isdigit():
        page = int(d['page']) + pdfpages.offset()
    if page is None:
        words = plain_text(job.caption).split(' ')[:6]
        page = pdfpages.find_page(' '.join(words))
    if page is None:
        return False
    # caption bbox
    y0, y1 = 60.0, 760.0
    rc, _ = run([PDFTOTEXT, '-f', str(page), '-l', str(page), '-bbox-layout', str(MAIN_PDF),
                 str(figs_dir / (job.name + '.bbox.xml'))])
    if rc == 0:
        try:
            tree = ET.parse(figs_dir / (job.name + '.bbox.xml'))
            ns = {'x': 'http://www.w3.org/1999/xhtml'}
            prefix = ('Figure' if job.kind == 'figure' else 'Algorithm') + ' ' + (d['num'] if d else '')
            for block in tree.getroot().iter('{http://www.w3.org/1999/xhtml}block'):
                words = [w.text or '' for w in block.iter('{http://www.w3.org/1999/xhtml}word')]
                text = ' '.join(words)
                if text.startswith(prefix):
                    y1 = float(block.get('yMax')) + 6
                    break
        except Exception as exc:  # noqa: BLE001
            warn('bbox parse failed for %s: %s' % (job.name, exc))
    scale = 150 / 72.0
    x, y = int(70 * scale), int(y0 * scale)
    w, h = int((612 - 70 - 40) * scale), int((y1 - y0) * scale)
    out = figs_dir / (job.name + '-crop')
    rc, msg = run([PDFTOPPM, '-png', '-r', '150', '-f', str(page), '-l', str(page), '-x', str(x), '-y', str(y),
                   '-W', str(w), '-H', str(h), str(MAIN_PDF), str(out)])
    if rc != 0:
        return False
    pngs = sorted(figs_dir.glob(job.name + '-crop*.png'))
    if not pngs:
        return False
    shutil.move(str(pngs[-1]), str(IMAGES / (job.name + '.png')))
    job.ext = 'png'
    job.method = 'fallback'
    return True


def pdf_page_size(pdf):
    rc, msg = run([which('pdfinfo', '/opt/homebrew/bin/pdfinfo'), str(pdf)])
    m = re.search(r'Page size:\s+([0-9.]+) x ([0-9.]+)', msg)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def content_bbox(pdf, figs_dir, name):
    """Bounding box (pt) of the non-white content of a one-page PDF, via a 72 dpi PGM render."""
    out = figs_dir / (name + '-bbox')
    rc, _ = run([PDFTOPPM, '-gray', '-r', '72', '-f', '1', '-l', '1', str(pdf), str(out)])
    pgms = sorted(figs_dir.glob(name + '-bbox*.pgm'))
    if rc != 0 or not pgms:
        return None
    data = pgms[-1].read_bytes()
    for pg in pgms:
        pg.unlink()
    # PGM header: P5 <w> <h> <maxval> then raw bytes
    m = re.match(rb'P5\s+(\d+)\s+(\d+)\s+(\d+)\s', data)
    if not m:
        return None
    w, h = int(m.group(1)), int(m.group(2))
    pix = data[m.end():]
    if len(pix) < w * h:
        return None
    rows = [y for y in range(h) if any(b < 240 for b in pix[y * w:(y + 1) * w])]
    if not rows:
        return None
    y0, y1 = rows[0], rows[-1]
    x0, x1 = w, -1
    for y in rows:
        row = pix[y * w:(y + 1) * w]
        xs = [x for x in range(w) if row[x] < 240]
        if xs:
            x0, x1 = min(x0, xs[0]), max(x1, xs[-1])
    return (x0, y0, x1 + 1, y1 + 1)


def tighten_svg(job, pdf, svg, figs_dir):
    """Safety net: if standalone did not crop the page (letter-size output), set the SVG
    viewBox to the drawn bounding box plus a 4 pt margin."""
    w, h = pdf_page_size(pdf)
    if w < 550 or h < 700:
        return False
    box = content_bbox(pdf, figs_dir, job.name)
    if not box:
        warn('%s: full-page output and no content bbox found' % job.name)
        return False
    x0, y0, x1, y1 = box
    pad = 4
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(w, x1 + pad), min(h, y1 + pad)
    text = svg.read_text(encoding='utf-8', errors='replace')
    new_tag = 'width="%.2fpt" height="%.2fpt" viewBox="%.2f %.2f %.2f %.2f"' % (x1 - x0, y1 - y0, x0, y0, x1 - x0, y1 - y0)
    text2, n = re.subn(r'width="[0-9.]+pt" height="[0-9.]+pt" viewBox="[^"]*"', new_tag, text, count=1)
    if n:
        svg.write_text(text2, encoding='utf-8')
        warn('%s: standalone cropping failed; SVG viewBox tightened to the drawn content' % job.name)
    return bool(n)


def compile_job(job, figs_dir, labels, pdfpages):
    texfile = figs_dir / (job.name + '.tex')
    texfile.write_text(job.tex, encoding='utf-8')
    pdf = figs_dir / (job.name + '.pdf')
    svg = IMAGES / (job.name + '.svg')
    for attempt, extra in enumerate(([], ['-Z', 'continue-on-errors'])):
        if pdf.exists():
            pdf.unlink()
        cmd = [TECTONIC, '-X', 'compile', '--keep-logs', '--outdir', str(figs_dir)] + extra + [texfile.name]
        rc, msg = run(cmd, cwd=figs_dir, timeout=600)
        if pdf.exists() and pdf.stat().st_size > 0:
            rc2, msg2 = run([PDFTOCAIRO, '-svg', str(pdf), str(svg)])
            if rc2 == 0 and svg.exists():
                tighten_svg(job, pdf, svg, figs_dir)
                job.method = 'tectonic'
                job.ext = 'svg'
                if attempt == 1:
                    warn('%s compiled only with continue-on-errors; check tools/_build/figs/%s.log'
                         % (job.name, job.name))
                return job
            job.error = 'pdftocairo failed: ' + msg2[-400:]
        else:
            errs = [ln for ln in msg.split('\n') if 'error' in ln.lower()]
            job.error = '\n'.join(errs[-6:]) or msg[-400:]
    warn('figure %s failed to compile (%s); using PDF crop fallback' % (job.name, (job.error or '').strip()[:300]))
    if fallback_crop(job, labels, pdfpages, figs_dir):
        return job
    job.method = 'missing'
    warn('figure %s: fallback crop failed too' % job.name)
    return job


def build_figures(jobs, pre, resolver, cite_numbers, figs_dir, labels, jobs_n, force):
    IMAGES.mkdir(parents=True, exist_ok=True)
    figs_dir.mkdir(parents=True, exist_ok=True)
    for f in ('quantikz.sty', 'tikzlibraryquantikz2.code.tex'):
        if (THESIS / f).exists():
            shutil.copy(THESIS / f, figs_dir / f)
    manifest = {}
    if MANIFEST.exists() and not force:
        try:
            manifest = json.loads(read(MANIFEST))
        except Exception:  # noqa: BLE001
            manifest = {}
    pdfpages = PdfPages(MAIN_PDF)
    todo = []
    for job in jobs:
        job.tex = job_tex(job, pre, resolver, cite_numbers)
        job.hash = hashlib.sha256(job.tex.encode('utf-8')).hexdigest()[:16]
        cached = manifest.get(job.name)
        if (cached and cached.get('hash') == job.hash and cached.get('method') == 'tectonic'
                and (IMAGES / (job.name + '.' + cached.get('ext', 'svg'))).exists()):
            job.method = 'cached'
            job.ext = cached.get('ext', 'svg')
        else:
            todo.append(job)
    log('figures: %d total, %d cached, %d to compile (%d workers)' % (len(jobs), len(jobs) - len(todo), len(todo), jobs_n))
    t0 = time.time()
    if todo:
        with ThreadPoolExecutor(max_workers=jobs_n) as ex:
            for job in ex.map(lambda j: compile_job(j, figs_dir, labels, pdfpages), todo):
                log('  %-40s %s%s' % (job.name, job.method, '' if job.method == 'tectonic' else ' (' + job.ext + ')'))
    log('figures done in %.0f s' % (time.time() - t0))
    new_manifest = {}
    for job in jobs:
        if job.method in ('tectonic', 'cached', 'fallback'):
            new_manifest[job.name] = {'hash': job.hash, 'method': 'tectonic' if job.method == 'cached' else job.method,
                                      'ext': job.ext, 'label': job.label}
    MANIFEST.write_text(json.dumps(new_manifest, indent=1, sort_keys=True), encoding='utf-8')
    # remove stale images
    keep = {job.name + '.' + job.ext for job in jobs}
    for p in IMAGES.iterdir():
        if p.suffix in ('.svg', '.png') and p.name not in keep:
            p.unlink()
    return jobs


# --------------------------------------------------------------------------------------
# numbering walk: headings, captions, equations, listings
# --------------------------------------------------------------------------------------

EVENT = re.compile(
    r'\\HtmlMarker\{(?P<marker>[a-z]+)\}'
    r'|\\(?P<head>chapter|section|subsection|subsubsection)\s*\{'
    r'|\\begin\{(?P<env>figure|table|equation|align|lstlisting)\}')


def split_lines(body):
    """Split an align body at top-level \\\\ (outside braces / nested environments)."""
    lines = []
    depth = 0
    envdepth = 0
    i = 0
    start = 0
    n = len(body)
    while i < n:
        if body.startswith('\\begin{', i):
            envdepth += 1
            i += 7
            continue
        if body.startswith('\\end{', i):
            envdepth -= 1
            i += 5
            continue
        c = body[i]
        if c == '\\' and i + 1 < n and body[i + 1] == '\\' and depth == 0 and envdepth == 0:
            lines.append(body[start:i])
            start = i + 2
            i += 2
            continue
        if c == '\\':
            i += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        i += 1
    lines.append(body[start:])
    return lines


class Numberer:
    def __init__(self, labels):
        self.labels = labels
        self.mode = 'front'
        self.chap = 0              # arabic chapter counter / appendix index
        self.sec = self.subsec = self.subsubsec = 0
        self.fig = self.tab = self.eq = self.lst = 0
        self.alg = 0
        self.listing_nums = {}
        self.mismatches = []

    def chap_str(self):
        return chr(ord('A') + self.chap - 1) if self.mode == 'appendix' else str(self.chap)

    def aux_num(self, label, types):
        d = self.labels.get(label)
        if d and (d['type'] in types or d['type'] == '?'):
            return d['num']
        return None

    def check(self, label, computed, aux):
        if aux is not None and computed is not None and aux != computed:
            self.mismatches.append('%s: computed %s, main.aux says %s' % (label, computed, aux))

    def heading(self, level, title, label):
        if level == 'chapter':
            self.chap += 1
            self.sec = self.subsec = self.subsubsec = 0
            self.fig = self.tab = self.eq = self.lst = 0
            if self.mode == 'appendix':
                computed = chr(ord('A') + self.chap - 1)
                aux = self.aux_num(label, ('appendix', 'chapter')) if label else None
                self.check(label, computed, aux)
                num = aux or computed
                if len(num) == 1 and num.isalpha():
                    self.chap = ord(num) - ord('A') + 1
                return 'Appendix %s. %s' % (num, title)
            computed = roman(self.chap)
            aux = self.aux_num(label, ('chapter',)) if label else None
            self.check(label, computed, aux)
            num = aux or computed
            if re.fullmatch(r'[IVXLC]+', num):
                self.chap = roman_to_int(num)
            return 'Chapter %s. %s' % (num, title)
        if level == 'section':
            self.sec += 1
            self.subsec = self.subsubsec = 0
            computed = '%s.%d' % (self.chap_str(), self.sec)
        elif level == 'subsection':
            self.subsec += 1
            self.subsubsec = 0
            computed = '%s.%d.%d' % (self.chap_str(), self.sec, self.subsec)
        else:
            self.subsubsec += 1
            computed = '%s.%d.%d.%d' % (self.chap_str(), self.sec, self.subsec, self.subsubsec)
        aux = self.aux_num(label, ('section', 'subsection', 'subsubsection', 'subappendix', 'subsubappendix')) if label else None
        self.check(label, computed, aux)
        num = aux or computed
        parts = num.split('.')
        try:
            if level == 'section' and len(parts) >= 2:
                self.sec = int(parts[1])
            elif level == 'subsection' and len(parts) >= 3:
                self.sec, self.subsec = int(parts[1]), int(parts[2])
            elif level == 'subsubsection' and len(parts) >= 4:
                self.sec, self.subsec, self.subsubsec = int(parts[1]), int(parts[2]), int(parts[3])
        except ValueError:
            pass
        return '%s %s' % (num, title)

    def float_num(self, kind, label):
        if kind == 'algorithm':
            self.alg += 1
            computed = str(self.alg)
            aux = self.aux_num(label, ('algocf', 'algorithm')) if label else None
            self.check(label, computed, aux)
            num = aux or computed
            if num.isdigit():
                self.alg = int(num)
            return num
        if kind == 'figure':
            self.fig += 1
            computed = '%s.%d' % (self.chap_str(), self.fig)
            aux = self.aux_num(label, ('figure',)) if label else None
        elif kind == 'table':
            self.tab += 1
            computed = '%s.%d' % (self.chap_str(), self.tab)
            aux = self.aux_num(label, ('table',)) if label else None
        elif kind == 'listing':
            self.lst += 1
            computed = '%s.%d' % (self.chap_str(), self.lst)
            aux = self.aux_num(label, ('lstlisting', 'listing')) if label else None
        else:  # equation
            self.eq += 1
            computed = '%s.%d' % (self.chap_str(), self.eq)
            aux = self.aux_num(label, ('equation',)) if label else None
        self.check(label, computed, aux)
        num = aux or computed
        tail = num.split('.')[-1]
        if tail.isdigit():
            setattr(self, {'figure': 'fig', 'table': 'tab', 'listing': 'lst', 'equation': 'eq'}[kind], int(tail))
        return num


def number_document(doc, labels):
    nb = Numberer(labels)
    out = []
    pos = 0
    while True:
        m = EVENT.search(doc, pos)
        if not m:
            break
        out.append(doc[pos:m.start()])
        if m.group('marker'):
            marker = m.group('marker')
            if marker == 'ttumainmatter':
                nb.mode = 'main'
                nb.chap = 0
            elif marker == 'ttuappendices':
                nb.mode = 'appendix'
                nb.chap = 0
            elif marker == 'ttureferences':
                out.append('\n\\chapter*{References}\n')
            pos = m.end()
            continue
        if m.group('head'):
            level = m.group('head')
            e = match_brace(doc, m.end() - 1)
            title = doc[m.end():e]
            k = e + 1
            lm = re.match(r'\s*\\label\{([^}]*)\}', doc[k:k + 200])
            label = lm.group(1).strip() if lm else None
            if nb.mode == 'front':
                out.append(doc[m.start():e + 1])
                pos = e + 1
                continue
            out.append('\\%s{%s}' % (level, nb.heading(level, title, label)))
            pos = e + 1
            continue
        env = m.group('env')
        end_tag = '\\end{%s}' % env
        e = doc.find(end_tag, m.end())
        if e == -1:
            out.append(doc[m.start():m.end()])
            pos = m.end()
            continue
        block = doc[m.start():e + len(end_tag)]
        inner = doc[m.end():e]
        if env in ('figure', 'table'):
            lm = re.search(r'\\label\{([^}]*)\}', inner)
            label = lm.group(1).strip() if lm else None
            im = re.search(r'@@IMG:(alg-[^@]*|algorithm-\d+)@@', inner)
            kind = 'algorithm' if (env == 'figure' and ((label or '').startswith('alg:') or im)) else env
            num = nb.float_num(kind, label)
            name = {'figure': 'Figure', 'table': 'Table', 'algorithm': 'Algorithm'}[kind]

            def prefix(a, o, name=name, num=num):
                return '\\caption{\\textbf{%s %s.} %s}' % (name, num, a[0].strip())
            block = replace_cmd(block, 'caption', 1, prefix, allow_opt=True)
            out.append(block)
        elif env == 'lstlisting':
            om = re.match(r'\\begin\{lstlisting\}\[', block)
            label = None
            if om:
                e2 = match_bracket(block, om.end())
                opts = block[om.end():e2]
                lm = re.search(r'label=\{?([^},]*)\}?', opts)
                label = lm.group(1).strip() if lm else None
            num = nb.float_num('listing', label)
            if label:
                nb.listing_nums[label] = num
            out.append(block)
        elif env == 'equation':
            labs = re.findall(r'\\label\{([^}]*)\}', inner)
            body = re.sub(r'\\label\{[^}]*\}', '', inner).strip('\n')
            label = labs[0].strip() if labs else None
            num = nb.float_num('equation', label)
            anchors = ''.join('\\hypertarget{%s}{}' % l.strip() for l in labs)
            out.append('%s\\[\n%s\n\\tag{%s}\\]' % (anchors, body, num))
        elif env == 'align':
            lines = split_lines(inner)
            anchors = []
            new_lines = []
            for ln in lines:
                labs = re.findall(r'\\label\{([^}]*)\}', ln)
                ln2 = re.sub(r'\\label\{[^}]*\}', '', ln)
                anchors += [l.strip() for l in labs]
                if not ln2.strip():
                    new_lines.append(ln2)
                    continue
                if re.search(r'\\(nonumber|notag)\b', ln2):
                    new_lines.append(ln2)
                    continue
                num = nb.float_num('equation', labs[0].strip() if labs else None)
                new_lines.append(ln2.rstrip() + ' \\tag{%s}' % num)
            out.append(''.join('\\hypertarget{%s}{}' % l for l in anchors)
                       + '\\begin{align}' + '\\\\'.join(new_lines) + '\\end{align}')
        pos = e + len(end_tag)
    out.append(doc[pos:])
    return ''.join(out), nb


# --------------------------------------------------------------------------------------
# text preprocessing
# --------------------------------------------------------------------------------------

MATH_PATTERNS = [
    re.compile(r'\\\[.*?\\\]', re.S),
    re.compile(r'\\\(.*?\\\)', re.S),
    re.compile(r'\$\$.*?\$\$', re.S),
    re.compile(r'(?<!\\)\$(?:[^$\\]|\\.)*\$', re.S),
    re.compile(r'\\begin\{(equation|align|gather|multline|eqnarray|alignat|flalign)\*?\}.*?\\end\{\1\*?\}', re.S),
]


def math_spans(doc):
    spans = []
    for pat in MATH_PATTERNS:
        for m in pat.finditer(doc):
            spans.append((m.start(), m.end()))
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def in_math(pos, spans):
    import bisect
    i = bisect.bisect_right(spans, (pos, float('inf'))) - 1
    return i >= 0 and spans[i][0] <= pos < spans[i][1]


SI_PREFIX = {'yotta': 'Y', 'zetta': 'Z', 'exa': 'E', 'peta': 'P', 'tera': 'T', 'giga': 'G', 'mega': 'M',
             'kilo': 'k', 'hecto': 'h', 'deca': 'da', 'deci': 'd', 'centi': 'c', 'milli': 'm',
             'micro': '\u00b5', 'nano': 'n', 'pico': 'p', 'femto': 'f', 'atto': 'a',
             'kibi': 'Ki', 'mebi': 'Mi', 'gibi': 'Gi', 'tebi': 'Ti'}
SI_UNIT = {'byte': 'B', 'bit': 'bit', 'second': 's', 'hour': 'h', 'minute': 'min', 'percent': '%',
           'meter': 'm', 'metre': 'm', 'gram': 'g', 'hertz': 'Hz', 'joule': 'J', 'watt': 'W', 'volt': 'V',
           'ampere': 'A', 'kelvin': 'K', 'day': 'd', 'year': 'yr', 'degree': '\u00b0', 'celsius': '\u00b0C',
           'electronvolt': 'eV', 'liter': 'L', 'litre': 'L', 'mole': 'mol', 'ohm': '\u03a9', 'tesla': 'T',
           'pascal': 'Pa', 'newton': 'N', 'farad': 'F', 'henry': 'H', 'coulomb': 'C', 'siemens': 'S',
           'decibel': 'dB', 'flop': 'FLOP', 'qubit': 'qubit'}


def si_unit(unit, math):
    out = []
    i = 0
    per = False
    while i < len(unit):
        if unit[i] == '\\':
            m = re.match(r'\\([A-Za-z]+)', unit[i:])
            if not m:
                i += 1
                continue
            name = m.group(1)
            i += m.end()
            if name == 'per':
                out.append('/')
                per = True
            elif name in SI_PREFIX:
                out.append(SI_PREFIX[name])
            elif name in SI_UNIT:
                out.append(SI_UNIT[name])
            elif name == 'squared':
                out.append('\u00b2')
            elif name == 'cubed':
                out.append('\u00b3')
            else:
                out.append(name)
        elif unit[i] in '{}':
            i += 1
        else:
            out.append(unit[i])
            i += 1
    text = ''.join(out)
    if math:
        text = text.replace('%', '\\%').replace('\u00b5', '\\mu ')
        return '\\mathrm{%s}' % text
    return text.replace('%', '\\%')


def si_number(num, math):
    num = num.strip().replace('{', '').replace('}', '')
    m = re.fullmatch(r'([+-]?[0-9.]+)\s*[eE]\s*([+-]?[0-9]+)', num)
    if m:
        mant, exp = m.group(1), int(m.group(2))
        body = '%s\\times 10^{%d}' % (mant, exp)
        return body if math else '$%s$' % body
    return num


def expand_siunitx(doc):
    spans = math_spans(doc)
    NBSP = '\u202f'  # narrow no-break space

    def si(a, o, pos):
        math = in_math(pos, spans)
        num = si_number(a[0], math)
        unit = si_unit(a[1], math)
        if math:
            return '%s\\,%s' % (num, unit)
        if num.startswith('$') and num.endswith('$'):
            return num[:-1] + '\\,' + ('\\mathrm{%s}' % unit.replace('\\%', '\\%')) + '$'
        return num + NBSP + unit

    def num(a, o, pos):
        return si_number(a[0], in_math(pos, spans))

    def unit_only(a, o, pos):
        return si_unit(a[0], in_math(pos, spans))

    def apply(doc, name, nargs, fn):
        spans[:] = math_spans(doc)      # positions shift after every pass
        out = []
        pos = 0
        pat = re.compile(r'\\' + name + r'(?![A-Za-z])')
        while True:
            m = pat.search(doc, pos)
            if not m:
                break
            k = m.end()
            if k < len(doc) and doc[k] == '[':
                k = match_bracket(doc, k + 1) + 1
            args = []
            ok = True
            for _ in range(nargs):
                if k < len(doc) and doc[k] == '{':
                    e = match_brace(doc, k)
                    args.append(doc[k + 1:e])
                    k = e + 1
                else:
                    ok = False
                    break
            if not ok:
                out.append(doc[pos:m.end()])
                pos = m.end()
                continue
            out.append(doc[pos:m.start()])
            out.append(fn(args, None, m.start()))
            pos = k
        out.append(doc[pos:])
        return ''.join(out)

    doc = apply(doc, 'SI', 2, si)
    doc = apply(doc, 'qty', 2, si)
    doc = apply(doc, 'num', 1, num)
    doc = apply(doc, 'si', 1, unit_only)
    doc = apply(doc, 'unit', 1, unit_only)
    return doc


def expand_text_macros(doc, text_macros):
    for name, value in text_macros.items():
        pat = re.compile(r'\\' + name + r'(\{\}|\\ |(?![A-Za-z]))')
        doc = pat.sub(lambda m, v=value: v + (' ' if m.group(1) == '\\ ' else ''), doc)
    return doc


def convert_tables(doc):
    # custom column types are expanded, not declared (\newcolumntype{L}[1]{...})
    out = []
    pos = 0
    for m in re.finditer(r'\\newcolumntype\{[^}]*\}(\[\d+\])?\s*(?=\{)', doc):
        e = match_brace(doc, m.end())
        out.append(doc[pos:m.start()])
        pos = e + 1
    out.append(doc[pos:])
    doc = ''.join(out)

    def simplify_spec(spec):
        spec = re.sub(r'>\{(?:[^{}]|\{[^{}]*\})*\}', '', spec)
        spec = re.sub(r'@\{(?:[^{}]|\{[^{}]*\})*\}', '', spec)
        spec = re.sub(r'!\{(?:[^{}]|\{[^{}]*\})*\}', '', spec)
        spec = re.sub(r'[LpmbX]\{[^{}]*\}', 'l', spec)
        spec = re.sub(r'\*\{(\d+)\}\{([^{}]*)\}', lambda m: m.group(2) * int(m.group(1)), spec)
        spec = spec.replace('X', 'l').replace('|', '').replace(' ', '').replace('\n', '')
        return spec

    def tabularx(a, o):
        return '\\begin{tabular}{%s}' % simplify_spec(a[1])

    doc = replace_cmd(doc, 'begin{tabularx}', 2, tabularx)
    doc = doc.replace('\\end{tabularx}', '\\end{tabular}')
    doc = replace_cmd(doc, 'begin{tabular}', 1, lambda a, o: '\\begin{tabular}{%s}' % simplify_spec(a[0]))
    doc = replace_cmd(doc, 'begin{tabular*}', 2, lambda a, o: '\\begin{tabular}{%s}' % simplify_spec(a[1]))
    doc = doc.replace('\\end{tabular*}', '\\end{tabular}')

    # longtable -> table + tabular (first head + body + last foot)
    def longtable(m):
        spec = simplify_spec(m.group(1))
        inner = m.group(2)
        caption = ''
        label = ''
        cm = re.search(r'\\caption(?![A-Za-z])', inner)
        if cm:
            k = cm.end()
            if inner[k] == '[':
                k = match_bracket(inner, k + 1) + 1
            e = match_brace(inner, k)
            caption = inner[k + 1:e]
            inner = inner[:cm.start()] + inner[e + 1:]
        lm = re.search(r'\\label\{([^}]*)\}', inner)
        if lm:
            label = lm.group(1)
            inner = inner[:lm.start()] + inner[lm.end():]
        inner = re.sub(r'^\s*\\\\', '', inner.strip())
        head = body = foot = ''
        if '\\endfirsthead' in inner:
            head, rest = inner.split('\\endfirsthead', 1)
        else:
            rest = inner
            if '\\endhead' in rest:
                head, rest = rest.split('\\endhead', 1)
        if '\\endhead' in rest:
            rest = rest.split('\\endhead', 1)[1]
        if '\\endfoot' in rest:
            rest = rest.split('\\endfoot', 1)[1]
        if '\\endlastfoot' in rest:
            foot, rest = rest.split('\\endlastfoot', 1)
            foot = re.sub(r'\\multicolumn\{\d+\}\{[^}]*\}\{[^}]*\}\s*\\\\', '', foot)
        body = rest
        lab = '\\label{%s}\n' % label if label else ''
        return ('\\begin{table}\n\\caption{%s}\n%s\\begin{tabular}{%s}\n%s\n%s\n%s\n\\end{tabular}\n\\end{table}\n'
                % (caption, lab, spec, head.strip(), body.strip(), foot.strip()))

    doc = re.sub(r'\\begin\{longtable\}\{((?:[^{}]|\{[^{}]*\})*)\}(.*?)\\end\{longtable\}', longtable, doc, flags=re.S)

    doc = doc.replace('\\begin{threeparttable}', '').replace('\\end{threeparttable}', '')
    doc = replace_cmd(doc, 'multicolumn', 3,
                      lambda a, o: '\\multicolumn{%s}{%s}{%s}' % (a[0], simplify_spec(a[1]) or 'l', a[2]))

    def tablenotes(m):
        inner = m.group(1)
        inner = re.sub(r'^\s*\\(footnotesize|small|scriptsize)\b', '', inner)
        inner = re.sub(r'\\item\s*\[([^\]]*)\]\s*', lambda im: '\n\n\\textsuperscript{%s}\u202f' % im.group(1), inner)
        inner = re.sub(r'\\item\s+', '\n\n', inner)
        return '\\begin{tablenotes}\n' + inner.strip() + '\n\\end{tablenotes}'

    doc = re.sub(r'\\begin\{tablenotes\}(.*?)\\end\{tablenotes\}', tablenotes, doc, flags=re.S)
    doc = replace_cmd(doc, 'tnote', 1, lambda a, o: '\\textsuperscript{%s}' % a[0])
    doc = re.sub(r'\\cmidrule(\([^)]*\))?\{[^}]*\}', '', doc)
    doc = re.sub(r'\\addlinespace(\[[^\]]*\])?', '', doc)
    doc = re.sub(r'\\\\\[[^\]]*\]', r'\\\\', doc)
    doc = re.sub(r'\\(toprule|midrule|bottomrule)(\[[^\]]*\])?', r'\\\1', doc)
    return doc


def convert_frontmatter(doc):
    doc = doc.replace('\\begin{acknowledgments}', '\\chapter*{Acknowledgments}\n')
    doc = doc.replace('\\end{acknowledgments}', '')
    doc = doc.replace('\\begin{ttuabstract}', '\\chapter*{Abstract}\n')
    doc = doc.replace('\\end{ttuabstract}', '')
    doc = doc.replace('\\begin{abbreviations}', '\\chapter*{List of Abbreviations}\n\\begin{description}\n')
    doc = doc.replace('\\end{abbreviations}', '\\end{description}\n')
    doc = replace_cmd(doc, 'abbrev', 2, lambda a, o: '\\item[%s] %s' % (a[0], a[1]))
    return doc


def convert_declarations(doc):
    doc = replace_cmd(doc, 'aideclaration', 1,
                      lambda a, o: '\n\\begin{aideclaration}\n\\emph{AI-use declaration.} %s\n\\end{aideclaration}\n' % a[0])
    doc = replace_cmd(doc, 'authorshipstatement', 1,
                      lambda a, o: '\n\\begin{authorshipstatement}\n\\emph{Publication note.} %s\n\\end{authorshipstatement}\n' % a[0])
    return doc


def strip_misc(doc):
    doc = replace_cmd(doc, 'todo', 1, lambda a, o: '')
    doc = replace_cmd(doc, 'setlength', 2, lambda a, o: '')
    doc = replace_cmd(doc, 'needspace', 1, lambda a, o: '')
    doc = replace_cmd(doc, 'vspace*', 1, lambda a, o: '')
    doc = replace_cmd(doc, 'vspace', 1, lambda a, o: '')
    doc = replace_cmd(doc, 'hspace*', 1, lambda a, o: ' ')
    doc = replace_cmd(doc, 'hspace', 1, lambda a, o: ' ')
    doc = replace_cmd(doc, 'linespread', 1, lambda a, o: '')
    doc = re.sub(r'\\(centering|begingroup|endgroup|singlespacing|onehalfspacing|doublespacing|medskip|smallskip'
                 r'|bigskip|clearpage|newpage|phantomsection|selectfont|allowbreak|hfill|raggedright|arraybackslash'
                 r'|sloppy|fussy|nopagebreak|pagebreak)(?![A-Za-z])', ' ', doc)
    doc = re.sub(r'\\begin\{(description|enumerate|itemize)\}\[[^\]]*\]', r'\\begin{\1}', doc)
    doc = re.sub(r'\\code\{([^{}]*)\}\{([^{}]*)\}\{([^{}]*)\}', r'[[\1,\2,\3]]', doc)
    doc = re.sub(r'\\HtmlMarker\{[a-z]+\}', '', doc)
    return doc


def citation_order(doc):
    order = {}
    for m in re.finditer(r'\\cite(?:\[[^\]]*\])?\{([^}]*)\}', doc):
        for k in m.group(1).split(','):
            k = k.strip()
            if k and k not in order:
                order[k] = len(order) + 1
    return order


# --------------------------------------------------------------------------------------
# pandoc template, MathJax configuration, CSS
# --------------------------------------------------------------------------------------

def mathjax_config(text_macros):
    macros = {
        'bm': ['\\boldsymbol{#1}', 1],
        'bigO': ['\\mathcal{O}\\!\\left(#1\\right)', 1],
        'eps': '\\varepsilon',
        'Hcost': 'H_C', 'Hmix': 'H_M',
        'code': ['[[#1,#2,#3]]', 3],
        'R': '\\mathbb{R}', 'C': '\\mathbb{C}', 'Z': '\\mathbb{Z}',
        'poly': '\\operatorname{poly}',
        'argmin': '\\operatorname*{arg\\,min}', 'argmax': '\\operatorname*{arg\\,max}',
        'SI': ['#1\\,\\mathrm{#2}', 2], 'num': ['#1', 1], 'si': ['\\mathrm{#1}', 1],
        'qty': ['#1\\,\\mathrm{#2}', 2], 'unit': ['\\mathrm{#1}', 1],
        'giga': 'G', 'tera': 'T', 'mega': 'M', 'kilo': 'k', 'micro': '\\mu', 'nano': 'n', 'gibi': 'Gi',
        'byte': 'B', 'second': 's', 'hour': 'h', 'minute': 'min', 'percent': '\\%', 'per': '/',
        'textsc': ['\\text{#1}', 1],
        'textsuperscript': ['^{\\text{#1}}', 1],
        'lstick': ['#1', 1],
    }
    for name, value in text_macros.items():
        macros[name] = '\\text{%s}' % value.replace('\\', '\\\\')
    cfg = {
        'loader': {'load': ['[tex]/physics', '[tex]/boldsymbol', '[tex]/mathtools']},
        'tex': {
            'inlineMath': [['\\(', '\\)'], ['$', '$']],
            'displayMath': [['\\[', '\\]'], ['$$', '$$']],
            'processEscapes': True,
            'processEnvironments': True,
            'tags': 'ams',
            'tagSide': 'right',
            'packages': {'[+]': ['physics', 'boldsymbol', 'mathtools']},
            'macros': macros,
        },
        'options': {
            'skipHtmlTags': ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
            'ignoreHtmlClass': 'tex2jax_ignore',
        },
        'chtml': {'displayAlign': 'center', 'scale': 1.0},
    }
    return json.dumps(cfg, indent=1)


def write_template(meta, text_macros, path):
    tpl = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="author" content="$author$">
<meta name="description" content="$title$ - $doctype$ by $author$, Texas Tech University, $month$ $year$">
<title>$title$ - $author$</title>
<link rel="stylesheet" href="style.css">
<script>
window.MathJax = __MATHJAX__;
</script>
<script id="MathJax-script" async src="__MATHJAX_URL__"></script>
</head>
<body>
<a id="top"></a>
<header class="topbar">
  <a class="brand" href="#top">$title$</a>
  <nav class="topnav">
    <a href="#TOC">Contents</a>
    <a href="#list-of-figures">Figures</a>
    <a href="#list-of-tables">Tables</a>
    <a href="#references">References</a>
  </nav>
</header>
<main>
<section class="titlepage" id="title-page">
  <p class="tp-title">$title$</p>
  <p class="tp-by">by</p>
  <p class="tp-author">$author$, $credentials$</p>
  <p class="tp-type">$doctype$</p>
  <p class="tp-in">In</p>
  <p class="tp-dept">$department$</p>
  <p class="tp-submit">Submitted to the Graduate Faculty<br>of Texas Tech University in<br>Partial Fulfillment of<br>the Requirements for<br>the Degree of</p>
  <p class="tp-degree">$degree$</p>
  <p class="tp-approved">Approved</p>
  <p class="tp-member">$chair$<br><span class="tp-role">Chair of the Committee</span></p>
$for(committee)$
  <p class="tp-member">$committee$</p>
$endfor$
  <p class="tp-member">$dean$<br><span class="tp-role">Dean of the Graduate School</span></p>
  <p class="tp-date">$month$, $year$</p>
  <p class="tp-copyright">Copyright $year$, $author$</p>
</section>
$if(toc)$
<nav id="TOC" role="doc-toc">
<h1 class="unnumbered toc-title">Table of Contents</h1>
$table-of-contents$
</nav>
$endif$
<div id="lists-placeholder"></div>
$body$
</main>
<footer class="pagefoot">
  <p>$title$ &mdash; $author$, Texas Tech University, $month$ $year$. HTML edition generated from the LaTeX source by tools/build_html.py.</p>
</footer>
</body>
</html>
'''
    # a literal $ must be doubled in a pandoc template
    tpl = tpl.replace('__MATHJAX__', mathjax_config(text_macros).replace('$', '$$')).replace('__MATHJAX_URL__', MATHJAX_URL)
    path.write_text(tpl, encoding='utf-8')


CSS = r'''/* style.css - generated by tools/build_html.py */
:root {
  --bg: #fdfdfb;
  --fg: #1d1d1b;
  --muted: #5b5b57;
  --accent: #8a1c1c;
  --link: #0b4f8a;
  --rule: #d9d6cf;
  --code-bg: #f3f2ee;
  --figure-bg: #ffffff;
  --topbar-bg: rgba(253, 253, 251, 0.94);
  --font-body: "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", Times, serif;
  --font-head: "Palatino Linotype", Palatino, Georgia, serif;
  --font-mono: "SFMono-Regular", Menlo, Consolas, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #15171a;
    --fg: #e4e2dc;
    --muted: #a7a49c;
    --accent: #f0a4a4;
    --link: #8ec3f2;
    --rule: #3b3f45;
    --code-bg: #1f2227;
    --figure-bg: #fbfbf9;
    --topbar-bg: rgba(21, 23, 26, 0.94);
  }
}
html { scroll-behavior: smooth; scroll-padding-top: 3.4rem; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: var(--font-body);
  font-size: 17px;
  line-height: 1.6;
  text-rendering: optimizeLegibility;
}
main { max-width: 60em; margin: 0 auto; padding: 1.5rem 1.25rem 4rem; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
p { margin: 0 0 1em; text-align: justify; hyphens: auto; }

/* top bar */
.topbar {
  position: sticky; top: 0; z-index: 10;
  display: flex; flex-wrap: wrap; gap: 0.5rem 1.5rem; align-items: baseline;
  padding: 0.55rem 1.25rem;
  background: var(--topbar-bg); backdrop-filter: blur(6px);
  border-bottom: 1px solid var(--rule);
  font-size: 0.92rem;
}
.topbar .brand { color: var(--fg); font-weight: 600; letter-spacing: 0.01em; }
.topbar .topnav a { margin-right: 1rem; color: var(--link); }

/* title page */
.titlepage { text-align: center; padding: 2.5rem 1rem 2rem; border-bottom: 1px solid var(--rule); margin-bottom: 2rem; }
.titlepage p { text-align: center; margin: 0.65em 0; }
.tp-title { font-size: 1.7rem; font-weight: 600; line-height: 1.25; margin-bottom: 1em; }
.tp-author { font-size: 1.15rem; }
.tp-degree { text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }
.tp-submit, .tp-member, .tp-date { margin-top: 1.2em; }
.tp-role { color: var(--muted); font-size: 0.9em; }
.tp-copyright { margin-top: 2.5em; color: var(--muted); font-size: 0.95em; }

/* table of contents and lists */
#TOC { border: 1px solid var(--rule); border-radius: 6px; padding: 1rem 1.4rem; margin: 0 0 2rem; background: var(--code-bg); }
#TOC ul { list-style: none; padding-left: 0; margin: 0.2em 0; }
#TOC > ul > li { margin: 0.45em 0; font-weight: 600; }
#TOC ul ul { padding-left: 1.4em; font-weight: 400; }
#TOC ul ul li { margin: 0.15em 0; }
#TOC a { color: var(--fg); }
#TOC a:hover { color: var(--link); }
.toc-title { margin-top: 0.2em; }
details.list { border: 1px solid var(--rule); border-radius: 6px; padding: 0.5rem 1.2rem; margin: 0 0 1rem; }
details.list summary { cursor: pointer; font-weight: 600; font-family: var(--font-head); }
details.list ol { padding-left: 1.4em; }
details.list li { margin: 0.35em 0; font-size: 0.95em; text-align: left; }

/* headings */
h1, h2, h3, h4, h5, h6 { font-family: var(--font-head); line-height: 1.25; color: var(--fg); }
h1 { font-size: 1.75rem; margin: 3rem 0 1.2rem; text-align: center; padding-top: 1rem; border-top: 3px double var(--rule); }
h1 .chapter-kicker { display: block; font-size: 0.8rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.4rem; font-weight: 600; }
h1.unnumbered { text-align: center; }
h2 { font-size: 1.3rem; margin: 2.2rem 0 0.8rem; }
h3 { font-size: 1.1rem; font-style: italic; margin: 1.8rem 0 0.6rem; }
h4 { font-size: 1rem; font-style: italic; font-weight: 400; margin: 1.4rem 0 0.5rem; }
h5 { font-size: 1rem; font-weight: 700; margin: 1.1rem 0 0.2rem; }
.secnum { color: var(--accent); margin-right: 0.45em; font-weight: 600; }
.chapter-title { display: block; }

/* figures */
figure { margin: 1.8rem auto; text-align: center; max-width: 100%; }
figure img { max-width: 100%; height: auto; display: inline-block; background: var(--figure-bg); padding: 6px; border-radius: 4px; }
figcaption { text-align: left; font-size: 0.93em; line-height: 1.45; margin-top: 0.7em; color: var(--fg); }
figcaption strong { font-weight: 700; }
figure.fallback img { border: 1px dashed var(--rule); }

/* tables */
table { border-collapse: collapse; margin: 1.6rem auto; font-size: 0.9em; line-height: 1.35; max-width: 100%; }
table caption { caption-side: top; text-align: left; margin-bottom: 0.5em; font-size: 1.03em; }
th, td { padding: 0.3em 0.6em; border-bottom: 1px solid var(--rule); vertical-align: top; text-align: left; }
thead th { border-bottom: 2px solid var(--fg); border-top: 2px solid var(--fg); }
tbody tr:last-child td { border-bottom: 2px solid var(--fg); }
.tablenotes { font-size: 0.85em; color: var(--muted); max-width: 48em; margin: -0.8rem auto 1.6rem; }
.tablenotes p { text-align: left; margin: 0.2em 0; }
.table-wrap { overflow-x: auto; }

/* code */
code { font-family: var(--font-mono); font-size: 0.88em; background: var(--code-bg); padding: 0.05em 0.3em; border-radius: 3px; }
pre { background: var(--code-bg); padding: 0.9rem 1rem; border-radius: 6px; overflow-x: auto; line-height: 1.4; font-size: 0.85em; border: 1px solid var(--rule); }
pre code { background: none; padding: 0; font-size: 1em; }
.listing-caption { font-size: 0.93em; margin: 1.6rem 0 0.4rem; text-align: left; }
div.sourceCode { margin-bottom: 1.6rem; }
pre a.sourceLine, pre > code > span > a { color: var(--muted); }

/* theorem-like environments and declarations */
.theorem, .lemma, .proposition, .corollary, .definition, .assumption, .remark {
  margin: 1.2em 0; padding: 0.6em 1em; border-left: 3px solid var(--accent); background: var(--code-bg); border-radius: 0 4px 4px 0;
}
.proof { margin: 1em 0; }
.aideclaration, .authorshipstatement { font-size: 0.9em; color: var(--muted); border-left: 3px solid var(--rule); padding-left: 1em; margin: 1em 0 1.4em; }
.aideclaration p, .authorshipstatement p { text-align: left; }
blockquote { margin: 1em 1.5em; padding-left: 1em; border-left: 3px solid var(--rule); color: var(--fg); font-style: italic; }

/* lists */
ul, ol { padding-left: 1.6em; }
li { margin: 0.25em 0; }
dl.abbreviations { display: grid; grid-template-columns: max-content 1fr; gap: 0.35em 1.4em; }
dl.abbreviations dt { font-weight: 600; }
dl.abbreviations dd { margin: 0; }
dt { font-weight: 600; margin-top: 0.6em; }
dd { margin: 0 0 0.4em 1.6em; }
dd p { margin: 0; }

/* citations and references */
.citation a { color: var(--link); }
#refs { font-size: 0.93em; }
.csl-entry { display: flex; gap: 0.6em; margin: 0.55em 0; text-align: left; }
.csl-left-margin { min-width: 2.6em; text-align: right; flex: 0 0 auto; }
.csl-right-inline { flex: 1 1 auto; }

.math.display { display: block; overflow-x: auto; overflow-y: hidden; margin: 0.4em 0; }
mjx-container[display="true"] { margin: 0.8em 0 !important; }
.pagefoot { max-width: 60em; margin: 2rem auto; padding: 1rem 1.25rem; border-top: 1px solid var(--rule); color: var(--muted); font-size: 0.85em; }
@media (max-width: 700px) {
  body { font-size: 16px; }
  main { padding: 1rem 0.8rem 3rem; }
  h1 { font-size: 1.45rem; }
  .topbar .topnav a { margin-right: 0.7rem; }
}
@media print {
  .topbar { display: none; }
  main { max-width: none; }
}
'''


# --------------------------------------------------------------------------------------
# HTML post-processing
# --------------------------------------------------------------------------------------

def find_div_end(html, start):
    """index just after the </div> that closes the <div ...> starting at `start`."""
    depth = 0
    pos = start
    tag = re.compile(r'<div\b|</div>')
    while True:
        m = tag.search(html, pos)
        if not m:
            return len(html)
        if m.group(0) == '</div>':
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
        pos = m.end()


def move_references(html):
    m = re.search(r'<div id="refs"', html)
    h = re.search(r'<h1[^>]*id="references"[^>]*>.*?</h1>', html, re.S)
    if not m or not h:
        warn('could not relocate the reference list')
        return html
    end = find_div_end(html, m.start())
    refs = html[m.start():end]
    html = html[:m.start()] + html[end:]
    h = re.search(r'<h1[^>]*id="references"[^>]*>.*?</h1>', html, re.S)
    return html[:h.end()] + '\n' + refs + html[h.end():]


def listing_captions(html, listing_nums):
    def repl(m):
        attrs = m.group(1)
        lab = re.search(r'id="([^"]*)"', attrs)
        cap = re.search(r'data-caption="([^"]*)"', attrs)
        if not cap:
            return m.group(0)
        num = listing_nums.get(lab.group(1)) if lab else None
        prefix = '<strong>Listing %s.</strong> ' % num if num else ''
        return '<p class="listing-caption">%s%s</p>\n%s' % (prefix, cap.group(1), m.group(0))
    return re.sub(r'<div class="sourceCode"([^>]*)>', repl, html)


def style_headings(html):
    def h1(m):
        attrs, text = m.group(1), m.group(2)
        km = re.match(r'(Chapter [IVXLC]+|Appendix [A-Z])\. (.*)$', text, re.S)
        if km:
            return '<h1%s><span class="chapter-kicker">%s</span><span class="chapter-title">%s</span></h1>' % (attrs, km.group(1), km.group(2))
        return m.group(0)
    html = re.sub(r'<h1([^>]*)>(.*?)</h1>', h1, html, flags=re.S)

    def hn(m):
        tag, attrs, text = m.group(1), m.group(2), m.group(3)
        nm = re.match(r'([A-Z]?\d*(?:\.\d+)+|[A-Z]\.\d+) (.*)$', text, re.S)
        if nm:
            return '<%s%s><span class="secnum">%s</span>%s</%s>' % (tag, attrs, nm.group(1), nm.group(2), tag)
        return m.group(0)
    html = re.sub(r'<(h[234])([^>]*)>(.*?)</\1>', hn, html, flags=re.S)
    return html


def image_sizes(html, jobs):
    """Set a width on each image from the SVG's natural size (1 pt -> 1.6 px, capped by CSS)."""
    for job in jobs:
        path = IMAGES / (job.name + '.' + job.ext)
        if not path.exists():
            continue
        width = None
        if job.ext == 'svg':
            head = path.read_text(encoding='utf-8', errors='replace')[:600]
            wm = re.search(r'<svg[^>]*\swidth="([0-9.]+)pt"', head)
            if wm:
                width = int(float(wm.group(1)) * 1.6)
        else:
            width = 900
        if width:
            html = html.replace('<img src="images/%s.%s" />' % (job.name, job.ext),
                                '<img src="images/%s.%s" width="%d" alt="%s" />' % (job.name, job.ext, width,
                                                                                    htmlmod.escape(plain_text(job.caption)[:200], quote=True)))
        if job.method == 'fallback':
            html = re.sub(r'<figure id="%s"' % re.escape(job.label or ''), r'<figure class="fallback" id="%s"' % (job.label or ''), html)
    return html


def lists_of_floats(html):
    figs = []
    tabs = []
    for m in re.finditer(r'<figure id="([^"]*)"[^>]*>.*?<figcaption>(.*?)</figcaption>', html, re.S):
        fid, cap = m.group(1), m.group(2)
        if fid.startswith('alg:'):
            continue
        figs.append((fid, cap))
    for m in re.finditer(r'<table id="([^"]*)">\s*<caption>(.*?)</caption>', html, re.S):
        tabs.append((m.group(1), m.group(2)))

    def entries(items):
        out = []
        for fid, cap in items:
            cap = re.sub(r'\s+', ' ', cap).strip()
            out.append('<li><a href="#%s">%s</a></li>' % (fid, cap))
        return '\n'.join(out)
    block = ('<details class="list" id="list-of-figures"><summary>List of Figures (%d)</summary><ol>\n%s\n</ol></details>\n'
             '<details class="list" id="list-of-tables"><summary>List of Tables (%d)</summary><ol>\n%s\n</ol></details>\n'
             % (len(figs), entries(figs), len(tabs), entries(tabs)))
    return html.replace('<div id="lists-placeholder"></div>', block)


def abbreviations_class(html):
    return re.sub(r'(<h1[^>]*id="list-of-abbreviations"[^>]*>.*?</h1>\s*)<dl>', r'\1<dl class="abbreviations">', html, flags=re.S)


def wrap_tables(html):
    return re.sub(r'(<table[^>]*>.*?</table>)', r'<div class="table-wrap">\1</div>', html, flags=re.S)


# --------------------------------------------------------------------------------------
# verification
# --------------------------------------------------------------------------------------

def verify(html, jobs, source_fig_count, labels, theorem_envs):
    report = []
    n_fig = len(re.findall(r'<figure\b', html))
    n_img = len(re.findall(r'<img\b', html))
    report.append('figure environments in source: %d (+%d algorithms) -> <figure> elements: %d, <img>: %d'
                  % (source_fig_count, len([j for j in jobs if j.kind == 'algorithm']), n_fig, n_img))
    if n_fig != len(jobs):
        warn('figure count mismatch: %d jobs vs %d <figure> elements' % (len(jobs), n_fig))
    body = html.split('<main>', 1)[1] if '<main>' in html else html
    text = re.sub(r'<span class="math (?:inline|display)">.*?</span>', ' ', body, flags=re.S)
    text = re.sub(r'<pre\b.*?</pre>', ' ', text, flags=re.S)
    text = re.sub(r'<script\b.*?</script>', ' ', text, flags=re.S)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = htmlmod.unescape(text)
    residue = {}
    for pat in [r'\\cref', r'\\Cref', r'\\SI\b', r'\\num\b', r'\\qgear', r'\\deal\b', r'\\cudaq', r'\\qiskit', r'\\todo',
                r'\\begin\{', r'\\end\{', r'\\label', r'\\code\b', r'\\tnote', r'\\item\b', r'\\textsuperscript',
                r'\\cite', r'\\ref\b', r'\\hyperref', r'\\caption', r'\\textbf', r'\\emph', r'\\texttt', r'\\\\',
                r'\?\?', r'@@IMG', r'@@LST', r'\\HtmlMarker', r'\\abbrev', r'\\labelcref', r'\\percent', r'\\giga']:
        n = len(re.findall(pat, text))
        if n:
            residue[pat] = n
    report.append('LaTeX residue in text (outside math): %s' % (residue or 'none'))
    n_math = len(re.findall(r'class="math (?:inline|display)"', html))
    report.append('MathJax math elements: %d (display: %d)' % (n_math, len(re.findall(r'class="math display"', html))))
    # theorem numbering check against main.aux
    bad = []
    for lab, d in labels.items():
        if d['type'] in theorem_envs:
            m = re.search(r'<div id="%s"[^>]*>\s*<p><strong>([^<]*)</strong>' % re.escape(lab), html)
            if not m:
                bad.append('%s (no heading found)' % lab)
            else:
                expected = '%s %s' % (theorem_envs[d['type']], d['num'])
                if m.group(1).strip() != expected:
                    bad.append('%s: html says "%s", aux says "%s"' % (lab, m.group(1).strip(), expected))
    report.append('theorem numbering vs main.aux: %s' % ('ok' if not bad else '; '.join(bad)))
    # dangling internal links
    ids = set(re.findall(r'\sid="([^"]+)"', html))
    missing = {}
    for href in re.findall(r'href="#([^"]+)"', html):
        if href not in ids:
            missing[href] = missing.get(href, 0) + 1
    report.append('dangling internal links: %s' % (missing or 'none'))
    return report


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------

def main():
    global BUILD
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--jobs', type=int, default=4, help='parallel tectonic processes (default 4)')
    ap.add_argument('--force', action='store_true', help='recompile every figure, ignore the cache')
    ap.add_argument('--skip-figures', action='store_true', help='do not compile figures (reuse what is in html/images)')
    ap.add_argument('--build-dir', default=str(HERE / '_build'), help='directory for intermediate files')
    args = ap.parse_args()
    BUILD = Path(args.build_dir)
    BUILD.mkdir(parents=True, exist_ok=True)
    figs_dir = BUILD / 'figs'
    HTML.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)

    if not CSL.exists():
        log('downloading ieee.csl ...')
        rc, _ = run(['curl', '-sS', '-L', '--max-time', '60', '-o', str(CSL), CSL_URL])
        if rc != 0 or not CSL.exists():
            warn('could not download ieee.csl; writing a minimal numeric style')
            CSL.write_text(MINIMAL_CSL, encoding='utf-8')

    t_start = time.time()
    log('reading main.tex, preamble.tex, main.aux')
    meta, items = parse_main(read(MAIN_TEX))
    labels = parse_aux(MAIN_AUX)
    preamble_text = read(PREAMBLE_TEX)
    text_macros, math_lines, theorem_envs, newtheorem_lines = parse_preamble(preamble_text)
    pre = standalone_preamble(preamble_text)

    log('flattening %d inputs' % len([i for i in items if i[0] == 'input']))
    doc = flatten(items)
    doc, listing_bodies = protect_listings(doc)
    source_fig_count = len(re.findall(r'\\begin\{figure\}', doc))

    sub_parent = {}
    doc, jobs = extract_floats(doc, sub_parent)
    log('extracted %d figures and %d algorithms' % (len([j for j in jobs if j.kind == 'figure']),
                                                     len([j for j in jobs if j.kind == 'algorithm'])))
    doc = strip_comments(doc)
    doc = convert_frontmatter(doc)
    doc = convert_tables(doc)          # before numbering so that longtables are counted
    doc, nb = number_document(doc, labels)
    for msg in nb.mismatches:
        warn('numbering: ' + msg + ' (main.aux used; rebuild the PDF if the source changed)')

    resolver = RefResolver(labels, theorem_envs, sub_parent)
    cite_numbers = citation_order(doc)

    if args.skip_figures:
        manifest = json.loads(read(MANIFEST)) if MANIFEST.exists() else {}
        for job in jobs:
            job.tex = job_tex(job, pre, resolver, cite_numbers)
            job.hash = hashlib.sha256(job.tex.encode('utf-8')).hexdigest()[:16]
            ent = manifest.get(job.name, {})
            job.ext = ent.get('ext', 'svg')
            job.method = ent.get('method', 'missing') if (IMAGES / (job.name + '.' + job.ext)).exists() else 'missing'
    else:
        build_figures(jobs, pre, resolver, cite_numbers, figs_dir, labels, args.jobs, args.force)
    for job in jobs:
        doc = doc.replace('@@IMG:%s@@' % job.name, 'images/%s.%s' % (job.name, job.ext))

    log('preprocessing text')
    doc = resolver.apply(doc, link=True)
    if resolver.unresolved:
        warn('unresolved labels: %s' % sorted(set(resolver.unresolved)))
    doc = expand_text_macros(doc, text_macros)
    for job in jobs:
        job.caption = expand_text_macros(job.caption, text_macros)
    doc = expand_siunitx(doc)
    doc = convert_declarations(doc)
    doc = strip_misc(doc)
    doc = restore_listings(doc, listing_bodies)

    header = '\\documentclass{report}\n' + '\n'.join(newtheorem_lines) + '\n' + '\n'.join(math_lines) + '\n\\begin{document}\n'
    tex_out = BUILD / 'thesis.tex'
    tex_out.write_text(header + doc + '\n\\end{document}\n', encoding='utf-8')

    meta_file = BUILD / 'meta.json'
    meta_file.write_text(json.dumps(meta, indent=1), encoding='utf-8')
    template = HERE / 'template.html'
    write_template(meta, text_macros, template)

    log('running pandoc')
    out_html = HTML / 'index.html'
    cmd = [PANDOC, '-s', '--from', 'latex', '--to', 'html5', '--math-method=mathjax', '--toc', '--toc-depth=2',
           '--citeproc', '--bibliography', str(BIB), '--csl', str(CSL), '--template', str(template),
           '--metadata-file', str(meta_file), '--metadata', 'link-citations=true', '--metadata', 'lang=en',
           '--wrap=none', '-o', str(out_html), str(tex_out)]
    rc, msg = run(cmd, cwd=BUILD, timeout=900)
    for line in msg.strip().split('\n'):
        if line.strip():
            log('  pandoc: ' + line.strip())
    if rc != 0:
        log('pandoc failed (exit %d)' % rc)
        sys.exit(1)

    log('post-processing html')
    html = read(out_html)
    html = move_references(html)
    html = listing_captions(html, nb.listing_nums)
    html = style_headings(html)
    html = image_sizes(html, jobs)
    html = wrap_tables(html)
    html = abbreviations_class(html)
    html = lists_of_floats(html)
    out_html.write_text(html, encoding='utf-8')
    (HTML / 'style.css').write_text(CSS, encoding='utf-8')

    report = verify(html, jobs, source_fig_count, labels, theorem_envs)
    log('')
    log('==== build report ====')
    for line in report:
        log(line)
    n_svg = len([j for j in jobs if j.ext == 'svg' and j.method in ('tectonic', 'cached')])
    fallback = [j for j in jobs if j.method == 'fallback']
    missing = [j for j in jobs if j.method == 'missing']
    log('images: %d SVG via tectonic, %d via PDF-crop fallback%s, %d missing%s'
        % (n_svg, len(fallback), (' (' + ', '.join(j.label or j.name for j in fallback) + ')') if fallback else '',
           len(missing), (' (' + ', '.join(j.name for j in missing) + ')') if missing else ''))
    size = out_html.stat().st_size
    total = sum(p.stat().st_size for p in HTML.rglob('*') if p.is_file())
    log('html/index.html: %.1f KB; html/ total: %.1f MB' % (size / 1024, total / 1024 / 1024))
    if WARNINGS:
        log('%d warning(s):' % len(WARNINGS))
        for w in WARNINGS:
            log('  - ' + w)
    log('done in %.0f s -> %s' % (time.time() - t_start, out_html))


MINIMAL_CSL = '''<?xml version="1.0" encoding="utf-8"?>
<style xmlns="http://purl.org/net/xbiblio/csl" class="in-text" version="1.0">
  <info><title>Minimal numeric (IEEE-like)</title><id>minimal-numeric</id><updated>2026-01-01T00:00:00+00:00</updated></info>
  <citation collapse="citation-number"><sort><key variable="citation-number"/></sort>
    <layout prefix="[" suffix="]" delimiter="], ["><text variable="citation-number"/></layout></citation>
  <bibliography entry-spacing="0" second-field-align="flush">
    <layout suffix=".">
      <text variable="citation-number" prefix="[" suffix="]"/>
      <names variable="author" suffix=", "><name initialize-with=". " and="text" delimiter=", "/></names>
      <text variable="title" quotes="true" suffix=", "/>
      <text variable="container-title" font-style="italic" suffix=", "/>
      <text variable="volume" prefix="vol. " suffix=", "/>
      <text variable="page" prefix="pp. " suffix=", "/>
      <date variable="issued"><date-part name="year"/></date>
      <text variable="DOI" prefix=", doi: "/>
    </layout>
  </bibliography>
</style>
'''

if __name__ == '__main__':
    main()
