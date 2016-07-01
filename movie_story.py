import movie_actions as actions

from story import Story, StoryNode

def movie_story_factory():
    """Create and return the movie story
    """
    start = StoryNode('start', actions.movie_greeting)
    box_office = StoryNode('box office', actions.box_office)
    concessions = StoryNode('concessions', actions.concessions)
    ticket_checker = StoryNode('ticket checker', actions.ticket_checker)
    movie = StoryNode('watch movie', actions.watch_movie)

    dependencies = {ticket_checker: {box_office: None}}

    movie_story = Story(start, dependencies=dependencies)
    dir_edges = [(start, box_office),
                 (start, concessions),
                 (box_office, ticket_checker),
                 (concessions, ticket_checker),
                 (ticket_checker, movie)]
    undir_edges = [(box_office, concessions)]
    movie_story.add_edges_from(dir_edges)
    movie_story.add_undirected_edges_from(undir_edges)

    return movie_story

if __name__ == '__main__':
    movie_story_factory()
