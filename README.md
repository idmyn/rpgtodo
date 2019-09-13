# rpgtodo

An attempt at (yet another) one-way (for now) sync script from [Todoist](https://todoist.com/) to [Habitica](https://habitica.com/).

## Why?

Because [Kusold/todoist-habitrpg](https://github.com/Kusold/todoist-habitrpg) seems defunct, and although [eringiglio/Habitica-todo](https://github.com/eringiglio/Habitica-todo) works with some edits (see: [my fork](idmyn/Habitica-todo)), the maintainer seems to have abandoned it. This project will likely take some inspiration from the latter, since I plan to follow in its footsteps by similarly making use of [the official Todoist Python API library](https://github.com/Doist/todoist-python).

## Intended behaviour

To keep things simple, this script:

- focuses exclusively on Habitica To-Dos, ignoring Habits and Dailies
- will treat tasks deleted in Todoist as completed
- completely ignores tasks originally created in Habitica
- assigns all tasks the 'easy' difficulty in Habitica
- ignores Habitica's [task-based auto-allocation feature](https://habitica.fandom.com/wiki/Automatic_Allocation)
