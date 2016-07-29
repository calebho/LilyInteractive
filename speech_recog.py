import speech_recognition as sr

r = sr.Recognizer()
r.pause_threshold = 1
r.energy_threshold = 2200

def get_input(): # TODO: add keyword recognition?
    """Using audio data recorded from the microphone, do speech to text on the
    audio and return the transcription
    """
    # FOR DEBUGGING 
    # return raw_input('input: ')
    
    t = 0.8 # confidence threshold
    s = None
    while not s:
        # use the default microphone as the audio source
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration = 0.5)
            print "listening..."
            audio = r.listen(source)
        try:
            s = r.recognize_google(audio)
        except sr.UnknownValueError:
            pass
    
    return s

def main():
    print(get_input())

if __name__ == '__main__':
    main()
