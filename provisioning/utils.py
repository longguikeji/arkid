from .models import Config
from inventory.models import User


def build_users_url(c: Config) -> str:
    return f'{c.endpoint}/Users'


def user_exists(c: Config, user: User) -> bool:
    '''
    GET /Users?filter=userName eq "demo"

    Assume:

    200 OK
    404 NOT FOUND
    '''
    pass


def create_user(c: Config, user: User):
    '''
    POST /Users
    '''
    pass


def list_users(c: Config):
    '''
    GET /Users
    '''
    pass


def retrieve_user(c: Config):
    '''
    GET /Users/$user_id
    '''
    pass


def update_user(c: Config):
    '''
    PUT /Users/$user_id

    '''


def patch_user(c: Config):
    '''
    PATCH /Users/$user_id

    '''


def delete_user(c: Config):
    '''
    DELETE /Users/$user_id
    '''



def create_groups(c: Config):
    '''
    POST /Groups
    '''


def list_groups(c: Config):
    '''
    GET /Groups?startIndex=1&count=100 HTTP/1.1
    '''


def retrieve_group(c: Config):
    '''
    GET /Groups/$groupID
    '''


def update_group(c: Config):
    '''
    PUT /Groups/$group_id

    '''


def patch_group(c: Config):
    '''
    PATCH /Groups/$group_id

    '''


def delete_group(c: Config):
    '''
    DELETE /Groups/$group_id
    '''
