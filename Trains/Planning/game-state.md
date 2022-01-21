## The Game State

The game state reflects all game resources in the form of [connection](https://github.ccs.neu.edu/CS4500-F21/boise/blob/master/Trains/Planning/map-design.md#connection) ownership, player resources (colored cards and rails), and available resources/connections (colored cards in the deck and unaquired connections).  Colored cards represent the cards that players use to make connections.  Rails represents the number of rail segments that players have and use to acquire connections.  A Player is the representation of a player in the Trains game, containing their resources and interface for interacting with the game state.  The Referee maintains the game state and enforces the rules of the game by checking legality of player actions.  The Referee holds a master instance of the [Map](https://github.ccs.neu.edu/CS4500-F21/boise/blob/master/Trains/Planning/map-design.md#the-map) and provides an interface for players to influence the game state.

The state of the game for players is reflected by the resources that each player respectively possesses.  This is represented by a dataclass called PlayerGameState with the following fields: "connections" that contains a set of their connections, "colored_cards" that contains a list of their colored cards, "rails" that has an int indicating how many rail segments a player has, and "destinations" that contains a set of 2 Destinations (set of two [cities](https://github.ccs.neu.edu/CS4500-F21/boise/blob/master/Trains/Planning/map-design.md#city)) that the player is attempting fulfill.  Each player has their own instance of PlayerGameState.  The Referee will track available game resources as fields in the Referee (free_connections and colored_card_deck) and store a dictionary that associate players with their PlayerGameState.

---
## Operations Wishlist

Referee operations:
- Assigns players resources at the start of the game and throughout ( ColoredCards and rail segments)
- Displays game map to players
- Update players on game state
- Checks legality of a player's action
- Modifies game state to carry out legal actions  
-- Hand out 2 randomly chosen ColoredCards  
-- Give connections
- Penalize "cheating"
- Check end conditions
- Scoring the game (end of game)  
-- Checks if player accomplished connection their destination cities

Player Operations:
- Take actions  
-- Acquire a connection  
-- Draw 2 ColoredCards
- Request game state (at the start of each turn)

---
## Example Game State
```python
referee.game_state = {
    player1: PlayerGameState(connections, colored_cards, rails, destinations),
    ...
}
```