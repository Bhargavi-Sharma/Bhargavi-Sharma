"""Chat layer: Claude reads the full dossier and can call back into the engine for exact dates."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import anthropic

from . import dasha as D
from . import timing, transits
from .ashtakavarga import compute as av_compute
from .chart import Chart
from .dossier import serialise

MODEL = os.environ.get("JYOTISH_MODEL", "claude-opus-5-5")

SYSTEM_PROMPT = """You are a Jyotish (Vedic astrology) analyst. You read one person's chart from a complete, \
pre-computed DOSSIER produced by a deterministic engine (Swiss Ephemeris positions; rules from BPHS, Brihat Jataka, \
Phaladeepika, Saravali, Jataka Parijata, Jaimini Sutras; Lal Kitab kept separate). The dossier is the only source \
of chart facts. Never compute or guess planetary positions, dashas or transits yourself - read them from the \
dossier or call a tool.

HOW TO ANSWER EVERY QUESTION (always, in this order):
1. Identify the life area, its houses, their lords, the karaka(s) and the divisional chart (D9 marriage, D10 career, \
D7 children, D2 wealth, D4 property, D12 parents, D24 education, D20 spiritual).
2. Read ALL favourable and unfavourable factors for that area from the dossier: life_areas.<area>.promise, the \
planet_condition of the lord and karaka, functional_nature, shadbala, ashtakavarga, yogas (including their \
cancellations/weakenings) and doshas (including cancellations). Apply every exception the dossier lists \
(neecha bhanga, combustion, planetary war, retrogression, kendradhipati dosha, dusthana lordship, vargottama). \
Do not mention a yoga without its verdict (active / weakened / cancelled).
3. Timing: use vimshottari (MD/AD/PD) and life_areas.<area>.timing.windows. An event needs dasha AND double transit \
to be called 'high'. Use tools for exact pratyantar dates or for dates outside the precomputed range.
4. Conclude: a clear verdict, then dates as month-year windows with a confidence label (High / Medium / Low), \
then the 3-6 factors that decided it. End with a compact 'Factors checked' line listing what you examined, so \
the user can see nothing was skipped.

CONSISTENCY RULES:
- Weigh everything before you answer, so you never need to reverse yourself. If the factors conflict, say so up \
front and say which side wins and why (dignity and strength beat mere placement; varga confirmation beats a \
single D1 indication; a cancelled yoga does not count).
- If the user pushes back, re-check the dossier. Change your answer ONLY if (a) they point to a dossier factor you \
failed to weigh, or (b) they give new information (corrected birth time, an actual past event). Otherwise keep \
your answer and explain which factors outweigh their point. Never agree just to please.
- If a conclusion depends on a disputed point (see variants_in_use) or on a time-sensitive chart point (see \
birth_time_sensitivity), say so explicitly.

HONESTY RULES (the user asked for brutal honesty):
- State difficult results plainly: weak marriage promise, separation risk, career stagnation, debt, illness-prone \
periods, bad dashas. No softening, no 'everything happens for a reason'. Use direct words.
- Do not inflate good results either. If the promise is weak, say the event may not happen or may come late.
- Health: name the vulnerable periods (health_vigilance_periods, 6/8/12 dashas, Sade Sati, Ashtama Shani) and the \
body areas, and advise medical check-ups. Give the Jaimini longevity compartment if asked, with its reality_check. \
Do NOT give a date or year of death: the classical texts themselves call longevity the least reliable judgement \
(BPHS ch.44). Say this directly if asked, then give the vigilance windows instead.
- Past windows: when a predicted window is in the past, ask whether the event happened - this is how the \
birth time gets verified. Suggest rectification if past events do not match.
- Cite sources only at chapter level as given in the dossier. Do not invent verse numbers or Sanskrit quotations.
- Lal Kitab and Parashari often disagree; present Lal Kitab as a separate view and never merge them silently.

DESCRIPTIONS: for questions like "what will my spouse look like", "how many children / which order", "what \
career", "is my mind stable", use dossier.profiles (spouse indicators incl. marks/scars, children incl. \
pregnancy-obstacle indicators, career fields incl. govt job, mind stressors/stabilisers) together with D9/D7/D10. \
Give a concrete description (build, complexion, features, temperament, marks), say which indicators agree, and \
mark conflicting ones. Be specific - a vague answer is useless to this user - but never claim certainty the \
factors do not support.

PRECISION OF DATES: give month-year windows; narrow to weeks only via get_pratyantars plus transits, and say \
that day-level dates are beyond what the method supports.

REMEDIES: when asked, use remedies.gemstones (respect 'avoid' statuses, cautions and conflicts - finger and \
enemy-gem clashes), remedies.mantra_daan and remedies.lal_kitab. Never recommend a gem the dossier says to avoid.

STYLE: Reply in the user's language (Hindi, English or Hinglish - match them). Be concise and structured with \
headings and bullet points. Use Sanskrit terms with a short meaning in brackets the first time. The UI already \
shows a general disclaimer, so do not add one to each answer."""

TOOLS = [
    {"name": "get_dasha_at", "description": "Running Vimshottari mahadasha/antardasha/pratyantar on a date.",
     "input_schema": {"type": "object", "properties": {"date": {"type": "string", "description": "YYYY-MM-DD"}},
                      "required": ["date"], "additionalProperties": False}},
    {"name": "get_pratyantars", "description": "All pratyantardashas (with dates) inside one mahadasha/antardasha.",
     "input_schema": {"type": "object", "properties": {"mahadasha": {"type": "string"}, "antardasha": {"type": "string"},
                                                       "occurrence_year": {"type": "integer",
                                                                           "description": "any year inside that period"}},
                      "required": ["mahadasha", "antardasha", "occurrence_year"], "additionalProperties": False}},
    {"name": "get_transits", "description": "Transit positions on a date, judged from natal Moon with vedha, "
                                            "ashtakavarga bindus, Sade Sati status and double-transit houses.",
     "input_schema": {"type": "object", "properties": {"date": {"type": "string", "description": "YYYY-MM-DD"}},
                      "required": ["date"], "additionalProperties": False}},
    {"name": "find_event_windows", "description": "Ranked time windows for a life area between two years using "
                                                  "dasha significators + double transit + ashtakavarga.",
     "input_schema": {"type": "object", "properties": {
         "area": {"type": "string", "enum": list(timing.AREAS)},
         "from_year": {"type": "integer"}, "to_year": {"type": "integer"}},
         "required": ["area", "from_year", "to_year"], "additionalProperties": False}},
    {"name": "rectify_birth_time", "description": "Score candidate birth times (+/- minutes) against known past life "
                                                  "events. Use when the user gives dated events.",
     "input_schema": {"type": "object", "properties": {
         "events": {"type": "array", "items": {"type": "object", "properties": {
             "area": {"type": "string", "enum": list(timing.AREAS)}, "date": {"type": "string"}},
             "required": ["area", "date"], "additionalProperties": False}},
         "window_minutes": {"type": "integer"}},
         "required": ["events", "window_minutes"], "additionalProperties": False}},
]
for _t in TOOLS:
    _t["strict"] = True


def _utc(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str[:10]).replace(tzinfo=timezone.utc)


def run_tool(chart: Chart, name: str, args: dict) -> str:
    v = D.vimshottari(chart.lon["Moon"], chart.utc, chart.settings["dasha_year"])
    if name == "get_dasha_at":
        r = D.running(v, _utc(args["date"]))
        out = {k: {"lord": r[k]["lord"], "start": D.fmt(r[k]["start"]), "end": D.fmt(r[k]["end"])} for k in r}
    elif name == "get_pratyantars":
        out = []
        for md in v["mahadashas"]:
            if md["lord"] != args["mahadasha"]:
                continue
            for ad in D.antardashas(md):
                if ad["lord"] == args["antardasha"] and ad["start"].year <= args["occurrence_year"] <= ad["end"].year:
                    out = [{"pratyantar": p["lord"], "start": D.fmt(p["start"]), "end": D.fmt(p["end"])}
                           for p in D.pratyantars(md, ad)]
    elif name == "get_transits":
        out = transits.transit_report(chart, _utc(args["date"]), av_compute(chart.sign, chart.lagna))
    elif name == "find_event_windows":
        a = datetime(args["from_year"], 1, 1, tzinfo=timezone.utc)
        b = datetime(args["to_year"], 12, 31, tzinfo=timezone.utc)
        out = timing.event_windows(chart, args["area"], a, b, top=10)
    elif name == "rectify_birth_time":
        mins = max(5, min(int(args["window_minutes"]), 120))
        out = timing.rectify_by_events(lambda b: Chart(b, chart.settings), chart.birth, args["events"], mins)
    else:
        raise ValueError(f"unknown tool {name}")
    return json.dumps(out, default=serialise, ensure_ascii=False)


def _valid(block) -> bool:
    schema = next(t for t in TOOLS if t["name"] == block.name)["input_schema"]
    return isinstance(block.input, dict) and all(k in block.input for k in schema["required"])


def _echo_safe(content: list) -> list:
    """After a server-side fallback, drop model-internal blocks that precede the last fallback block."""
    idx = [i for i, b in enumerate(content) if getattr(b, "type", "") == "fallback"]
    if not idx:
        return content
    cut = idx[-1]
    drop = {"thinking", "redacted_thinking", "tool_use"}
    return [b for i, b in enumerate(content) if i > cut or b.type not in drop]


class Session:
    """One chat about one chart. History is append-only (thinking blocks stay valid)."""

    def __init__(self, chart: Chart, dossier: dict):
        self.chart = chart
        self.dossier_text = json.dumps(dossier, default=serialise, ensure_ascii=False, separators=(",", ":"))
        self.messages: list[dict] = []
        self.client = anthropic.Anthropic()

    def ask(self, text: str):
        """Yields ('text', chunk) / ('tool', name) / ('error', msg) events."""
        self.messages.append({"role": "user", "content": text})
        system = [
            {"type": "text", "text": SYSTEM_PROMPT},
            {"type": "text", "text": "DOSSIER (JSON):\n" + self.dossier_text,
             "cache_control": {"type": "ephemeral", "ttl": "1h"}},
        ]
        for _ in range(8):  # tool rounds
            with self.client.beta.messages.stream(
                model=MODEL, max_tokens=32000, system=system, messages=self.messages, tools=TOOLS,
                thinking={"type": "adaptive"}, output_config={"effort": "high"},
                betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            ) as stream:
                for event in stream:
                    if event.type == "content_block_delta" and event.delta.type == "text_delta":
                        yield "text", event.delta.text
                msg = stream.get_final_message()
            content = _echo_safe(msg.content)
            self.messages.append({"role": "assistant", "content": content})
            if msg.stop_reason == "refusal":
                yield "error", "The model declined this request."
                return
            if msg.stop_reason == "pause_turn":
                continue
            uses = [b for b in content if b.type == "tool_use"]
            if msg.stop_reason == "max_tokens" or not uses:
                return
            results = []
            for b in uses:
                yield "tool", b.name
                if not _valid(b):
                    results.append({"type": "tool_result", "tool_use_id": b.id, "is_error": True,
                                    "content": "invalid tool input"})
                    continue
                try:
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": run_tool(self.chart, b.name, b.input)})
                except Exception as e:  # report tool failures back to the model
                    results.append({"type": "tool_result", "tool_use_id": b.id, "is_error": True, "content": str(e)})
            self.messages.append({"role": "user", "content": results})
            yield "text", "\n\n"
