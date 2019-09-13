# rpgtodo

An attempt at (yet another) one-way (for now) sync script from [Todoist](https://todoist.com/) to [Habitica](https://habitica.com/). It seems to work, but I won’t be publicising it until I’m more confident that it is bug-free! For now, I recommend you run it manually whenever you add/complete a task in Todoist. If you set it up to run every minute and there was some kind of bug, it could wreak havoc on your Habitica account.

## Usage

I plan to package this script properly in due course, but for now I think you can satisfy the dependencies with the command `pip install todoist-python`. You'll also need edit `rpgtodo/api_keys.txt` to input your [Todoist API token](https://todoist.com/prefs/integrations), [Habitica User ID](https://habitica.com/user/settings/api), and [Habitica API Token](https://habitica.com/user/settings/api).

To run the script, run `python rpgtodo/rpgtodo.py`

### Why does this script exist?

Because [Kusold/todoist-habitrpg](https://github.com/Kusold/todoist-habitrpg) seems defunct, and although [eringiglio/Habitica-todo](https://github.com/eringiglio/Habitica-todo) works with some edits (see: [my fork](idmyn/Habitica-todo)), the maintainer seems to have abandoned it. This project will likely take some inspiration from the latter, since I plan to follow in its footsteps by similarly making use of [the official Todoist Python API library](https://github.com/Doist/todoist-python).

### Intended behaviour

To keep things simple, this script:

- focuses exclusively on Habitica To-Dos, ignoring Habits and Dailies
- treats tasks deleted in Todoist as completed
- completely ignores tasks originally created in Habitica
- assigns all tasks the 'easy' difficulty in Habitica
- ignores [Habitica's task-based auto-allocation feature](https://habitica.fandom.com/wiki/Automatic_Allocation)
