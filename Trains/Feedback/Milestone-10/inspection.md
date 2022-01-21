Pair: siuslaw

Commit: [`539e21`](https://github.ccs.neu.edu/CS4500-F21/siuslaw/tree/539e2133eb51f9e865e0936de6dd315d2ed43d8c) 

Score: 88/100

Grader: Sindhu

20/20: accurate self eval

68/80

1. 20/20 pts for `remote-proxy-player` implementation satisfying the player interface

2. 8/20 pts for unit tests of `remote-proxy-player`: (giving you 40%, since you mentioned that you dont' have any test cases)

   - Does it come with unit tests for all methods
     (start, setup, pick, play, more, win, end)?

3. 20/20 pts for separating the `server` function (at least) into the following two pieces of functionality:
   - signing up enough players in at most two rounds of waiting, with a different requirement for a min number of players
   - signing up a single player: which requires three steps: connect, check name, create remote-proxy player

4. 20/20 pts for implementing `remote-proxy-manager-referee` to the manager and referee interfaces.
