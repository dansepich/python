import requests
import os
from datetime import date
import textAlert
import yaml

key = os.environ['trelloKey']
token = os.environ['trelloToken']
prop_file = 'trello.yaml'

def create_board():
    url = "https://api.trello.com/1/boards/"
    query_string = {"name":"Daily To Do's","defaultLabels":"true","defaultLists":"true","keepFromSource":"none","prefs_permissionLevel":"private","prefs_voting":"disabled","prefs_comments":"members","prefs_invitations":"members","prefs_selfJoin":"true","prefs_cardCovers":"true","prefs_background":"blue","prefs_cardAging":"regular","key":key,"token":token}

    response = requests.request("POST", url, params=query_string)
    board_id=response.json()['id']
    return board_id

def get_list(board_id, list_name):
    url = "https://api.trello.com/1/boards/"+board_id+"/lists"
    query_string = {"cards":"none","card_fields":"all","filter":"open","fields":"all","key":key,"token":token}
    response = requests.request("GET", url, params=query_string)
    for list in response.json():
        if list['name'] == list_name:
            return list['id']

    return 'No ID Found'

def add_cards(list_id):
    add_cards_URL = "https://api.trello.com/1/cards"
    existing_cards_URL = "https://api.trello.com/1/lists/"+list_id+"/cards/"
    query_string = {"key":key,"token":token}
    existing_cards_details = requests.request("GET", existing_cards_URL, params=query_string)
    for todo in get_list_from_props('todos'):
        if not todo in existing_cards_details.text:
            query_string = {"idList":list_id,"keepFromSource":"all","key":key,"token":token,"name":todo}
            response = requests.request("POST", add_cards_URL, params=query_string)
            add_label(response.json()['id'], 'blue')

def add_label(card_id, color):
    url = "https://api.trello.com/1/cards/"+card_id+"/labels"
    querystring = {"color":color,"key":key,"token":token}
    response = requests.request("POST", url, params=querystring)
    return response

def text_link(board_id):
    url = "https://api.trello.com/1/boards/"+board_id

    query_string = {"fields":"url","key":key,"token":token}
    response = requests.request("GET", url, params=query_string)
    for number in get_list_from_props('numbers'):
        print(str(number)+'@mms.att.net', str(date.today())+' Trello Board: '+ response.json()['url'])
        textAlert.sendEmail(os.environ['gmail'], os.environ['gmailpswd'], str(number)+'@mms.att.net', 'Trello Board', str(date.today())+' Trello Board: '+ response.json()['url'])


def get_list_from_props(key_name):
    with open(prop_file) as file:
        documents = yaml.full_load(file)
        for key, val in documents.items():
            if(key == key_name):
                return val

def board_exists(board_ID):
    url = "https://api.trello.com/1/boards/"+board_ID
    query_string = {"key":key,"token":token}
    response = requests.request("GET", url, params=query_string)
    return(response)

def cleanup_list(list_ID):
    url = "https://api.trello.com/1/lists/"+list_ID+"/archiveAllCards"
    query_string = {"key":key,"token":token}
    response = requests.request("POST", url, params=query_string)
    return(response)

def main():
    board_ID = '0'
    if os.path.exists("activeBoard.txt"):
        with open("activeBoard.txt") as f: # The with keyword automatically closes the file when you are done
            board_ID = f.read().replace('\n', '')
    if str(board_exists(board_ID)) == '<Response [200]>':
        ##Archive cards in Done column
        cleanup_list(get_list(board_ID,'Done'))
        ##Add default items to list
        add_cards(get_list(board_ID,'To Do'))

    else:
        board_ID = create_board()
        add_cards(get_list(board_ID, 'To Do'))
        with open("activeBoard.txt", 'w') as f:
            f.write(board_ID)

    text_link(board_ID)

if __name__ == '__main__':
        main()



