import spacy
import spacy.parts_of_speech as pos

from spacy.attrs import TAG

NLP = spacy.en.English()
NLP.matcher.add("ItemChoice", "PRODUCT", {}, # arbitrary attributes ???
    [ # patterns
        [ # i.e. some chocolate
            {TAG: "DT"},
            {TAG: "NN"}
        ],
        [ # i.e. popcorn
            {TAG: "NN"}
        ],
        [ # i.e. a cup of soda
            {TAG: "DT"},
            {TAG: "NN"},
            {TAG: "IN"},
            {TAG: "NN"}
        ]
    ]
)

def parse_choices(s, example):
    """Given a sentence `s` of user choices and an example sentence `example`,
    parse and return a list of the choices
    """
    sim_threshold = 0.6
    user_sent = NLP(unicode(s))
    ex_sent = NLP(unicode(example))
    if user_sent.similarity(ex_sent) < sim_threshold:
        raise RuntimeError("The sentences\n%s\n%s\naren't similiar enough" % \
            (user_sent, ex_sent))

    choices = []
    for ent in user_sent:
        if len(ent) == 1: # just a noun
            choices.append(ent.text)
        else: # get the base noun
            noun_phrase = NLP(ent.text)
            chunk = noun_phrase.noun_chunks
            assert len(chunk) == 1
            choices.append(chunk.text)

    return choices 

def main():
    test_sents = [u'I want popcorn and soda',
                  u'Popcorn, candy, and chocolate',
                  u"I'd like some soda and a cup of coffee"]

    for test_sent in test_sents:
        doc = NLP(test_sent)
        for ent in doc.ents:
            print ent.text, ent.label_, [w.tag_ for w in ent]

if __name__ == '__main__':
    main()
