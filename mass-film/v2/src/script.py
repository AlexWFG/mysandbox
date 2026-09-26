"""The narration, one line per entry: (section, text). Single source for the scratch VO,
the edit timing, captions, and the final ElevenLabs take."""

VO = [
    ('open', "Every deal. Every job. Every shipment."),
    ('open', "It all begins with a company."),
    ('open', "And every company has to prove it exists. Again. And again."),
    ('aisha', "Karachi. Two a.m. Aisha built her product in a week."),
    ('aisha', "Making it official will take months:"),
    ('aisha', "the same checks, at every office, at every bank."),
    ('aisha', "And at the next border, she starts again."),
    ('omar', "In Abu Dhabi, Nadia approves new companies for a free zone."),
    ('omar', "Her systems don't talk to each other. So she retypes. Re-checks. And waits."),
    ('ministry', "At the ministry, the economy arrives in pieces."),
    ('ministry', "Dozens of systems. Every number, out of date."),
    ('peak', "Three people. One economy. Held back by systems that were never built to talk to each other."),
    ('turn', "What if a company only had to prove itself once?"),
    ('turn', "One living record. Created in minutes. Trusted everywhere."),
    ('reveal', "This is Mass."),
    ('demo', "Aisha tells her agent what she's building."),
    ('demo', "It prepares everything, and checks every rule before filing."),
    ('demo', "Nadia receives it complete. Nothing to retype. Nothing to chase. She simply decides."),
    ('demo', "Four minutes later, Aisha is in business."),
    ('demo', "The ministry sees it happen, live."),
    ('demo', "And when a rule changes, every company gets it the same day."),
    ('trust', "Every action is checked before it happens."),
    ('layers', "At the base: the registry. Run by the government, under its own keys."),
    ('layers', "On top, the economy builds: licences, banking, trade."),
    ('trade', "And with a record every bank can trust, trade finance flows from day one."),
    ('network', "Now imagine this across borders."),
    ('network', "When another nation joins, it recognises the record. No starting over."),
    ('network', "Each keeps its own laws, its own data, its own keys. Together: one economy."),
    ('close', "Formed. Licensed. Banked. Recognised."),
    ('close', "Mass. The operating system for sovereign economies."),
]

# Pause AFTER each line (seconds), tuned for picture and music; the edit breathes here.
PAUSE_AFTER = {
    ('open', 0): 0.3, ('open', 1): 0.4, ('open', 2): 1.0,
    ('aisha', 0): 0.4, ('aisha', 1): 0.1, ('aisha', 2): 0.35, ('aisha', 3): 0.9,
    ('omar', 0): 0.3, ('omar', 1): 0.9,
    ('ministry', 0): 0.3, ('ministry', 1): 0.8,
    ('peak', 0): 1.8,
    ('turn', 0): 0.7, ('turn', 1): 0.8,
    ('reveal', 0): 2.2,
    ('demo', 0): 2.2, ('demo', 1): 1.8, ('demo', 2): 1.4, ('demo', 3): 1.6, ('demo', 4): 0.5, ('demo', 5): 1.6,
    ('trust', 0): 0.35,
    ('layers', 0): 0.45, ('layers', 1): 0.55, ('trade', 0): 1.2,
    ('network', 0): 1.0, ('network', 1): 0.5, ('network', 2): 1.0,
    ('close', 0): 1.0, ('close', 1): 3.2,
}
LEAD_IN = 1.25  # music/picture before the first line

# Pace: gaps between lines tightened slightly (review note: "a tiny bit more speedy"). The demo keeps
# most of its breathing room so the UI stays readable; the end card keeps its full hold.
PACE = {'demo': 0.95, 'reveal': 0.9}
for _k in list(PAUSE_AFTER):
    if _k != ('close', 1):
        PAUSE_AFTER[_k] = round(PAUSE_AFTER[_k] * PACE.get(_k[0], 0.85), 3)


def full_text():
    """The whole narration as one take (for the one-shot TTS request)."""
    return ' '.join(t for _, t in VO)


def keyed():
    """[(key, text)] with key = (section, index within section)."""
    out, count = [], {}
    for sec, txt in VO:
        i = count.get(sec, 0)
        count[sec] = i + 1
        out.append(((sec, i), txt))
    return out
