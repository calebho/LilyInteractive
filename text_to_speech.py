import pyaudio
import wave
import time

from StringIO import StringIO
from watson_developer_cloud import TextToSpeechV1
from timeout import timeout_decorate, TimeoutError

# define enter/exit methods for use in a context manager
StringIO.__enter__ = lambda self: self
StringIO.__exit__ = lambda self, e_type, e_val, tb: self.close()

TextToSpeechV1.synthesize = timeout_decorate(TextToSpeechV1.synthesize, seconds=5)
tts = TextToSpeechV1(username='68819f91-e8a5-49e3-b284-3b66ed470bb9',
                     password='1tkAyaLoSdhm')
wf = None # the wave file

class SpeechError(Exception):
    pass

def callback(in_data, frame_count, time_info, status):
    """pyaudio callback
    """
    data = wf.readframes(frame_count)
    return data, pyaudio.paContinue

def speak(s):
    """Do TTS on a string `s`
    """
    global wf
    
    audio = None
    for i in range(3):
        try:
            audio = tts.synthesize(s, accept='audio/wav', voice='en-US_AllisonVoice')
        except TimeoutError:
            print('Timemout %d occured' % i)
        else:
            break
    if not audio:
        raise SpeechError('No response received')

    with StringIO(audio) as f:
        wf = wave.open(f, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)

        stream.start_stream()
        while stream.is_active():
            time.sleep(0.1)
        stream.stop_stream()
        stream.close()
        p.terminate()

def wrap_text(s, t=None):
    """Wrap a string `s` with speak and express-as tags using type `t`
    """
    if t:
        return u"<speak><express-as type=\"%s\">" % t + \
               unicode(s) + \
               u"</express-as></speak>"
    else:
       return u"<speak>" + unicode(s) + u"</speak>"

def englishify(l, conj=True):
    """Unpack a list to natural english
    """
    if len(l) == 1:
        return l[0]
    elif len(l) == 2:
        return ' and '.join(l) if conj else ' or '.join(l)
    else:
        l_copy = l[:]
        if conj:
            l_copy[-1] = 'and ' + l_copy[-1]
        else:
            l_copy[-1] = 'or ' + l_copy[-1]
        return ', '.join(l_copy)

def main():
    speak('This is some test text')

if __name__ == '__main__':
    main()

"""
import pyttsx
import win32con, win32api


'''This file handles the text to speech aspect of the interactive story using the pyttsx module to
produce the speech. Additionally, we use the win32api module for python, which encapsulates the Windows win32api, allowing
us to send a click to our avatar. Each click changes the current avatar animation being run, simulating a talking or idle state. '''

def onStart(name):
        click(100,100)

def onEnd(name, completed):
        click(100,100)

engine = pyttsx.init()
engine.connect("started-utterance", onStart)
engine.connect("finished-utterance", onEnd)
#get functions return current state of speech engine
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
volume = engine.getProperty('volume')
#set the speaking volume
engine.setProperty('volume', volume + .99)
#set the speaking rate
#engine.setProperty('rate', rate - 40)
#set the voice to one of three
engine.setProperty('voice', voices[1].id)


import ctypes
import time
import math

#lib = ctypes.CDLL('FakeInputWin')

def speak(string):
        engine.say(string)
        engine.runAndWait()
        print string


def click(x,y):
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)



#IN THE EVENT BALDISYNC IS USED REPLACE SPEAK WITH BELOW CODE
#lib.typeInBaldi(string)
#time.sleep(2*math.log10(len(string)) + 1)
"""
