import re
from todoist.api import TodoistAPI


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
todoist_uncompleted = todoist.projects.get_data(todoist_inbox_id)['items']
