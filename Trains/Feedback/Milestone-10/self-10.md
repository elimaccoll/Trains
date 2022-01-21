## Self-Evaluation Form for Milestone 10

Indicate below each bullet which file/unit takes care of each task.

The `remote proxy patterns` and `server-client` implementation calls for several
different design-implementation tasks. Point to each of the following:

1. the implementation of the `remote-proxy-player`
   - https://github.ccs.neu.edu/CS4500-F21/siuslaw/blob/539e2133eb51f9e865e0936de6dd315d2ed43d8c/Trains/Remote/remote_proxy_player.py#L31-L233
   - With one sentence explain how it satisfies the player interface.
     - `RemoteProxyPlayer` directly implements (inherits) our `PlayerInterface`, which allows the administrative components (Manager and Referee) to interact seamlessly with the client by handling the serialization and deserialization of data over the TCP connection.



2. the unit tests for the `remote-proxy-player`
   1. Unfortunately, we did not have the time to write any. 😕
      1. But we ran the integration tests from milestones 8 and 9 manually to confirm our clients and server were working and outputting the expected results (winners and cheaters, or not enough destinations).



3. the `server` and especially the following two pieces of factored-out
   functionality:
   - https://github.ccs.neu.edu/CS4500-F21/siuslaw/blob/539e2133eb51f9e865e0936de6dd315d2ed43d8c/Trains/Remote/trains_server.py#L20-L116
   - signing up enough players in at most two rounds of waiting
     - https://github.ccs.neu.edu/CS4500-F21/siuslaw/blob/539e2133eb51f9e865e0936de6dd315d2ed43d8c/10/xserver#L90-L138
       - The `TrainsServer` is simply responsible for listening and storing connections to `RemoteProxyPlayers`, so the "waiting periods" are only enforced by the `xserver` script.
   - signing up a single player (connect, check name, create proxy)
     - https://github.ccs.neu.edu/CS4500-F21/siuslaw/blob/539e2133eb51f9e865e0936de6dd315d2ed43d8c/Trains/Remote/trains_server.py#L56-L75



4. the `remote-proxy-manager-referee`
   - https://github.ccs.neu.edu/CS4500-F21/siuslaw/blob/539e2133eb51f9e865e0936de6dd315d2ed43d8c/Trains/Remote/remote_player_invoker.py#L16-L122
     - We think this functions as the `remote-proxy-manager-referee` since it acts as a bridge between a TCP connection to the server (manager and referee) and a Player instance, and it is responsible for passing messages to and from clients. Though we named it differently (`RemotePlayerInvoker`) because we interpreted its purpose slightly differently.
   - With one sentence, explain how it deals with all calls from the manager and referee on the server side.
     - The `RemotePlayerInvoker` consists of a TCP connection to the server and a `PlayerInterface`, and it periodically (every 0.25 seconds) polls the TCP connection for some JSON function call from the server (either the manager or the referee), which is then parsed and matched to a direct call on the `PlayerInterface` object, and the result is then serialized back to JSON and sent over the TCP connection to the server.




The ideal feedback for each of these three points is a GitHub
perma-link to the range of lines in a specific file or a collection of
files.

A lesser alternative is to specify paths to files and, if files are
longer than a laptop screen, positions within files are appropriate
responses.

You may wish to add a sentence that explains how you think the
specified code snippets answer the request.

If you did *not* realize these pieces of functionality, say so.

