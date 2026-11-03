# Emotion in Motion
# Text -> Emotion -> Visual
# Processing, Python Mode (Jython / Python 2.7 syntax: no f-strings)
#
# HOW TO USE: type a sentence, press ENTER. Move your mouse to interact.
# Try: "I feel so happy today", "I am angry and furious",
#      "I'm scared and anxious", "I feel sad and lonely",
#      "I feel calm and peaceful", "I love you so much"

# ---------------------------------------------------------------
# 1. MOOD DEFINITIONS (edit these to experiment!)
#    keywords : words that trigger the mood (partial matches count)
#    col      : particle colour (R, G, B)
#    bg       : background colour (R, G, B)
#    speed    : how energetic the movement is
#    size     : average particle size
# ---------------------------------------------------------------
MOODS = {
    "joy": {
        "keywords": ["happy", "joy", "excited", "great", "fun", "love it",
                     "amazing", "laugh", "smile", "wonderful", "yay"],
        "col": (255, 200, 40), "bg": (255, 120, 60),
        "speed": 3.0, "size": 18},
    "sadness": {
        "keywords": ["sad", "cry", "lonely", "miss", "lost", "empty",
                     "tired", "down", "hurt", "grief", "alone"],
        "col": (90, 130, 220), "bg": (15, 20, 50),
        "speed": 0.8, "size": 14},
    "anger": {
        "keywords": ["angry", "mad", "furious", "hate", "rage", "annoyed",
                     "frustrated", "unfair", "irritated"],
        "col": (240, 40, 30), "bg": (40, 0, 0),
        "speed": 5.0, "size": 20},
    "fear": {
        "keywords": ["scared", "afraid", "fear", "anxious", "nervous",
                     "worried", "panic", "terrified", "stress"],
        "col": (170, 140, 230), "bg": (10, 10, 25),
        "speed": 2.0, "size": 8},
    "calm": {
        "keywords": ["calm", "peace", "relax", "quiet", "still", "gentle",
                     "safe", "content", "serene"],
        "col": (90, 210, 200), "bg": (10, 50, 70),
        "speed": 0.6, "size": 40},
    "love": {
        "keywords": ["love", "adore", "care", "heart", "kiss", "hug",
                     "cherish", "grateful", "thankful"],
        "col": (255, 110, 160), "bg": (70, 10, 45),
        "speed": 1.5, "size": 22},
    "neutral": {
        "keywords": [],
        "col": (200, 200, 200), "bg": (25, 25, 30),
        "speed": 1.0, "size": 12},
}

NUM_PARTICLES = 160
MAX_CHARS = 70

typed = ""            # what the user is currently typing
last_sentence = ""    # last submitted sentence
mood = "neutral"      # current detected mood
particles = []
cur_col = [200, 200, 200]
cur_bg = [25, 25, 30]
cur_speed = 1.0
cur_size = 12.0


# ---------------------------------------------------------------
# 2. TEXT -> EMOTION (basic keyword detection)
# ---------------------------------------------------------------
def detect_mood(sentence):
    text = sentence.lower()
    best_mood = "neutral"
    best_score = 0
    for name in MOODS:
        score = 0
        for word in MOODS[name]["keywords"]:
            if word in text:
                score += 1
        if score > best_score:
            best_score = score
            best_mood = name
    return best_mood


# ---------------------------------------------------------------
# 3. PARTICLE CLASS (each mood moves differently)
# ---------------------------------------------------------------
class Particle(object):
    def __init__(self):
        self.x = random(width)
        self.y = random(height)
        self.vx = random(-1, 1)
        self.vy = random(-1, 1)
        self.phase = random(TWO_PI)
        self.scale = random(0.5, 1.5)

    def update(self, m):
        t = frameCount * 0.03
        sp = cur_speed

        if m == "joy":
            # bouncy, rising upward
            self.vy -= 0.05 * sp
            self.vx += sin(t * 2 + self.phase) * 0.05 * sp
        elif m == "sadness":
            # slow drifting downward, like falling rain
            self.vy += 0.03
            self.vx *= 0.95
        elif m == "anger":
            # sharp, jittery, aggressive
            self.vx += random(-1, 1) * sp * 0.4
            self.vy += random(-1, 1) * sp * 0.4
        elif m == "fear":
            # twitchy, flees from the mouse
            self.vx += random(-0.5, 0.5)
            self.vy += random(-0.5, 0.5)
            d = dist(self.x, self.y, mouseX, mouseY)
            if d < 150 and d > 0:
                self.vx += (self.x - mouseX) / d * 1.2
                self.vy += (self.y - mouseY) / d * 1.2
        elif m == "calm":
            # slow flowing sine-wave drift
            self.vx += cos(t + self.phase) * 0.01
            self.vy += sin(t * 0.8 + self.phase) * 0.01
        elif m == "love":
            # swirl gently around the centre of the screen
            dx = width / 2 - self.x
            dy = height / 2 - self.y
            d = max(dist(self.x, self.y, width / 2, height / 2), 1)
            self.vx += dx / d * 0.04 + (-dy / d) * 0.08
            self.vy += dy / d * 0.04 + (dx / d) * 0.08
        else:
            self.vx += random(-0.1, 0.1)
            self.vy += random(-0.1, 0.1)

        # gentle mouse attraction for every mood except fear
        if m != "fear":
            d = dist(self.x, self.y, mouseX, mouseY)
            if d < 200 and d > 1:
                self.vx += (mouseX - self.x) / d * 0.05
                self.vy += (mouseY - self.y) / d * 0.05

        # speed limit and friction
        limit = max(cur_speed, 0.5) * 1.5
        v = sqrt(self.vx * self.vx + self.vy * self.vy)
        if v > limit:
            self.vx = self.vx / v * limit
            self.vy = self.vy / v * limit
        self.vx *= 0.98
        self.vy *= 0.98

        self.x += self.vx
        self.y += self.vy

        # wrap around the edges
        if self.x < -20:
            self.x = width + 20
        if self.x > width + 20:
            self.x = -20
        if self.y < -20:
            self.y = height + 20
        if self.y > height + 20:
            self.y = -20

    def show(self, m):
        s = cur_size * self.scale
        noStroke()

        if m == "joy":
            fill(cur_col[0], cur_col[1], cur_col[2], 200)
            ellipse(self.x, self.y, s, s)
        elif m == "sadness":
            fill(cur_col[0], cur_col[1], cur_col[2], 160)
            ellipse(self.x, self.y, s * 0.5, s * 1.6)   # teardrop-ish
        elif m == "anger":
            fill(cur_col[0], cur_col[1], cur_col[2], 220)
            pushMatrix()
            translate(self.x, self.y)
            rotate(self.phase + frameCount * 0.1)
            triangle(-s / 2, s / 2, s / 2, s / 2, 0, -s)   # sharp shapes
            popMatrix()
        elif m == "fear":
            fill(cur_col[0], cur_col[1], cur_col[2], random(60, 255))  # flicker
            ellipse(self.x, self.y, s, s)
        elif m == "calm":
            fill(cur_col[0], cur_col[1], cur_col[2], 60)
            ellipse(self.x, self.y, s * 2, s * 2)       # big, soft
        elif m == "love":
            pulse = 1 + 0.4 * sin(frameCount * 0.08 + self.phase)
            fill(cur_col[0], cur_col[1], cur_col[2], 190)
            ellipse(self.x, self.y, s * pulse, s * pulse)
        else:
            fill(cur_col[0], cur_col[1], cur_col[2], 150)
            ellipse(self.x, self.y, s, s)


# ---------------------------------------------------------------
# 4. SETUP / DRAW
# ---------------------------------------------------------------
def setup():
    size(900, 600)
    smooth()
    textFont(createFont("Arial", 20))
    for i in range(NUM_PARTICLES):
        particles.append(Particle())


def draw():
    global cur_speed, cur_size

    target = MOODS[mood]

    # smoothly blend colours, speed and size towards the new mood
    for i in range(3):
        cur_col[i] = lerp(cur_col[i], target["col"][i], 0.04)
        cur_bg[i] = lerp(cur_bg[i], target["bg"][i], 0.04)
    cur_speed = lerp(cur_speed, target["speed"], 0.04)
    cur_size = lerp(cur_size, target["size"], 0.04)

    # semi-transparent background = soft motion trails
    noStroke()
    fill(cur_bg[0], cur_bg[1], cur_bg[2], 40)
    rect(0, 0, width, height)

    for p in particles:
        p.update(mood)
        p.show(mood)

    draw_interface()


def draw_interface():
    # dark strip so the text is always readable
    fill(0, 0, 0, 120)
    noStroke()
    rect(0, height - 70, width, 70)

    fill(255)
    textAlign(LEFT, CENTER)
    textSize(20)
    cursor = "|" if (frameCount // 30) % 2 == 0 else ""
    if typed == "":
        fill(255, 255, 255, 130)
        text("Type how you feel and press ENTER...", 20, height - 35)
    else:
        text(typed + cursor, 20, height - 35)

    textSize(14)
    fill(255, 255, 255, 200)
    textAlign(RIGHT, TOP)
    if last_sentence != "":
        text("detected emotion: " + mood.upper(), width - 20, 15)
    textAlign(LEFT, TOP)
    text("Emotion in Motion", 20, 15)


# ---------------------------------------------------------------
# 5. KEYBOARD INPUT (Processing has no built-in text box)
# ---------------------------------------------------------------
def keyPressed():
    global typed, last_sentence, mood

    # special keys (arrows, shift etc.) have codes above 255, so ignore them
    if ord(key) == 10 or ord(key) == 13:          # ENTER
        if typed.strip() != "":
            last_sentence = typed
            mood = detect_mood(typed)
            typed = ""
    elif ord(key) == 8:                           # BACKSPACE
        typed = typed[:-1]
    elif 32 <= ord(key) < 127 and len(typed) < MAX_CHARS:
        typed += key
