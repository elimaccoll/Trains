## Self-Evaluation Form for Milestone 7

Please respond to the following items with

1. the item in your `todo` file that addresses the points below.

2. a link to a git commit (or set of commits) and/or git diffs the resolve
   bugs/implement rewrites: 

It is possible that you had "perfect" data definitions/interpretations
(purpose statement, unit tests, etc) and/or responded to feedback in a
timely manner. In that case, explain why you didn't have to add this
to your `todo` list.

These questions are taken from the rubric and represent some of 
critical elements of the project, though by no means all of them.

If there is anything special about any of these aspects below, you may also point to your `reworked.md` and/or `bugs.md` files. 

### Game Map 

- a proper [data definition](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Common/map.py#L202) with an [_interpretation_](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Common/map.py#L204-L207) for the game _map_
   - Fixes based on feedback were handled prior to this milestone (see the milestone 2 section in [reworked.md](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/7/reworked.md))

### Game States 

- a proper [data definition](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Common/player_game_state.py#L8) and an [_interpretation_](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Common/player_game_state.py#L10-L13) for the player game state
   - The player game state data definition was not changed for this milestone, but a fix was made in the constructor that is documented in [bugs.md](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/7/bugs.md) (3rd bullet point from the bottom).
   - This is addressed by the 'Add/Fix PlayerGameState unit tests' item in todo.md.

- a [purpose statement](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Admin/referee_game_state.py#L105-L116) for the "legality" functionality on states and connections 
   - The functionality for the "legality" function was not changed for this milestone.

- at [least _two_ unit tests](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Other/Unit_Tests/referee_game_state_tests.py#L100-L116) for the "legality" functionality on states and connections
   - Unit tests existed prior to this milestone, but we caught a bug in the unit test 'test_verify_legal_connection_invalid_not_enough_colored_cards' that is documented by the first bullet point in [bugs.md](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/7/bugs.md)
   - This is addressed by the 'Add/Fix referee unit tests' item in todo.md
 
### Referee and Scoring a Game

The functionality for computing scores consists of 4 distinct pieces of functionality:

  - awarding players for the connections they connected
      - [Functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Admin/referee.py#L470) 
      - [Unit test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Other/Unit_Tests/referee_test.py#L315-L320)
      - There were no changes made for this milestone.

  - awarding players for destinations connected
      - [Functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Admin/referee.py#L485) 
      - [Unit test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Other/Unit_Tests/referee_test.py#L327-L336)
      - There were no changes made for this milestone.

  - awarding players for constructing the longest path(s)
      - [Functionality for calculating longest path](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Admin/referee.py#L388) 
      - [Functionality for awarding points](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Admin/referee.py#L524-L525) 
      - [Unit test for calculating longest path](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Other/Unit_Tests/referee_test.py#L402-L404) 
      - [Unit test for awarding points based on longest path](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Other/Unit_Tests/referee_test.py#L353-L362)
      - There were no changes made for this milestone.

  - ranking the players based on their scores 
      - [Functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Admin/referee.py#L445)
      - [Unit test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Other/Unit_Tests/referee_test.py#L375-L386)
      - There were no changes made for this milestone.

Point to the following for each of the above: 

  - piece of functionality separated out as a method/function:
  - a unit test per functionality

### Bonus

Explain your favorite "debt removal" action via a paragraph with
supporting evidence (i.e. citations to git commit links, todo, `bug.md`
and/or `reworked.md`).

Our favorite "debt removal" action was changing the representation of opponent info in the player game state. Opponent info was originally a dictionary of opponent player name to their acquired connections [original definition](https://github.ccs.neu.edu/CS4500-F21/boise/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Common/player_game_state.py#L60-L61).  It was changed to a list of dictionaries (a dictionary for each opponent) in the turn order of the game.  Each dictionary contains a field for the set of connections acquired by that opponent and a field for the natural number that represents the number of cards in that opponent's hand [new definition](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/Trains/Common/player_game_state.py#L56-L61).  This is addressed by the following items in [todo.md](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/7/todo.md): 
   - Create a data representation for opponent information that a player can see
   - Change 'opponent_info' in the player state from a dictionary mapping player names to a list of opponent information in the turn order of the players  

There was also a bug discovered as a result of changing the opponent information data representation.  The bug was that the referee was not updating its own game state when getting the updated state to send to the player.  This is documented by the second bullet point in [bugs.md](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/44143b0a1e2b5365d927ea11d7c7928fc8505ffa/7/bugs.md) and was ultimately a result of missing integration tests.  The lack of integration tests was also documented as a bug and has since been remedied.

