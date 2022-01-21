## Tournament Manager Organization
The manager will support adding players/observers to tournaments and then to games(handled in the communication layer). It will do this by creating referees for each game and then adding players. It will have the functionality to organize tournament games according to some specification(elimination, cumulative score, etc). It will be able to get game specifics needed for overall tournament statistics from the referee (booted players, winner, final scores, etc). It will update observers with ongoing actions within games and inform players and observers of tournament outcomes.

Over the course of a tournament, the manager will receive players and observers. It will setup/run the games and the results of those games. After a tournament is over, the tournament manager will compute score (however implemented) and notify players whether they won or lost. The tournament manager will also update observers about the state of current games.

Design for Tournament Manager:
```python
def organize_games(players: set(), observers: set()):
    """
    From the given players and observers, organize players into games and allow observers to view games
    Parameters:
            players(set): players to be in a given game
            observers(set): observers in a tournament
    """
    pass

def run_game(players: set()) -> PlayerInterface:
    """
    Creates a Referee that facilitate a game of Trains with the given players
    One full method run represents one full game
    ONLY CALLED ONCE(PER GAME)
        Parameters:
            players(set): players to be in a given game
        Returns:
            winner (set(PlayerInterface)): The winner of this game instance
    """
    pass

def update_observers(observers: set()):
    """
    Updates each observer with the state of the game(s) they are observing
    MUTATES each observer game state with current game info
        Parameters:
            observers(set): all observers in the tournament
    """
    pass

def get_after_game_statistics(player: PlayerInterface) -> PlayerStatistics:
    """
    Gets the tournament statistics for the given player
        Parameters:
            observers(set): all observers in the tournament
        Returns:
            (PlayerStatistics): tournament statistics for the given player
    """
    pass
```

### PlayerStatistics
This class will represent relevant information for a tournament
This will likely include wins, bans, and potentially cumulative score

```python
# The class would likely resemble this definition
@dataclass
class PlayerStatistics:
    self.wins: int
    self.losses: int
    self.bans: int
    self.cumulative_score: int
```

### Player Interface Expansion
The player interface will be expanded to include functionalities relevant to the tournament manager. These functionalities include getting tournament statistics as the tournament progresses and whether or not a player won after a tournament has finished. The following API will be added to player to accommodate this:


```python
def get_tournament_stats(tournament_statistics: dict()):
    """
    Gives players the ongoing tournament statistics
        Parameters:
            tournament_statistics (dict(PlayerStatics)): A player indexed dictionary of player statistics
    """
    pass

def win_tournament(win_tournament: bool):
    """
    Notifies player if they won or lost the tournament
        Parameters:
            win_tournament(bool): True if winner of whole tournament, False otherwise
    """
    pass
```
