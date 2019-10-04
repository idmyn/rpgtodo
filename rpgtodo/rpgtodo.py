import re
import pickle
from todoist.api import TodoistAPI
import requests
import os


def run():
    auth = FileRW().parse_auth()
    todoist = TodoistAPI(auth["todoist_api"])
    todoist.sync()

    master_tasklist = FileRW().load_master_tasklist()

    todoist_project_ids = [project['id'] for project in todoist.state['projects']]
    current_todoist = [todoist.projects.get_data(project_id)['items'] for project_id in todoist_project_ids]
    current_todoist = [y for x in current_todoist for y in x]

    actionable_tasks = get_actionable_tasks(master_tasklist, current_todoist)
    new_tasks = actionable_tasks['new']
    completed_tasks = actionable_tasks['completed']

    if new_tasks:
        new_habitica_tasks_response = new_tasks_to_habitica(auth, new_tasks).json()['data']
        new_tasks_to_master(new_habitica_tasks_response, new_tasks, master_tasklist)

    if completed_tasks:
        complete_tasks_on_habitica(auth, completed_tasks)
        remove_completed_from_master(completed_tasks, master_tasklist)

    print('master:')
    print(master_tasklist)
    print('\nnew:')
    print(new_tasks)
    print('\ncompleted:')
    print(completed_tasks)

    print('\nmaster:')
    print(master_tasklist)

    FileRW().save_master_tasklist(master_tasklist)


class FileRW:
    def __init__(self):
        self.dirname = os.path.dirname(__file__)
        self.pickle_path = os.path.join(self.dirname, 'master_tasklist.pickle')

    def parse_auth(self):
        api_keys_path = os.path.join(self.dirname, 'api_keys.txt')
        auth_contents = open(api_keys_path).readlines()
        todoist_api_token = re.search(r"(?<=: )\S*", auth_contents[0]).group()
        habitica_user_id = re.search(r"(?<=: )\S*", auth_contents[1]).group()
        habitica_api_token = re.search(r"(?<=: )\S*", auth_contents[2]).group()
        auth_dict = {
            "todoist_api": todoist_api_token.translate({ord(c): None for c in '()'}),
            "habitica_user": habitica_user_id.translate({ord(c): None for c in '()'}),
            "habitica_api": habitica_api_token.translate({ord(c): None for c in '()'})
        }
        # TODO: throw helpful error if user hasn't edited the api_keys.txt file
        return auth_dict

    def load_master_tasklist(self):
        try:
            readable_picklefile = open(self.pickle_path, "rb")
            return pickle.load(readable_picklefile)
        except IOError:
            return []

    def save_master_tasklist(self, master_tasklist):
        pickle.dump(master_tasklist, open(self.pickle_path, "wb"))


# TODOIST


def get_current_ids(task):
    return task['id']


def get_previous_ids(task):
    return task['todoist_id']


def get_actionable_tasks(master_tasklist, current_todoist):
    previous_ids = map(get_previous_ids, master_tasklist)
    current_ids = map(get_current_ids, current_todoist)
    new_ids = set(current_ids) - set(previous_ids)
    # subtracting the sets appears to be destructive
    previous_ids = map(get_previous_ids, master_tasklist)
    current_ids = map(get_current_ids, current_todoist)
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


# HABITICA


def make_header(auth, type, url):
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


def new_tasks_to_habitica(auth, new_tasks):
    url = 'https://habitica.com/api/v3/tasks/user'
    header = make_header(auth, 'POST', url)
    payload = []
    for task in new_tasks:
        payload.append({
            'type': 'todo',
            'text': task['content'],
            'notes': task['id']})
    return requests.post(url, json=payload, headers=header)


def new_tasks_to_master(habitica_response, new_tasks, master_tasklist):
    if len(new_tasks) > 1:
        for task in habitica_response:
            master_tasklist.append({
                'text': task['text'],
                'todoist_id': int(task['notes']),
                'habitica_id': task['id']
            })
    # if there is only 1 new task, habitica_response returns it as its own dict (not nested in a list)
    else:
        master_tasklist.append({
            'text': habitica_response['text'],
            'todoist_id': int(habitica_response['notes']),
            'habitica_id': habitica_response['id']
        })


# completed tasks


def complete_tasks_on_habitica(auth, completed_tasks):
    for task in completed_tasks:
        id = task['habitica_id']
        url = 'https://habitica.com/api/v3/tasks/' + id + '/score/up'
        header = make_header(auth, 'POST', url)
        try:
            response = requests.post(url, headers=header).json()['data']
            if 'drop' in response['_tmp']:
                print('')
                print(response['_tmp']['drop']['dialog'])
                print('')
        except KeyError:
            print("\ncouldn't find pending Habitica task matching '" + task['text'] + "'")


def remove_completed_from_master(completed_tasks, master_tasklist):
    for task in completed_tasks:
        master_tasklist.remove(task)


if __name__ == "__main__":
    run()
