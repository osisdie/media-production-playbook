#!/usr/bin/env python3
"""Drag detection: find a token that is held far too long and runs straight into the next one.

Autoregressive TTS (GPT-SoVITS and friends) sometimes stalls on a syllable or repeats it. ASR still transcribes
the right words, so CER/WER passes — this check uses ASR word timestamps instead.

A token is flagged when:  duration > limit  AND  the next word starts within 0.05 s (no pause after it).
Limits: one CJK character 0.50 s; an English/number token 0.75 s × max(1, letters/3).
The first word and tokens next to punctuation are skipped: Whisper folds the lead-in silence into the first
word and the pause for a comma into the neighbouring token. Script and transcript are folded to the same
Chinese script (opencc t2s) before alignment, so Simplified ASR output still lines up with a Traditional script.
"""
import difflib
import re

try:
    import opencc
    _fold = opencc.OpenCC("t2s").convert   # compare Simplified ASR output with a Traditional script
except Exception:
    def _fold(x):
        return x

CJK_MAX, EN_MAX = 0.50, 0.75
PUNCT = "，。、：；！？,.:;!?「」『』（）()／\"'“”‘’—–-"
_TOKEN = r"[A-Za-z0-9']+|[一-鿿]"


def _ref_tokens(text):
    toks = re.findall(r"[A-Za-z0-9']+|[一-鿿]|[%s]" % re.escape(PUNCT), text)
    out = []
    for i, t in enumerate(toks):
        if t in PUNCT:
            continue
        prev_p = i == 0 or toks[i - 1] in PUNCT
        next_p = i + 1 < len(toks) and toks[i + 1] in PUNCT
        out.append((_fold(t.lower()), prev_p or next_p))
    return out


def drags(words, text=None):
    """words: [[start, end, word], ...] from ASR. Returns [(word, duration, start), ...]."""
    near_punct = {}
    if text:
        ref = _ref_tokens(text)
        hyp = [(_fold(t.lower()), wi) for wi, (_, _, w) in enumerate(words) for t in re.findall(_TOKEN, w)]
        sm = difflib.SequenceMatcher(a=[r[0] for r in ref], b=[h[0] for h in hyp], autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n):
                if ref[a + k][1]:
                    near_punct[hyp[b + k][1]] = True
    out = []
    for i, (s, e, w) in enumerate(words[:-1]):
        # the first word absorbs the lead-in silence/onset, and tokens next to punctuation absorb pauses
        if i == 0 or near_punct.get(i):
            continue
        w = w.strip()
        if words[i + 1][0] - e > 0.05:   # a pause follows → natural phrase ending
            continue
        n_cjk = len(re.findall(r"[一-鿿]", w))
        n_en = len(re.findall(r"[A-Za-z0-9]", w))
        lim = CJK_MAX * max(n_cjk, 1) if n_cjk else EN_MAX * max(1, n_en / 3)
        if e - s > lim:
            out.append((w, round(e - s, 2), round(s, 2)))
    return out


def score(words, text=None):
    """Total seconds over the limit (0 = no drag)."""
    return round(sum(d - (CJK_MAX if re.search(r"[一-鿿]", w) else EN_MAX) for w, d, _ in drags(words, text)), 2)
