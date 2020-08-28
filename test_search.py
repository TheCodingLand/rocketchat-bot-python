from atlassian import Confluence


confluence = Confluence(
    url='https://confluence.julien.tech',
    username='confluence',
    password='186o73l7')
 

def search_word_in_space(space, word):
    """
    Get all found pages with order by created date
    :param space
    :param word:
    :return: json answer
    """
    cql = f"space in ({space}) and (text ~ \"{word}\")"
    print(cql)
    answers = confluence.cql(cql, expand='space,body.view')
    
    
    for answer in answers.get('results'):
        print(answer)
    print(answers)
    return answers.get('results')

search_word_in_space('TEAM',"Points de discussion")
#atlassian-python-api   1.16.1