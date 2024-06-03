"""
Auteurs     - Andre Pinel, Maryam Mouatadid
But         - Programmation d'un jeu de Bataille Navale avec implementation d'une IA.
Date        - Trimestre Automne 2023
Version     - BattleshipV2


Programme principal :

"""

import pygame
from program import Player
from program import Game
from program import Ship

pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)
pygame.display.set_caption("Battleship_v2")

font = pygame.font.SysFont("Comic Sans MS", 50)   # police du texte à afficher.
label_font = pygame.font.SysFont("Arial", 15)
# Trois fichiers audios chargés pour les effets sonores.
hit_sound = pygame.mixer.Sound("/Users/Leonardo Cruz/Battleship/battleship_v2_GUI/touche.wav")
miss_sound = pygame.mixer.Sound("/Users/Leonardo Cruz/Battleship/battleship_v2_GUI/rate.wav")
end_game_sound = pygame.mixer.Sound("/Users/Leonardo Cruz/Battleship/battleship_v2_GUI/finJeu.wav")


# Variables Globales de dimensionnement
square_size = 35                                # taille en pixels des cases dans la grille
horizontal_margin = square_size*2     # horizontal margin between window borders and game grid
vertical_margin = square_size*2  #                  #
WIDTH = square_size * 10 * 2 + horizontal_margin*2    #
HEIGHT = square_size * 10 * 2 + vertical_margin*3    #
MARGIN = 10
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

#variables booléennes qui décident quels types d'agents participeront à la partie
human_agent1 = True
human_agent2 = False

GREY = (65,65,65)
WHITE = (230,230,230)
BLUE = (152,245,255)
GREEN = (50, 200, 150)
ORANGE = (250, 140, 20)
RED = (250, 50, 100)
SHIP = (102,205,170)
STATES = {"U": GREY, "R": BLUE, "H": ORANGE, "S": RED}

placing_ships = True
current_ship_index = 0
ship_sizes = [5, 4, 3, 3, 2]
current_orientation = "horizontal"
player_ships = []
player_searches = ["U" for _ in range(100)]
game_started = False


def draw_grids(player, left=40, top=40, search=False):
    """Fonction qui dessine la grille de jeu et/ou de recherche"""
    for row in range(10):
        row_label = label_font.render(str(row + 1), True, WHITE)
        SCREEN.blit(row_label, (left - 20, top + row * square_size + square_size // 2 - row_label.get_height() // 2))

    # Draw column letters
    for col in range(10):
        col_label = label_font.render(chr(65 + col), True, WHITE)
        SCREEN.blit(col_label, (left + col * square_size + square_size // 2 - col_label.get_width() // 2, top - 20))

    for i in range(100):
        x = left + i % 10 * square_size
        y = top + i // 10 * square_size
        square = pygame.Rect(x, y, square_size, square_size)
        pygame.draw.rect(SCREEN, WHITE, square, width=3)
        if search:
            x += square_size // 2
            y += square_size // 2
            pygame.draw.circle(SCREEN, STATES[player.searches[i]], (x, y), radius=square_size // 4)




def draw_ships(player, left=50, top=50):
    """Fonction qui dessine les bateaux dans la grille de jeu"""
    for ship in player.ships:
        # coordonnée haute gauche du bateau
        x = left + (ship.column - 3) * square_size + horizontal_margin 
        y = top + (ship.row - 3) * square_size + vertical_margin + 7
        if ship.orientation == "horizontal":
            width = ship.size * square_size - 2 * MARGIN
            height = square_size - 2 * MARGIN
        else:
            width = square_size - 2 * MARGIN
            height = ship.size *  square_size - 2 * MARGIN
        # dessin d'un bateau utilisant une forme rectangle
        rectangle = pygame.Rect(x, y, width, height)
        pygame.draw.rect(SCREEN, SHIP, rectangle, border_radius=15)

def draw_start_button():
    """Draw the start button"""
    start_button = pygame.Rect(WIDTH//2 - 50, HEIGHT - 100, 100, 50)
    pygame.draw.rect(SCREEN, GREEN, start_button)
    text = font.render("Start", True, WHITE)
    SCREEN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 90))
    return start_button

def draw_orientation_buttons():
    """Draw buttons to select ship orientation"""
    horizontal_button = pygame.Rect(WIDTH//2 - 150, HEIGHT - 200, 100, 50)
    vertical_button = pygame.Rect(WIDTH//2 + 50, HEIGHT - 200, 100, 50)
    pygame.draw.rect(SCREEN, BLUE if current_orientation == "horizontal" else GREY, horizontal_button)
    pygame.draw.rect(SCREEN, BLUE if current_orientation == "vertical" else GREY, vertical_button)
    horizontal_text = label_font.render("Horizontal", True, WHITE)
    vertical_text = label_font.render("Vertical", True, WHITE)
    SCREEN.blit(horizontal_text, (WIDTH//2 - 150 + (100 - horizontal_text.get_width())//2, HEIGHT - 200 + (50 - horizontal_text.get_height())//2))
    SCREEN.blit(vertical_text, (WIDTH//2 + 50 + (100 - vertical_text.get_width())//2, HEIGHT - 200 + (50 - vertical_text.get_height())//2))
    return horizontal_button, vertical_button

def draw_ship_placement_grid():
    """Draw the grid for placing ships"""
    draw_grids(None)
    for ship in player_ships:
        x = ship.column * square_size + MARGIN
        y = ship.row * square_size + MARGIN
        if ship.orientation == "horizontal":
            width = ship.size * square_size - 2 * MARGIN
            height = square_size - 2 * MARGIN
        else:
            width = square_size - 2 * MARGIN
            height = ship.size * square_size - 2 * MARGIN
        rectangle = pygame.Rect(x, y, width, height)
        pygame.draw.rect(SCREEN, SHIP, rectangle, border_radius=15)

def place_ship(x, y):
    """Place a ship on the grid"""
    global current_ship_index
    if current_ship_index < len(ship_sizes):
        row = y // square_size
        column = x // square_size
        new_ship = Ship(ship_sizes[current_ship_index])
        new_ship.row = row
        new_ship.column = column
        new_ship.orientation = current_orientation
        player_ships.append(new_ship)
        current_ship_index += 1





# MAIN
game = Game(human_agent1, human_agent2)


animation = True
pause = False
while animation:

    # GESTION DES EVENTS UTILISATEURS
    for event in pygame.event.get():

        # SOURIS
        # Si l'utilisateur ferme la fenêtre d'animation
        if event.type == pygame.QUIT:
            animation = False

        # Si l'utilisateur clique une fois :
        if event.type == pygame.MOUSEBUTTONDOWN and not game.end:
            x,y = pygame.mouse.get_pos()
            if not game_started:
                if current_ship_index < len(ship_sizes):
                    if y < HEIGHT - 200:  # Ensure clicks on buttons don't place ships
                        place_ship(x, y)
                else:
                    start_button = draw_start_button()
                    if start_button.collidepoint(x, y):
                        game_started = True
                        game.player1.ships = player_ships
                        game.player2 = Player()  # re-initialize player2 to reset ships for AI
                horizontal_button, vertical_button = draw_orientation_buttons()    
                if horizontal_button.collidepoint(x, y):
                    current_orientation = "horizontal"
                elif vertical_button.collidepoint(x, y):
                    current_orientation = "vertical"
            elif not game.end:
            # tour du 1er joueur
                if game.player1Turn and (x < square_size*11) and (y < square_size*11): # (on verifie que le joueur joue son coup dans la case de recherche adverse)
                    row = y // square_size -1
                    column = x // square_size -1
                    index = row*10 + column
                    game.play_move(index)
                    if game.player1Turn:
                        hit_sound.play()  # Joue le son de touche pour le joueur 1
                    else:
                        miss_sound.play()  # Joue le son d'eau pour le joueur 2

                # tour du 2nd joueur
                elif not game.player1Turn and (x > WIDTH - square_size*11) and (y > square_size*11 + vertical_margin): # (on verifie que le joueur2 joue son coup dans la case de recherche adverse)
                    row = (y - square_size*10 - vertical_margin) // square_size - 1
                    column = (x - square_size*10 - horizontal_margin) // square_size - 1
                    index = row*10 + column
                    game.play_move(index)
                    if not game.player1Turn:
                        hit_sound.play()  # Joue le son de touche pour le joueur 1
                    else:
                        miss_sound.play()  # Joue le son d'eau pour le joueur 2

        # CLAVIER :
        if event.type == pygame.KEYDOWN:
            # la touche ESC quitte l'animation
            if event.key == pygame.K_ESCAPE:
                animation = False
            # et la barre d'espace pause/reprend l'animation
            if event.key == pygame.K_SPACE:
                pause = not pause
            # touche ENTRER pour redémarrer une partie
            if event.key == pygame.K_RETURN:
                game = Game(human_agent1, human_agent2)

    #  EXECUTION
    if not pause:

        # dessine l'arrière-plan
        SCREEN.fill(GREY)
        if not game_started:
            draw_ship_placement_grid()
            start_button = draw_start_button()
            horizontal_button, vertical_button = draw_orientation_buttons()
        else:
            draw_grids(game.player1, search=True)  # dessine la grille de recherche du joueur 1, en haut à gauche
            draw_grids(game.player2, left=((WIDTH - horizontal_margin) // 2 + horizontal_margin), top=((HEIGHT - vertical_margin)//2 + vertical_margin), search=True,)  # dessine la grille de recherche du joueur 2, en haut à droite

            # dessine les grilles de jeu des bateaux
            draw_grids(game.player1, top=((HEIGHT - vertical_margin) // 2 + vertical_margin))  # dessine la grille de jeu du joueur 1, en bas à gauche
            draw_grids(game.player2, left=((WIDTH - horizontal_margin) // 2 + horizontal_margin))  # dessine la grille de jeu du joueur 2, en bas à droite

            # dessine les bateaux dans la grille de jeu
            draw_ships(game.player1, top=(HEIGHT - vertical_margin) // 2 + vertical_margin)
            #dessiner_bateaux(jeu.joueur2, gauche=(HEIGHT - margeVert) // 2 + margeHorz)


        # Coups IA
            if not game.end and game.AITurn:
                if game.player1Turn :
                    game.intermidiate_AI()
                else:
                    game.intermidiate_AI()

            # Affiche le message de fin partie
            if game.end:
                end_game_sound.play()
                message = "Player " + str(game.result) + " won!"
                textbox = font.render(message, False, GREY, WHITE)
                SCREEN.blit(textbox, (WIDTH//2 - 240, HEIGHT//2 - 50))
        pygame.display.update()
        
        # met à jour l'affichage
        pygame.time.wait(100)
        pygame.display.flip()
pygame.quit()