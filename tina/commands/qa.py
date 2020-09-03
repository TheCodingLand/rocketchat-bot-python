
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
        if len(result[0][0]['answer'][0]) >0:
            answer=result[0][0]['answer'][a]
            proba=result[1][0]['probability'][a]
            break
    
    root.warn(answer)

    context = context.replace("\n", " ")
    context = context.replace("\t", " ")
    
    
    start=context.find(answer)
    end = start + len(answer)
    html_answer=f'<p>{context[start-20:start]}</p><span style="background-color:#dfd;">{context[start:end]}</span><p>{context[end:end+20]}</p>'
    #print(html_answer)

    return { "context": context, "question" : question, "start" : start, "end": end, "html" :html_answer, "link": "test", 'proba': proba}



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
                full_context = f"\n{text_content}"
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
            

            await self.master.ddp.send_message(message.roomid, f"{best['html']}")

                

            
            
            
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
            

test =  {'context': ' To replicate this installation from scratch (new vm)Install Docker (run this script, or use an Ansible playbook)install.sh\nsudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common\ncurl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -\nsudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"\nsudo apt-get update && apt-get install docker-ce docker-ce-cli containerd.io \nsudo apt-get install docker-compose\nsudo docker network create proxy\nThen:Create the docker-compose.yml file (see the contents below)Create a /opt/confluence_deployment/.env file (for environment variables, containing two variable definitions ; DOMAIN (probably "ctg.lu"), and DB_PASS. DB_PASS is the password for the confluence postgres database)Create /opt/confluence_deployment/volumes folderAdd the configuration and certificates for traefik (/opt/conflunce_deployment/traefik)run docker-compose up -dTo restore the server in a new VM (Ubuntu)Install docker (see script above)Restore  /opt/confluence_deployment/ (maybe see the volumes descriptions below)Run docker-compose up -ddocker-compose.ymldocker-compose.yml\nversion: "2.4"\nservices:\n\n  traefik:\n    image: traefik:v2.2\n    restart: unless-stopped\n    command:\n      - "--api=true"\n      - "--api.dashboard=true"\n      - "--entrypoints.web.address=:80"\n      - "--entrypoints.websecure.address=:443"\n      - "--providers.file.directory=/configuration/"\n      - "--providers.docker=true"\n      - "--providers.docker.exposedbydefault=false"\n      - "--providers.docker.watch=true"\n      - "--providers.docker.endpoint=unix:///var/run/docker.sock"\n      - "--providers.docker.network=proxy"\n      - "--entrypoints.web.http.redirections.entryPoint.to=websecure"\n      - "--entrypoints.web.http.redirections.entryPoint.scheme=https"\n      - "--entrypoints.web.http.redirections.entrypoint.permanent=true"\n\n    volumes:\n      - /var/run/docker.sock:/var/run/docker.sock\n      - ./volumes/traefik/certs:/certs\n      - ./volumes/traefik/configuration:/configuration/\n\n    networks:\n      - proxy\n\n    ports:\n      - 80:80\n      - 443:443\n\n    labels:\n\n        - "traefik.enable=true"\n        - "traefik.http.routers.traefik.rule=Host(`traefik-confluence.${DOMAIN}`)"\n        - "traefik.http.routers.traefik.service=api@internal"\n        - "traefik.http.routers.traefik.middlewares=traefik-auth"\n\n  postgres:\n    image: postgres:10\n    restart: unless-stopped\n    volumes:\n      - ./volumes/database:/var/lib/postgresql/data\n    networks:\n      - proxy\n    environment:\n      - POSTGRES_PASSWORD=${DB_PASS}\n      - POSTGRES_USER=confluence\n      - POSTGRES_DB=confluence\n\n  confluence:\n    image: atlassian/confluence-server:7.6.1\n    restart: unless-stopped\n    environment:\n      ATL_PROXY_NAME: confluence.ctg.lu\n      ATL_PROXY_PORT: 443\n      ATL_TOMCAT_SCHEME: https\n      JVM_MAXIMUM_MEMORY: 4096m\n      JAVA_TOOL_OPTIONS: " -Duser.timezone=\\"Europe/Berlin\\" "\n\n    volumes:\n      - ./volumes/confluence-home:/var/atlassian/application-data/confluence\n\n    labels:\n      - "traefik.http.routers.confluence_http.rule=Host(`confluence.${DOMAIN}`)"\n      - "traefik.http.routers.confluence_http.entrypoints=web,websecure"\n      - "traefik.enable=true"\n      - "traefik.http.routers.confluence_http.tls=true"\n      - "traefik.http.services.confluence_http.loadbalancer.server.port=8090"\n\n    networks:\n      - proxy\n\n\nnetworks:\n    proxy:\n        external: true\n\n\nUpgradingTo upgrade to a new version:1 - check that the plugins are available for the new version https://confluence.ctg.lu/plugins/servlet/troubleshooting/pre-upgrade/2 - check availability of the official docker image :https://hub.docker.com/r/atlassian/confluence-server/tags3 - write down the tag name, here, 7.6.2.4 - for safety; create a copy of /opt/confluence_deployment/volumes (as a temporary backup)6 - Update all plugins.5 - edit docker-compose.yml, and change the line where the image version is defined. like this:\n  confluence:\n    image: atlassian/confluence-server:7.6.1 \n    restart: unless-stopped\nTo:\n  confluence:\n    image: atlassian/confluence-server:7.6.2\n    restart: unless-stopped\n6 - type docker-compose up -d7 - Confluence can take up to 4-5mn to start, so just relax, take a cup of tea. traefik will give you a bad gateway error. it is normal. after 4 to 5 mn, you\'ll have this page after logging in.You are done.TroubleshootingYou a have access to all the normal log files in  /opt/confluence_deployment/confluence-home/logsYou can also just type docker-compose logs -t confluence to see the standard output of the server.InfrastructureI used the out of the box configuration to facilitate the move towards a cluster install if required down the line.3 containers are running in an isolated network owned by root (Docker Group): - confluence (no ports exposed) - postgres (no ports exposed) - traefik : port 80-443 exposedThe host itself has port 80 and 443 exposed to ctg.lu network.We use the setup below, where local home is in a volume, and database server\'s data is also in a volume (detailed below)Volumes detailsConfluence Home is in: /opt/confluence_deployment/volumes/confluence-home/Database is in: /opt/confluence_deployment/volumes/databaseReverse proxy config file traefik.toml is in: /opt/confluence_deployment/volumes/traefik/configurationCertificates for https are in: /opt/confluence_deployment/volumes/traefik/certsCluster setup1 - Expose the database:Currently, the database server is postgres 10, running in a container locally on the host, in the isolated network. it does not directly expose it\'s ports, but you could do that by adding a ports directive in the docker-compose file.ports\n   image: postgres:10\n   restart: unless-stopped\n   ports:\n     - 5432:5432\nAlso expose the host port, so your other confluence installs can communicateOr, if you want a dedicated postgres server, create a new VM, install postgres and copy the content of /opt/confluence_deployment/volumes/database/ in your postgres root.in both cases, you have to update the confluence config:You will have to update the connexion details in confluence.To do that, just edit /opt/confluence_deployment/volumes/confluence-home/confluence.cfg.xml and change the host name of the jdbc <property name="hibernate.connection.url"> string.if you exposed the current container to other hosts, just use  <property name="hibernate.connection.url">jdbc:postgresql://confluence.ctg.lu:5432/confluence</property>2 - Share the ./volumes/confluence-home/shared-home folder between all hosts:Can be done easily by creating a share on some nfs server and mounting it into /opt/volumes/confluence-home/shared-homeFAQWhat is traefik.toml ?It\'s just a file that helps traefik find the correct certificates to serve for https.Here is the contents.traefik.toml\n[[tls.certificates]]\n  certFile = "/certs/server.pem"\n  keyFile = "/certs/ctg_lu_wildcard.key"\n\n\nHow do I renew the https certificates when they expire ?put the new root certificate in /opt/ctglu-wildcard-certcd /opt/Run the script below. (CERT_NAME variable is the base file name of the key / crt files) There is no error checking, so please backups the /confluence_deployment/volumes/traefik folder if necessary.renew_certificates.sh\n#generate server .pem for traefik\n\nCERT_NAME=ctg_lu_wildcard_2019\n\necho "key file is $CERT_NAME.key"\ncat "ctglu-wildcard-cert/$CERT_NAME.crt" > server.pem\ncat "ctglu-wildcard-cert/$CERT_NAME-ca.crt" >> server.pem\n\n\ncp $CERT_NAME.key ./confluence_deployment/volumes/traefik/certs/ctg_lu_wildcard.key\ncp server.pem ./confluence_deployment/volumes/traefik/certs/server.pem\ndocker-compose restart traefik\n\n\n\n', 'question': 'docker', 'start': -1, 'end': 26, 'html': '<p>e restart traefik\n\n\n</p><span style="background-color:#dfd;"></span><p>ation from scratch (</p>', 'link': 'test', 'proba': 0.12751578821925358}