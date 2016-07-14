import speech_recognition as sr

from watson_developer_cloud import SpeechToTextV1
from text_to_speech import speak

# Watson speech to text service credentials
UNAME = '68cf9a6e-63a2-404a-9c96-295de6aac15d'
PWD = 'D8MFSdf2TsWS'

stt = SpeechToTextV1(username=UNAME, password=PWD)

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
            # print "listening..."
            audio = r.listen(source).get_wav_data()
        response = stt.recognize(audio, content_type='audio/wav',
                model='en-US_BroadbandModel')
        best_transcript = response['alternatives'][0]
        s = best_transcript['transcript'] if best_transcript['confidence'] > t else None
    
    return s

def main():
    pass 

if __name__ == '__main__':
    main()
