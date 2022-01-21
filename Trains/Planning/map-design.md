## The Map
The map represents the game board, which is composed of cities (nodes) and connections between cities (edges).  The map consists of a dictionary with player identifiers as keys and connections as values that define the game board.  A player idenifier is a unique id assigned to each instance of a player object when it is eventually implemented, and will be used to represent ownerships of connections.  The instance of a referee will hold a data object created by the map class and govern the acquisition of connections.


Example describing initial game state:
```python
available_connections = { Connection1, Connection2, Connection3, ... }
referee.game_map = { player1.key: {},
                     player2.key: {},
                     Identifier.FREE: available_connections }
```
### Connection
A connection is an edge between two cities and is defined as having a set of 2 cities, an integer length in the range [3, 4, 5], and a connection color

Example:
```python
Connection({boise, seattle}, 4, ConnectionColor.RED)
```
In this example, "boise" and "seattle" are cities as defined below.

### City
A city is a node on the map that can be used to form valid connections with other, distinct cities.  Cities are defined as having a name represented by a string, an x position, and a y position.  The x and y positions are integer values normalized relative to the size of the map on a scale of [0,100].

Example:
```python
City("Boston", 90, 20)
```
In this example, "90" is the x position and "20" is the y position.

### Connection Color
An enumeration of RED, BLUE, GREEN, or WHITE. Used as one of the defining features of a connection.

### Visual 
The game will be rendered by using the map held by the instance of a referee.  It contains all the necessary fields to visualize cities and connections between cities, and the owners of connections (if there is one), which will be important later on in development.