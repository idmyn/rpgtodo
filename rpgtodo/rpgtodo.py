import re
import pickle
from todoist.api import TodoistAPI
import requests


# TODOIST


def parse_auth():
    auth_contents = open("api_keys.txt").readlines()
    todoist_api_token = re.search(r"(?<=: )\S*", auth_contents[0]).group()
    habitica_user_id = re.search(r"(?<=: )\S*", auth_contents[1]).group()
    habitica_api_token = re.search(r"(?<=: )\S*", auth_contents[2]).group()
    auth_dict = {
        "todoist_api": todoist_api_token,
        "habitica_user": habitica_user_id,
        "habitica_api": habitica_api_token
    }
    # TODO: throw helpful error if user hasn't edited the api_keys.txt file
    return auth_dict


auth = parse_auth()
todoist = TodoistAPI(auth["todoist_api"])
todoist.sync()


def find_todoist_inbox(projects):
    for project in projects:
        try:
            project['inbox_project']
        except KeyError:
            pass
        else:
            break
    return project


todoist_inbox_id = find_todoist_inbox(todoist.state['projects'])['id']
current_uncompleted = todoist.projects.get_data(todoist_inbox_id)['items']


def load_previous_uncompleted():
    try:
        readable_picklefile = open("previous_uncompleted.pickle", "rb")
        return pickle.load(readable_picklefile)
    except IOError:
        return ''


previous_uncompleted = load_previous_uncompleted()


def get_uncompleted_ids(task):
    return task['id']


def get_completed_tasks():
    previous_ids = map(get_uncompleted_ids, previous_uncompleted)
    current_ids = map(get_uncompleted_ids, current_uncompleted)
    completed_ids = set(previous_ids) - set(current_ids)
    completed_tasks = []
    for id in completed_ids:
        for task in previous_uncompleted:
            if task['id'] == id:
                completed_tasks.append(task)
    return completed_tasks


completed_tasks = get_completed_tasks()

pickle.dump(current_uncompleted, open("previous_uncompleted.pickle", "wb"))

# HABITICA


def get_habitica_todos():
    url = 'https://habitica.com/api/v3/tasks/user'
    header = {
        'url': url,
        'type': 'GET',
        'dataType': 'json',
        'cache': 'false',
        'x-client': 'f7326ed7-2543-4335-ae82-c6bc91bb1483-rpgtodo',
        'x-api-user': auth['habitica_user'],
        'x-api-key': auth['habitica_api'],
    }
    todos = {'type': 'todos'}
    return requests.get(url, params=todos, headers=header).json()['data']


habitica_todos = get_habitica_todos()
