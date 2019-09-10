import re

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