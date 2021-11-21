import requests


def get_data(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return {}


def gen_user_password(len=9):
    from password_generator import PasswordGenerator

    pwo = PasswordGenerator()
    pwo.minlen = len
    pwo.maxlen = len
    pwo.minuchars = 1
    pwo.minlchars = 1
    pwo.minnumbers = 1
    pwo.minschars = 1
    return pwo.generate()


def gen_user_attributes(user):
    data = {
        'first_name': user['name']['givenName'],
        'last_name': user['name']['familyName'],
        'nickname': user['name']['formatted'],
        'userName': user['userName'],
    }
    result = {}
    result['raw_data'] = user
    result['id'] = user['userName']
    result['name'] = data['nickname']
    status = user['urn:ietf:params:scim:schemas:extension:hr:2.0:User']['FSTATUS']
    result['status'] = 'enabled' if str(status) == '1' else 'disabled'
    result['group_id'] = user['urn:ietf:params:scim:schemas:extension:hr:2.0:User'].get('FDEPT_ID')
    result['attributes'] = data

    return result


def gen_group_attributes(group):
    result = {}
    result['raw_data'] = group
    result['id'] = group['id']
    status= group['urn:ietf:params:scim:schemas:extension:hr:2.0:Group']['FSTATUS']
    result['status'] = 'enabled' if str(status) == '3' else 'disabled'
    result['name'] = group['displayName'].strip().strip('/').replace('/','_')
    result['members'] = group.get('members',[])
    return result
