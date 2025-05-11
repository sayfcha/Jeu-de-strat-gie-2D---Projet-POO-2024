import random   #probabilité de coup critique et de précision
from unit import *

class Skills:
    """
    Classe rassemblant les méthodes des compétences que chaque unité peuvent jouer

    Attributs
    -----------
    critique : bool
        Indique si le coup est critique
    miss : bool
        Indique si le coup est manqué

    Méthodes
    ----------
    attack(target)
        Attaque au corps à corps la target
    
    heal(target)
        Soigne une unité
    fire_ball(pointeur, x_pointeur, y_pointeur)
        Lance une boule de feu avec une zone d'effet de neuf cases
    invisibility()
        Rend l'unité invisible
    bow(target)
        Tir à l'arc sur la target
    """
    def __init__(self):
        self.critique = False
        self.miss = False

    #Pour tout le monde:
    def attack(self,target):
        """Attaque une unité cible au corps à corps."""

        if target.defense_shield >= self.attack_power:
            target.defense_shield -= self.attack_power
        else:
            target.health -= self.attack_power - target.defense_shield
            target.defense_shield = 0
            
    #pour les mages:
    def heal(self,target):
        """Soigne les points de vie d'une unité alliée à portée, et utilise du mana""" 
        p1 = random.random()
        p2 = random.random()
        if p1 < 0.2: #20% de chances de coup critique
            self.critique = True
        if p2 < 0.4: #40% de chances de rater
            self.miss = True
        if self.miss:
            print("Manqué !")
        elif not self.critique:
            if target.team == "player":
                target.health += self.mana
                self.mana = 0
            else:
                raise TypeError ("Cette compétence ne peut être utiliser que sur des unités alliées")
        elif self.critique:
            if target.team == "player":
                target.health += self.mana*2
                self.mana = 0
            else:
                raise TypeError ("Cette compétence ne peut être utiliser que sur des unités alliées")
            print("Critique !")
        if target.max_health < target.health:
            target.health = target.max_health

    #pour les mages:     
    def fire_ball(self,pointeur_x,pointeur_y,unit):
        """
        Attaque à distance qui explose sur une zone d'effet importante

        ----------
        pointeur_x, pointeur_y : position de la case visée
        unit : liste de toutes les unités (alliées et ennemies)
        """
        # Déplacements adjacents (x, y) : incluant la position centrale et les cases autour
        directions = [(-1, -1), (0, -1), (1, -1),  # haut-gauche, haut, haut-droite
                    (-1,  0), (0,  0), (1,  0),  # gauche, centre, droite
                    (-1,  1), (0,  1), (1,  1)]  # bas-gauche, bas, bas-droite

        list_unit_trouvees = []

        for dx, dy in directions:
            for u in unit:  # Parcours des unités
                if pointeur_x + dx == u.x and pointeur_y + dy == u.y:
                    list_unit_trouvees.append(u)

        p1 = random.random()
        p2 = random.random()
        if p1 < 0.2: #20% de chances de coup critique
            self.critique = True
        if p2 < 0.1: #10% de chances de rater
            self.miss = True
            
        for target in list_unit_trouvees:
            if self.miss:
                print("Coup raté !")
            elif not self.critique :
                if target.defense_shield >= round(self.attack_power*0.8):
                    target.defense_shield -= round(self.attack_power*0.8)
                else:
                    target.health -= round((self.attack_power - target.defense_shield)*0.8)
                    target.defense_shield = 0
            elif self.critique:
                if target.defense_shield >= self.attack_power:
                    target.defense_shield -= self.attack_power
                else:
                    target.health -= (self.attack_power - target.defense_shield)
                    target.defense_shield = 0
                print('Coup critique !')


    #pour les voleurs:
    def invisibility(self):
        """Porte l'anneau et se rend invisible (et donc intouchable) des unités ennemies pour un tour.
            Ne peut pas non plus se faire soigner par le mage !"""
        #coûte des points de bouclier (ça fatigue!), puis des points de vie quand le bouclier est à 0.
        self.is_invisible = True
        if self.defense_shield >= 3:
            self.defense_shield -= 3
        else:
            self.health -= 3 - self.defense_shield
            self.defense_shield = 0


    #pour les guerriers:       
    def bow(self,target):
        """Attaque (divisée par 2) à longue portée avec un arc"""
        
        p1 = random.random()
        p2 = random.random()
        if p1 < 0.2: #20% de chances de coup critique
            self.critique = True
        if p2 < 0.3: #30% de chances de rater la cible
            self.miss = True
        if self.miss:
            print("Coup raté !")
        elif not self.critique :
            if target.defense_shield >= round(self.attack_power*0.5):
                target.defense_shield -= round(self.attack_power*0.5)
            else:
                target.health -= round((self.attack_power - target.defense_shield)*0.5)
                target.defense_shield = 0
        elif self.critique:
            if target.defense_shield >= self.attack_power:
                target.defense_shield -= self.attack_power
            else:
                target.health -= (self.attack_power - target.defense_shield)
                target.defense_shield = 0
            print('Coup critique !')
            