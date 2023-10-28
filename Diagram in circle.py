import matplotlib.pyplot as plt

# Données à représenter dans le diagramme circulaire
categories = ['Catégorie A', 'Catégorie B', 'Catégorie C', 'Catégorie D']
valeurs = [30, 45, 15, 10]  # Les pourcentages ou les valeurs numériques

# Couleurs pour chaque catégorie (optionnel)
couleurs = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']

# Explode (pour séparer les portions, optionnel)
explode = (0.05, 0, 0, 0)

# Crée le diagramme circulaire
plt.figure(figsize=(8, 8))
plt.pie(valeurs, explode=explode, labels=categories, colors=couleurs, autopct='%1.1f%%', shadow=False, startangle=140)

# Titre du diagramme
plt.title('Diagramme circulaire d\'exemple')

# Affiche le diagramme
plt.axis('equal')  # Assure que le diagramme soit un cercle et non une ellipse
plt.show()
