"""Text normalisation + error rate for narration QA.

- Chinese (zh): CER on characters. Both sides are folded to Simplified (if `opencc` is installed) — the
  many-to-one direction, so ASR output in either script compares fairly (converting Simplified → Traditional
  can pick the wrong character, e.g. 冲 → 衝 where the script says 沖). Digits are spelled out and
  punctuation removed — so "3 個" and "三個" count as the same.
- English (en): WER on words, lower-cased, punctuation removed, digits spelled out (0–999 999).
"""
import re

try:
    import opencc
    _cc = opencc.OpenCC("t2s")
except Exception:  # optional dependency
    _cc = None

ZH_DIGITS = "零一二三四五六七八九"
EN_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
EN_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_zh(n):
    if n < 10:
        return ZH_DIGITS[n]
    if n >= 10000:
        hi, lo = divmod(n, 10000)
        return num_zh(hi) + "萬" + ("" if lo == 0 else ("零" if lo < 1000 else "") + num_zh(lo))
    out, zero = "", False
    for unit, v in ((1000, "千"), (100, "百"), (10, "十")):
        d, n = divmod(n, unit)
        if d:
            out += ("零" if zero and out else "") + ("" if unit == 10 and d == 1 and not out else ZH_DIGITS[d]) + v
            zero = False
        elif out:
            zero = True
    return out + (("零" if zero else "") + ZH_DIGITS[n] if n else "")


def num_en(n):
    if n < 20:
        return EN_ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return EN_TENS[t] + ("" if o == 0 else " " + EN_ONES[o])
    if n < 1000:
        h, r = divmod(n, 100)
        return EN_ONES[h] + " hundred" + ("" if r == 0 else " " + num_en(r))
    th, r = divmod(n, 1000)
    return num_en(th) + " thousand" + ("" if r == 0 else " " + num_en(r))


_warned = False


def norm_zh(s):
    global _warned
    s = s.lower().replace("〇", "零")
    s = re.sub(r"\d+", lambda m: num_zh(int(m.group())) if len(m.group()) <= 8 and not m.group().startswith("0")
               else "".join(ZH_DIGITS[int(c)] for c in m.group()), s)
    if _cc:
        s = _cc.convert(s)
    elif not _warned:
        import sys
        print("warning: opencc not installed — Simplified vs Traditional characters will count as errors "
              "(pip install opencc-python-reimplemented)", file=sys.stderr)
        _warned = True
    return re.sub(r"[\W_]+", "", s)


def norm_en(s):
    s = s.lower().replace("%", " percent").replace("&", " and ")
    s = re.sub(r"\d+", lambda m: num_en(int(m.group())) if len(m.group()) <= 6 else " ".join(EN_ONES[int(c)] for c in m.group()), s)
    s = re.sub(r"[^a-z0-9' ]+", " ", s.replace("-", " "))
    return s.split()


def edit_distance(a, b):
    d = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(b) + 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
    return d[len(b)]


def error_rate(ref, hyp, lang="zh"):
    """CER for zh, WER for en (0 = perfect)."""
    if lang.startswith("zh"):
        r, h = norm_zh(ref), norm_zh(hyp)
    else:
        r, h = norm_en(ref), norm_en(hyp)
    return edit_distance(r, h) / max(len(r), 1)


cer = error_rate  # backwards-compatible name
