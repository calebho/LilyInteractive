import random
import zoo_actions as actions

from story import Story, StoryNode

def get_remaining():
    """Create and return a list of exhibits not visited yet
    """

def zoo_story_factory():
    s = Story()
    s.add_node(actions.entrance, start=True)
    s.add_node(actions.wallet)
    s.add_node(actions.parking_lot)

    exhibits = [actions.monkeys, actions.elephants, actions.lions, 
                actions.tigers, actions.penguins, actions.otters, 
                actions.pandas]
    exhibits = random.sample(exhibits, 4)
    for exhibit in exhibits:
        s.add_node(exhibit)
    
    dir_edges = [(actions.entrance, exhibit) for exhibit in exhibits]
    dir_edges += [(exhibit, actions.parking_lot) for exhibit in exhibits]
    dir_edges.append((actions.wallet, actions.parking_lot))
    undir_edges = []
    # the exhibits are fully connected
    for i, v in enumerate(exhibits):
        for w in exhibits[i+1:]:
            undir_edges.append((v, w))
    s.add_edges_from(dir_edges)
    s.add_undirected_edges_from(undir_edges)

    s.node[actions.entrance]['dynamic_events'][actions.wallet] = 0.01

    context = {'name': None,
               'remaining': [e.__name__ for e in exhibits]}
    s.update_context(context)

    return s

if __name__ == '__main__':
    zoo_story_factory()
