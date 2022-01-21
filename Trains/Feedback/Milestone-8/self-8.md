## Self-Evaluation Form for Milestone 8

Indicate below each bullet which file/unit takes care of each task.

The `manager` performs five completely distinct tasks, with one
closely related sub-task. Point to each of them:  

1. [inform players of the beginning of the game, retrieve maps](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Admin/manager.py#L50)

2. [pick a map with enough destinations](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Admin/manager.py#L113)
	- [including the predicate that decides "enough destinations"](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Admin/manager.py#L66)

3. [allocating players to a bunch of games per round](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Admin/manager.py#L80)

4. [run the tournament](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Admin/manager.py#L207) and its two major pieces of functionality:
   - [run a  round of games](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Admin/manager.py#L151)
   - [run all rounds, discover termination conditions](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Admin/manager.py#L184)

5. [inform survining players at the very end whether they won the tournament](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Admin/manager.py#L196)

Next point to unit tests for:

- [testing the `manager` on the same inputs as the `referee`, because
  you know the outcome](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Other/Unit_Tests/manager_tests.py#L261)
	- This unit test uses [mock players](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Other/Mocks/mock_tournament_player.py#L12) and a [configurable manager](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Other/Mocks/configurable_manager.py#L11) to run a deterministic tournament round.

- [testing the allocation of players to the games of one round](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Other/Unit_Tests/manager_tests.py#L119-L183)

Finally, the specification of the `cheat` strategy says "like BuyNow",
which suggests (F II) to derive (`extend`) the base class or re-use some
functionality:

- point to the [cheat strategy](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Player/cheat_strategy.py#L9) and how it partially reusess existing code
	- Our initial implementation of the Cheat strategy extended Buy_Now, but we ran into issues with dynamically loading a strategy that didn't directly subclass AbstractPlayerStrategy, so we resorted to that approach.
- [point to a unit test that makes sure the requested acquisition is impossible](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/80aa96cdd879ca8ba040be0a8f8c58ecade006dc/Trains/Other/Unit_Tests/manager_tests.py#L261)
	- We used a mock tournament player to mimic the behavior of a cheat strategy (acquiring a bogus connection)

The ideal feedback for each of these three points is a GitHub
perma-link to the range of lines in a specific file or a collection of
files.

A lesser alternative is to specify paths to files and, if files are
longer than a laptop screen, positions within files are appropriate
responses.

You may wish to add a sentence that explains how you think the
specified code snippets answer the request.

If you did *not* realize these pieces of functionality, say so.
