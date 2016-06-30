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

'''
from story import Story
from story_node import StoryNode
from player import Player
from activity import Activity
from theater_acts import *
from text_to_speech import *


#create each node in the story
theater = StoryNode("theater")
box_office = StoryNode("box office")
concessions = StoryNode("concessions")
ticket_checker = StoryNode("ticket checker")
movie = StoryNode("movie")

#add connections between nodes
theater.addChild(box_office).addChild(concessions)

concessions.addChild(box_office).addChild(ticket_checker)
box_office.addChild(concessions).addChild(ticket_checker)
ticket_checker.addChild(movie)


#add prerequisites (something that must be completed before moving to this node)
ticket_checker.addPrereq("ticket")

#movies and menu are lists of options for the activity
movies = ["Inside Out", "Tomorrowland", "Minions", "Home"]
menu = ["soda", "popcorn", "candy", "finished"]

#create activities and add them to their corresponding nodes
theater.setActivity(Activity(theaterActivity))
box_office.setActivity(Activity(boxOfficeActivity, movies))
concessions.setActivity(Activity(concessionsActivity, menu))
ticket_checker.setActivity(Activity(ticketCheckerActivity))
movie.setActivity(Activity(movieActivity))


movie_story_line = [theater, concessions, box_office, ticket_checker, movie]
'''
