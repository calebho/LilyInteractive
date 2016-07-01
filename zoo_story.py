import random
import zoo_actions as actions

from story import Story, StoryNode

def zoo_story_factory():
    entrance = StoryNode("entrance", actions.entrance)
    parking_lot = StoryNode("parking lot", actions.parking_lot)
    monkeys = StoryNode("monkeys", actions.monkeys)
    elephants = StoryNode("elephants", actions.elephants)
    lions = StoryNode("lions", actions.lions)
    tigers = StoryNode("tigers", actions.tigers)
    penguins = StoryNode("penguins", actions.penguins)
    otters = StoryNode("otters", actions.otters)
    pandas = StoryNode("pandas", actions.pandas)

    exhibits = [monkeys, elephants, lions, tigers, penguins, otters, pandas]
    exhibits = random.sample(exhibits, 4)

    zoo_story = Story(entrance)
    dir_edges = [(entrance, exhibit) for exhibit in exhibits]
    dir_edges += [(exhibit, parking_lot) for exhibit in exhibits]
    undir_edges = []
    for i, v in enumerate(exhibits):
        for w in exhibits[i+1:]:
            undir_edges.append((v, w))
    zoo_story.add_edges_from(dir_edges)
    zoo_story,add_undirected_edges_from(undir_edges)

    return zoo_story
