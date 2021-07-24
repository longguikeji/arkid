import json
from siteapi.v1.serializers.user import EmployeeSerializer, UserWithPermSerializer
from siteapi.v1.serializers.group import GroupDetailSerializer
from siteapi.v1.serializers.dept import DeptDetailSerializer

# def generate_app_payload(app):
#     data = {
#         'uuid': app.uuid,
#         'name': app.name,
#         'url': app.url,
#         'description': app.description,
#         'type': app.type,
#         'data': app.data,
#     }
#     return json.dumps(data)


def generate_user_payload(user, from_register=False):
    if from_register:
        data = UserWithPermSerializer(user).data
    else:
        data = EmployeeSerializer(user).data
    return json.dumps(data)


def generate_group_payload(group):
    data = GroupDetailSerializer(group).data
    return json.dumps(data)


def generate_dept_payload(dept):
    data = DeptDetailSerializer(dept).data
    return json.dumps(data)
