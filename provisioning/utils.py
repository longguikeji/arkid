import json
from .models import Config
from inventory.models import User
from scim2_client.scim_service import ScimService


def build_users_url(c: Config) -> str:
    return f'{c.endpoint}/Users'


def user_exists(service: ScimService, c: Config, user: User) -> bool:
    """
    GET /Users?filter=userName eq "demo"

    Assume:

    200 OK
    404 NOT FOUND
    """
    # filter_str = 'userName eq "{}"'.format(user.username)
    # 'emails[primary eq "true" and type eq "work" and value eq "test@qq.com"]'
    for filter_str in c.get_filter_str(user):
        print(filter_str)
        code, text = service.search('Users').filter(filter_str).invoke()
        print(code, text)
        if code == 200:
            total = json.loads(text).get('totalResults')
            if total == 0:
                continue
            else:
                id = json.loads(text).get('Resources')[0].get("id")
                return id
        else:
            continue
    return False


def create_user(service: ScimService, c: Config, user: User):
    """
    POST /Users
    """

    data = c.get_user_mapped_data(user)
    data.update(
        {
            'externalId': user.uuid.hex,
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        }
    )
    code, text = service.create('Users', data).invoke()
    print(code, text)
    if code == 201:
        return json.loads(text).get('id')
    else:
        return False


def list_users(service: ScimService, c: Config):
    """
    GET /Users
    """
    code, text = service.search('Users').invoke()
    print(code, text)


def retrieve_user(service: ScimService, c: Config, user_id: str):
    """
    GET /Users/$user_id
    """
    code, text = service.retrieve('Users/', user_id).invoke()
    print(code, text)


def update_user(service: ScimService, c: Config, user: User, user_id: str):
    """
    PUT /Users/$user_id

    """
    data = c.get_user_mapped_data(user)
    data.update(
        {
            "externalId": user.uuid.hex,
            "id": user_id,
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        }
    )
    code, text = service.replace('Users/', user_id, data).invoke()
    print(code, text)


def patch_user(service: ScimService, c: Config, user_id: str):
    """
    PATCH /Users/$user_id

    """
    code, text = service.modify('Users/', user_id).invoke()
    print(code, text)


def delete_user(service: ScimService, c: Config, user_id: str):
    """
    DELETE /Users/$user_id
    """
    code, text = service.delete('Users/', user_id).invoke()
    print(code, text)
    if code == 204:
        return True
    else:
        return False


def create_groups(service: ScimService, c: Config):
    """
    POST /Groups
    """


def list_groups(c: Config):
    """
    GET /Groups?startIndex=1&count=100 HTTP/1.1
    """


def retrieve_group(c: Config):
    """
    GET /Groups/$groupID
    """


def update_group(c: Config):
    """
    PUT /Groups/$group_id

    """


def patch_group(c: Config):
    """
    PATCH /Groups/$group_id

    """


def delete_group(c: Config):
    """
    DELETE /Groups/$group_id
    """
