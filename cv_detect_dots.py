import cv2 as cv
import numpy as np
import math
import os
import json

# LIEN IMAGE PARIS: https://upload.wikimedia.org/wikipedia/commons/9/99/1920_Robelin_Map_of_Paris%2C_France_-_Geographicus_-_Paris-robelin-1920.jpg

# Importation et gestion des images (image de base et template de points).
img_rgb = cv.imread('./CarteMetroParis_Points_White.png')
img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
template = cv.imread('./template_point.png',0)
w, h = template.shape[::-1]
res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
threshold = 0.8
loc = np.where( res >= threshold)

# Variables perso
n = 0
# Dico dans lequel je stocke les informations des points trouvés (coordonnées, points adjacents sous forme (nom_point, distance)).
dico_points = {}

# On parcourt tous les points de l'image.
for pt in zip(*loc[::-1]):
    n+=1
    nom_point = str(n)
    cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2) # On dessine le rectangle autour de chaque point.
    cv.putText(img_rgb, nom_point, (pt[0]-10, pt[1]-10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2) # On écrit le nom du point sur l'image.
    # On ajoute le point et ses coordonnées à la liste.
    dico_points[nom_point] = {"COORDONNEES": (int(pt[0]+(w//2)), int(pt[1]+(h//2))), "ADJACENTS": []}

# On sauvegarde l'image.
cv.imwrite('only_points_blanc.png',img_rgb)


# On parcourt toute la liste de points pour définir manuellement les points adjacents. LAISSER COMMENTÉ SI NON UTILISÉ !!
for point in dico_points.keys():
    boucle_active = True
    liste_adj = []
    while boucle_active:
        # Demander les points adjacents à l'utilisateur
        answer = input(f"Adjacents (''=pass, rm [pt]=remove) {point} -> {liste_adj}: ").upper()
        if "RM" in answer:
            answer = answer.split(" ")
            for i in range(len(liste_adj)):
                if liste_adj[i][0] == answer[1]:
                    liste_adj.pop(i)
                    break
        elif answer == "":
            boucle_active = False
        else:
            answer = answer.split(".")
            # Ajouter le nom des points adjacents et calculer la distance entre ces deux points à l'aide du dico (coordonnées)
            for point_answer in answer:
                pointA = dico_points[point]["COORDONNEES"]
                pointB = dico_points[point_answer]["COORDONNEES"]
                distance = int(round(math.sqrt((pointB[0]-pointA[0])**2+(pointB[1]-pointA[1])**2)))
                rep = (point_answer, distance)
                if rep not in liste_adj:
                    liste_adj.append(rep)
    dico_points[point]["ADJACENTS"] = liste_adj
    os.system('cls')
    # On sauvegarde la nouvelle ligne dans le json
    with open('points_infosFROM_304_x.json','w') as outfile:
            print(dico_points)
            json.dump(dico_points,outfile, indent=2)
            print("\n\nNouveau dico sauvegardé dans points_infos.json.\n\n")



# TODO Sauvegarder le dico de points dans un csv/json/base de données et ensuite supprimer le doublon 469-470 et 472/473 et 492/493 et d'autres erreurs potentielles.
