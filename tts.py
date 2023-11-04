from gtts import gTTS


def tts(name, text):
    audio = gTTS(text=text, lang="en", slow=False)
    audio.save(f"{name}.mp3")


def init_sounds():
    tts(0, str(0))
    tts(1, str(1))
    tts(2, str(2))
    tts(3, str(3))
    tts("DETECT", "DETECT")
    tts("PEACE", "OK")
    tts("FAKJOE", "FAKJOE")
    tts("HIT", "HIT")
    tts("BUST", "BUST")


init_sounds()
