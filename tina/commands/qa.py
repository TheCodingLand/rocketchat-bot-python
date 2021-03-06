
import re
from typing import List, Tuple
import urllib
import unicodedata
import rocketbot.commands as c
import rocketbot.models as m
from atlassian import Confluence
import logging
from tina.ia.qa import QA

from bs4 import BeautifulSoup
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s', "%Y-%m-%d %H:%M:%S"))
root = logging.getLogger()
root.handlers.clear()
root.addHandler(console)

# Configure logglevels
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("rocketbot").setLevel(logging.INFO)


confluence = Confluence(
    url='https://confluence.ctg.lu',
    username='confluence_rc_bot',
    password='B186o73l7')
    
qa = QA() 


def get_body_content(t):
    

    text = BeautifulSoup(t, 'lxml').text
    text = unicodedata.normalize("NFKD", text)
    
    return text
def qa_prediction(question,context):
    result = qa.predict(context, question)
    
    root.warn(result)
    
    for a in range(0,len(result[0][0]['answer'])):
        if len(result[0][0]['answer'][a]) >0:
            answer= result[0][0]['answer'][a]
            proba=result[1][0]['probability'][a]
            break
    
    root.warn(answer)

    context = context.replace("\n", " ")
    context = context.replace("\t", " ")
    
    
    start=context.find(answer)
    end = start + len(answer)
    html_answer=f'<p>{context[start-20:start]}</p><span style="background-color:#dfd;">{context[start:end]}</span><p>{context[end:end+20]}</p>'
    #print(html_answer)

    return { "context": context, "question" : question, "start" : start, "end": end, "html" :html_answer, "link": "test", 'proba': proba, "answer": answer}



def search_word_in_space(space, word):
    """
    Get all found pages with order by created date
    :param space
    :param word:
    :return: json answer
    """
    #text= urllib.parse.quote(f'"{word}"', safe='')
    cql = f"type=page and space in ({space}) and (text ~ \"{word}\")"
    
    answers = confluence.cql(cql, expand='space,body.view')
    
    #root.warning(answers)
    return answers.get('results')[0:3]



class Confluence(c.BaseCommand):
    def usage(self) -> List[Tuple[str, str]]:
        return [
            ('search <sentence>', 'Searches for a sentence in confluence and refines results using AI.'),
        ]

    def can_handle(self, command: str) -> bool:
        """Check whether the command is applicable
        """
        return command in ['search', 'how do i']

    async def handle(self, command: str, args: str, message: m.Message) -> None:
        """Handle the incoming message
        """
        root.warning(message)
        if command == 'search':
            
            args = args.strip().lower()
            
            urls = []
            root.warning(args)
            results = search_word_in_space("DEV", args)
            for word in args.split(' '):
                for result in search_word_in_space("DEV", word):
                    results.append(result)
            #root.warning(results)
            pages =[]
            for answer in results:
                urls.append(answer['content']['_links']['webui'])
                page=confluence.get_page_by_id(answer['content']['id'], expand='body.view', status=None, version=None)
                pages.append(page)

            await self.master.ddp.send_message(message.roomid, f"Most relavant link:")
            await self.master.ddp.send_message(message.roomid, f"https://confluence.ctg.lu/{urls[0]}")
            await self.master.ddp.send_message(message.roomid, f"Some Results from Tina:")

            #final_results=[]
            full_context=""
            for page in pages:
                text_content = get_body_content(page['body']['view']['value'])
                full_context = f" {full_context} {text_content}"
                #root.warning(text_content)
                #return page_content['title'], page_content
            final_result = qa_prediction(args, full_context)
            #root.warn(final_result['context'])
            #final_results.append(final_result)
            best = final_result
            root.warn(best)
            
            #for result in final_results:
            #    
            #    if best == None:
            #        best = result
            #    else:
            #        if result['proba']>best['proba']:
            #            best=result
            #    root.warn(f"best proba: {best['proba']}")
            #    root.warn(f"best proba: {best['html']}")
            

            await self.master.ddp.send_message(message.roomid, f"{best['answer']}")
            return
                

            
            
            
            #user = message.mentions[0]
            #if user.username == message.created_by.username:
            #    await self.master.ddp.send_message(message.roomid, "Please mention someone other than yourself")
            #    return

            #result = await self.master.rest.users_list(count=0)
            #users = [m.create(m.User, u) for u in result.json()['users']]

            #username = user.name if user.name is not None else user.username
            #username = re.sub(r'\s', '_', username).lower()
            #name = f'geburtstag_{username}'
            #members = [u.username for u in users if u.username != user.username]
            #result = await self.master.rest.groups_create(name=name, members=members)

            #if result.status_code != 200:
            #    await self.master.ddp.send_message(message.roomid, result.json()['error'])
            #    return
            #room = m.create(m.Room, result.json()['group'])
            #await self.master.rest.groups_add_owner(room_id=room._id, user_id=message.created_by._id)
            
