# ==================================================================
#  EMOTION IN MOTION
#  Bronwyn Kitson  |  Creative Coding A2 Code Prototype  |  2026
#  Built in Processing (Python Mode)
#
#  THE BIG IDEA:   TEXT  ->  EMOTION  ->  VISUAL
#  1. The viewer types how they feel and presses ENTER.
#  2. The WORDS they use decide WHICH emotion (synonym lists).
#  3. HOW they write it (CAPS, !!!, "sooo", "really") decides the
#     INTENSITY: a number from 0.1 (barely) to 1.0 (MAXIMUM).
#  4. Each emotion has its own generative artwork, and the
#     intensity controls how big, fast and busy it gets.
#
#  CONTROLS
#     Type + ENTER ...... turn your feeling into art
#     ENTER (on art) .... go back and type a new feeling
#     Mouse click ....... poke the artwork
#     TAB ............... show/hide "how I read your words"
#     S ................. save a screenshot (screenshots folder)
#
#  NOTE: Processing's Python Mode runs Python 2.7 (Jython), so this
#  code avoids newer Python features like f-strings.
#
#  FILE MAP
#     1. Emotion data (synonyms, opposites, colours)
#     2. Text analysis (which emotion + how intense)
#     3. Shared helpers (particles, ripples, rainbow text, meter)
#     4. The artworks (one class per emotion)
#     5. Screens (home screen + artwork screen)
#     6. Processing events (setup, draw, keyboard, mouse)
# ==================================================================

import re


# ------------------------------------------------------------------
# 1. EMOTION DATA
# ------------------------------------------------------------------

# Every emotion has a list of words (synonyms) that trigger it.
# Multi-word phrases like "on edge" work too.
EMOTION_WORDS = {
    "happy": ["happy", "glad", "joyful", "joy", "cheerful", "good", "great",
              "delighted", "content", "stoked", "awesome", "amazing",
              "wonderful", "fantastic", "lovely", "grateful", "smiling",
              "over the moon", "on top of the world"],
    "sad": ["sad", "down", "upset", "unhappy", "blue", "miserable", "lonely",
            "heartbroken", "crying", "cry", "depressed", "gloomy", "low",
            "hurt", "teary", "devastated", "bummed", "flat"],
    "angry": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated",
              "fuming", "livid", "filthy", "rage", "raging", "cranky",
              "grumpy", "fed up", "heated", "seething"],
    "calm": ["calm", "relaxed", "chill", "chilled", "peaceful", "mellow",
             "zen", "fine", "okay", "ok", "at ease", "serene", "settled",
             "rested", "grounded", "tranquil", "cruisy"],
    "excited": ["excited", "pumped", "hyped", "hype", "thrilled", "buzzing",
                "ecstatic", "keen", "can't wait", "cant wait", "eager",
                "psyched", "amped", "elated"],
    "nervous": ["nervous", "anxious", "worried", "worry", "worries", "scared",
                "stressed", "uneasy", "on edge", "jittery", "tense",
                "overwhelmed", "panicking", "panicked", "afraid", "nervy",
                "freaking out", "butterflies"],
    "disgusted": ["disgusted", "disgusting", "gross", "grossed out", "ew",
                  "yuck", "yucky", "revolted", "repulsed", "sick",
                  "sickened", "nauseous", "icky", "vile"],
}

# If a feeling word is negated ("not happy"), we flip it to its opposite.
OPPOSITES = {
    "happy": "sad",
    "sad": "happy",
    "angry": "calm",
    "calm": "nervous",
    "excited": "calm",
    "nervous": "calm",      # "no worries" -> calm!
    "disgusted": "calm",
}

# Words that cancel out a feeling word that comes just after them.
NEGATORS = ["not", "never", "no", "isn't", "isnt", "aren't", "arent",
            "don't", "dont", "didn't", "didnt", "hardly", "wasn't", "wasnt"]

# Words that turn the volume UP...
INTENSIFIERS = ["very", "really", "so", "extremely", "super", "totally",
                "absolutely", "incredibly", "completely", "literally",
                "seriously", "insanely", "beyond", "hella"]

# ...and words that turn it DOWN.
SOFTENERS = ["bit", "kinda", "slightly", "little", "somewhat", "sorta",
             "mildly", "fairly"]

# Each emotion's signature hue (0-360 around the colour wheel). Used for
# the intensity meter on the artwork screen.
ACCENT_HUE = {
    "happy": 45, "sad": 210, "angry": 5, "calm": 160, "excited": 290,
    "nervous": 270, "disgusted": 90, "mystery": 0,
}


# ------------------------------------------------------------------
# 2. TEXT ANALYSIS
# ------------------------------------------------------------------

def clean_words(text):
    """Turns the raw sentence into a list of simple lowercase words.
    "I'm SO HAPPY!!!"  ->  ["i'm", "so", "happy"]"""
    text = text.lower().replace(u"\u2019", "'")  # curly apostrophe -> straight
    text = re.sub(r"[^a-z' ]", " ", text)        # anything not a letter, ' or space -> space
    return text.split()


def squash(word, keep):
    """Shrinks any letter repeated 3+ times down to `keep` copies.
    squash("happyyyy", 1) -> "happy"     squash("gooood", 2) -> "good" """
    return re.sub(r"(.)\1{2,}", r"\1" * keep, word)


def word_variants(word):
    """All the spellings we accept for one typed word. Trying both
    squash levels means "happyyyy" AND "gooood" are both recognised."""
    return [word, squash(word, 1), squash(word, 2)]


def matches_at(words, i, phrase_words):
    """True if a phrase (e.g. ["on", "edge"]) starts at position i."""
    if i + len(phrase_words) > len(words):
        return False
    for j in range(len(phrase_words)):
        if phrase_words[j] not in word_variants(words[i + j]):
            return False
    return True


def is_negated(words, i):
    """Looks up to two words back for a negator, so both "not happy"
    and "don't feel happy" count as negated."""
    for back in (1, 2):
        if i - back >= 0 and words[i - back] in NEGATORS:
            return True
    return False


def detect_emotion(text):
    """Works out WHICH emotion the sentence is about.
    Returns an emotion name, or "mystery" if no feeling words are found."""
    words = clean_words(text)
    scores = {}      # emotion -> how many times it was mentioned
    last_seen = {}   # emotion -> position of its latest mention

    for emotion_name in EMOTION_WORDS:
        for phrase in EMOTION_WORDS[emotion_name]:
            phrase_words = phrase.split()
            for i in range(len(words)):
                if matches_at(words, i, phrase_words):
                    found = emotion_name
                    if is_negated(words, i):
                        found = OPPOSITES[emotion_name]  # "not happy" counts as sad
                    scores[found] = scores.get(found, 0) + 1
                    last_seen[found] = max(last_seen.get(found, -1), i)

    if len(scores) == 0:
        return "mystery"

    # The most-mentioned emotion wins. In a tie, the one mentioned LAST
    # wins, because "I was sad but now I'm happy" should show happy.
    best = None
    for emotion_name in scores:
        if best is None or (scores[emotion_name], last_seen[emotion_name]) > (scores[best], last_seen[best]):
            best = emotion_name
    return best


def analyse_intensity(text):
    """Works out HOW STRONGLY the feeling is written.
    Returns (intensity, details) where intensity runs 0.1 -> 1.0 and
    details records what was found (shown in the TAB panel)."""
    letters = [c for c in text if c.isalpha()]

    # a) CAPITALS: what fraction of letters are capitals? Normal sentence
    #    capitals (under 20%) are ignored so "I feel happy" isn't shouting.
    caps = 0.0
    if len(letters) >= 3:
        capitals = len([c for c in letters if c.isupper()])
        caps = float(capitals) / len(letters)
    caps_score = max(0.0, (caps - 0.2) / 0.8)

    # b) EXCLAMATION MARKS: up to 5 count (more is still the maximum)
    exclaims = text.count("!")

    # c) STRETCHED WORDS: 3+ of the same letter in a row ("sooo", "nooo")
    stretched = re.search(r"([a-zA-Z])\1\1", text) is not None

    # d) BOOSTER words ("really", "so") and SOFTENER words ("a bit", "kinda")
    words = clean_words(text)
    boosters = 0
    for w in words:
        for v in word_variants(w):
            if v in INTENSIFIERS:
                boosters += 1
                break
    softened = len([w for w in words if w in SOFTENERS]) > 0

    # Add it all up, starting from a calm-ish baseline of 0.25
    value = 0.25
    value += caps_score * 0.35
    value += min(exclaims, 5) / 5.0 * 0.30
    if stretched:
        value += 0.15
    value += min(boosters, 3) / 3.0 * 0.20
    if softened:
        value -= 0.20
    value = constrain(value, 0.1, 1.0)

    details = {"caps": caps, "exclaims": exclaims, "stretched": stretched,
               "boosters": boosters, "softened": softened}
    return value, details


# ------------------------------------------------------------------
# 3. SHARED HELPERS
# ------------------------------------------------------------------

def pick(options):
    """Returns a random item from a list."""
    return options[int(random(len(options)))]


def random_edge_point():
    """A random point just outside one of the four window edges."""
    side = int(random(4))
    if side == 0:
        return random(width), -20
    if side == 1:
        return width + 20, random(height)
    if side == 2:
        return random(width), height + 20
    return -20, random(height)


class Particle(object):
    """A small spark that flies, slows down, falls and fades away.
    Re-used by several artworks: bubble pops, angry sparks, fireworks
    and slime splashes."""

    def __init__(self, x, y, vx, vy, hue, sat, bri, size, gravity, drag, fade):
        self.x = x
        self.y = y
        self.vx = vx            # speed sideways
        self.vy = vy            # speed up/down
        self.hue = hue
        self.sat = sat
        self.bri = bri
        self.size = size
        self.gravity = gravity  # how much it gets pulled down each frame
        self.drag = drag        # air resistance (0.97 = loses 3% speed per frame)
        self.fade = fade        # how fast it disappears
        self.life = 100.0       # doubles as its transparency

    def update(self):
        self.vy += self.gravity
        self.vx *= self.drag
        self.vy *= self.drag
        self.x += self.vx
        self.y += self.vy
        self.life -= self.fade

    def display(self):
        stroke(self.hue % 360, self.sat, self.bri, self.life)
        strokeWeight(self.size)
        # A short line pointing backwards along its path = a motion streak
        line(self.x, self.y, self.x - self.vx * 2, self.y - self.vy * 2)

    def is_dead(self):
        return self.life <= 0


def burst(x, y, count, hues, min_speed, max_speed, size=3, gravity=0.0,
          drag=0.96, fade=2.5, sat=80, bri=100):
    """Makes `count` particles flying outward from (x, y) in all directions."""
    parts = []
    for i in range(count):
        angle = random(TWO_PI)
        speed = random(min_speed, max_speed)
        parts.append(Particle(x, y, cos(angle) * speed, sin(angle) * speed,
                              pick(hues) + random(-10, 10), sat, bri,
                              size, gravity, drag, fade))
    return parts


class Ripple(object):
    """An expanding ring that fades out. `flat` squashes it into an oval
    so it looks like it's lying on the ground (1.0 = a perfect circle)."""

    def __init__(self, x, y, hue, sat, bri, grow, flat, alpha=70, fade=1.8):
        self.x = x
        self.y = y
        self.hue = hue
        self.sat = sat
        self.bri = bri
        self.grow = grow
        self.flat = flat
        self.alpha = alpha
        self.fade = fade
        self.r = 1.0

    def update(self):
        self.r += self.grow
        self.alpha -= self.fade

    def display(self):
        noFill()
        stroke(self.hue, self.sat, self.bri, self.alpha)
        strokeWeight(1.5)
        ellipse(self.x, self.y, self.r * 2, self.r * 2 * self.flat)

    def is_dead(self):
        return self.alpha <= 0


def text_width_sum(txt):
    """Width of a line of text, measured letter by letter (the same way
    the rainbow text is drawn, so centring lines up exactly)."""
    total = 0
    for c in txt:
        total += textWidth(c)
    return total


def fitted_size(txt, max_size, max_width):
    """The biggest text size (up to max_size) that keeps txt narrower
    than max_width, so long sentences shrink instead of running off-screen."""
    textSize(max_size)
    w = text_width_sum(txt)
    if w > max_width:
        return max_size * max_width / w
    return max_size


def draw_rainbow_text(txt, cx, cy, max_size, sat, bri, born=None, max_width=None):
    """Draws txt centred at (cx, cy) with every letter a different colour.
    The colours slide along over time, so the words shimmer, and each
    letter bobs on a gentle wave. `born` (optional) lists the frame each
    letter was typed, so brand-new letters 'pop' in.
    Returns (x where the line ends, text size used)."""
    if max_width is None:
        max_width = width * 0.85
    txt_size = fitted_size(txt, max_size, max_width)
    textSize(txt_size)
    textAlign(CENTER, CENTER)

    x = cx - text_width_sum(txt) / 2.0   # left edge, so the line is centred
    for i in range(len(txt)):
        letter = txt[i]
        w = textWidth(letter)

        # Hue: each letter is 24 degrees further round the colour wheel,
        # and the whole rainbow slides 2 degrees every frame.
        hue = (i * 24 + frameCount * 2) % 360

        # Bob: a sine wave, offset per letter, so the line ripples
        bob = sin(frameCount * 0.08 + i * 0.45) * txt_size * 0.06

        # Pop: new letters grow from nothing, overshoot slightly, then settle
        pop = 1.0
        if born is not None and i < len(born):
            age = frameCount - born[i]
            if age < 10:
                t = age / 10.0
                pop = max(0.01, t + sin(t * PI) * 0.5)

        pushMatrix()
        translate(x + w / 2.0, cy + bob)
        scale(pop)
        fill(hue, sat, bri)
        text(letter, 0, 0)
        popMatrix()
        x += w
    return x, txt_size


def draw_meter(x, y, level, hue, sat, bri):
    """A row of 10 little bars showing intensity (like a volume meter)."""
    filled = int(round(level * 10))
    noStroke()
    for i in range(10):
        if i < filled:
            fill(hue, sat, bri, 90)
        else:
            fill(hue, sat, bri, 18)
        rect(x + i * 15, y, 12, 8, 3)


class AmbientDot(object):
    """Soft grey dots drifting on the home screen so it never feels static.
    Perlin noise gives smooth, wandering movement instead of random jumps."""

    def __init__(self):
        self.seed = random(1000)
        self.size = random(6, 60)
        self.alpha = random(5, 14)

    def display(self):
        t = frameCount * 0.0015
        x = noise(self.seed, t) * width * 1.4 - width * 0.2
        y = noise(self.seed + 40, t) * height * 1.4 - height * 0.2
        noStroke()
        fill(0, 0, 55, self.alpha)
        ellipse(x, y, self.size, self.size)


# ------------------------------------------------------------------
# 4. THE ARTWORKS
#  Every artwork class has the same three parts, so the main program
#  can treat them all the same way:
#    __init__(intensity)  set up, using intensity to decide how much/how fast
#    run()                update + draw one frame
#    poke(x, y)           react to a mouse click
#  Each also has self.ink: the brightness of overlay text (light text on
#  dark artworks, dark text on light ones).
# ------------------------------------------------------------------

# ---------- HAPPY: warm bubbles that float up and pop -------------

class Bubble(object):
    """One bubble that floats up, wobbles side to side and eventually pops."""
    HUES = [45, 52, 335, 345, 20, 30]   # sunny yellows, bubblegum pinks, peach

    def __init__(self, x, y, intensity):
        self.x = x
        self.y = y
        self.r = random(8, 20) + intensity * random(5, 25)
        self.speed = random(0.6, 1.4) * (1 + intensity * 2.5)
        self.wobble = random(TWO_PI)
        self.hue = pick(Bubble.HUES)
        self.pop_height = random(-60, height * 0.5)   # where it will pop
        self.popped = False

    def update(self):
        self.y -= self.speed
        self.wobble += 0.05
        self.x += sin(self.wobble) * 0.8   # sine wave = side-to-side sway
        self.r += 0.02                     # bubbles grow a little as they rise
        if self.y < self.pop_height:
            self.popped = True

    def display(self):
        d = self.r * 2
        noStroke()
        fill(self.hue, 35, 100, 30)                 # see-through body
        ellipse(self.x, self.y, d, d)
        noFill()
        stroke(self.hue, 65, 95, 85)                # coloured rim
        strokeWeight(2)
        ellipse(self.x, self.y, d, d)
        stroke(0, 0, 100, 90)                       # white shine, top-left
        strokeWeight(max(2, self.r * 0.12))
        arc(self.x, self.y, d * 0.7, d * 0.7, PI + 0.4, PI + HALF_PI - 0.1)


class HappyArt(object):
    def __init__(self, intensity):
        self.intensity = intensity
        self.ink = 20
        self.max_bubbles = int(25 + intensity * 90)
        self.bubbles = []
        self.sparkles = []
        # Start with some bubbles already on screen so it isn't empty
        for i in range(self.max_bubbles // 2):
            self.bubbles.append(Bubble(random(width), random(height * 0.3, height + 40), intensity))

    def run(self):
        background(45, 10, 100)   # warm cream

        # A soft sun glow that pulses (pulses harder when happier)
        noStroke()
        pulse = 1 + sin(frameCount * 0.04) * 0.06 * (1 + self.intensity)
        for ring in range(6, 0, -1):
            fill(48, 45, 100, 7)
            d = ring * 110 * pulse
            ellipse(width / 2.0, height * 0.42, d, d)

        # Keep topping up bubbles from below the screen
        if len(self.bubbles) < self.max_bubbles and random(1) < 0.5 + self.intensity * 0.5:
            self.bubbles.append(Bubble(random(width), height + 40, self.intensity))

        for b in self.bubbles:
            b.update()
            b.display()
            if b.popped:
                self.pop(b)
        self.bubbles = [b for b in self.bubbles if not b.popped]

        for p in self.sparkles:
            p.update()
            p.display()
        self.sparkles = [p for p in self.sparkles if not p.is_dead()]

    def pop(self, b):
        """Turns a bubble into a little burst of sparkles."""
        self.sparkles += burst(b.x, b.y, int(6 + self.intensity * 10), [b.hue],
                               1.5, 4.5, size=3, gravity=0.05, fade=4, sat=70, bri=95)

    def poke(self, x, y):
        for i in range(8):
            self.bubbles.append(Bubble(x + random(-30, 30), y + random(-30, 30), self.intensity))


# ---------- SAD: blue rain with ripples ----------------------------

class RainDrop(object):
    def __init__(self, intensity, anywhere):
        self.intensity = intensity
        self.reset(anywhere)

    def reset(self, anywhere):
        """Sends the drop back to the top (or anywhere, at the start)."""
        self.x = random(-150, width + 50)
        # 'ground' is where this drop will land. Lower on screen = closer to us.
        self.ground = random(height * 0.55, height)
        if anywhere:
            self.y = random(-height, self.ground)
        else:
            self.y = random(-200, -20)
        self.speed = random(7, 11) * (0.6 + self.intensity * 1.1)
        self.length = random(10, 22) * (0.6 + self.intensity * 1.2)
        self.landed = False

    def update(self, wind):
        self.y += self.speed
        self.x += wind
        if self.y > self.ground:
            self.landed = True

    def display(self, wind):
        stroke(212, 35, 85, 55)
        strokeWeight(1.3)
        # The streak points back along its direction of travel (wind slant)
        line(self.x, self.y, self.x - wind * self.length / self.speed, self.y - self.length)


class SadArt(object):
    def __init__(self, intensity):
        self.intensity = intensity
        self.ink = 95
        self.wind = intensity * 3.0     # heavier sadness = more sideways rain
        self.drops = [RainDrop(intensity, True) for i in range(int(80 + intensity * 320))]
        self.ripples = []
        self.clouds = [[random(width), random(-40, 90), random(250, 500)] for i in range(7)]
        self.first_frame = True

    def run(self):
        if self.first_frame:
            background(222, 55, 16)
            self.first_frame = False
        # Instead of clearing the screen, paint a see-through layer over it.
        # Old frames fade slowly, leaving soft motion trails.
        noStroke()
        fill(222, 55, 16, 35)
        rect(0, 0, width, height)

        # Heavy clouds drifting across the top
        for c in self.clouds:
            c[0] += 0.2 + self.intensity * 0.6
            if c[0] - c[2] / 2 > width:
                c[0] = -c[2] / 2
            fill(225, 25, 32, 12)
            ellipse(c[0], c[1], c[2], c[2] * 0.45)

        for drop in self.drops:
            drop.update(self.wind)
            drop.display(self.wind)
            if drop.landed:
                # Drops landing lower down are 'closer', so their ripples are
                # bigger. This fakes a 3D ground with flat 2D ovals.
                depth = (drop.ground - height * 0.55) / (height * 0.45)
                self.ripples.append(Ripple(drop.x, drop.ground, 205, 25, 90,
                                           0.4 + depth * 1.2, 0.3, 60))
                drop.reset(False)

        for r in self.ripples:
            r.update()
            r.display()
        self.ripples = [r for r in self.ripples if not r.is_dead()][-400:]

    def poke(self, x, y):
        for i in range(4):
            self.ripples.append(Ripple(x, y, 200, 30, 100, 1.0 + i * 0.8, 0.35, 80))


# ---------- ANGRY: spiky pulsing core, lightning, sparks, shake ----

class Bolt(object):
    """A jagged lightning bolt from (x1, y1) to (x2, y2) that flashes and fades."""

    def __init__(self, x1, y1, x2, y2, intensity):
        self.points = []
        steps = 12
        for i in range(steps + 1):
            t = i / float(steps)
            x = lerp(x1, x2, t)          # a point along the straight line...
            y = lerp(y1, y2, t)
            if 0 < i < steps:            # ...pushed off course (except the ends)
                jitter = 40 * (1 + intensity)
                x += random(-jitter, jitter)
                y += random(-jitter, jitter)
            self.points.append((x, y))
        self.life = 100.0
        self.hue = random(0, 35)

    def update(self):
        self.life -= 12

    def display(self):
        noFill()
        # Drawn twice: thick + faint for a glow, then thin + bright for the core
        for weight, sat, strength in ((10, 80, 0.15), (3, 30, 1.0)):
            stroke(self.hue, sat, 100, self.life * strength)
            strokeWeight(weight)
            beginShape()
            for p in self.points:
                vertex(p[0], p[1])
            endShape()

    def is_dead(self):
        return self.life <= 0


class AngryArt(object):
    def __init__(self, intensity):
        self.intensity = intensity
        self.ink = 95
        self.bolts = []
        self.sparks = []
        self.first_frame = True

    def run(self):
        if self.first_frame:
            background(0, 85, 8)
            self.first_frame = False
        noStroke()
        fill(0, 85, 8, 30)            # see-through layer = fading trails
        rect(0, 0, width, height)

        # SCREEN SHAKE: shift the whole drawing by a random amount each frame
        shake = self.intensity * 14
        pushMatrix()
        translate(random(-shake, shake), random(-shake, shake))

        cx = width / 2.0
        cy = height / 2.0

        # A heartbeat-like pulse that beats faster when angrier
        beat = abs(sin(frameCount * (0.05 + self.intensity * 0.08)))
        for layer in range(3):        # dark red outside -> yellow-hot centre
            radius = (180 - layer * 55) * (0.8 + beat * 0.4) * (0.7 + self.intensity * 0.5)
            self.draw_spiky_ring(cx, cy, radius, layer)

        # A new lightning bolt every few frames (more often when angrier)
        every = max(3, int(14 - self.intensity * 10))
        if frameCount % every == 0:
            ex, ey = random_edge_point()
            self.bolts.append(Bolt(ex, ey, cx + random(-60, 60), cy + random(-60, 60), self.intensity))
        for b in self.bolts:
            b.update()
            b.display()
        self.bolts = [b for b in self.bolts if not b.is_dead()]

        # Sparks spraying out of the core
        for i in range(int(2 + self.intensity * 8)):
            a = random(TWO_PI)
            s = random(2, 6 + self.intensity * 6)
            self.sparks.append(Particle(cx, cy, cos(a) * s, sin(a) * s, random(5, 45),
                                        90, 100, random(2, 4), 0.12, 0.97, 2.2))
        for p in self.sparks:
            p.update()
            p.display()
        self.sparks = [p for p in self.sparks if not p.is_dead()][-600:]

        popMatrix()

    def draw_spiky_ring(self, cx, cy, radius, layer):
        """A jagged star shape. Every other point sticks out, and noise +
        randomness make the spikes flicker."""
        hues = [0, 15, 40]
        sats = [90, 90, 70]
        noStroke()
        fill(hues[layer], sats[layer], 100, 50 if layer == 0 else 70)
        beginShape()
        points = 36
        for i in range(points):
            angle = TWO_PI * i / points
            spike = radius * 0.35 if i % 2 == 0 else 0
            n = noise(i * 0.4, layer * 5, frameCount * 0.06)
            r = radius + spike * n * (1 + self.intensity) + random(-3, 3) * self.intensity * 3
            vertex(cx + cos(angle) * r, cy + sin(angle) * r)
        endShape(CLOSE)

    def poke(self, x, y):
        self.bolts.append(Bolt(x, y, width / 2.0, height / 2.0, self.intensity))
        self.sparks += burst(x, y, 30, [10, 30], 2, 8, size=3, gravity=0.15, fade=3)


# ---------- CALM: slow Perlin-noise waves + a breathing circle -----

class CalmArt(object):
    def __init__(self, intensity):
        self.intensity = intensity
        self.ink = 25
        self.layers = 6
        self.speed = 0.002 + intensity * 0.004
        self.amp = 90 + intensity * 90          # wave height
        # [x, y, size, rising speed] for little floating light specks
        self.motes = [[random(width), random(height), random(1.5, 4), random(0.1, 0.4)] for i in range(40)]
        self.ripples = []

    def run(self):
        background(262, 10, 98)                 # very pale lavender
        self.draw_breathing_circle()

        t = frameCount * self.speed
        noStroke()
        for layer in range(self.layers):
            mix = layer / float(self.layers - 1)    # 0 = back layer, 1 = front layer
            hue = lerp(265, 155, mix)               # lavender at the back -> soft green at the front
            fill(hue, 18 + mix * 25, 96 - mix * 22, 75)
            base_y = height * 0.45 + layer * height * 0.09
            beginShape()
            vertex(0, height)
            x = 0
            while x <= width + 10:
                # Perlin noise gives smooth hills instead of random spikes.
                # Moving through 'time' (t) makes the hills roll.
                n = noise(x * 0.0022, layer * 7.3, t + layer * 0.2)
                vertex(x, base_y + (n - 0.5) * self.amp)
                x += 10
            vertex(width, height)
            endShape(CLOSE)

        for m in self.motes:
            m[1] -= m[3]
            if m[1] < -10:
                m[1] = height + 10
            fill(0, 0, 100, 70)
            ellipse(m[0], m[1], m[2], m[2])

        for r in self.ripples:
            r.update()
            r.display()
        self.ripples = [r for r in self.ripples if not r.is_dead()]

    def draw_breathing_circle(self):
        # One full breath every 5 seconds (300 frames at 60fps)
        angle = frameCount * TWO_PI / 300.0 - HALF_PI
        breath = (sin(angle) + 1) / 2.0             # 0 = breathed out, 1 = breathed in
        r = 50 + breath * (50 + self.intensity * 50)
        cx = width / 2.0
        cy = height * 0.3
        noStroke()
        for i in range(5, 0, -1):                   # soft glow
            fill(40, 25, 100, 10)
            ellipse(cx, cy, r * 2 + i * 30, r * 2 + i * 30)
        fill(40, 15, 100, 80)
        ellipse(cx, cy, r * 2, r * 2)
        # cos(angle) > 0 means the circle is currently growing
        word = "breathe in" if cos(angle) > 0 else "breathe out"
        textFont(font_regular)
        textAlign(CENTER, CENTER)
        textSize(14)
        fill(260, 20, 50, 70)
        text(word, cx, cy)

    def poke(self, x, y):
        for i in range(3):
            self.ripples.append(Ripple(x, y, 250, 30, 70, 0.8 + i * 0.6, 1.0, 50, 0.8))


# ---------- EXCITED: fireworks -------------------------------------

class Rocket(object):
    def __init__(self, x, intensity):
        self.x = x
        self.y = height + 10
        self.vx = random(-1.5, 1.5)
        self.vy = -random(8.5, 11.5) * (0.95 + intensity * 0.1)
        self.hue = random(360)
        self.exploded = False

    def update(self):
        self.vy += 0.15                  # gravity slows it down...
        self.x += self.vx
        self.y += self.vy
        if self.vy > -1.5:               # ...and near the top of its flight, BOOM
            self.exploded = True

    def display(self):
        stroke(self.hue, 40, 100)
        strokeWeight(3)
        line(self.x, self.y, self.x - self.vx * 3, self.y - self.vy * 3)


class ExcitedArt(object):
    def __init__(self, intensity):
        self.intensity = intensity
        self.ink = 95
        self.rockets = []
        self.particles = []
        self.flashes = []
        # [x, y, size, twinkle offset] for background stars
        self.stars = [[random(width), random(height * 0.7), random(1, 2.5), random(TWO_PI)] for i in range(90)]
        self.first_frame = True

    def run(self):
        if self.first_frame:
            background(255, 60, 10)
            self.first_frame = False
        noStroke()
        fill(255, 60, 10, 22)            # fading trails make sparks look like streaks
        rect(0, 0, width, height)

        for s in self.stars:             # twinkling stars
            fill(55, 10, 100, 40 + 40 * sin(frameCount * 0.05 + s[3]))
            ellipse(s[0], s[1], s[2], s[2])

        # Launch new rockets: the more excited, the more often
        if random(1) < 0.02 + self.intensity * 0.08:
            self.rockets.append(Rocket(random(width * 0.1, width * 0.9), self.intensity))

        for r in self.rockets:
            r.update()
            r.display()
            # a little gold glitter trail behind each rocket
            self.particles.append(Particle(r.x, r.y, random(-0.5, 0.5), random(0, 1), 45,
                                           60, 100, 2, 0.02, 0.95, 5))
            if r.exploded:
                self.explode(r.x, r.y, r.hue)
        self.rockets = [r for r in self.rockets if not r.exploded]

        for f in self.flashes:           # quick glow at each explosion
            fill(f[3], 30, 100, f[2])
            ellipse(f[0], f[1], 220, 220)
            f[2] -= 6
        self.flashes = [f for f in self.flashes if f[2] > 0]

        for p in self.particles:
            p.update()
            p.display()
        self.particles = [p for p in self.particles if not p.is_dead()][-1500:]

    def explode(self, x, y, hue):
        count = int(50 + self.intensity * 80)
        hues = [hue]
        if self.intensity > 0.5:         # big excitement = two-colour bursts
            hues = [hue, (hue + 150) % 360]
        self.particles += burst(x, y, count, hues, 0.5, 4.5 + self.intensity * 3,
                                size=3, gravity=0.05, drag=0.975, fade=random(1.2, 1.8))
        self.flashes.append([x, y, 25, hue])

    def poke(self, x, y):
        self.explode(x, y, random(360))


# ---------- NERVOUS: butterflies in your stomach -------------------

class Butterfly(object):
    def __init__(self, x, y, intensity):
        self.x = x
        self.y = y
        self.vx = random(-1, 1)
        self.vy = random(-1, 1)
        self.size = random(9, 17)
        self.hue = random(255, 300)
        self.flap = random(TWO_PI)
        self.flap_speed = random(0.25, 0.4) + intensity * 0.5
        self.jitter = 0.4 + intensity * 2.0          # how twitchy it is
        self.max_speed = 2 + intensity * 4
        self.dart_chance = 0.005 + intensity * 0.03  # chance of a sudden dart

    def update(self, cx, cy):
        # 1. Nervous twitching: a small random nudge every frame
        self.vx += random(-self.jitter, self.jitter)
        self.vy += random(-self.jitter, self.jitter)

        # 2. A gentle pull back toward the 'stomach' so they stay clustered
        self.vx += (cx - self.x) * 0.0012
        self.vy += (cy - self.y) * 0.0012

        # 3. Every now and then, a sudden panicked dart
        if random(1) < self.dart_chance:
            a = random(TWO_PI)
            self.vx += cos(a) * 7
            self.vy += sin(a) * 7

        # 4. Flee from the mouse
        d = dist(self.x, self.y, mouseX, mouseY)
        if 0 < d < 110:
            push = (110 - d) / 110.0 * 1.5
            self.vx += (self.x - mouseX) / d * push
            self.vy += (self.y - mouseY) / d * push

        # 5. Friction and a speed limit
        self.vx *= 0.93
        self.vy *= 0.93
        speed = sqrt(self.vx * self.vx + self.vy * self.vy)
        limit = self.max_speed * 2
        if speed > limit:
            self.vx = self.vx / speed * limit
            self.vy = self.vy / speed * limit

        self.x += self.vx
        self.y += self.vy

    def display(self):
        self.flap += self.flap_speed
        open_amount = abs(sin(self.flap))     # 0 = wings shut, 1 = wide open
        pushMatrix()
        translate(self.x, self.y)
        rotate(atan2(self.vy, self.vx) + HALF_PI)   # face the way it's flying
        s = self.size
        noStroke()
        fill(self.hue, 35, 95, 80)                  # upper wings
        ellipse(-s * 0.5 * open_amount, -s * 0.15, s * open_amount, s * 1.1)
        ellipse(s * 0.5 * open_amount, -s * 0.15, s * open_amount, s * 1.1)
        fill((self.hue + 20) % 360, 40, 92, 80)     # lower wings
        ellipse(-s * 0.35 * open_amount, s * 0.4, s * 0.7 * open_amount, s * 0.7)
        ellipse(s * 0.35 * open_amount, s * 0.4, s * 0.7 * open_amount, s * 0.7)
        fill(self.hue, 45, 35)                      # body
        ellipse(0, s * 0.1, s * 0.18, s * 0.95)
        popMatrix()


class NervousArt(object):
    def __init__(self, intensity):
        self.intensity = intensity
        self.ink = 25
        self.butterflies = [Butterfly(width / 2.0 + random(-200, 200),
                                      height / 2.0 + random(-150, 150), intensity)
                            for i in range(int(14 + intensity * 46))]
        self.seed = random(1000)
        self.first_frame = True

    def run(self):
        if self.first_frame:
            background(268, 7, 97)
            self.first_frame = False
        noStroke()
        fill(268, 7, 97, 45)
        rect(0, 0, width, height)

        # The 'stomach' slowly wanders around and the butterflies follow it
        cx = width / 2.0 + (noise(self.seed, frameCount * 0.004) - 0.5) * width * 0.5
        cy = height / 2.0 + (noise(self.seed + 99, frameCount * 0.004) - 0.5) * height * 0.4
        self.draw_tension_rings(cx, cy)

        for b in self.butterflies:
            b.update(cx, cy)
            b.display()

    def draw_tension_rings(self, cx, cy):
        """Faint trembling circles around the stomach. They shake more
        at higher intensity."""
        noFill()
        strokeWeight(1)
        tremble = 1 + self.intensity * 6
        for i in range(1, 6):
            stroke(270, 25, 70, 22)
            beginShape()
            for k in range(41):
                a = TWO_PI * k / 40
                r = i * 45 + random(-tremble, tremble)
                vertex(cx + cos(a) * r, cy + sin(a) * r)
            endShape()

    def poke(self, x, y):
        """Startle! Butterflies near the click scatter."""
        for b in self.butterflies:
            d = dist(b.x, b.y, x, y)
            if 0 < d < 250:
                b.vx += (b.x - x) / d * 12
                b.vy += (b.y - y) / d * 12


# ---------- DISGUSTED: oozing, wobbling, dripping slime ------------

SLIME_HUE = 92


class Drip(object):
    """A slime drip. It stretches down from where it's stuck, then lets go,
    falls, and splats into the puddle at the bottom."""

    def __init__(self, x, top, intensity, falling=False, hue=SLIME_HUE):
        self.x = x
        self.top = top
        self.length = 0.0
        self.max_length = random(30, 110)
        self.grow = random(0.25, 0.7) * (1 + intensity * 1.5)
        self.r = random(5, 9) * (1 + intensity * 0.4)
        self.hue = hue
        self.falling = falling
        self.y = top
        self.vy = 0.5
        self.splatted = False

    def update(self, new_top, floor_y):
        if not self.falling:
            self.top = new_top          # stays stuck to the wobbling goo
            self.length += self.grow
            if self.length > self.max_length:
                self.falling = True     # too heavy: let go!
                self.y = self.top + self.length
        else:
            self.vy += 0.3
            self.y += self.vy
            if self.y > floor_y:
                self.splatted = True

    def display(self):
        noStroke()
        fill(self.hue, 65, 52)
        if not self.falling:
            bottom = self.top + self.length
            # A tapering neck (wide at the top, thin at the bottom) + a round bulb
            quad(self.x - self.r, self.top - 4, self.x + self.r, self.top - 4,
                 self.x + self.r * 0.3, bottom, self.x - self.r * 0.3, bottom)
            ellipse(self.x, bottom, self.r * 2, self.r * 2.3)
            hx = self.x
            hy = bottom
        else:
            stretch = 1 + min(self.vy * 0.08, 1.0)   # stretches as it speeds up
            ellipse(self.x, self.y, self.r * 1.6, self.r * 1.6 * stretch)
            hx = self.x
            hy = self.y
        fill(0, 0, 100, 45)                          # glossy highlight
        ellipse(hx - self.r * 0.35, hy - self.r * 0.3, self.r * 0.5, self.r * 0.5)


class Blob(object):
    """A wobbly blob of slime. Its outline is a circle whose radius is
    bent in and out by Perlin noise, so it jiggles like jelly."""

    def __init__(self, x, y, r, intensity):
        self.x = x
        self.y = y
        self.r = r
        self.seed = random(1000)
        self.hue = random(80, 105)
        self.wobble = 0.25 + intensity * 0.35

    def update(self):
        t = frameCount * 0.01
        self.x += (noise(self.seed, t) - 0.5) * 1.5
        self.y += (noise(self.seed + 50, t) - 0.5) * 1.2
        self.x = constrain(self.x, self.r, width - self.r)
        self.y = constrain(self.y, height * 0.25, height * 0.75)

    def display(self):
        noStroke()
        fill(self.hue, 60, 60, 90)
        beginShape()
        steps = 24
        # curveVertex makes smooth curves; the 3 extra points wrap round
        # so the start and end of the outline join up smoothly.
        for i in range(steps + 3):
            a = TWO_PI * i / steps
            n = noise(self.seed + cos(a) * 1.2 + 1, self.seed + sin(a) * 1.2 + 1, frameCount * 0.02)
            rr = self.r * (1 + (n - 0.5) * 2 * self.wobble)
            curveVertex(self.x + cos(a) * rr, self.y + sin(a) * rr)
        endShape()
        fill(0, 0, 100, 45)
        ellipse(self.x - self.r * 0.35, self.y - self.r * 0.35, self.r * 0.4, self.r * 0.25)


class DisgustedArt(object):
    def __init__(self, intensity):
        self.intensity = intensity
        self.ink = 20
        self.drips = []
        self.splashes = []
        self.cols = 64                               # puddle is split into 64 columns
        self.puddle = [random(15, 30) for i in range(self.cols + 1)]
        self.blobs = [Blob(random(150, width - 150), random(height * 0.3, height * 0.65),
                           random(35, 70), intensity) for i in range(3 + int(intensity * 4))]
        self.seed = random(1000)

    def goo_edge(self, x):
        """The wobbly bottom edge of the slime hanging from the top."""
        return 45 + noise(self.seed + x * 0.008, frameCount * 0.01) * 70 * (1 + self.intensity * 0.6)

    def column(self, x):
        return int(constrain(x / float(width) * self.cols, 0, self.cols))

    def floor_at(self, x):
        """How high the puddle surface is at this x position."""
        return height - self.puddle[self.column(x)]

    def run(self):
        background(65, 22, 90)                       # sickly pale yellow-green

        # New drips form along the goo (more often when more disgusted)
        if random(1) < 0.04 + self.intensity * 0.12:
            x = random(20, width - 20)
            self.drips.append(Drip(x, self.goo_edge(x), self.intensity))

        for blob in self.blobs:
            blob.update()
            blob.display()
            if random(1) < 0.004 + self.intensity * 0.01:   # blobs drip too
                self.drips.append(Drip(blob.x, blob.y + blob.r * 0.8, self.intensity, True, blob.hue))

        for drip in self.drips:
            drip.update(self.goo_edge(drip.x), self.floor_at(drip.x))
            drip.display()
            if drip.splatted:
                self.splat(drip.x, drip.r)
        self.drips = [d for d in self.drips if not d.splatted]

        self.draw_top_goo()      # drawn after drips so their tops tuck in neatly
        self.settle_puddle()
        self.draw_puddle()

        for p in self.splashes:
            p.update()
            p.display()
        self.splashes = [p for p in self.splashes if not p.is_dead()]

    def draw_top_goo(self):
        noStroke()
        fill(SLIME_HUE, 65, 52)
        beginShape()
        vertex(0, 0)
        x = 0
        while x <= width + 10:
            vertex(x, self.goo_edge(x))
            x += 10
        vertex(width, 0)
        endShape(CLOSE)
        noFill()                                     # glossy shine line
        stroke(80, 30, 85, 60)
        strokeWeight(3)
        beginShape()
        x = 0
        while x <= width + 10:
            vertex(x, self.goo_edge(x) - 10)
            x += 10
        endShape()

    def splat(self, x, r):
        """A drip landed: raise the puddle around that spot and splash."""
        i = self.column(x)
        for k in range(-4, 5):
            j = i + k
            if 0 <= j <= self.cols:
                self.puddle[j] = min(self.puddle[j] + r * 0.6 * (1 - abs(k) / 5.0), height * 0.22)
        self.splashes += burst(x, self.floor_at(x), 8, [SLIME_HUE], 1, 4, size=4,
                               gravity=0.25, drag=0.97, fade=4, sat=65, bri=55)

    def settle_puddle(self):
        """Each column slowly levels out toward its neighbours, like liquid
        spreading, and the puddle very slowly drains so it never overflows."""
        new = list(self.puddle)
        for i in range(self.cols + 1):
            left = self.puddle[max(0, i - 1)]
            right = self.puddle[min(self.cols, i + 1)]
            new[i] = self.puddle[i] * 0.9 + (left + right) / 2.0 * 0.1
            new[i] = max(12, new[i] * 0.9995)
        self.puddle = new

    def draw_puddle(self):
        noStroke()
        fill(95, 70, 42)
        col_w = width / float(self.cols)
        beginShape()
        vertex(0, height)
        for i in range(self.cols + 1):
            wobble = (noise(i * 0.3, frameCount * 0.02) - 0.5) * 8
            vertex(i * col_w, height - self.puddle[i] + wobble)
        vertex(width, height)
        endShape(CLOSE)

    def poke(self, x, y):
        if len(self.blobs) < 12:
            self.blobs.append(Blob(x, y, random(30, 55), self.intensity))
        self.splashes += burst(x, y, 14, [SLIME_HUE], 1, 5, size=5, gravity=0.25,
                               fade=3, sat=65, bri=55)


# ---------- MYSTERY: no feeling words found ------------------------

class MysteryArt(object):
    def __init__(self, intensity):
        self.intensity = intensity
        self.ink = 30
        self.orbs = [[random(1000), random(80, 260)] for i in range(10)]  # [noise seed, size]
        self.ripples = []

    def run(self):
        background(0, 0, 94)
        noStroke()
        t = frameCount * 0.003
        for orb in self.orbs:
            x = noise(orb[0], t) * width
            y = noise(orb[0] + 50, t) * height
            fill(0, 0, 60, 10)
            ellipse(x, y, orb[1], orb[1])
        for r in self.ripples:
            r.update()
            r.display()
        self.ripples = [r for r in self.ripples if not r.is_dead()]

        textFont(font_bold)
        textAlign(CENTER, CENTER)
        textSize(40)
        fill(0, 0, 35)
        text("Hmm, that's a new one.", width / 2.0, height * 0.42)
        textFont(font_regular)
        textSize(18)
        fill(0, 0, 50)
        text("I couldn't find a feeling in there. Press ENTER and try another word.",
             width / 2.0, height * 0.42 + 50)

    def poke(self, x, y):
        for i in range(3):
            self.ripples.append(Ripple(x, y, 0, 0, 50, 1 + i * 0.7, 1.0, 50, 1.2))


# Which artwork class belongs to which emotion. Adding a new emotion =
# a new word list in section 1 + a new class + one line here.
ARTWORKS = {
    "happy": HappyArt,
    "sad": SadArt,
    "angry": AngryArt,
    "calm": CalmArt,
    "excited": ExcitedArt,
    "nervous": NervousArt,
    "disgusted": DisgustedArt,
    "mystery": MysteryArt,
}


# ------------------------------------------------------------------
# 5. SCREENS
# ------------------------------------------------------------------

state = "home"        # "home" = typing screen, "art" = artwork screen
typed = ""            # what the viewer has typed so far
typed_born = []       # the frame each letter was typed (for the pop effect)
submitted = ""        # the sentence that made the current artwork
emotion = "mystery"
intensity = 0.25
details = {}
artwork = None
show_details = False
fade = 0              # white fade between screens (100 = fully white)
ambient = []
font_regular = None
font_bold = None
MAX_LETTERS = 60


def draw_home():
    background(60, 2, 96)                 # warm off-white
    for d in ambient:
        d.display()

    textAlign(CENTER, CENTER)
    if typed == "":
        # Nothing typed yet: big cheeky headline
        textFont(font_bold)
        textSize(56)
        fill(0, 0, 30)
        text("Feelings go in.", width / 2.0, height * 0.38)
        fill(0, 0, 62)
        text("Art comes out.", width / 2.0, height * 0.38 + 66)

        textFont(font_regular)
        textSize(18)
        fill(0, 0, 50)
        text("Type how you feel, then press ENTER", width / 2.0, height * 0.62)
        textSize(14)
        fill(0, 0, 65)
        text("psst... CAPS and !!! make it louder", width / 2.0, height * 0.62 + 30)

        if (frameCount // 30) % 2 == 0:   # blinking cursor (on 30 frames, off 30)
            stroke(0, 0, 45)
            strokeWeight(2)
            line(width / 2.0, height * 0.73, width / 2.0, height * 0.73 + 30)
    else:
        # Typing: headline shrinks to the top, the words take centre stage
        textFont(font_regular)
        textSize(20)
        fill(0, 0, 60)
        text("Feelings go in. Art comes out.", width / 2.0, 60)

        textFont(font_bold)
        end_x, txt_size = draw_rainbow_text(typed, width / 2.0, height * 0.45, 52, 85, 85, typed_born)
        if (frameCount // 30) % 2 == 0:
            stroke(0, 0, 45)
            strokeWeight(2)
            line(end_x + 6, height * 0.45 - txt_size * 0.5, end_x + 6, height * 0.45 + txt_size * 0.5)

        # Live reading: shows the analysis working as you type
        guess = detect_emotion(typed)
        level, _ = analyse_intensity(typed)
        textFont(font_regular)
        textAlign(CENTER, CENTER)
        textSize(16)
        fill(0, 0, 55)
        if guess == "mystery":
            text("sounds like... hmm, not sure yet", width / 2.0, height * 0.6)
        else:
            text("sounds like... " + guess, width / 2.0, height * 0.6)
        draw_meter(width / 2.0 - 74, height * 0.6 + 22, level, 0, 0, 40)
        textSize(14)
        fill(0, 0, 65)
        text("press ENTER when you're ready", width / 2.0, height * 0.8)


def draw_art_screen():
    artwork.run()
    ink = artwork.ink

    # Top-left: emotion name + intensity meter
    textFont(font_bold)
    textAlign(LEFT, TOP)
    textSize(22)
    fill(0, 0, ink, 90)
    text(emotion.upper(), 40, 34)
    textFont(font_regular)
    textSize(13)
    fill(0, 0, ink, 70)
    text("intensity", 40, 66)
    meter_bri = 100 if ink > 50 else 70
    meter_sat = 0 if emotion == "mystery" else 70
    draw_meter(40, 88, intensity, ACCENT_HUE[emotion], meter_sat, meter_bri)

    # Top-right: controls
    textAlign(RIGHT, TOP)
    textSize(12)
    fill(0, 0, ink, 55)
    text("ENTER  new feeling      CLICK  poke it      TAB  how I read it      S  save",
         width - 40, 38)

    # Bottom: their sentence in rainbow letters on a dark see-through pill
    textFont(font_bold)
    txt_size = fitted_size(submitted, 30, width * 0.8)
    textSize(txt_size)
    pill_w = text_width_sum(submitted) + 60
    pill_h = txt_size + 30
    noStroke()
    fill(0, 0, 0, 40)
    rect(width / 2.0 - pill_w / 2.0, height - 100, pill_w, pill_h, pill_h / 2.0)
    draw_rainbow_text(submitted, width / 2.0, height - 100 + pill_h / 2.0, 30, 60, 100,
                      None, width * 0.8)

    if show_details:
        draw_details_panel()


def draw_details_panel():
    """The 'how I read your words' panel (TAB key). Shows the text
    analysis behind the artwork - handy for the explainer video."""
    lines = [
        "HOW I READ YOUR WORDS",
        "feeling detected:  " + emotion,
        "capital letters:  %d%%" % int(details["caps"] * 100),
        "exclamation marks:  %d" % details["exclaims"],
        "stretched words:  " + ("yes" if details["stretched"] else "no"),
        "booster words:  %d" % details["boosters"],
        "softener words:  " + ("yes" if details["softened"] else "no"),
        "intensity:  %.2f out of 1.00" % intensity,
    ]
    noStroke()
    fill(0, 0, 0, 55)
    rect(30, 120, 300, 30 + len(lines) * 24, 14)
    textFont(font_regular)
    textAlign(LEFT, TOP)
    textSize(14)
    for i in range(len(lines)):
        fill(0, 0, 100, 100 if i == 0 else 85)
        text(lines[i], 48, 136 + i * 24)


# ------------------------------------------------------------------
# 6. PROCESSING EVENTS
# ------------------------------------------------------------------

def setup():
    global font_regular, font_bold, ambient
    size(1280, 720)                       # 16:9, ideal for screen-recording the video
    frameRate(60)
    # HSB colour: Hue 0-360 (colour wheel), Saturation 0-100, Brightness
    # 0-100, Alpha 0-100. Much easier than RGB for rainbows and moods.
    colorMode(HSB, 360, 100, 100, 100)
    # "SansSerif" is built into Java so it always works. To use a nicer
    # font, put a .ttf/.otf in a 'data' folder and use its file name here.
    font_regular = createFont("SansSerif", 64, True)
    font_bold = createFont("SansSerif.bold", 64, True)
    ambient = [AmbientDot() for i in range(28)]


def draw():
    global fade
    if state == "home":
        draw_home()
    else:
        draw_art_screen()

    # Soft white fade when switching screens
    if fade > 0:
        noStroke()
        fill(60, 2, 96, fade)
        rect(0, 0, width, height)
        fade = max(0, fade - 3)


def keyPressed():
    global state, typed, typed_born, submitted, emotion, intensity
    global details, artwork, show_details, fade

    if key == CODED:                      # shift, arrow keys etc. - ignore
        return

    if state == "home":
        if key == BACKSPACE:
            typed = typed[:-1]
            typed_born = typed_born[:-1]
        elif key == ENTER or key == RETURN:
            if typed.strip() != "":
                # THE MAIN PIPELINE: TEXT -> EMOTION -> VISUAL
                submitted = typed.strip()
                emotion = detect_emotion(submitted)
                intensity, details = analyse_intensity(submitted)
                artwork = ARTWORKS[emotion](intensity)
                state = "art"
                fade = 100
        elif len(typed) < MAX_LETTERS and 32 <= ord(key) < 127:
            typed += key                  # only normal printable characters
            typed_born.append(frameCount)
    else:
        if key == ENTER or key == RETURN:
            state = "home"
            typed = ""
            typed_born = []
            show_details = False
            fade = 100
        elif key == TAB:
            show_details = not show_details
        elif key == "s" or key == "S":
            saveFrame("screenshots/emotion-####.png")


def mousePressed():
    if state == "art" and artwork is not None:
        artwork.poke(mouseX, mouseY)
