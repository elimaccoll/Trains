## Player Interface

The following API is the method of interaction between the player and the referee. The referee is the expected caller of all of these methods. The expected protocol for the referee is to call the following methods in the specified order:

1.  Call `setup` to give player the map and its initial resources.

2.  Call `pick` to have player choose their destinations and return the ones they did not choose.

3.  While the game is ongoing for each player turn:

    -   Call `play` on the current player. This will either return an action for getting more cards or an action requesting to acquire a specified connection.
        -   If the player requests more cards, the referee will call the player's `more` method after drawing [0, 2] cards from the deck and hand the player those resources.
        -   If the player requests to acquire a connection, the referee will acquire the connection for the player if it is a valid transaction. Otherwise, it will note the Player is cheating.
    -   If a player "cheats", call `boot_player_from_game`()
    -   Otherwise, update ref state and call update_player_game_state() to ensure player is up to date

4.  Call `win` when the game is over and inform the player if it won.

Interface/API for Player:

```python
def setup(self, map: Map, rails: int, cards: dict) -> None:
    """
    Sets the player up with a map, a number of rails, and a hand of cards.
        Parameters:
            - map (Map): The map of the game.
            - rails (int): The number of rails the player will start with.
            - cards (dict): The hand of cards the player starts with.
    """


def update_player_game_state(updated_game_state: PlayerGameState): -> None
    """
    Receives a game_state from the referee to reflect changes made by a player's move.
        Parameters:
            updated_game_state(PlayerGameState): The new game state for the player
    """

def play(self, active_game_state: PlayerGameState) -> PlayerMove:
    """
    Polls the player strategy for a move.
        Parameters:
            active_game_state (PlayerGameState): The game state of this player when they've become active.
        Return:
            A PlayerMove indicating a player's intended move
    """


def pick(self, destinations: set) -> set:
    """
    Given a set of destinations, the player picks two destinations and the three
    that were not chosen are returned.
        Parameters:
            destinations (set(Destination)): Set of five destinations to choose from.
        Return:
            A set(Destination) containing the three destinations the player did not pick.
    """

def more(self, cards: list) -> None:
    """
    Hands this player some cards
        Parameters:
            cards (list(Color)): cards being handed to player
    """


def boot_player_from_game(reason_for_boot: str): -> None
    """
    Informs a player that they have been booted from the game and why.
    Local response to boot is upt to implementation, but the referee will not continue to query the player for moves
        Paramters:
            reason_for_boot (str): Written reason for booting the player
    """

def win(winner: bool): -> None
    """
    Informs player that the game is over, telling players what their score is and they won
    ONLY CALLED ONCE(PER PLAYER) AT END
        Parameters:
            winner (bool): True if this player won, False otherwise
    """
```
