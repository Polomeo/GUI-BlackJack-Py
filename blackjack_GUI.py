# Blackjack con GUI - Completado en 2023-12-04 por Polomeo
import random
import tkinter as tk
from pathlib import Path

# Dirección a la carpeta de assets
assets_folder = Path(__file__).parent / 'assets'

# Clases
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

        card_file_name = self.suit + self.value + ".png"
        self.img = tk.PhotoImage(file=assets_folder / card_file_name)

    def __repr__(self):
        return " of ".join((self.value, self.suit))

    def get_file(self):
        return self.img

    @classmethod
    def get_back_file(cls):
        cls.back = tk.PhotoImage(file=assets_folder / "back.png")
        return cls.back


class Deck:
    def __init__(self):
        # List Comprehension (arma una lista basado en otras listas)
        # Crea cartas con el nombre 'Spades4' por ejemplo
        self.cards = [Card(s, v)
                      for s in ["Spades", "Clubs",
                                "Hearts", "Diamonds"]
                      for v in ["A", "2", "3",
                                          "4", "5", "6",
                                          "7", "8", "9",
                                          "10", "J", "Q",
                                          "K"]]

    # Si hay más de una carta, mezcla
    def shuffle(self):
        if len(self.cards) > 1:
            random.shuffle(self.cards)

    # Si hay más de una carta, devuelve una carta
    def deal(self):
        if len(self.cards) > 1:
            return self.cards.pop(0)


class Hand:
    def __init__(self, dealer=False):
        self.dealer = dealer
        self.cards = []
        self.value = 0

    def add_card(self, card):
        self.cards.append(card)

    def calculate_value(self):
        self.value = 0
        has_ace = False
        for card in self.cards:
            if card.value.isnumeric():
                self.value += int(card.value)
            else:
                if card.value == "A":
                    has_ace = True
                    self.value += 11
                else:
                    self.value += 10

        if has_ace and self.value > 21:
            self.value -= 10

    def get_value(self):
        self.calculate_value()
        return self.value


class GameState:
    def __init__(self):
        # Crea un mazo y mezcla
        self.deck = Deck()
        self.deck.shuffle()

        # Crea las manos
        self.player_hand = Hand()
        self.dealer_hand = Hand(dealer=True)

        # Reparte 2 cartas a cada uno
        for i in range(2):
            self.player_hand.add_card(self.deck.deal())
            self.dealer_hand.add_card(self.deck.deal())

        self.has_winner = ''

    # True si el player se pasó de 21
    def player_is_over(self):
        return self.player_hand.get_value() > 21

    # Devuelve quién tiene BlackJack
    def someone_has_blackjack(self):
        player = False
        dealer = False

        if self.player_hand.get_value() == 21:
            player = True
        if self.dealer_hand.get_value() == 21:
            dealer = True

        if dealer and player:
            return 'dp'
        elif player:
            return 'p'
        elif dealer:
            return 'd'

        return False

    # Pide carta
    def hit(self):
        self.player_hand.add_card(self.deck.deal())
        if self.someone_has_blackjack() == 'p':
            self.has_winner = 'p'
        if self.player_is_over():
            self.has_winner = 'd'

        return self.has_winner

    # Estado de la partida
    def get_table_state(self):
        blackjack = False
        winner = self.has_winner

        if not winner:
            winner = self.someone_has_blackjack()
            if winner:
                blackjack = True

        table_state = {
            'player_cards': self.player_hand.cards,
            'dealer_cards': self.dealer_hand.cards,
            'has_winner': winner,
            'blackjack': blackjack,
        }

        return table_state

    # Cuando el jugador decide quedarse
    def calculate_final_state(self):
        player_hand_value = self.player_hand.get_value()
        dealer_hand_value = self.dealer_hand.get_value()
        winner = self.has_winner

        if player_hand_value == dealer_hand_value:
            winner = 'dp'
        elif player_hand_value > dealer_hand_value:
            winner = 'p'
        else:
            winner = 'd'

        table_state = {
            'player_cards': self.player_hand.cards,
            'dealer_cards': self.dealer_hand.cards,
            'has_winner': winner,
        }

        return table_state

    # Devuelve el Score del player en String
    def player_score_as_text(self):
        return "Valor de su mano: " + str(self.player_hand.get_value())


class GameScreen(tk.Tk):
    def __init__(self):
        super().__init__()

        # Ventana
        self.title("BlackJack GUI por Polomeo")
        self.geometry("800x640")
        self.resizable(False, False)

        # Constantes
        self.CARD_ORIGINAL_POSITION = 100
        self.CARD_WIDTH_OFFSET = 100

        self.DEALER_CARD_HEIGHT = 100
        self.PLAYER_CARD_HEIGHT = 300

        self.PLAYER_SCORE_TEXT_COORDS = (400, 450)
        self.WINNER_TEXT_COORDS = (400, 250)

        # Creamos un nuevo juego
        self.game_state = GameState()

        # Canvas para Cartas --> 800x500
        self.game_screen = tk.Canvas(self, bg="white", width=800, height=500)

        # Frame para Botones --> 800x140
        self.bottom_frame = tk.Frame(self, width=800, height=140, bg="red")
        # Se expande para ocupar todo el W & H
        self.bottom_frame.pack_propagate(0)

        # Botones
        self.hit_button = tk.Button(
            self.bottom_frame, text="Pedir", width=25, command=self.hit)
        self.stick_button = tk.Button(
            self.bottom_frame, text="Quedarse", width=25, command=self.stick)
        self.play_again_button = tk.Button(
            self.bottom_frame, text="Jugar de nuevo", width=25, command=self.play_again)
        self.quit_button = tk.Button(
            self.bottom_frame, text="Salir", width=25, command=self.destroy)

        # Pack sólo a los botones que se van a ver al principio (init)
        self.hit_button.pack(side=tk.LEFT, padx=(100, 200))
        self.stick_button.pack(side=tk.LEFT)

        # Pantalla
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.game_screen.pack(side=tk.LEFT, anchor=tk.N)

        # Mostramos los elementos gráficos en el canvas
        self.display_table()

    # Muestra el estado de la partida
    def display_table(self, hide_dealer=True, table_state=None):
        if not table_state:
            table_state = self.game_state.get_table_state()

        player_card_images = [card.get_file()
                              for card in table_state['player_cards']]
        dealer_card_images = [card.get_file()
                              for card in table_state['dealer_cards']]

        if hide_dealer and not table_state['blackjack']:
            dealer_card_images[0] = Card.get_back_file()

        # Dibujar el fondo
        self.game_screen.delete("all")
        self.tabletop_image = tk.PhotoImage(
            file=assets_folder / "tabletop.png")
        self.game_screen.create_image((400, 250), image=self.tabletop_image)

        # Colocar las cartas del jugador
        for card_number, card_image in enumerate(player_card_images):
            self.game_screen.create_image(
                (self.CARD_ORIGINAL_POSITION + self.CARD_WIDTH_OFFSET * card_number, self.PLAYER_CARD_HEIGHT), image=card_image)

        # Colocar las cartas del dealer
        for card_number, card_image in enumerate(dealer_card_images):
            self.game_screen.create_image(
                (self.CARD_ORIGINAL_POSITION + self.CARD_WIDTH_OFFSET * card_number, self.DEALER_CARD_HEIGHT), image=card_image)

        # Muestra el Score actual
        self.game_screen.create_text(
            self.PLAYER_SCORE_TEXT_COORDS, text=self.game_state.player_score_as_text(), font=(None, 20))

        # En caso de VICTORIA de alguno
        if table_state['has_winner']:
            if table_state['has_winner'] == 'p':
                self.game_screen.create_text(
                    self.WINNER_TEXT_COORDS, text="¡Usted gana!", font=(None, 50))
            elif table_state['has_winner'] == 'dp':
                self.game_screen.create_text(
                    self.WINNER_TEXT_COORDS, text="¡Empate!", font=(None, 50))
            else:
                self.game_screen.create_text(
                    self.WINNER_TEXT_COORDS, text="¡La casa gana!", font=(None, 50))

            # Si terminó el juego, se muestran opciones para reiniciar
            self.show_play_again_options()

    # Muestra el menú para reiniciar
    def show_play_again_options(self):
        # Ocultamos los botones de juego
        self.hit_button.pack_forget()
        self.stick_button.pack_forget()

        # Mostramos los botones de reinicio y salir
        self.play_again_button.pack(side=tk.LEFT, padx=(100, 200))
        self.quit_button.pack(side=tk.LEFT)

    # Pide carta
    def hit(self):
        self.game_state.hit()
        self.display_table()

    # Se queda
    def stick(self):
        table_state = self.game_state.calculate_final_state()
        self.display_table(False, table_state)

    # Reinicia el juego
    def play_again(self):
        self.show_gameplay_buttons()
        self.game_state = GameState()
        self.display_table()

    # Muestra el menú para jugar
    def show_gameplay_buttons(self):
        self.play_again_button.pack_forget()
        self.quit_button.pack_forget()

        self.hit_button.pack(side=tk.LEFT, padx=(100, 200))
        self.stick_button.pack(side=tk.LEFT)

# Main-loop
if __name__ == "__main__":
    gs = GameScreen()
    gs.mainloop()
