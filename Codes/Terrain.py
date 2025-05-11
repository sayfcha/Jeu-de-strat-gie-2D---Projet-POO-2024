import os
import pygame
from unit import *
from personnages import*


class Terrain():
    def __init__(self):
        self.visible = True  # visibilité
        
         # Définit une image par défaut pour Terrain
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))  # Crée une surface de base
        self.image.fill((100, 100, 100))  # Colore la surface en gris par défaut
    
    
    def apply_effect(self, unit):
        """Appliquer l'effet du terrain à l'unité, implémenté dans les sous-classes"""
        return True
    
    
    def remove_effect(self, unit):
        """Retirer l'effet du terrain sur l'unité, s'il y a un effet persistant"""
        pass

    def draw(self, screen, x, y):
        """Dessine le terrain sur la grille."""
        screen.blit(self.image, (x * CELL_SIZE, y * CELL_SIZE))

class Bush(Terrain):
    def __init__(self):
        super().__init__()
        self.visible = True  # Le buisson est visible
        
        project_root = os.path.dirname(os.path.dirname(__file__))
        image_path = os.path.join(project_root, "images", "bush.png")
        
        self.image = pygame.image.load(image_path)  # Charge l'image du buisson
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))# assurer qu l'image est le bon size

    def apply_effect(self, unit):
     
        if not hasattr(unit, 'original_speed'):
            unit.original_speed = unit.speed # Sauvegarde la vitesse originale
        unit.invisible = True  # Rendre l'unité invisible
        unit.speed = unit.original_speed * 2  # Double la vitesse
        return True
    
        
    
    def remove_effect(self, unit):
        print(f"Before remove: {unit.speed}")
        """Méthode appelée lorsque l'unité quitte le buisson"""
        if hasattr(unit, 'original_speed'):
            unit.speed = unit.original_speed  # # Restaure la vitesse originale
        unit.invisible = False # Rendre l'unité non invisible
        print(f"After remove: {unit.speed}")
        
        
class Rock(Terrain):
    def __init__(self):
        super().__init__()
        self.passable = False  # Par défaut, le rocher est infranchissable
        
        # Chargement de l'image du rocher
        project_root = os.path.dirname(os.path.dirname(__file__))
        image_path = os.path.join(project_root, "images", "rock.png")
        
        self.image = pygame.image.load(image_path)  # Charge l'image du rocher
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))# assurer qu l'image est le bon size


    def apply_effect(self, unit):
        """Gère la logique lorsque l'unité tente d'entrer dans une case rocheuse"""
        if isinstance(unit, Guerrier):
            self.passable = True  # Le Guerrier peut passer le rock
            return True  # Permet au Guerrier de continuer son mouvement
        return False  # Les autres unités ne peuvent pas traverser le rocher

    def remove_effect(self, unit):
        pass
    
class Water(Terrain):
    def __init__(self):
        super().__init__()
        self.visible = True  # L'eau est visible
        
        # Chargement de l'image du rocher
        project_root = os.path.dirname(os.path.dirname(__file__))
        image_path = os.path.join(project_root, "images", "water.png")
        
        self.image = pygame.image.load(image_path)  # Charge l'image de l'eau
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))# assurer qu l'image est le bon size

    def apply_effect(self, unit):
        """Méthode appelée lorsque l'unité traverse de l'eau"""
        if not hasattr(unit, 'original_speed'):
            unit.original_speed = unit.speed  # Sauvegarde la vitesse originale
        unit.speed = max(1, int(unit.original_speed * 0.5)) # Ralentit la vitesse
        
        if isinstance(unit, Mage):
            self.passable = False  # Le Mage peut  passer le water 
            return False  # Permet au Guerrier de continuer son mouvement
        return True  # Les autres unités ne peuvent pas traverser le rocher
      
    
    
    def remove_effect(self, unit):
        """Méthode appelée lorsque l'unité quitte l'eau"""
        if hasattr(unit, 'original_speed'):
            unit.speed = unit.original_speed  # revient au vitesse original
      
      
class HealthPack(Terrain):
    def __init__(self):
        super().__init__()
        self.visible = True  # Le pack de soins est visible
        
         # Chargement de l'image du pack de soins
        project_root = os.path.dirname(os.path.dirname(__file__))
        image_path = os.path.join(project_root, "images", "health_pack.png")
        

        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # 确保大小正确

    def apply_effect(self, unit):
        """
        Soigne l'unité d'un point de vie et transforme la case en terrain normal.
        """
        if hasattr(unit, 'health') and hasattr(unit, 'max_health'):
            if unit.health < unit.max_health:  # Soigne seulement si l'unité n'est pas en pleine santé
                unit.health = min(unit.health + 1, unit.max_health) #si le santé est déja au max, ne soigne pas 
                print(f"{unit} has healed 1 HP!")
        
        # Transforme la case actuelle en terrain normal
        unit.replace_current_terrain(Terrain())

        return True  # L'unité peut continuer son mouvement

