import pyaudio
import wave
import time

from StringIO import StringIO
from watson_developer_cloud import TextToSpeechV1
from timeout import timeout_decorate, TimeoutError
from pymouse import PyMouse

# define enter/exit methods for use in a context manager
StringIO.__enter__ = lambda self: self
StringIO.__exit__ = lambda self, e_type, e_val, tb: self.close()

TextToSpeechV1.synthesize = timeout_decorate(TextToSpeechV1.synthesize, seconds=5)
tts = TextToSpeechV1(username='68819f91-e8a5-49e3-b284-3b66ed470bb9',
                     password='1tkAyaLoSdhm')
wf = None # the wave file

m = PyMouse()
def click():
    """Click the mouse to start/stop avatar animation
    """
    x, y = map(lambda n: n/2, m.screen_size())
    m.click(x, y, 1)

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

        click()
        stream.start_stream()
        while stream.is_active():
            time.sleep(0.1)
        stream.stop_stream()
        stream.close()
        p.terminate()
        click()

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

