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
current_todoist = todoist.projects.get_data(todoist_inbox_id)['items']


def load_master_tasklist():
    try:
        readable_picklefile = open("master_tasklist.pickle", "rb")
        return pickle.load(readable_picklefile)
    except IOError:
        return []


master_tasklist = load_master_tasklist()


def get_current_ids(task):
    return task['id']


def get_previous_ids(task):
    return task['todoist_id']


def get_actionable_tasks():
    previous_ids = map(get_previous_ids, master_tasklist)
    current_ids = map(get_current_ids, current_todoist)
    new_ids = set(current_ids) - set(previous_ids)
    completed_ids = set(previous_ids) - set(current_ids)
    actionable_tasks = {'new': [], 'completed': []}
    for id in new_ids:
        for task in current_todoist:
            if task['id'] == id:
                actionable_tasks['new'].append(task)
    for id in completed_ids:
        for task in master_tasklist:
            if task['todoist_id'] == id:
                actionable_tasks['completed'].append(task)
    return actionable_tasks


actionable_tasks = get_actionable_tasks()
new_tasks = actionable_tasks['new']
completed_tasks = actionable_tasks['completed']

print('master:')
print(master_tasklist)
print('new:')
print(new_tasks)
print('completed:')
print(completed_tasks)

# HABITICA


def make_header(type, url):
    return {
        'url': url,
        'type': type,
        'dataType': 'json',
        'cache': 'false',
        'x-client': 'f7326ed7-2543-4335-ae82-c6bc91bb1483-rpgtodo',
        'x-api-user': auth['habitica_user'],
        'x-api-key': auth['habitica_api'],
    }


# new tasks


def new_tasks_to_habitica():
    url = 'https://habitica.com/api/v3/tasks/user'
    header = make_header('POST', url)
    payload = []
    for task in new_tasks:
        payload.append({
            'type': 'todo',
            'text': task['content'],
            'notes': task['id']})
    return requests.post(url, json=payload, headers=header)


def new_tasks_to_master(new_tasks):
    for task in new_tasks:
        master_tasklist.append({
            'text': task['text'],
            'todoist_id': task['notes'],
            'habitica_id': task['id']
        })


new_habitica_tasks_response = new_tasks_to_habitica().json()['data']
new_tasks_to_master(new_habitica_tasks_response)

print('master:')
print(master_tasklist)

# completed tasks

# pickle.dump(current_todoist, open("master_tasklist.pickle", "wb"))
