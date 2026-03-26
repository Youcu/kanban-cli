"""Box drawing primitives for AI CLI style layout."""

from __future__ import annotations

import re
import unicodedata

# Wide enough for Korean option lines; used by all standard boxes.
INNER_WIDTH = 52
BORDER_WIDTH = INNER_WIDTH + 4  # includes 2-space padding on each side

TL = '╭'
TR = '╮'
BL = '╰'
BR = '╯'
H = '─'
V = '│'
ML = '├'
MR = '┤'

_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
_ANSI_OR_CHAR_RE = re.compile(r'\x1b\[[0-9;]*m|.', re.DOTALL)
_RESET = '\033[0m'
_TRUNC_SUFFIX = '...'


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub('', text)


def display_width(text: str) -> int:
    """Monospace terminal display width (fullwidth CJK = 2 cols)."""
    total = 0
    for ch in unicodedata.normalize('NFC', _strip_ansi(text)):
        ea = unicodedata.east_asian_width(ch)
        total += 2 if ea in ('F', 'W') else 1
    return total


def _visible_len(text: str) -> int:
    """Same as display width; name kept for call sites expecting “visible” length."""
    return display_width(text)


def _pad(text: str, width: int) -> str:
    return text + ' ' * max(0, width - display_width(text))


def _truncate_to_display_width(text: str, max_width: int) -> str:
    if max_width <= 0:
        return ''
    if display_width(text) <= max_width:
        return text
    reserve = display_width(_TRUNC_SUFFIX)
    budget = max(0, max_width - reserve)
    out: list[str] = []
    w = 0
    had_ansi = False

    for token in _ANSI_OR_CHAR_RE.findall(unicodedata.normalize('NFC', text)):
        if _ANSI_RE.fullmatch(token):
            had_ansi = True
            out.append(token)
            continue

        ea = unicodedata.east_asian_width(token)
        cw = 2 if ea in ('F', 'W') else 1
        if w + cw > budget:
            break
        out.append(token)
        w += cw

    truncated = ''.join(out) + _TRUNC_SUFFIX
    if had_ansi and not truncated.endswith(_RESET):
        truncated += _RESET
    return truncated


def truncate_to_width(text: str, max_width: int) -> str:
    """Truncate to at most ``max_width`` terminal columns; appends … if shortened."""
    return _truncate_to_display_width(text, max_width)


def pad_between(left: str, right: str) -> str:
    """Pad so left and right align within INNER_WIDTH (display-aware)."""
    gap = INNER_WIDTH - display_width(left) - display_width(right)
    return left + ' ' * max(1, gap) + right


def top(title: str = '') -> str:
    if title:
        w_title = display_width(title)
        right_dashes = max(0, (2 + BORDER_WIDTH) - 7 - w_title)
        return f'{TL}{H * 3} {title} {H * right_dashes}{TR}'
    return TL + H * BORDER_WIDTH + TR


def divider() -> str:
    return ML + H * BORDER_WIDTH + MR


def bottom() -> str:
    return BL + H * BORDER_WIDTH + BR


def row(content: str = '') -> str:
    if display_width(content) > INNER_WIDTH:
        content = _truncate_to_display_width(content, INNER_WIDTH)
    padded = _pad(content, INNER_WIDTH)
    return f'{V}  {padded}  {V}'


def empty_row() -> str:
    return row()


# ── Kanban multi-column board ──────────────────────────────────────────────

K_COL_INNER = 20  # content width per column
K_COL_TOTAL = K_COL_INNER + 2  # + 1 space padding each side
K_NC = 4  # number of columns

TC = '┬'
BC = '┴'
CC = '┼'


def _k_border(left: str, junction: str, right: str) -> str:
    seg = H * K_COL_TOTAL
    return left + junction.join([seg] * K_NC) + right


def k_top() -> str:
    return _k_border(TL, TC, TR)


def k_header_divider() -> str:
    return _k_border(ML, CC, MR)


def k_bottom() -> str:
    return _k_border(BL, BC, BR)


def k_row(cells: list[str]) -> str:
    """Render one row across K_NC columns. Each cell padded/truncated to K_COL_INNER."""
    formatted = [' ' + _k_cell(c) + ' ' for c in cells]
    return V + V.join(formatted) + V


def _k_cell(text: str) -> str:
    if display_width(text) > K_COL_INNER:
        text = _truncate_to_display_width(text, K_COL_INNER)
    visible = display_width(text)
    return text + ' ' * max(0, K_COL_INNER - visible)
