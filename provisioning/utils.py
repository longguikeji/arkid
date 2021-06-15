import json
import aiohttp
import asyncio
from .models import Config
from inventory.models import User
from scim_client.async_client import AsyncSCIMClient

def build_users_url(c: Config) -> str:
    return f'{c.endpoint}/Users'


def user_exists(client: AsyncSCIMClient, c: Config, user: User) -> bool:
    """
    GET /Users?filter=userName eq "demo"

    Assume:

    200 OK
    404 NOT FOUND
    """
    # filter_str = 'userName eq "{}"'.format(user.username)
    # 'emails[primary eq "true" and type eq "work" and value eq "test@qq.com"]'
    filter_str = c.get_match_filter(user)
    print(filter_str)
    response = asyncio.run(client.search_users(start_index=1, count=100, filter=filter_str))
    print(response)
    if response.status_code == 200:
        users = response.users
        if len(users) > 0:
            return True
        else:
            return False
    return False


def create_user(client: AsyncSCIMClient, c: Config, user: User):
    """
    POST /Users
    """

    data = c.get_user_mapped_data(user)
    # data.update(
    #     {
    #         'externalId': user.uuid.hex,
    #         "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    #     }
    # )
    response = asyncio.run(client.create_user(data))
    print(response)
    if response.status_code == 201:
        # return json.loads(text).get('id')
        print('create user success')
        return response.user
    else:
        return False


def list_users(client: AsyncSCIMClient, c: Config):
    """
    GET /Users
    """
    response = asyncio.run(client.search_users(count=50, start_index=1))
    print(response.users)


def retrieve_user(client: AsyncSCIMClient, c: Config, user_id: str):
    """
    GET /Users/$user_id
    """
    response = asyncio.run(client.read_user(user_id))
    print(response.user)


def update_user(client: AsyncSCIMClient, c: Config, user: User, user_id: str):
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
    response = asyncio.run(client.update_user(user_id, data))
    print(response.user)


def patch_user(client: AsyncSCIMClient, c: Config, user:User, user_id: str):
    """
    PATCH /Users/$user_id

    """
    data = c.get_user_mapped_data(user)
    response = asyncio.run(client.patch_user(user_id, data))
    print(response.user)


def delete_user(client: AsyncSCIMClient, c: Config, user_id: str):
    """
    DELETE /Users/$user_id
    """
    response = asyncio.run(client.delete_user(user_id))
    print(response)
    if response.status_code == 204:
        return True
    else:
        return False


def create_groups(client: AsyncSCIMClient, c: Config):
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
