"""Single source of truth for timing, shared by picture (shots.py) and sound (audio.py).
All times in seconds. Music: 120 BPM from REVEAL (one bar = 2 s)."""

DURATION = 30.0
BPM = 120.0
BEAT = 60.0 / BPM

# ---- shots
S1 = (0.35, 2.40)     # typewriter macro
S2 = (2.40, 4.40)     # typewriter + note + stamp
S3 = (4.40, 6.25)     # waiting room + day counter
S4 = (6.25, 8.05)     # customs hall + reset
S5 = (8.05, 9.50)     # black: "Until now."
S6 = (9.50, 11.50)    # Mass reveal
S7 = (11.50, 13.50)   # founder: Karachi -> agent
S7_CUT = 12.30        # Karachi -> keyboard
S8 = (13.50, 15.50)   # Abu Dhabi: layers + keys
S9 = (15.50, 17.50)   # Suez: trade on one record
S10 = (17.50, 23.50)  # Earth network
S11 = (23.50, 25.50)  # montage
S12 = (25.50, 30.00)  # end card

REVEAL = S6[0]

# ---- Act I words (typewriter strikes), one clack per word
LINE1 = "Every economy runs on companies."
LINE1_T = [0.70, 0.92, 1.12, 1.30, 1.50]
LINE2 = "Yet every company still lives on paper."
LINE2_T = [2.56, 2.68, 2.80, 2.93, 3.03, 3.14, 3.26]
LINE3 = "Months to start one."
LINE3_T = [4.56, 4.76, 4.93, 5.10]
LINE4 = "Every border, back to zero."
LINE4_T = [6.42, 6.60, 6.76, 6.90, 7.02]
BELL = 1.78                     # carriage-return bell after line 1
PAPER_RUSTLE = 2.42
STAMP = 3.52                    # PENDING stamp impact
COUNTER = (4.52, 6.10)          # DAY 001 -> DAY 117 (accelerating)
COUNTER_MAX = 117
CHIME = 6.34                    # airport "ding-dong"
RESET = 7.22                    # counter glitch -> DAY 000
HEARTBEATS = (8.30, 8.72)
UNTIL_NOW = (8.34, 9.28)

# ---- Act II
MARK_STROKES = [9.50, 9.58, 9.66]
FLYTHROUGH = (11.18, 11.50)
AGENT_TYPE = (12.34, 12.60)
CHECKS = [12.66, 12.82, 12.98, 13.14]
LAYERS = [13.62, 13.78, 13.94, 14.10, 14.26, 14.42]
KEY_LOCK = 14.74
SHIP_HORN = 15.50
TAGS = [15.92, 16.16, 16.40]

# ---- Act III: nodes ignite when their corridor arrives from Abu Dhabi
HUB = ('ABU DHABI', 24.45, 54.38)
HUB_IGNITE = 17.72
NODES = [
    # name, lat, lon, ignite time, show label. One city per target corridor country in the
    # deck's network map; corridors are the roadmap, none is live yet.
    ('KARACHI', 24.86, 67.00, 18.30, True),            # Pakistan
    ('MUMBAI', 19.08, 72.88, 18.55, True),             # India
    ('RIYADH', 24.71, 46.68, 18.80, True),             # Saudi Arabia
    ('ISTANBUL', 41.01, 28.98, 19.05, True),           # Türkiye
    ('CAIRO', 30.04, 31.24, 19.30, True),              # Egypt
    ('DHAKA', 23.81, 90.41, 19.55, False),             # Bangladesh
    ('JAKARTA', -6.21, 106.85, 19.80, True),           # Indonesia
    ('HO CHI MINH CITY', 10.82, 106.63, 20.05, False),  # Vietnam
    ('LONDON', 51.51, -0.13, 20.30, True),             # United Kingdom
    ('KUALA LUMPUR', 3.14, 101.69, 20.55, False),      # Malaysia
    ('MANILA', 14.60, 120.98, 20.80, False),           # Philippines
    ('SHANGHAI', 31.23, 121.47, 21.05, False),         # China
    ('SEOUL', 37.57, 126.98, 21.30, True),             # Korea
]
ARC_TRAVEL = 0.42     # seconds for a corridor to draw from the hub to its node
MESH = [  # node-to-node corridors once the hub network is up (one accession links every member)
    ('LONDON', 'ISTANBUL', 21.45), ('ISTANBUL', 'CAIRO', 21.60), ('RIYADH', 'CAIRO', 21.75),
    ('DHAKA', 'JAKARTA', 21.90), ('JAKARTA', 'HO CHI MINH CITY', 22.05), ('MANILA', 'SEOUL', 22.20),
    ('SEOUL', 'SHANGHAI', 22.35), ('MUMBAI', 'DHAKA', 22.50), ('KUALA LUMPUR', 'MANILA', 22.65),
]
EARTH_TITLE1 = (18.40, 20.75)
EARTH_TITLE2 = (21.00, 23.40)
RISER = (21.60, 23.50)

# ---- montage and end
MONTAGE = [23.50, 24.00, 24.50, 25.00]
FINAL_HIT = 25.50
TAGLINE_IN = 26.30
URL_IN = 27.20
FADE_OUT = (29.15, 30.00)
