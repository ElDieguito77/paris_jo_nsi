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

        self.clock = pygame.time.Clock()

        # Mouvement par points
        self.direction_est_fixee = False
        self.dernier_point_visite = point_depart
        self.prochains_points_a_visiter = []

    # Fonction destination_atteinte_rayon()
    def destination_atteinte_rayon(self, destination:str, rayon:int) -> bool:
        """
        
        """
        coord_destination = self.paris_graphe.get_graphe().nodes[destination]["COORDONNEES"]
        dist = sqrt((self.pos[0]-coord_destination[0])**2+(self.pos[1]-coord_destination[1])**2)
        return dist <= rayon

    # Fonction calculer_direction()
    def calculer_direction(self, destination) -> None:
        """
        
        """
        coord_destination = self.paris_graphe.get_graphe().nodes[destination]["COORDONNEES"]
        self.direction = pygame.Vector2(coord_destination[0]-self.pos[0],coord_destination[1]-self.pos[1])

    # Fonction parcourir_trajet()
    def parcourir_trajet(self, trajet:list) -> None:
        """

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
                self.prochains_points_a_visiter = self.paris_graphe.trouver_trajet(self.dernier_point_visite, destination)
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
        self.rect.bottomleft = self.pos-pygame.Vector2(self.rect.width//2,0) # Pour affiche le sprite par rapport au midbottom


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
        self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
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
    def center_target_camera(self,target):
        """
            Permet de center la caméra autour du joueur en le gardant en centre.
        """
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    # Fonction box_target_camera()
    def box_target_camera(self,target):
        """
            Prend en charge le mouvement du rectangle de caméra autour du joueur.
        """
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right
        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        if target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom

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
    def custom_draw(self,player):
        """
            Affiche périodiquement les sprites de tous les objets du groupe de caméra.
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


# Boucle principale.
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos_on_click = pygame.mouse.get_pos()+global_offset
            player.definir_trajet(mouse_pos_on_click)
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