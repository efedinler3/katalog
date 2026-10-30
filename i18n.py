"""Dil secimi ve ceviri.

python build.py --lang tr   -> Turkce katalog
python build.py --lang en   -> Ingilizce katalog
Ceviriler ceviri-tr.json dosyasindadir: {"Ingilizce metin": "Turkce metin"}.
Bos veya eksik ceviri Ingilizce kalir ve derleme sonunda listelenir.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANG = "en"
if "--lang" in sys.argv:
    LANG = sys.argv[sys.argv.index("--lang") + 1]
COLLECT = "--collect" in sys.argv

_TR = {}
if LANG == "tr":
    with open(os.path.join(HERE, "ceviri-tr.json"), encoding="utf-8") as f:
        _TR = {k: v for k, v in json.load(f).items() if v}
_TR_VALUES = set(_TR.values())

SEEN = {}          # metin -> ilk goruldugu yer (toplama modu)
MISSING = []
_where = ["ui"]


def where(tag):
    _where[0] = tag


_UNITS = {"mm", "kg", "Nm", "Hz", "kgf", "lbs", "ft", "hp", "x", "Shore"}


def needs_translation(s):
    """Motor kodu, parca no, olcu gibi metinler cevrilmez (ornek: '4JH3-TE', 'M16 × 1.5', '55 Shore')."""
    if re.fullmatch(r"[A-Za-z]{1,3}\.", s.strip()):      # 'p.' gibi kisaltmalar
        return True
    words = re.findall(r"[A-Za-z]+", s)
    return any(re.search(r"[a-z]", w) and w not in _UNITS and len(w) >= 2 for w in words)


def T(s):
    """Arayuz / veri metnini secili dile cevirir."""
    if not s:
        return s
    if COLLECT and s not in SEEN:
        SEEN[s] = _where[0]
    if LANG == "en":
        return s
    t = _TR.get(s)
    if t is None:
        if s in _TR_VALUES:              # zaten cevrilmis metin
            return s
        if s not in MISSING and needs_translation(s):
            MISSING.append(s)
        return s
    return t


def Tf(s, **kw):
    """Yer tutuculu metin: Tf('Engine finder · {i} of {n}', i=1, n=3)."""
    return T(s).format(**kw)
