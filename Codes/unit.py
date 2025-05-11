import pygame

# Constantes
GRID_SIZE = 17  # Taille de la grille (nombre de cases par côté)
CELL_SIZE = 45  # Taille d'une cellule en pixels
WIDTH = GRID_SIZE * CELL_SIZE  # Largeur totale de la grille
HEIGHT = GRID_SIZE * CELL_SIZE  # Hauteur totale de la grille
FPS = 30  # Nombre d'images par seconde
WHITE = (255, 255, 255)  # Couleur blanche
BLACK = (0, 0, 0)  # Couleur noire
RED = (255, 0, 0)  # Couleur rouge
BLUE = (0, 0, 255)  # Couleur bleue
GREEN = (0, 255, 0)  # Couleur verte pour les cases de mouvement
YELLOW = (0, 255, 255)  # Couleur jaune

class Unit:
    """
    Classe pour représenter une unité et gérer ses déplacements.

    Attributs :
    -----------
    - x : Position X de l'unité dans la grille.
    - y : Position Y de l'unité dans la grille.
    - team : Équipe de l'unité ('player', 'enemy' ou 'pointeur').
    - is_selected : Indique si l'unité est sélectionnée.
    - game : Instance du jeu pour accéder à la grille et aux éléments.

    Méthodes :
    ----------
    - move(dx, dy) : Déplace l'unité dans la direction donnée.
    - update_move_range() : Met à jour les cases accessibles pour l'unité.
    - draw_move_range(screen) : Dessine les cases accessibles sur l'écran.
    - replace_current_terrain(new_terrain) : Remplace le terrain actuel de l'unité.
    """

    def __init__(self, x, y, team, game):
        self.x = x  # Position de l'unité sur l'axe X
        self.y = y  # Position de l'unité sur l'axe Y
        self.team = team  # Équipe de l'unité ('player', 'enemy' ou 'pointeur')
        self.__is_selected = False  # Indique si l'unité est sélectionnée
        self.game = game  # Référence à l'instance du jeu
        self.green_cases = []  # Liste des cases accessibles (mises en évidence)
        
    def move(self, dx, dy):
        """
        Déplace l'unité d'une distance donnée (dx, dy).
        """
        dx = int(dx)
        dy = int(dy)
        
        new_x = int(self.x + dx)
        new_y = int(self.y + dy)
        
        # Déplacement spécifique pour le pointeur
        if self.team == 'pointeur':
            if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                self.x = new_x
                self.y = new_y

        # Déplacement IA simple pour les ennemis
        elif self.team == 'enemy':
            if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                self.x = new_x
                self.y = new_y

        else:  # Déplacement des unités du joueur
            # Vérifie si la destination est dans la portée autorisée
            if (new_x, new_y) not in self.green_cases:
                print(f"Déplacement vers ({new_x}, {new_y}) interdit.")
                return
            
            if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                # Gestion du terrain
                old_terrain = self.game.board.grid[self.y][self.x]
                new_terrain = self.game.board.grid[new_y][new_x]

                # Applique les effets du terrain
                can_move = new_terrain.apply_effect(self)
                print(f"Tentative de déplacement vers ({new_x}, {new_y}) - Autorisé : {can_move}")

                if can_move:  # Met à jour la position si le mouvement est autorisé
                    old_terrain.remove_effect(self)
                    self.x = new_x
                    self.y = new_y
                    print("Déplacement effectué :", new_x, new_y)
                else:
                    print("Déplacement bloqué par le terrain :", new_x, new_y)

    def update_move_range(self):
        """
        Met à jour la liste des cases accessibles pour l'unité.
        Les mages ignorent les restrictions liées à l'eau.
        """
        from personnages import Mage
        from Terrain import Water

        self.green_cases = []  # Réinitialise les cases accessibles
        start_x, start_y = self.x, self.y  # Position initiale de l'unité
        speed = int(self.speed)
        print(f"Vitesse : {speed}, Position : ({self.x}, {self.y})")

        # Ajoute la position actuelle comme case accessible
        self.green_cases.append((start_x, start_y))

        # Parcourt la zone autour de l'unité pour calculer les déplacements possibles
        for dy in range(-speed, speed + 1):
            for dx in range(-speed, speed + 1):
                green_x = start_x + dx
                green_y = start_y + dy

                # Vérifie si la case est dans les limites de la grille
                if 0 <= green_x < GRID_SIZE and 0 <= green_y < GRID_SIZE:
                    # Vérifie si la case est occupée
                    if not self.game.is_occupied(green_x, green_y):
                        terrain = self.game.board.grid[green_y][green_x]

                        # Ajoute la case si le terrain permet le déplacement
                        if terrain.apply_effect(self):
                            self.green_cases.append((green_x, green_y))

        # Les mages ne sont pas affectés par les restrictions des cases d'eau
        if not isinstance(self, Mage):
            return

        # Filtre les cases bloquées par les terrains d'eau
        filtered_cases = self.green_cases[:]
        for green_x, green_y in self.green_cases:
            for water_y in range(GRID_SIZE):
                for water_x in range(GRID_SIZE):
                    terrain = self.game.board.grid[water_y][water_x]
                    if isinstance(terrain, Water):
                        # Logique de restriction pour les terrains d'eau
                        if (
                            (start_x <= water_x and start_y <= water_y and green_x > water_x and green_y > water_y) or
                            (start_x >= water_x and start_y >= water_y and green_x < water_x and green_y < water_y) or
                            (start_x <= water_x and start_y >= water_y and green_x > water_x and green_y < water_y) or
                            (start_x >= water_x and start_y <= water_y and green_x < water_x and green_y > water_y)
                        ):
                            if (green_x, green_y) in filtered_cases:
                                filtered_cases.remove((green_x, green_y))
        
        self.green_cases = filtered_cases  # Met à jour les cases accessibles

    def draw_move_range(self, screen):
        """
        Dessine les cases accessibles en vert sur l'écran.
        """
        for green_x, green_y in self.green_cases:
            pygame.draw.rect(screen, GREEN, (green_x * CELL_SIZE, green_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
    
    def replace_current_terrain(self, new_terrain):
        """
        Remplace le terrain actuel sur lequel se trouve l'unité.
        """
        self.game.board.grid[self.y][self.x] = new_terrain

    @property
    def is_selected(self):
        return self.__is_selected

    @is_selected.setter
    def is_selected(self, value):
        if not isinstance(value, bool):
            raise ValueError("L'attribut 'is_selected' doit être un booléen.")
        self.__is_selected = value

    image_chemins = {
        "Bilbon": "images/Bilbon.png",
        "Gollum": "images/gollum.png",
        "Le Roi-Sorcier d'Angmar": "images/Angmar.png",
        "Aragorn": "images/aragorn.jpg",
        "Gandalf le Gris": "images/gandalf.png",
        "Saroumane le Blanc": "images/Saroumane.png",
    }
