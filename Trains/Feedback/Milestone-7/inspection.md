Pair: lassen

Commit: [`44143b`](https://github.ccs.neu.edu/CS4500-F21/lassen/tree/44143b0a1e2b5365d927ea11d7c7928fc8505ffa) *(Multiple hashes found: `44143b`, `a6d152`. Using `44143b` instead.)*

Score: 288/290

Grader: Darpan Mehra

18/20: self eval
  -  Bonus point original implementation is not correct.

`git log inspection`

60/60

You got full points if the answer to "Did you copy code?" appeared to be "no".

`Improved Project Code`

200/210

For each of the sections below, criteria aliases and descriptions:

| Criteria Alias         | Description  | Points |                                                    
| :--------------------- | :-------------------- | :----------------------------------------------------------------------------: | 
| A                      | the item in your `todo` file or an explanation that about why it was not in your `todo` file (you already had the functionality prior to this milestone, you fixed an issue "immediately", etc. But you can't get these points if you didn't implement the functionality.)  | 5 | 
| B                      |  link to a git commit (or set of) and/or git diffs or files that contain the functionality | 5 | 
| C                      | quick-check accuracy (1. matches 2. date of fix (2 is relevant for git commits)) | 5 | 
| D                      | quality (see below) | 15 | 

**Scores**


| Category                                  | A  | B | C | D | Total                                                   
| :--------------------- | :-------------------- | :----------------------------------------------------------------------------: | :--------: | :---------: | :---------:
| Game Map                                   | 5 | 5 | 5 | 12 | 27
| Game States                                | 5 | 5 | 5 | 13 | 28
| Strategy                                   | 5 | 5 | 5 | 10 | 25
| Referee's Scoring (Connection Points)      | 5 | 5 | 5 | 15 | 30
| Referee's Scoring (Destinations Connected) | 5 | 5 | 5 | 15 | 30
| Referee's Scoring (Longest Path)           | 5 | 5 | 5 | 15 | 30
| Referee's Scoring (Ranking)                | 5 | 5 | 5 | 15 | 30

`Game Map Notes & Quality Criteria`
- Quality
  - how are connections between two cities represented?
    - example: if you constructed a map with BOS and NYC on it, connected with 4 red segments, how would the data representation express this?
  - is every connection between two cities represented once or twice?
    - example: if you have a 3-blue BOS--NYC connection, does it show up once or twice?
  - does the data representation say how to translate it into a graphic layout?
    - example: how large is the map? Where would NYC show up (in the above example)?
  - For each, 5 pts
  - Feedback
    - You can abstract your code and also simplify it rather than having so many classes together. 


`Game States Notes & Quality Criteria`
- Quality
  - a proper data definition including an interpretation for the player game state
  - a purpose statement for the "legality" functionality on player game states and connections
  - two unit tests for the "legality" functionality on states and connections
  - For each, 5 pts
  - Feedback

  


`Strategy Notes & Quality Criteria`
- Quality
  - do the purpose statements of the strategies' methods/functions express how it makes decisions?
  - are common pieces abstracted now?
    - I cannot see any abstraction in your implementation

`Referee Notes & Quality Criteria`
- Quality
  - separate method; clear naming and/or good purpose statement; unit tests
  - For each, 5 pts

`Bonus`

10/20

- 5/10 for quick-check accuracy (1. matches 2: date or fix)
  - Your original method link is not correct. Cannot verify the 
- 5/10 for quality if it is convincing that your "favorite debt removal action" removed a critical technical debt



