import pygame
from gtts import gTTS

# Initialisez pygame.mixer
pygame.mixer.init()

# Fonction pour générer une réaction audio à partir d'un texte donné
def generer_reaction_audio(texte):
    # Utilisez la bibliothèque gTTS pour convertir le texte en audio en anglais
    reaction_audio = gTTS(text=texte, lang='en')

    # Enregistrez le fichier audio généré
    reaction_audio.save("reaction.mp3")

    # Chargez le fichier audio avec pygame
    pygame.mixer.music.load("reaction.mp3")
    print("Avant la lecture audio")  # Débogage
    pygame.mixer.music.play()

    # Attendez la fin de la lecture audio
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Assurez-vous que le jeu ne devient pas non réactif en attendant

    print("Après la lecture audio")  # Débogage

# Exemple d'utilisation
texte1 = "Well played"
generer_reaction_audio(texte1)


