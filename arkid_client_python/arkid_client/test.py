from arkid_client.auth.client import ConfidentialAppAuthClient
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.user import UserClient
from arkid_client.client import ArkIDClient


if __name__ == '__main__':
    ac = ConfidentialAppAuthClient()
    ac.start_auth('admin', 'admin')
    ba = BasicAuthorizer(oneid_token=ac.get_token())
    # uc = UserClient(authorizer=ba)
    # q = uc.query_user_list()
    ac = ArkIDClient('user', authorizer=ba)
    q = ac.query_user_list()
    print('q is', q)
