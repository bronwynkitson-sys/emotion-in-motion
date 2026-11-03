EMOTION IN MOTION  

By Bronwyn Kitson  
Creative Coding, Assessment 2 (Code Prototype Project), UTS, 2026  

What it is  

Emotion in Motion is an interactive artwork made in Processing (Python Mode). You type how you are feeling, and the program turns your words into a moving artwork. The words you use decide which emotion it shows, and the way you write them (capital letters, exclamation marks, stretched-out words like "sooo") decides how intense the artwork is.  

There are seven emotions: happy, sad, angry, calm, excited, nervous and disgusted. Each one has its own artwork. If the program can't find a feeling in what you typed, it shows a "mystery" screen and asks you to try again.  

Happy - bubbles that float up and pop  
Sad - rain with ripples  
Angry - a spiky pulsing shape with lightning and sparks  
Calm - slow rolling waves and a breathing circle  
Excited - fireworks  
Nervous - twitchy butterflies  
Disgusted - dripping slime  

The more intense the input, the bigger, faster and busier the artwork gets.  

What you need  

Processing 4, which you can download for free from https://processing.org/download  
Python Mode for Processing (installed from inside Processing, see below)  
No extra libraries are needed.  

Note: Python Mode runs Python 2.7, so the code does not use newer Python features like f-strings.  

How to run it  

1. Download this repository (click the green Code button, then Download ZIP) and unzip it.  
2. Open Processing.  
3. If you haven't used Python Mode before, click the mode menu in the top right corner (it usually says Java), choose Add Mode, find Python Mode for Processing, click Install, then restart Processing.  
4. Switch the mode menu to Python.  
5. Go to File, then Open, and open EmotionInMotion.pyde inside the EmotionInMotion folder. The file needs to stay inside a folder with the same name or Processing won't open it.  
6. Press Run. A window will open.  
7. Type how you feel and press Enter.  

Controls  

Type and press Enter - turn your feeling into art  
Enter (on the artwork) - go back and type a new feeling  
Click - poke the artwork  
Tab - show or hide how the program read your words  
S - save a screenshot into the screenshots folder  
Backspace - delete a letter  

Some things to try: "i'm a bit sad" and then "I AM SO SAD!!!", "not happy", "no worries", "I was angry but now I'm calm".  

Files  

EmotionInMotion/EmotionInMotion.pyde - all of the code is in this one file  
README.md - this file  
A screenshots folder is created automatically when you press S.  

How the code is organised  

The code is split into six sections, and each one is commented in the file.  

1. Emotion data - the lists of words for each emotion, the opposites used when a feeling is negated (so "not happy" becomes sad), and the booster and softener words.  
2. Text analysis - detect_emotion() works out which emotion was typed, and analyse_intensity() works out how strongly it was written, as a score from 0.1 to 1.0.  
3. Shared helpers - particles, ripples, the rainbow text and the intensity meter, which are reused by several artworks.  
4. The artworks - one class for each emotion. They all have the same three methods (init, run and poke), so one dictionary called ARTWORKS can create whichever artwork is needed.  
5. Screens - the typing screen, the artwork screen and the Tab panel.  
6. Processing events - setup(), draw(), keyPressed() and mousePressed().  

To add a new emotion you would add a word list in section 1, write a new class in section 4, and add one line to ARTWORKS.  

Acknowledgements and references  

[ADD YOUR AI ACKNOWLEDGEMENT HERE IF NEEDED]  

[ADD ANY TUTORIALS OR CODE SOURCES YOU USED HERE]  

Processing Foundation. (n.d.). Processing (Version 4) [Computer software]. https://processing.org  

Processing Foundation. (n.d.). Processing.py: Python Mode for Processing [Computer software]. https://py.processing.org  

Łyczywek, R. (2018, October 15). How to write a good README for your GitHub project? Bulldogjob. https://bulldogjob.com/readme/how-to-write-a-good-readme-for-your-github-project  
