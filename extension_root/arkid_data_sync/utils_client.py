import requests
import json


def get_data(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return {}


def gen_user_attributes(user):
    data = {
        "first_name": user["name"].get("givenName", "") if user.get("name") else "",
        "last_name": user["name"].get("familyName", "") if user.get("name") else "",
        "nickname": user["name"].get("formatted", "") if user.get("name") else "",
        # "employee_id": user[
        #     "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
        # ].get("employeeNumber"),
        "username": user["userName"],
        "email": user["emails"][0].get("value", "") if user.get("emails") else "",
        "scim_external_id": user["id"],
    }
    result = {}
    result["raw_data"] = user
    result["id"] = user["id"]
    result["name"] = data["nickname"]
    # status = user['urn:ietf:params:scim:schemas:extension:hr:2.0:User']['FSTATUS']
    # result['status'] = 'enabled' if str(status) == '1' else 'disabled'
    result["group_id"] = user[
        "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
    ].get("department")
    result["attributes"] = data

    return result


def gen_group_attributes(group):
    result = {}
    result["raw_data"] = group
    result["id"] = group["id"]
    # status = group["urn:ietf:params:scim:schemas:extension:hr:2.0:Group"]["FSTATUS"]
    # result["status"] = "enabled" if str(status) == "3" else "disabled"
    result["name"] = group["displayName"]
    result["members"] = group.get("members", [])
    return result
