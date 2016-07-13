import spacy
import spacy.parts_of_speech as pos

from spacy.attrs import TAG

NLP = spacy.en.English()
NLP.matcher.add("ItemChoice", "PRODUCT", {}, # arbitrary attributes ???
    [ # patterns
        [ # i.e. popcorn
            {TAG: "NN"}
        ],
        [ # i.e. ice cream
            {TAG: "NN"},
            {TAG: "NN"},
        ],
        [ # i.e. some chocolate
            {TAG: "DT"},
            {TAG: "NN"}
        ],
        [ # i.e. a cup of soda
            {TAG: "DT"},
            {TAG: "NN"},
            {TAG: "IN"},
            {TAG: "NN"}
        ]
        # TODO: a large cup of soda, ice cream in a cone, etc.
    ]
)

def parse_choices(s, examples):
    """Given a sentence `s` of user choices and a list of example sentences
    `examples`, parse and return a list of the choices
    """
    sim_threshold = 0.7
    user_sent = NLP(unicode(s))
    examples = [NLP(unicode(example)) for example in examples]
    ex_sent = max(examples, key=lambda s: s.similarity(user_sent))
    if user_sent.similarity(ex_sent) < sim_threshold:
        raise RuntimeError(
            "\nThe sentences\n\t%s\n\t%s\naren't similiar enough\n" % \
            (user_sent, ex_sent) + \
            "similarity score: %.4f" % user_sent.similarity(ex_sent))

    choices = []
    for ent in user_sent.ents:
        choices.append(ent.text)

    return choices

def are_similar(s, *examples, t=0.7):
    """Given a sentence `s` and an arbitrary number of example sentences,
    check the similarity between `s` and the example sentences

    Paramters:
    s {str|unicode} The sentence to compare
    *examples {str|unicode} The sentences against which `s` is compared 
    t {float} The similarity score lower bound

    Returns: {bool} True if the similarity score between `s` and at least one
    example sentence is greater than `t`; False otherwise
    """
    s = NLP(unicode(s))
    for ex in examples:
        ex_doc = NLP(unicode(ex))
        if s.similarity(ex_doc) >= t:
            return True

    return False

def main():
    food_sents = [u'I want popcorn and soda',
                  u'popcorn, candy, and chocolate',
                  u"I'd like some soda and a cup of coffee"]
    examples = ["I want an apple and an orange",
                "A glass of water and some chips"]

    for test_sent in food_sents:
        print parse_choices(test_sent, examples)

    movie_sents = [u'I want to watch captain america',
                   u"I'd like a ticket for spiderman",
                   u'Up, please'] # TODO: fails 
    examples = ["I want to watch Minions",
                "Tomorrowland, please",
                "Inside Out"]

    for test_sent in movie_sents:
        print parse_choices(test_sent, examples)


if __name__ == '__main__':
    main()
