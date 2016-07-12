import movie_actions as actions

from story import Story, StoryNode

def movie_story_factory():
    """Create and return the movie story
    """
    s = Story()
    s.add_node(actions.movie_greeting, start=True)
    s.add_node(actions.box_office)
    s.add_node(actions.concessions)
    s.add_node(actions.ticket_checker)
    s.add_node(actions.watch_movie)
    
    dependencies = {actions.ticket_checker: {actions.box_office: None}}
    s.add_dependencies_from(dependencies)

    dir_edges = [(actions.movie_greeting, actions.box_office),
                 (actions.movie_greeting, actions.concessions),
                 (actions.box_office, actions.ticket_checker),
                 (actions.concessions, actions.ticket_checker),
                 (actions.ticket_checker, actions.watch_movie)]
    undir_edges = [(actions.box_office, actions.concessions)]
    s.add_edges_from(dir_edges)
    s.add_undirected_edges_from(undir_edges)

    context = {'name': None, # will be set later
               'movie_names': ["inside out", "tomorrowland", "minions", "home"],
               'movie_choice': None,
               'menu': ["soda", "popcorn", "candy"],
               'bought': []}
    s.update_context(context)

    s.verify()

    return s

if __name__ == '__main__':
    movie_story_factory()
