import requests
import os
from datetime import date
import textAlert
import yaml

key = os.environ['trelloKey']
token = os.environ['trelloToken']
propFile = 'trello.yaml'

def create_board():
    url = "https://api.trello.com/1/boards/"
    querystring = {"name":"Daily To Do's","defaultLabels":"true","defaultLists":"true","keepFromSource":"none","prefs_permissionLevel":"private","prefs_voting":"disabled","prefs_comments":"members","prefs_invitations":"members","prefs_selfJoin":"true","prefs_cardCovers":"true","prefs_background":"blue","prefs_cardAging":"regular","key":key,"token":token}

    response = requests.request("POST", url, params=querystring)
    board_id=response.json()['id']
    return board_id

def get_lists(board_id, list_name):
    url = "https://api.trello.com/1/boards/"+board_id+"/lists"
    querystring = {"cards":"none","card_fields":"all","filter":"open","fields":"all","key":key,"token":token}
    response = requests.request("GET", url, params=querystring)
    for list in response.json():
        if list['name'] == list_name:
            return list['id']

    return 'No ID Found'

def add_card(list_id):
    url = "https://api.trello.com/1/cards"
    
    for todo in getListFromProps('todos'):
        querystring = {"idList":list_id,"keepFromSource":"all","key":key,"token":token,"name":todo}
        response = requests.request("POST", url, params=querystring)


def text_link(board_id):
    url = "https://api.trello.com/1/boards/"+board_id

    querystring = {"actions":"all","boardStars":"none","cards":"none","card_pluginData":"false","checklists":"none","customFields":"false","fields":"name,desc,descData,closed,idOrganization,pinned,url,shortUrl,prefs,labelNames","lists":"open","members":"none","memberships":"none","membersInvited":"none","membersInvited_fields":"all","pluginData":"false","organization":"false","organization_pluginData":"false","myPrefs":"false","tags":"false","key":key,"token":token}
    response = requests.request("GET", url, params=querystring)
    for number in getListFromProps('numbers'):
        print(str(number)+'@mms.att.net', str(date.today())+' Trello Board: '+ response.json()['url'])
        textAlert.sendEmail(os.environ['gmail'], os.environ['gmailpswd'], str(number)+'@mms.att.net', 'Trello Board', str(date.today())+' Trello Board: '+ response.json()['url'])


def getListFromProps(keyName):
    with open(propFile) as file:
        documents = yaml.full_load(file)
        for key, val in documents.items():
            if(key == keyName):
                return val

def boardExists(boardID):
    url = "https://api.trello.com/1/boards/"+boardID
    querystring = {"key":key,"token":token}
    response = requests.request("GET", url, params=querystring)
    return(response)

def cleanupList(listID):
    url = "https://api.trello.com/1/lists/"+listID+"/archiveAllCards"
    querystring = {"key":key,"token":token}
    response = requests.request("POST", url, params=querystring)
    return(response)

def main():
    boardID = '0'
    if os.path.exists("activeBoard.txt"):
        with open("activeBoard.txt") as f: # The with keyword automatically closes the file when you are done
            boardID = f.read().replace('\n', '')
    if str(boardExists(boardID)) == '<Response [200]>':
        print('Board Exists')
        cleanupList(get_lists(boardID,'Done'))
    else:
        print('Board does not exist, creating new board')
        boardID = create_board()
        add_card(get_lists(boardID, 'To Do'))
        with open("activeBoard.txt", 'w') as f:
            f.write(boardID)

    text_link(boardID)

if __name__ == '__main__':
        main()



