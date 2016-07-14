import json

from watson_developer_cloud import ConversationV1

convo = ConversationV1(version='2016-07-11',
                       url="https://gateway.watsonplatform.net/conversation/api",
                       username='a183c3b3-538c-41ae-912e-6a4694261279',
                       password='XgEzF4MENrKf')

def get_entities(response, intent):
    """
    """
    if response['intents'][0]['intent'] == intent: # get intent w/ highest confidence
        return [entity['value'].lower() for entity in response['entities']]
    else:
        raise RuntimeError('Non-matching intents')

def parse(s, workspace_id):
    """Parse a string `s`

    Parameters:
    s {str} The string to parse
    workspace_id {str} The ID corresponding to the workspace created for 
                       any given storyline 

    Returns: {str} The response if the parse was successful
    """
    response = convo.message(workspace_id=workspace_id, message_input={'text': s})
    # print(json.dumps(response, indent=2))
    return response


def main():
    w_id = "569456a8-facf-431d-a963-493d905b77ea" # Movie workspace
    parse("I want to buy a ticket", w_id)

    parse("I want a ticket for Superman", w_id)

if __name__ == '__main__':
    main()


