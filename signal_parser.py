"""
Signal parser for two channel formats.

Format 1 (@gold_alicxzos110):
📊XAUUSD SELL NOW ( 4167 ) ✅
📊TARGET 1 ( 4163 )✅
📊TARGET 2 ( 4159 )✅
📊TARGET 3 ( 4159 )✅
📊TARGET 4 ( 4150 )✅
🚫 STOP LOSS ( 4177 )

Format 2 (@Xsd_Gold_SignaIs1):
XAUUSD SELL NOW 4171:::4180
✔️ Tp1 🔽 4166
✔️ Tp2 🔽 4161
✔️ Tp3 🔽 4156
✔️ Tp4 🔽 4151
✔️ Tp5 🔽 4146
✔️ Tp6 🔽 4140
✔️ Tp7 🔽 4130
❌ SL 4186 100% Sure Call
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Signal:
    symbol: str
    direction: str  # "BUY" or "SELL"
    entry: float
    stop_loss: float
    take_profits: list[float] = field(default_factory=list)
    raw_text: str = ""
    source_channel: str = ""

    def __repr__(self):
        tps = ", ".join(str(tp) for tp in self.take_profits)
        return (
            f"Signal({self.symbol} {self.direction} "
            f"Entry={self.entry} SL={self.stop_loss} "
            f"TPs=[{tps}] src={self.source_channel})"
        )


def parse_format1(text: str, channel: str) -> Optional[Signal]:
    """Parse Format 1: emoji-based with parentheses."""
    lines = text.strip().split("\n")
    full_text = text.strip()

    # Direction and entry: 📊XAUUSD SELL NOW ( 4167 ) ✅
    dir_match = re.search(
        r"📊\s*XAUUSD\s+(BUY|SELL)\s+NOW\s*\(\s*([\d.]+)\s*\)",
        full_text,
        re.IGNORECASE,
    )
    if not dir_match:
        return None

    direction = dir_match.group(1).upper()
    entry = float(dir_match.group(2))

    # Stop loss: 🚫 STOP LOSS ( 4177 )
    sl_match = re.search(r"STOP\s*LOSS\s*\(\s*([\d.]+)\s*\)", full_text, re.IGNORECASE)
    if not sl_match:
        return None
    stop_loss = float(sl_match.group(1))

    # Targets: 📊TARGET 1 ( 4163 )✅
    tp_matches = re.findall(r"TARGET\s*\d+\s*\(\s*([\d.]+)\s*\)", full_text, re.IGNORECASE)
    if not tp_matches:
        return None

    take_profits = [float(tp) for tp in tp_matches]

    return Signal(
        symbol="XAUUSD",
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        take_profits=take_profits,
        raw_text=text,
        source_channel=channel,
    )


def parse_format2(text: str, channel: str) -> Optional[Signal]:
    """Parse Format 2: ✔️ Tp format with ::: separator."""
    full_text = text.strip()

    # Direction and entry: XAUUSD SELL NOW 4171:::4180
    # The ::: separates entry from SL
    dir_match = re.search(
        r"XAUUSD\s+(BUY|SELL)\s+NOW\s+([\d.]+)\s*:::\s*([\d.]+)",
        full_text,
        re.IGNORECASE,
    )
    if not dir_match:
        return None

    direction = dir_match.group(1).upper()
    entry = float(dir_match.group(2))
    stop_loss = float(dir_match.group(3))

    # Take profits: ✔️ Tp1 🔽 4166
    tp_matches = re.findall(r"Tp\s*\d+\s*[🔽🔼🔻🔺]\s*([\d.]+)", full_text, re.IGNORECASE)
    if not tp_matches:
        # Try alternate without arrow
        tp_matches = re.findall(r"Tp\s*\d+\s+([\d.]+)", full_text, re.IGNORECASE)
    if not tp_matches:
        return None

    take_profits = [float(tp) for tp in tp_matches]

    return Signal(
        symbol="XAUUSD",
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        take_profits=take_profits,
        raw_text=text,
        source_channel=channel,
    )


PARSERS = {
    "format1": parse_format1,
    "format2": parse_format2,
}


def parse_signal(text: str, channel: str, fmt: str = "auto") -> Optional[Signal]:
    """
    Parse a signal message.

    If fmt is 'auto', try all parsers.
    If fmt is a known format name, use that parser only.
    """
    # Quick check: must mention XAUUSD or gold
    if "XAUUSD" not in text.upper() and "XAU" not in text.upper():
        return None

    if fmt != "auto" and fmt in PARSERS:
        result = PARSERS[fmt](text, channel)
        if result:
            return result

    # Auto: try all
    for parser_name, parser in PARSERS.items():
        result = parser(text, channel)
        if result:
            return result

    return None
