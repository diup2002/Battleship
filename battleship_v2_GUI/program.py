"""
Auteurs     - Andre Pinel, Maryam Mouatadid
But         - Programmation d'un jeu de Bataille Navale avec implementation d'une IA.
Date        - Trimestre Automne 2023
Version     - BattleshipV2


Programme principal :

"""

import random


class Ship:

    def __init__(self, size):
        """ Constructeur de classe """
        self.row = random.randrange(0, 9)
        self.column = random.randrange(0, 9)
        self.size = size
        self.orientation = random.choice(["horizontal", "vertical"])
        self.indexes = self.generate_index()

    def generate_index(self):
        """
        Génère les index des cases occupées par un bateau en fonction de sa position, taille et orientation.

        Returns:
            Liste des index des cases occupées par le bateau.
        """

        # On calcule l'index de départ en convertissant la position (ligne, colonne) en un index unique sur la grille de taille 10x10
        start_index = self.row * 10 + self.column
        # Si le bateau est orienté horizontalement, génère les index en ajoutant i à l'index de départ pour chaque i allant de 0 à taille-1
        if self.orientation == "horizontal":
            return [start_index + i for i in range(self.size)]
        # Si le bateau est orienté verticalement, génère les index en ajoutant i * 10 à l'index de départ pour chaque i allant de 0 à taille-1
        elif self.orientation == "vertical":
            return [start_index + i * 10 for i in range(self.size)]


class Player:

    def __init__(self):
        """ Constructeur de classe """
        self.ships = []  # bateaux du joueur
        self.searches = ["U" for i in
                           range(100)]  # tableau des emplacements : "I" pour inconnu, "T" pour Touché, "R" pour Raté
        self.place_ships(
            sizes=[5, 4, 3, 3, 2])  # fonction qui assure que les bateaux sont dans les bonnes dimensions
        list_of_lists = [ship.indexes for ship in self.ships]  # Liste des listes des indexes des bateaux
        self.indexes = [index for sublist in list_of_lists for index in sublist]

    def place_ships(self, sizes):
        """
        Place les bateaux sur la grille du jeu tout en respectant les limites et en évitant les collisions.

        Parameters:
            tailles (list): Liste des tailles des bateaux à placer.

        Returns:
            None
        """
        # Pour chaque taille de bateau spécifiée
        for size in sizes:

            is_placed = False
            # Tant que le bateau n'est pas placé avec succès
            while not is_placed:
                ship = Ship(size)  # creation d'un nouveau bateau
                position_is_valid = True  # verifier si la position choisie est possible

                # Vérifie chaque index du bateau
                for i in ship.indexes:
                    # Vérifie que tous les indexes sont inférieurs à 100 (dans les limites de la grille)
                    if i >= 100:
                        position_is_valid = False
                        break

                    # Calcule la nouvelle ligne et colonne à partir de l'index
                    new_row = i // 10
                    new_column = i % 10

                    # Vérifie que la nouvelle position ne diffère pas de celle du bateau
                    if new_row != ship.row and new_column != ship.column:
                        position_is_valid = False
                        break

                    # Vérifie s'il y a une intersection avec un autre bateau déjà placé
                    for other_ship in self.ships:
                        if i in other_ship.indexes:
                            position_is_valid = False
                            break

                # Place le nouveau bateau s'il n'y a pas de collision
                if position_is_valid:
                    self.ships.append(ship)
                    is_placed = True

    def display_ships(self):
        """
        Affiche les coordonnées des bateaux d'un joueur sur la grille.

        Returns:
            None
        """
        # Liste de symboles "-" pour les positions vides et "X" pour les positions occupées par un bateau
        indexes = ["-" if i not in self.indexes else "X" for i in range(100)]
        # Affiche la grille ligne par ligne
        for row in range(10):
            # Utilise " ".join pour afficher chaque ligne de la grille séparée par un espace
            print(" ".join(indexes[(row - 1) * 10:row * 10]))


class Game:

    def __init__(self, human1, human2):
        self.humanAgent1 = human1
        self.humanAgent2 = human2
        self.player1 = Player()  # joueur 1 de la partie
        self.player2 = Player()  # joueur2 de la partie
        self.player1Turn = True  # variable booleenne qui indique le tour du joueur, elle peut etre en fonction d'un des 2 joueurs seulement.
        self.AITurn = True if not self.humanAgent1 else False  # variable booleenne qui indique le tour de l'ordinateur
        self.end = False  # variable booléenne pour verifier la fin de la partie
        self.result = None  # Résultat du jeu/ de la partie

    def play_move(self, i):
        """
        Fonction qui permet de jouer un coup en fonction de l'indice (index) spécifié.

        Parameters:
            i (int): Indice de l'emplacement visé sur la grille.

        Returns:
            None
        """

        # On commence par designer qui est le joueur courant et qui est son adversaire
        currentPlayer = self.player1 if self.player1Turn else self.player2
        opponent = self.player2 if self.player1Turn else self.player1
        move = False

        # On établit les etats de coups tel que "T" pour touché si le coup est réussi ; sinon "R" pour raté
        if i in opponent.indexes:
            currentPlayer.searches[i] = "H"
            move = True
            # si le coup est réussi, on vérifie si le bateau est deja coulé ("C")
            for ship in opponent.ships:
                isSunk = True
                for i in ship.indexes:
                    if currentPlayer.searches[i] == "U":  # "I" désigne une position inconnue encore
                        isSunk = False
                        break
                if isSunk:
                    for i in ship.indexes:
                        currentPlayer.searches[i] = "S"
        else:
            currentPlayer.searches[i] = "R"

        # On vérifie si la partie est terminée
        isGameOver = True

        for i in opponent.indexes:
            if currentPlayer.searches[i] == "U":
                isGameOver = False
        self.end = isGameOver
        self.result = 1 if self.player1Turn else 2

        # Changer le joueur courant (passer la main)
        if not move:
            self.player1Turn = not self.player1Turn

            # Interchanger le tour entre l'agent humain et l'IA
            if (self.humanAgent1 and not self.humanAgent2) or (not self.humanAgent1 and self.humanAgent2):
                self.AITurn = not self.AITurn

    def random_AI(self):
        """ Fonction qui implémente un premier agent intelligent à coups aléatoires.
            L'agent choisi aléatoirement les positions de ses coups dans la liste des indexes marqués "I" de son opposant. """

        # Si c'est le tour du joueur1, on récupere sa liste de recherches ; sinon celle du joueur2
        searchList = self.player1.searches if self.player1Turn else self.player2.searches

        # On obtient les indices des positions marquées "I" pour inconnu
        unknownPositions = [i for i, char in enumerate(searchList) if char == "U"]

        # Si des positions inconnues existent
        if len(unknownPositions) > 0:
            # Choix aléatoire d'une position inconnue
            randomPosition = random.choice(unknownPositions)
            # Joue un coup à la position choisie
            self.play_move(randomPosition)

    def intermidiate_AI(self):
        """ Fonction qui implémente un agent intelligent avec calcul probabiliste des positions."""

        # On commence par récupérer la liste de recherches du joueur1
        # On obtient les indices des positions marquées "I" pour inconnu ; et les indices des positions "T" pour touché
        searchList = self.player1.searches if self.player1Turn else self.player2.searches
        unknownPositions = [i for i, char in enumerate(searchList) if char == "U"]
        hitPositions = [i for i, char in enumerate(searchList) if char == "H"]

        # Inspect the +1 adjacent squares to a "H" position
        unknownsWithAdjacentHit = []
        # Inspect the +2 adjacent squares to 2 "H" positions
        unknownsWithAdjacentHit2 = []
        for index in unknownPositions:
            if (index + 1 in hitPositions) or (index - 1 in hitPositions) or (
                    index - 10 in hitPositions) or (index + 10 in hitPositions):
                unknownsWithAdjacentHit.append(index)
            if (index + 2 in hitPositions) or (index + 2 in hitPositions) or (
                    index - 20 in hitPositions) or (index + 20 in hitPositions):
                unknownsWithAdjacentHit2.append(index)

        # Choose an "U" position with an n-1 adjacent "H" and an n-2 adjacent "H" 
        for index in unknownPositions:
            if index in unknownsWithAdjacentHit and index in unknownsWithAdjacentHit2:
                self.play_move(index)
                return

        # Otherwise, choose an "U" position with an n-1 adjacent "H" only
        if len(unknownsWithAdjacentHit) > 0:
            self.play_move(random.choice(unknownsWithAdjacentHit))
            return

        verifyBoard = []
        for index in unknownPositions:
            row = index // 10
            column = index % 10
            if (row + column) % 2 == 0:
                verifyBoard.append(index)
        if len(verifyBoard) > 0:
            self.play_move(random.choice(verifyBoard))
            return

        # Otherwise, choose a random "U" position
        self.random_AI()


# player1 = Player()
# player1.display_ships()