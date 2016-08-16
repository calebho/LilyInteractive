from story import Story 
from speech_recog import get_input
from text_to_speech import speak
from threading import Thread
from avatar_player import run_avatar

WKSPACE_ID = "569456a8-facf-431d-a963-493d905b77ea" 

def set_actions(s):
    # movie greeting
    text = "Hello! Welcome to the Lehigh Valley Movie Theater. " +\
            "You can go to the box office and get your ticket " +\
            "or you can go to the concessions for some snacks. " +\
            "Where would you like to go {name}?" 
    s.add_say('movie_greeting', text)

    # box office
    text = "Welcome to the box office. Which movie would you like to watch? " +\
            "We have tickets for {movie_names}" 
    s.add_say('box_office', text)
    fail_message = "Sorry we're not showing that at the moment. " +\
            "Please choose another movie to watch."
    s.add_listen('box_office', intent='buy_ticket', entity_type='movies', n_entities=1,
            verify_with='movie_names', context_key='movie_choice',
            fail_message=fail_message)
    text = "Here's your ticket. Enjoy the show. " +\
            "Would you like to go to the concessions or the auditorium?"
    s.add_say('box_office', text)

    # concessions
    text = "What can I get for you? We have {menu}"
    s.add_say('concessions', text)
    fail_message = "Sorry we don't have that on our menu."
    s.add_listen('concessions', intent='order_food', entity_type='snacks',
            verify_with='menu', context_key='bought', fail_message=fail_message)
    text = "Thank you. Here's your {bought}. " +\
            "If you do not have your ticket yet, go to the box office. " +\
            "Otherwise, you can go to the auditorium."
    s.add_say('concessions', text)

    # auditorium
    text = "Hello, ticket please! {movie_choice} is in theater 3 A, enjoy the movie! "
    s.add_say('auditorium', text)
    s.add_play('auditorium', "https://www.youtube.com/watch?v=_MC3XuMvsDI", 
            only_if=('movie_choice', 'inside out'))
    s.add_play('auditorium', "https://www.youtube.com/watch?v=1k59gXTWf-A", 
            only_if=('movie_choice', 'tomorrowland'))
    s.add_play('auditorium',"https://www.youtube.com/watch?v=eisKxhjBnZ0", 
            only_if=('movie_choice', 'minions'))
    s.add_play('auditorium', "https://www.youtube.com/watch?v=MyqZf8LiWvM", 
            only_if=('movie_choice', 'home'))

def get_name():
    speak('Could you spell your name for me?')
    return get_input()

def movie_story_factory():
    """Create and return the movie story
    """
    s = Story(input_fct=get_input, output_fct=speak, workspace_id=WKSPACE_ID)
    s.add_node('movie_greeting')
    s.add_node('box_office')
    s.add_node('concessions')
    s.add_node('auditorium')
    s.current = 'movie_greeting'
    set_actions(s)

    # dependencies = {actions.ticket_checker: {actions.box_office: None}}
    # s.require_visit('auditorium', 'box_office')

    dir_edges = [('movie_greeting', 'box_office'),
                 ('movie_greeting', 'concessions'),
                 ('box_office', 'auditorium'),
                 ('concessions', 'auditorium')]
    undir_edges = [('box_office', 'concessions')]
    s.add_edges_from(dir_edges)
    s.add_undirected_edges_from(undir_edges)

    context = {'name': get_name(), 
               'movie_names': ["inside out", "tomorrowland", "minions", "home"],
               'movie_choice': None,
               'menu': ["soda", "popcorn", "candy"],
               'bought': []}
    s.update_context(context)

    s.verify()

    return s

def main():
    s = movie_story_factory()
    thread = Thread(target=run_avatar)
    thread.daemon = True
    thread.start()
    while not s.is_finished:
        s()

if __name__ == '__main__':
    main()
