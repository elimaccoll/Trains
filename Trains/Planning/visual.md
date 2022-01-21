# Creating a Visual

From: Stephen: jayne.s@northeastern.edu, Eli: maccoll.e@northeastern.edu

## Input

A JSON string will be sent that represents the map and its connections. The JSON is formatted . Here is an example:

```json
{
    "FREE":
        [
            {
                "cities":
                    [
                        {"name": "Boston", "x": 90, "y": 20},
                        {"name": "New York", "x": 80, "y": 30}
                    ],
                "color": 1,
                "length": 3
            }, ...
        ],
    "PLAYER1" : ...
}
```

The top level JSON fields "FREE" and "PLAYER1" are placeholder names. Once the JSON is converted to a local structure, iterate over the dictionary/hashmap by key to access each list of connections. All other data is fixed. The fields "x" and "y" are normalized [0, 100] relative to the size of the map. The fields "color" and "length" will be used to describe how connections should be rendered.

### Color

A "color" is an enum that represents one of the four connection colors:

```python
    RED = 1
    BLUE = 2
    GREEN = 3
    WHITE = 4
```

## Calling the View

The function should be called as follows:

```python
json_connections = "{\"Free\": [{\"cities\": [{\"name\": \"Boston\", \"x\": 90, \"y\": 20}, ...], \"color\": 1, \"length\": 3}]}"
render_view(json_connections)
```

json_connection should be a string containing valid JSON as defined above.
A window containing the desired view should open on the screen. There is no return value.

## Desired View/GUI

The GUI window should contain a map with the window matching the map's size dimensions.
The dimensions of the map will be [10, 800] for both the width and height individually.

Cities should be red circles placed at their x and y coordinates (normalized as defined above), with the name of the city displayed over the city in white text.

Connections should be drawn between cities as a number of line segments equal to its "length" and as the "color" defined by the enumeration above. If there are multiple connections between a pair of cities, make sure each connection is distinct in some way (not overlapping).
