"""
搜索
"""
import re
from django.views import View
from django.http.response import JsonResponse
from inventory.models import Group, User, Tenant
from extension.models import Extension
from ..attribute_mappings import attribute_mappings as attr_ms


class Search(View):
    """
    搜索
    """

    def get(self, request, tenant_uuid):    # pylint: disable=unused-argument
        """
        GET
        """
        filters = dict(request.GET)

        dn = filters.pop("dn")
        scope = filters.pop("scope")
        if "attributes" in filters.keys():
            attributes = filters.pop("attributes")
        elif "attributes[]" in filters.keys():
            attributes = filters.pop("attributes[]")
        else:
            attributes = None

        # attribute_mappings = self.get_attribute_mappings()

        # 处理过滤条件：
        # type
        filter_type = filters.pop("type")
        if isinstance(filter_type, list):
            filter_type = filter_type[0]

        res = []
        print(dn)
        # 处理dn
        item = dn[0]
        if "," in item:
            items = item.split(",")
            item = items[0]
            dn = items[1:]

        dc_suf = ","+",".join(dn)

        match_params = re.findall("(.*)=(.*)", item)
        if match_params:
            match_params = match_params[0]
        if match_params[0] == "ou":
            if match_params[1] == "people":
                people_item = {
                    "dn": "ou=people" + dc_suf,
                    "attributes": {
                        "objectClass": ["top", "organizationUnit"],
                        "ou": "people"
                    }
                }
                res.append(people_item)
                dc_suf = f",{item}{dc_suf}"
                res.extend(
                    self.user_search(
                        self.deal_filters(
                            filters,
                            filter_type,
                            match_params[1]
                        ),
                        self.get_attribute_mappings(
                            match_params[1]
                        ),
                        dc_suf
                    )
                )
            elif match_params[1] == "group":
                dc_suf = f",{item}{dc_suf}"
                res.extend(
                    self.group_search(
                        self.deal_filters(
                            filters,
                            filter_type,
                            match_params[1]
                        ),
                        self.get_attribute_mappings(
                            match_params[1]
                        ),
                        dc_suf
                    )
                )
        elif match_params[0] == "o":
            res.extend(
                self.tenant_search(
                    match_params[1],
                    dc_suf
                )
            )
        elif match_params[0] == "dc":
            top_item = {
                "dn": f"{item}" + dc_suf,
                "attributes": {
                    "objectClass": ["top", "organization", "dcObject"],
                    "dc": match_params[1]
                }
            }
            res.append(top_item)
            for tenant in Tenant.objects.all():
                res.extend(
                    self.tenant_search(
                        tenant.uuid,
                        f",{item}{dc_suf}"
                    )
                )

        # res = self.user_search(filters, attribute_mappings)

        return JsonResponse(
            data={
                "error": 0,
                "results": res
            }
        )

    def user_search(self, filters, attribute_mappings, dc_suf=None):  # pylint: disable=no-self-use
        """
        搜索
        """

        users = User.active_objects.filter(**filters).all()
        data = []
        for user in users:
            res = {}
            attributes = {}
            for k in attribute_mappings.keys():
                attributes[k] = getattr(user, attribute_mappings[k], None)

            res["dn"] = f"cn={user.username},ou=people{dc_suf}"
            attributes["objectClass"] = [
                "top", "person", "organizationalPerson"]
            res["attributes"] = attributes
            data.append(res)
        return data

    def group_search(self, filters, attribute_mappings, dc_suf=None):
        """
        群组搜索
        """
        groups = Group.active_objects.filter(**filters).all()
        data = []
        for group in groups:
            res = {}
            attributes = {}
            for k in attribute_mappings.keys():
                attributes[k] = getattr(group, attribute_mappings[k], None)

            res["dn"] = f"cn={group.name},ou=group{dc_suf}"
            attributes["objectClass"] = ["top", "group", "groupOfNames"]
            attributes["member"] = []
            for member in group.user_set.all():
                attributes["member"].append(
                    f"cn={member.username},ou=people{dc_suf}"
                )
            res["attributes"] = attributes
            data.append(res)
        return data

    def get_attribute_mappings(self, key="people"):  # pylint: disable=no-self-use
        """
        获取自定义字段
        """
        extension = Extension.active_objects.filter(type="ldapserver").last()
        user_items = extension.data.get(key, attr_ms.get(key))
        attribute_mappings = {}
        for k in user_items.keys():
            if user_items[k] and k in attr_ms[key].keys():
                attribute_mappings[k] = attr_ms[key][k]
        return attribute_mappings

    def tenant_search(self, tenant_uuid, dc_suf):
        res = []
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        tenant_res = {
            "dn": f"o={tenant.uuid}" + dc_suf,
            "attributes": {
                "objectClass": ["top", "organization", ],
                "o": tenant.uuid
            }
        }
        res.append(tenant_res)
        people_item = {
            "dn": f"ou=people,o={tenant.uuid}" + dc_suf,
            "attributes": {
                "objectClass": ["top", "organizationUnit"],
                "ou": "people"
            }
        }
        res.append(people_item)
        res.extend(self.user_search(
            {}, self.get_attribute_mappings("people"), dc_suf))

        group_item = {
            "dn": f"ou=group,o={tenant.uuid}" + dc_suf,
            "attributes": {
                "objectClass": ["top", "organizationUnit"],
                "ou": "group"
            }

        }
        res.append(group_item)
        res.extend(self.group_search(
            {}, self.get_attribute_mappings("group"), dc_suf))

        return res

    def deal_filters(self, filters, filter_type="EqualityMatch", key="people"):
        attribute_mappings = self.get_attribute_mappings(key)
        if filter_type == "EqualityMatch":
            filter_attribute = filters.pop("attribute")
            filter_value = filters.pop("value")
            if isinstance(filter_value, str):
                filter_value = [filter_value]

            if isinstance(filter_attribute, str):
                filter_attribute = [filter_attribute]

            if isinstance(filter_attribute, list) and isinstance(filter_value, list) and len(filter_attribute) == len(filter_value):
                for i in range(len(filter_attribute)):
                    if filter_attribute[i] == "givenname":
                        filter_attribute[i] = "givenName"
                    elif filter_attribute[i] == "telephonenumber":
                        filter_attribute[i] = "telephoneNumber"
                    if filter_attribute[i] in attribute_mappings.keys():
                        filters[attribute_mappings[filter_attribute[i]]
                                ] = filter_value[i]
        else:
            filters = {}

        return filters
