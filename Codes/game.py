
import pygame
import random
import os 


from unit import *
from unit import GRID_SIZE, Unit, HEIGHT, WHITE, BLACK, RED, WIDTH, YELLOW 
from personnages import *
from skills import *
from unit import *
from Terrain import *

class GameBoard:
    def __init__(self, size, occupied_positions):
        self.size = size
        self.grid = [[Terrain() for _ in range(size)] for _ in range(size)]
        
        # Assurez-vous que la zone de gauche en bas à droite en haut est remplie de cases d'eau
        self.create_water_path()
        
        # Générer des autres cases aléatoires, en évitant les cases d'eau et les positions occupées
        self.place_terrain(Bush, random.randint(10, 20), occupied_positions)
        self.place_terrain(Rock, random.randint(30, 50), occupied_positions)
        self.place_terrain(HealthPack, random.randint(10, 15), occupied_positions)
       
    def create_water_path(self):
        """Génère un chemin d'eau de gauche en bas à droite en haut avec une épaisseur de 3 cases"""
        for i in range(self.size):
            for j in range(max(0, i - 1), min(self.size, i + 2)):  # Contrôle une épaisseur de 3 cases
                self.grid[self.size - 1 - i][j] = Water()  # Remplit les cases d'eau en diagonale

    def place_terrain(self, terrain_class, count, occupied_positions):
        """Place un terrain aléatoire en évitant les positions occupées et les cases d'eau"""
        available_positions = [
            (x, y) for x in range(self.size) for y in range(self.size)
            if isinstance(self.grid[x][y], Terrain) and not isinstance(self.grid[x][y], Water)  # Éviter de couvrir les case water
            and (x, y) not in occupied_positions
        ]
        
        random.shuffle(available_positions)
        for _ in range(min(count, len(available_positions))):
            x, y = available_positions.pop()
            self.grid[x][y] = terrain_class()


   
    def draw(self,screen):
        for y in range(self.size):
            for x in range(self.size):
                self.grid[y][x].draw(screen,x,y) # Dessine chaque case
                

class Game:
    """
    Classe pour représenter le jeu.

    ...
    Attributs
    ---------
    screen: pygame.Surface
        La surface de la fenêtre du jeu.
    player_units : list[Unit]
        La liste des unités du joueur.
    enemy_units : list[Unit]
        La liste des unités de l'adversaire.
    points : Unit
        Représente le pointeur pour sélectionner des cibles
    """

    def __init__(self, screen):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """
    
        self.screen = screen
        #self.board = GameBoard(GRID_SIZE)
        self.player_units = [Mage(0, 0, 'player',self),
                             Voleur(2, 0, 'player',self),
                             Guerrier(0, 2, 'player',self)]

        self.enemy_units = [Mage(GRID_SIZE - 1, GRID_SIZE - 1, 'enemy',self), 
                            Voleur(GRID_SIZE - 1, GRID_SIZE - 3, 'enemy',self),
                            Guerrier(GRID_SIZE - 3, GRID_SIZE - 1, 'enemy',self)]
        
        
        # Collect positions of all characters to avoid terrain overlap
        occupied_positions = {(unit.x, unit.y) for unit in self.player_units + self.enemy_units}
        self.board = GameBoard(GRID_SIZE, occupied_positions)
        self.point = Unit(0,0,"pointeur",self)
        self.point_aff = False
        
    
    def is_occupied(self, x, y):
        for unit in self.player_units + self.enemy_units:
            if unit.x == x and unit.y == y:
                return True
        return False


    



  
    def draw_hud(self):
        """Affiche un HUD stylé avec des barres de vie et des sections bien organisées."""

        # Couleurs
        BG_COLOR = (30, 30, 30)  # Fond du HUD
        BORDER_COLOR = (200, 200, 200)  # Bordure du HUD
        HEALTH_COLOR = (0, 200, 0)  # Couleur des PV
        SHIELD_COLOR = (0, 100, 255)  # Couleur du bouclier
        MANA_COLOR = (150, 0, 200)  # Couleur de la barre de mana (pour les mages)

        # Dimensions et positions
        hud_x = CELL_SIZE * GRID_SIZE + 20
        hud_y = 50
        hud_width = 600
        hud_height = HEIGHT - 100
        padding = 10

        # Dessiner le fond du HUD
        pygame.draw.rect(self.screen, BG_COLOR, (hud_x, hud_y, hud_width, hud_height))
        pygame.draw.rect(self.screen, BORDER_COLOR, (hud_x, hud_y, hud_width, hud_height), 3)  # Bordure

        # Titre du HUD
        chemin_police = "police/police.TTF"
        font_title = pygame.font.Font(chemin_police, 30)
        font_body = pygame.font.Font(chemin_police, 20)
        title_surface = font_title.render("Informations", True, WHITE)
        self.screen.blit(title_surface, (hud_x + padding, hud_y + padding))

        #legendes
        square_size = 15
        pygame.draw.rect(self.screen, HEALTH_COLOR, (hud_x+400, 150, square_size, square_size))
        vie=font_body.render('Health',True,(255,255,255))
        self.screen.blit(vie, (hud_x+405+square_size, 150))    # on trace une legende pour indiquer que la barre correspond à la barre de  vie

        pygame.draw.rect(self.screen, SHIELD_COLOR, (hud_x+400, 170, square_size, square_size))
        shield=font_body.render('Shield',True,(255,255,255))
        self.screen.blit(shield, (hud_x+405+square_size, 170))     #legende barre de shield

        pygame.draw.rect(self.screen, MANA_COLOR, (hud_x+400, 190, square_size, square_size))
        mana_=font_body.render('Mana',True,(255,255,255))
        self.screen.blit(mana_, (hud_x+405+square_size, 190))  #legende barre de mana 








        # Section joueur 1
        y_offset = hud_y + 50
        section_title = font_title.render("Joueur 1", True, WHITE)
        self.screen.blit(section_title, (hud_x + padding, y_offset))
        y_offset += 30

        for selected_unit in self.player_units:
            # Afficher l'image correspondante au joueur 
            unit_name = font_body.render(f"{selected_unit.nom}", True, WHITE)
            chemin=selected_unit.image_chemins[selected_unit.nom]
            self.image = pygame.image.load(chemin)
            self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
            
            self.screen.blit(self.image, (hud_x + padding, y_offset))

            # Afficher les barres de PV et bouclier
            bar_x = hud_x + padding + 50
            bar_width = hud_width /2 - 10 * padding 
            bar_height = 10

            # Barre de PV
            pv_ratio = selected_unit.health / selected_unit.max_health
            pygame.draw.rect(self.screen, HEALTH_COLOR, (bar_x, y_offset, int(bar_width * pv_ratio), bar_height))
            pygame.draw.rect(self.screen, BORDER_COLOR, (bar_x, y_offset, bar_width, bar_height), 1)

            # Barre de bouclier
            shield_ratio = selected_unit.defense_shield / selected_unit.max_defense_shield
            pygame.draw.rect(self.screen, SHIELD_COLOR, (bar_x, y_offset + 15, int(bar_width * shield_ratio), bar_height))
            pygame.draw.rect(self.screen, BORDER_COLOR, (bar_x, y_offset + 15, bar_width, bar_height), 1)

            # Afficher la barre de mana si c'est un mage
            if isinstance(selected_unit, Mage):
                if selected_unit.mana > selected_unit.max_mana:
                    selected_unit.max_mana = selected_unit.mana
                mana_ratio = selected_unit.mana / selected_unit.max_mana
                pygame.draw.rect(self.screen, MANA_COLOR, (bar_x, y_offset + 30, int(bar_width * mana_ratio), bar_height))
                pygame.draw.rect(self.screen, BORDER_COLOR, (bar_x, y_offset + 30, bar_width, bar_height), 1)

            y_offset += 50

        # Section joueur 2
        y_offset += 10
        section_title = font_title.render("Joueur 2", True, WHITE)
        self.screen.blit(section_title, (hud_x + padding, y_offset))
        y_offset += 30

        for selected_unit in self.enemy_units:
            # Afficher le nom
            unit_name = font_body.render(f"{selected_unit.nom}", True, WHITE)
            chemin=selected_unit.image_chemins[selected_unit.nom]
            self.image = pygame.image.load(chemin)
            self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
            
            self.screen.blit(self.image, (hud_x + padding, y_offset))

            # Afficher les barres de PV et bouclier
            bar_x = hud_x + padding + 50
            bar_width = hud_width /2 - 10 * padding 
            bar_height = 10

            # Barre de PV
            pv_ratio = selected_unit.health / selected_unit.max_health
            pygame.draw.rect(self.screen, HEALTH_COLOR, (bar_x, y_offset, int(bar_width * pv_ratio), bar_height))
            pygame.draw.rect(self.screen, BORDER_COLOR, (bar_x, y_offset, bar_width, bar_height), 1)

            # Barre de bouclier
            shield_ratio = selected_unit.defense_shield / selected_unit.max_defense_shield
            pygame.draw.rect(self.screen, SHIELD_COLOR, (bar_x, y_offset + 15, int(bar_width * shield_ratio), bar_height))
            pygame.draw.rect(self.screen, BORDER_COLOR, (bar_x, y_offset + 15, bar_width, bar_height), 1)

            y_offset += 50

   

    def handle_player_turn(self):
        
        """Tour du joueur"""

        
    
        for selected_unit in self.player_units:

            # Afficher la victoire (fin de partie)
            if len(self.enemy_units) == 0:
                # Quitter Pygame proprement
                pygame.mixer.music.stop()
                pygame.quit()

                # Réinitialisation de Pygame pour afficher l'écran de fin
                pygame.init()
                #Initialisation de la musique
                pygame.mixer.init()
                pygame.mixer.music.load("music/The_Bridge_of_Khazad_Dum.mp3")
                pygame.mixer.music.play(-1)  # Joue en boucle infinie

                # Instanciation de la fenêtre
                screen = pygame.display.set_mode((1450, 750))
                pygame.display.set_caption("Mon jeu de stratégie")

                # Écran titre
                image = pygame.image.load("images/minas_tirith.jpg")
                # Initialiser une police pour le texte
                font = pygame.font.Font(None, 30)  # Police par défaut, taille 30
                text1 = font.render("Appuyez sur SPACE pour quitter le jeu", True, BLACK)

                font = pygame.font.Font(None, 40)  # Police par défaut, taille 60
                text2 = font.render("La communauté de l'anneau a battu Sauron !", True, BLACK)

                # Obtenir la position centrale de l'image
                image_rect = image.get_rect(center=(700, 600))

                # Positionner le texte
                text_rect1 = text1.get_rect(center=(950,150))
                # Positionner le texte
                text_rect2 = text2.get_rect(center=(950,100))

                running = True
                while running:
                    # Gestion des événements
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                running = False

                    # Remplir l'écran avec une couleur unie (optionnel)
                    screen.fill((0, 0, 0))  # Fond noir

                    # Dessiner l'image sur l'écran
                    screen.blit(image, image_rect)

                    # Dessiner le texte sur l'écran
                    screen.blit(text1, text_rect1)
                    screen.blit(text2, text_rect2)

                    # Mettre à jour l'affichage
                    pygame.display.flip()

                # Quitter le jeu
                exit()

            # Tant que l'unité n'a pas terminé son tour
            selected_unit.is_selected = True # Marque l'unité comme sélectionnée, affiche la portée de déplacement
            
             # Met à jour l'effet du terrain actuel de l'unité (impacte le prochain mouvement)
            current_terrain = self.board.grid[selected_unit.y][selected_unit.x]
            current_terrain.apply_effect(selected_unit)  # Met à jour l'effet, par exemple, un changement de vitesse
            
            # Met à jour la portée de déplacement de l'unité
            selected_unit.update_move_range()
            selected_unit.draw_move_range(self.screen)# Met en surbrillance les cases accessibles

            #Affichage du HUD
            self.flip_display()
            
            # Si l'unité est un mage, il récupère 1 point de mana par tour
            if isinstance(selected_unit,Mage):
                selected_unit.mana += 1

            # Si l'unité est un voleur, il perd son invisibilité
            if isinstance(selected_unit,Voleur):
                selected_unit.is_invisible = False

            # Enregistrement de la position initiale de l'unité
            temp1 = selected_unit.x
            temp2 = selected_unit.y

            has_acted = False# Indique si l'unité a terminé son action, initialement elle ne l'a pas encore fait

            chemin_police = "police/police.TTF"
            
            while not has_acted:
                

                # Affichage du joueur
                font = pygame.font.Font(chemin_police, 30)
                y_offset = 500
                x_offset = CELL_SIZE * GRID_SIZE + 100
                unit_status = f"A {selected_unit.nom} de jouer "
                unit_surface = font.render(unit_status, True, WHITE)
                self.screen.blit(unit_surface, (x_offset, y_offset))
              
                if isinstance(selected_unit,Mage):
                    font = pygame.font.Font(None,30)
                    y_offset =550
                    x_offset = CELL_SIZE * GRID_SIZE + 50
                    unit_status = ["Déplacement avec les touches du clavier",
                                    "",
                                    " - Ne rien faire: tapez 1",
                                    " - Attaquer au corps à corps: tapez 2",  #afficher le nombre de mana
                                    " - Soigner: tapez 3",
                                    " - Boule de feu: tapez 4"]
                    for unit_status in unit_status:
                        unit_surface = font.render(unit_status, True, WHITE)
                        self.screen.blit(unit_surface, (x_offset, y_offset))
                        y_offset += 20
                
                # Si l'unité est un voleur
                elif isinstance(selected_unit,Voleur):
                    selected_unit.is_invisble = False
                    font = pygame.font.Font(None, 30)
                    y_offset = 550
                    x_offset = CELL_SIZE * GRID_SIZE + 50
                    unit_status = ["Déplacement avec les touches du clavier",
                                    "",
                                    "Compétences:",
                                    " - Ne rien faire: tapez 1",
                                    " - Attaquer au corps à corps: tapez 2",
                                    " - Se rendre invisible: tapez 3"]
                    for unit_status in unit_status:
                        unit_surface = font.render(unit_status, True, WHITE)
                        self.screen.blit(unit_surface, (x_offset, y_offset))
                        y_offset += 20

                elif isinstance(selected_unit,Guerrier):
                    
                    font = pygame.font.Font(None, 30)
                    y_offset = 550
                    x_offset = CELL_SIZE * GRID_SIZE + 50
                    unit_status = ["Déplacement avec les touches du clavier",
                                    "",
                                    "Compétences:",
                                    " - Ne rien faire: tapez 1",
                                    " - Attaquer au corps à corps: tapez 2",
                                    " - Tirer à l'arc: tapez 3"]
                    for unit_status in unit_status:
                        unit_surface = font.render(unit_status, True, WHITE)
                        self.screen.blit(unit_surface, (x_offset, y_offset))
                        y_offset += 25
                
                # Mettre à jour l'affichage
                pygame.display.flip() 

                for event in pygame.event.get():

                    attack = False
                    self.special_skill = False
                    self.special_skill2 = False
                    no_action = False

                    # Gestion de la fermeture de la fenêtre
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    # Gestion des touches du clavier
                    if event.type == pygame.KEYDOWN:

                        # Déplacement (touches fléchées)
                        dx, dy = 0, 0
                        
                        if event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        elif event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1
                        elif event.key == pygame.K_1:
                            no_action = True
                        elif event.key == pygame.K_2:
                            attack = True
                        elif event.key == pygame.K_3:
                            self.special_skill = True
                        elif event.key == pygame.K_4:
                            self.special_skill2 = True

                        
                        # Obtenir la nouvelle position
                        new_x = selected_unit.x + dx
                        new_y = selected_unit.y + dy
                        
                        # Vérifie si la nouvelle position est dans les cases accessibles (green_cases)
                        if (new_x, new_y) in selected_unit.green_cases:
                            
                           # **Supprimer l'effet du terrain actuel**
                            old_terrain = self.board.grid[selected_unit.y][selected_unit.x]
                            new_terrain = self.board.grid[new_y][new_x]   
                            
                            old_terrain.remove_effect(selected_unit)  # Supprime l'effet du terrain actuel
                            selected_unit.move(dx, dy) # Effectue le déplacement                       
                            new_terrain.apply_effect(selected_unit)  # Applique l'effet du nouveau terrain
                            
                            self.flip_display() 
                        

                        if attack: #attaque TOUS les ennemis qui sont à UN de distance.
                            for enemy in self.enemy_units:
                                if abs(enemy.x - selected_unit.x) <= 1 and abs(enemy.y - selected_unit.y) <= 1:
                                    if isinstance(enemy,Voleur):
                                        if not enemy.is_invisible:
                                            selected_unit.attack(enemy)
                                            has_acted = True
                                            selected_unit.is_selected = False
                                    else:
                                        selected_unit.attack(enemy)
                                        has_acted = True
                                        selected_unit.is_selected = False

                        if no_action:
                            has_acted = True
                            selected_unit.is_selected = False

                        elif isinstance(selected_unit,Voleur):
                            selected_unit.is_invisible = False
                            if self.special_skill:
                                selected_unit.invisibility()
                                has_acted = True
                                selected_unit.is_selected = False


                        #Sélection d'une cible
                        elif self.special_skill:
                            target = None
                            choose = False
                            self.point.x, self.point.y = selected_unit.x, selected_unit.y  # Centrez le pointeur sur l'unité
                            self.point.init_x, self.point.init_y = selected_unit.x, selected_unit.y  # Centrez le pointeur sur l'unité
                            while not choose and target is None:
                                self.point_aff = True
                                self.flip_display() #affichage du pointeur
                                
                                for event in pygame.event.get():

                                    if event.type == pygame.KEYDOWN:
                                        dx, dy = 0, 0
                                        if event.key == pygame.K_LEFT:
                                            dx = -1
                                        elif event.key == pygame.K_RIGHT:
                                            dx = 1
                                        elif event.key == pygame.K_UP:
                                            dy = -1
                                        elif event.key == pygame.K_DOWN:
                                            dy = 1
                                        elif event.key == pygame.K_SPACE:
                                            choose = True  # Valide la cible
                                        elif event.key == pygame.K_ESCAPE:
                                            self.point_aff = False
                                            choose = True
                                            target = 1
                                            self.special_skill = False
                                            self.flip_display()
                                            break
                                            
                                        # Déplace le pointeur dans la portée de 3
                                        if selected_unit.x - 3 <= self.point.x + dx <= selected_unit.x + 3 and selected_unit.y - 3 <= self.point.y + dy <= selected_unit.y + 3:
                                            self.point.move(dx,dy)
                                            self.flip_display()
                                            
                                            
                                        
                                        if choose:
                                            self.point_aff = False
                                            for enemy in self.enemy_units:
                                                for unit in self.player_units:
                                                    if (enemy.x == self.point.x and enemy.y == self.point.y):
                                                        target = enemy
                                                        break  # Trouvé la cible
                                                    if (unit.x == self.point.x and unit.y == self.point.y):
                                                        target = unit
                                                        break  # Trouvé la cible

                                            if target is None:
                                                # Affiche un message d'erreur si aucune cible n'est trouvée
                                                font = pygame.font.Font(None, 40)
                                                error_msg = "Aucune cible valide à cet endroit !"
                                                error_surface = font.render(error_msg, True, RED)
                                                self.screen.blit(error_surface, (CELL_SIZE * GRID_SIZE + 100, 600))
                                                pygame.display.flip()
                                                pygame.time.wait(1000)
                                                choose = False

                                            if isinstance(target,Voleur): # Vérification si la cible n'est pas invisible
                                                if target.is_invisible:
                                                    font = pygame.font.Font(None, 40)
                                                    error_msg = "Cette unité porte l'anneau ! Impossible !"
                                                    error_surface = font.render(error_msg, True, RED)
                                                    self.screen.blit(error_surface, (CELL_SIZE * GRID_SIZE + 50, 600))
                                                    pygame.display.flip()
                                                    pygame.time.wait(1000)
                                                    target = None
                                                    choose = False
                                    
                            if self.special_skill and isinstance(selected_unit,Guerrier):
                                selected_unit.bow(target)
                                has_acted = True
                            if self.special_skill and isinstance(selected_unit,Mage):
                                selected_unit.heal(target) #Peut accumuler des manas à tous les tours pour les utiliser d'un coup sur quelqu'un
                                has_acted = True
                                selected_unit.is_selected = False
                            
                            #Affichage des informations de coups critiques et manqués
                            if selected_unit.miss:
                                font = pygame.font.Font(None, 40)
                                y_offset = CELL_SIZE * target.y
                                x_offset = CELL_SIZE * target.x
                                a_status = f"Raté !"
                                a_surface = font.render(a_status, True, RED)
                                self.screen.blit(a_surface, (x_offset, y_offset))
                                # Mettre à jour l'affichage
                                pygame.display.flip()
                                pygame.time.wait(1000)
                                selected_unit.miss = False
                                selected_unit.critique = False

                            elif selected_unit.critique:
                                font = pygame.font.Font(None, 40)
                                y_offset = CELL_SIZE * target.y
                                x_offset = CELL_SIZE * target.x
                                a_status = f"Critique !"
                                a_surface = font.render(a_status, True, RED)
                                self.screen.blit(a_surface, (x_offset, y_offset))
                                # Mettre à jour l'affichage
                                pygame.display.flip()
                                pygame.time.wait(1000)
                                selected_unit.critique = False

                        elif self.special_skill2 and isinstance(selected_unit,Mage):
                            target = None
                            choose = False
                            self.point.x, self.point.y = selected_unit.x, selected_unit.y
                            self.point.init_x, self.point.init_y = selected_unit.x, selected_unit.y  # Centrez le pointeur sur l'unité
                            while not choose and target is None:
                                self.point_aff = True
                                self.flip_display() #affichage du pointeur
                                for event in pygame.event.get():

                                    if event.type == pygame.KEYDOWN:
                                        dx, dy = 0, 0
                                        if event.key == pygame.K_LEFT:
                                            dx = -1
                                        elif event.key == pygame.K_RIGHT:
                                            dx = 1
                                        elif event.key == pygame.K_UP:
                                            dy = -1
                                        elif event.key == pygame.K_DOWN:
                                            dy = 1
                                        elif event.key == pygame.K_SPACE:
                                            choose = True  # Valide la cible
                                        elif event.key == pygame.K_ESCAPE:
                                            self.point_aff = False
                                            choose = True
                                            target = 1
                                            self.special_skill2 = False
                                            break  # Valide la cible

                                        # Déplace le pointeur dans la portée de 2
                                        if selected_unit.x - 2 <= self.point.x + dx <= selected_unit.x + 2 and selected_unit.y - 2 <= self.point.y + dy <= selected_unit.y + 2:
                                            self.point.move(dx, dy)
                                            self.flip_display()
                                        
                                        if choose and self.special_skill2:
                                            self.point_aff = False
                                            selected_unit.fire_ball(self.point.x, self.point.y, self.player_units + self.enemy_units)
                                            has_acted = True

                            #Affichage des informations de coups critiques et manqués
                            if selected_unit.miss:
                                font = pygame.font.Font(None, 40)
                                y_offset = CELL_SIZE * self.point.y
                                x_offset = CELL_SIZE * self.point.x
                                a_status = f"Raté !"
                                a_surface = font.render(a_status, True, RED)
                                self.screen.blit(a_surface, (x_offset, y_offset))
                                # Mettre à jour l'affichage
                                pygame.display.flip()
                                pygame.time.wait(1000)
                                selected_unit.miss = False
                                selected_unit.critique = False

                            elif selected_unit.critique:
                                font = pygame.font.Font(None, 40)
                                y_offset = CELL_SIZE * self.point.y
                                x_offset = CELL_SIZE * self.point.x
                                a_status = f"Critique !"
                                a_surface = font.render(a_status, True, RED)
                                self.screen.blit(a_surface, (x_offset, y_offset))
                                # Mettre à jour l'affichage
                                pygame.display.flip()
                                pygame.time.wait(1000)
                                selected_unit.critique = False
                                self.flip_display()
                        
            #suppression des unités éliminées
            for enemy in self.enemy_units:
                if enemy.health <= 0:
                    self.enemy_units.remove(enemy)
            
            for unit in self.player_units:
                if unit.health <= 0:
                    self.player_units.remove(unit)
            
            selected_unit.is_selected = False
            self.flip_display()
            
            
            
             # Forcer la vitesse de réinitialisation à la vitesse d'origine
            selected_unit.speed = selected_unit.original_speed
            
            
            self.flip_display()  
                        

    
    
    
    def handle_enemy_turn(self):
        """IA très simple pour les ennemis."""
        for enemy in self.enemy_units:
            
            # Applique l'effet de séjour sur le terrain actuel
            current_terrain = self.board.grid[enemy.y][enemy.x]
            current_terrain.apply_effect(enemy)
            
            
            is_occupied = False
            # Déplacement aléatoire
            target = random.choice(self.player_units)
            
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
            
            
            # Vérifie si la position cible est occupée par une autre unité
            new_x, new_y = enemy.x + dx, enemy.y + dy
            
            if not self.is_occupied(new_x, new_y):
                enemy.move(dx, dy)

                # Réapplique les effets du terrain après le déplacement
                current_terrain = self.board.grid[enemy.y][enemy.x]
                current_terrain.apply_effect(enemy)
            
            
            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                if isinstance(target,Voleur):
                    if target.is_invisible :
                        pass
                    else:
                        enemy.attack(target)
                else:
                    enemy.attack(target)
                if target.health < 0:
                    self.player_units.remove(target)


    def flip_display(self):
        """Affiche le jeu et le HUD."""

        # Affiche la grille
        self.screen.fill(BLACK)
        
        #Affiche les terrains depuis le gameBoard
        self.board.draw(self.screen)
        
        # Dessine la case verte de l'unité sélectionnée
        for unit in self.player_units:
            if unit.is_selected:
                unit.draw_move_range(self.screen)


        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Affiche les unités
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)

        # Affiche le pointeur
        if self.point_aff:
            pygame.draw.rect(self.screen, RED, (self.point.x * CELL_SIZE,
                            self.point.y * CELL_SIZE, CELL_SIZE, CELL_SIZE),width=5)
            font = pygame.font.Font(None, 30)
            red = (255, 0, 0)
            info = "Echap pour annuler"
            info_surface = font.render(info, True, RED)
            self.screen.blit(info_surface, (CELL_SIZE * GRID_SIZE + 100, 10))
            
            if self.special_skill:
                case_yellow = []
                for dx in range(-3,4):
                    for dy in range(-3,4):
                        
                        rect_x = self.point.init_x + dx
                        rect_y = self.point.init_y + dy
                        case_yellow.append((rect_x,rect_y))
                
                for rect_x, rect_y in case_yellow:
                    pygame.draw.rect(self.screen, YELLOW, (rect_x * CELL_SIZE, rect_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
                    
            if self.special_skill2:
                case_yellow = []
                for dx in range(-2,3):
                    for dy in range(-2,3):
                        
                        rect_x = self.point.init_x + dx
                        rect_y = self.point.init_y + dy
                        case_yellow.append((rect_x,rect_y))
                
                for rect_x, rect_y in case_yellow:
                    pygame.draw.rect(self.screen, YELLOW, (rect_x * CELL_SIZE, rect_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
                    
                case_yellow = []
                for dx in range(-1,2):
                    for dy in range(-1,2):
                        
                        rect_x = self.point.x + dx
                        rect_y = self.point.y + dy
                        case_yellow.append((rect_x,rect_y))
                
                for rect_x, rect_y in case_yellow:
                    pygame.draw.rect(self.screen, (255, 165, 0), (rect_x * CELL_SIZE, rect_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
                

        # Affiche le HUD
        self.draw_hud()

        # Rafraîchit l'écran
        pygame.display.flip()





def main():

    # Initialisation de Pygame
    pygame.init()

    #Initialisation de la musique
    pygame.mixer.init()
    pygame.mixer.music.load("music/The_Shire.mp3")
    pygame.mixer.music.play(-1)  # Joue en boucle infinie

    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((1450, 750))
    pygame.display.set_caption("Mon jeu de stratégie")

    # Écran titre
    image = pygame.image.load("images/conte.jpg") #use / instead of \
    # Initialiser une police pour le texte
    font = pygame.font.Font(None, 30)  # Police par défaut, taille 30
    text1 = font.render("Appuyez sur SPACE pour lancer le jeu", True, BLACK)

    font = pygame.font.Font(None, 60)  # Police par défaut, taille 60
    text2 = font.render("Bienvenue dans la Comté !", True, BLACK) 

    # Obtenir la position centrale de l'image
    image_rect = image.get_rect(center=(700, 500))

    # Positionner le texte
    text_rect1 = text1.get_rect(center=(950,150))
    # Positionner le texte
    text_rect2 = text2.get_rect(center=(950,100))

    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False

        # Remplir l'écran avec une couleur unie (optionnel)
        screen.fill((0, 0, 0))  # Fond noir

        # Dessiner l'image sur l'écran
        screen.blit(image, image_rect)

        # Dessiner le texte sur l'écran
        screen.blit(text1, text_rect1)
        screen.blit(text2, text_rect2)

        # Mettre à jour l'affichage
        pygame.display.flip()

    # Quitter Pygame proprement
    pygame.mixer.music.stop()
    pygame.quit()


    # Initialisation de Pygame
    screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE * 2, GRID_SIZE * CELL_SIZE))
    pygame.display.set_caption("Mon jeu de stratégie")
    pygame.init()

    print(type(screen))

    #Initialisation de la musique
    pygame.mixer.init()
    pygame.mixer.music.load("music/The_Battle_of_the_Pelennor_Fields.mp3")
    pygame.mixer.music.play(-1)  # Joue en boucle infinie

    game = Game(screen)

    # Boucle principale du jeu
    while True:
        game.handle_player_turn()
        game.handle_enemy_turn()


if __name__ == "__main__":
    main()
