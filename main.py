# Imports

import pygame, sys
from random import randint
import networkx as nwx
import json
from math import sqrt, ceil

# Classes

# Classe Joueur()
class Joueur(pygame.sprite.Sprite):
    # Initialisation du joueur.
    def __init__(self, group, point_depart:str):
        super().__init__(group)
        self.paris_graphe = Points_Paris()
        self.pos = self.paris_graphe.get_graphe().nodes[point_depart]["COORDONNEES"]
        self.image = pygame.image.load('./images/test_player.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom = self.pos)
        self.direction = pygame.math.Vector2()
        self.speed = 0.5
        self.nom = "Joueur"

        self.clock = pygame.time.Clock()

        # Mouvement par points
        self.direction_est_fixee = False
        self.dernier_point_visite = point_depart
        self.prochains_points_a_visiter = []

    # Fonction derniere_visite()
    def derniere_visite(self):
        """
            Renvoie le dernier point visité par le joueur.\n
        """
        return self.dernier_point_visite

    # Fonction est_en_mouvement()
    def est_en_mouvement(self) -> bool:
        """
            Vérifie si le joueur est actuellement en train de suivre un itinéraire.\n

            Renvoie:\n
                - bool\n
        """
        return len(self.prochains_points_a_visiter) != 0

    # Fonction destination_atteinte_rayon()
    def destination_atteinte_rayon(self, destination:str, rayon:int) -> bool:
        """
            Vérifie si le joueur se trouve dans un certain rayon de la destination indiquée.\n

            Paramètres:\n
                - destination (str) : Nom du point de destination.\n
                - rayon (int) : rayon (en pixels) autour du point dans lequel la fonction considère que
                le joueur a atteint la destination.\n

            Renvoie:\n
                - bool : True si le joueur a atteint la destination.\n
                         False si le joueur n'est pas encore dans la destination.\n
        """
        coord_destination = self.paris_graphe.get_graphe().nodes[destination]["COORDONNEES"]
        dist = sqrt((self.pos[0]-coord_destination[0])**2+(self.pos[1]-coord_destination[1])**2)
        return dist <= rayon

    # Fonction calculer_direction()
    def calculer_direction(self, destination:str):
        """
            Calcule un vecteur directeur entre la position du joueur et sa destination.\n

            Paramètres:\n
                - destination (str) : Nom du point de destination.\n
        """
        coord_destination = self.paris_graphe.get_graphe().nodes[destination]["COORDONNEES"]
        self.direction = pygame.Vector2(coord_destination[0]-self.pos[0],coord_destination[1]-self.pos[1])

    # Fonction parcourir_trajet()
    def parcourir_trajet(self, trajet:list):
        """
            Prend en charge les déplacements des trajectoires du joueur en fonction d'un trajet donné.\n

            Paramètres:\n
                - trajet (list) : Liste contenant le nom (str) des prochains points jusqu'à la destination.\n
        """
        if self.prochains_points_a_visiter != []:
            if self.direction_est_fixee == False:
                self.calculer_direction(trajet[0])
                self.direction_est_fixee = True
            if self.destination_atteinte_rayon(trajet[0], 3):
                self.direction = pygame.Vector2()
                self.dernier_point_visite = trajet[0]
                trajet.pop(0)
                if self.prochains_points_a_visiter != []:
                    self.calculer_direction(trajet[0])
                else:
                    self.direction_est_fixee = False

    # Fonction definir_trajet()
    def definir_trajet(self, mouse_pos:list) -> None:
        """
            Définit un trajet constitué d'une liste de noms de points.\n

            Paramètres:\n
                - mouse_pos (list) : coordonnées de l'endroit où le joueur a clické sur la carte.\n
        """
        destination = self.paris_graphe.trouver_point_le_plus_proche(mouse_pos)
        if self.prochains_points_a_visiter != []:
            if self.prochains_points_a_visiter[-1] != destination:
                nouveau_depart = self.prochains_points_a_visiter[0]
                self.prochains_points_a_visiter = []    # Au cas-où, on réinitialise la liste des points à parcourir. N'est probablement pas utile, mais on ne sait jamais.
                self.prochains_points_a_visiter = self.paris_graphe.trouver_trajet(nouveau_depart, destination)
        else:
            self.prochains_points_a_visiter = self.paris_graphe.trouver_trajet(self.dernier_point_visite, destination)

    # Fonction update()
    def update(self):
        """
            Application du mouvement du joueur et tous les calculs nécessaires pendant le jeu.
        """
        self.parcourir_trajet(self.prochains_points_a_visiter)

        # Mouvement du joueur par rapport à delta_t (temps écoulé depuis la dernière frame).
        dt = self.clock.tick(60) / 1000
        self.pos[0] += self.direction.x * self.speed * dt
        self.pos[1] += self.direction.y * self.speed * dt
        # self.rect.center = self.pos       # Pour afficher le Sprite par rapport à son centre
        self.rect.bottomleft = self.pos-pygame.Vector2(self.rect.width//2,0) # Pour afficher le sprite par rapport au midbottom


class Icon(pygame.sprite.Sprite):
    # Initialisation de l'icône
    def __init__(self, pos, group, nom_icone:str):
        super().__init__(group)
        self.pos = pos
        self.image = pygame.image.load(f'./images/icons/{nom_icone}.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (70,70))
        self.rect = self.image.get_rect(center = self.pos)
        self.nom = nom_icone

    def get_nom(self):
        return self.nom


# Classe CameraGroup()
class CameraGroup(pygame.sprite.Group):
    # Initialisation du group de sprites de la caméra.
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # Décalage caméra.
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # Mise en place de la boîte autour du joueur.
        self.camera_borders = {'left': 300, 'right': 300, 'top': 200, 'bottom': 200}
        l = self.camera_borders['left'] ; t = self.camera_borders['top']
        w = self.display_surface.get_size()[0]  - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1]  - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l,t,w,h)

        # Fond d'écran.
        self.ground_surf = pygame.image.load('./images/CarteMetroParis.jpg').convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(topleft = (0,0))

        # Vitesse de la caméra.
        self.keyboard_speed = 6


    # Fonction center_target_camera()
    def center_target_camera(self,player:Joueur):
        """
            Permet de center la caméra autour du joueur en le gardant en centre.\n

            Paramètres:\n
                - player (Joueur) : Joueur autour duquel la box camera se centrera.\n
        """
        self.offset.x = player.rect.centerx - self.half_w
        self.offset.y = player.rect.centery - self.half_h

    # Fonction box_target_camera()
    def box_target_camera(self,player:Joueur):
        """
            Prend en charge le mouvement du rectangle de caméra autour du joueur.\n

            Paramètres:\n
                - player (Joueur) : Joueur autour duquel la box camera se centrera.\n
        """
        if player.rect.left < self.camera_rect.left:
            self.camera_rect.left = player.rect.left
        if player.rect.right > self.camera_rect.right:
            self.camera_rect.right = player.rect.right
        if player.rect.top < self.camera_rect.top:
            self.camera_rect.top = player.rect.top
        if player.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = player.rect.bottom

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    # Fonction keyboard_control()
    def keyboard_control(self):
        """
            Fonction qui prend en charge le mouvement omnidirectionnel de la caméra dépendant des touches
            préssées par le joueur (flèches directionnelles).
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.camera_rect.x -= self.keyboard_speed
        if keys[pygame.K_RIGHT]: self.camera_rect.x += self.keyboard_speed
        if keys[pygame.K_UP]: self.camera_rect.y -= self.keyboard_speed
        if keys[pygame.K_DOWN]: self.camera_rect.y += self.keyboard_speed

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    # Fonction custom_draw()
    def custom_draw(self,player:Joueur):
        """
            Affiche périodiquement les sprites de tous les objets du groupe de caméra.\n

            Paramètres:\n
                - player (Joueur) : Instance de la classe Joueur.\n

        """
        global global_offset

        self.center_target_camera(player)
        self.box_target_camera(player)
        self.keyboard_control()

        # Affichage du sol 
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surf,ground_offset)

        # Affichage des éléments du groupe de la caméra
        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_pos)  
        global_offset = self.offset


# Classe Points_Paris()
class Points_Paris():
    # Initialisation des points et du graphe de la carte de Paris.
    def __init__(self):
        # Création du graphe.
        self.G = nwx.Graph()

        # Informations des points.
        with open("points_final.json", "r") as json_f:
            points_data = json.load(json_f)
        # On ajoute chaque sommet du graphe.
        for node_id, node_data in points_data.items():
            self.G.add_node(node_id, COORDONNEES=node_data["COORDONNEES"])
        # On ajoute la pondération de chaque branche (distance en pixels entre chaque point et ses adjacents).
        for node_id, node_data in points_data.items():
            for adjacent_node, weight in node_data["ADJACENTS"]:
                self.G.add_edge(node_id, adjacent_node, weight=weight)


    # Accesseurs

    # GETTER
    def get_graphe(self):
        return self.G


    # Fonctions

    # Fonction trouver_trajet()
    def trouver_trajet(self, point_debut:str, point_fin:str) -> list:
        """
            Utilise l'algorithme A* dans le graphe pour trouver le trajet le plus court entre un point et un autre.\n

            Paramètres:\n
                - point_debut (str) : Nom du point de départ.\n
                - point_fin (str) : Nom du point où l'on souhaite arriver.\n
            
            Renvoie:\n
                - (list) : Trajet avec comme élements le nom (str) de tous les points à visiter.\n
        """
        assert type(point_debut) == str and type(point_fin) == str, "Des noms de points en chaînes de caractères sont attendues en paramètres."
        return nwx.algorithms.astar_path(self.G, point_debut, point_fin)

    # Fonction trouver_point_le_plus_proche()
    def trouver_point_le_plus_proche(self, coord_initiale:list) -> str:
        """
            A partir d'un tuple de coordonnées donné en paramètres, la fonction indique le point du graphe le
            plus proche de celle-ci.\n

            Paramètres:\n
                - coord_initiale (list or tuple) : coordonnées du point d'origine.\n

            Renvoie:\n
                - (str) : nom du point trouvé.\n
        """
        dist_min = float("inf")
        point_min = ""
        for nom_point, (x, y) in nwx.get_node_attributes(self.G, 'COORDONNEES').items():
            dist = sqrt((coord_initiale[0]-x)**2+(coord_initiale[1]-y)**2)
            if dist < dist_min:
                dist_min = dist
                point_min = nom_point
        return point_min





# Jeu

# Initialisation de variables et du jeu.

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

global_offset = pygame.math.Vector2()
camera_group = CameraGroup()
graphe_paris = Points_Paris()
player = Joueur(camera_group, "1")

# Icones principales
football_icon = Icon((3864, 1145), camera_group, "football2")



# Boucle principale.
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if pygame.mouse.get_pressed()[0] == 1:
            mouse_pos_on_click = pygame.mouse.get_pos()+global_offset
            player.definir_trajet(mouse_pos_on_click)
        if pygame.mouse.get_pressed()[2] == 1 and not player.est_en_mouvement():
            # Epreuve du footbal
            if player.derniere_visite() == "83" or player.derniere_visite() == "119":
                with open("./epreuves/football.py") as f:
                    exec(f.read())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    screen.fill('#71ddee')

    camera_group.update()
    camera_group.custom_draw(player)

    pygame.display.update()
    clock.tick(60)

# Fin du programme