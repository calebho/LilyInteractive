import speech_recognition as sr
from text_to_speech import speak


r = sr.Recognizer()
r.pause_threshold = 1
r.energy_threshold = 2200

def getInputString():
    """
    """
    s = None
    while not s:
        # use the default microphone as the audio source
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration = 0.5)
            print "listening..."
            audio = r.listen(source)
        try:
            all_list = r.recognize_google(audio)
            s = all_list
        except LookupError: # speech is unintelligible
            speak("Sorry, I didn't hear that.")
            s = None
    print(s)
    return str(s)


def getInputStringMultiple():
    s = None
    while not s:
        # use the default microphone as the audio source
        with sr.Microphone() as source:
            audio = r.adjust_for_ambient_noise(source, duration = 0.5)
            print "listening..."
            # listen for the first phrase and extract it into audio dataprint "heard"
            audio = r.listen(source)
        try:
            all_list = r.recognize(audio, show_all = True)
            s = ''
            for item in all_list:
                s +=item['text']+' '
            # recognize speech using Google Speech Recognition
        except LookupError: # speech is unintelligible
            speak("Sorry, I didn't hear that.")
            s = None
    print(s)
    return str(s)
