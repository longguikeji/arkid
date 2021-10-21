#!/usr/bin/env python3
from scim_server.schemas.attribute_names import AttributeNames


class ExtensionAttributeEnterpriseUserBase:
    @property
    def cost_center(self):
        if not hasattr(self, '_cost_center'):
            return None
        return self._cost_center

    @cost_center.setter
    def cost_center(self, value):
        self._cost_center = value

    @property
    def department(self):
        if not hasattr(self, '_department'):
            return None
        return self._department

    @department.setter
    def department(self, value):
        self._department = value

    @property
    def division(self):
        if not hasattr(self, '_division'):
            return None
        return self._division

    @division.setter
    def division(self, value):
        self._division = value

    @property
    def employee_number(self):
        if not hasattr(self, '_employee_number'):
            return None
        return self._employee_number

    @employee_number.setter
    def employee_number(self, value):
        self._employee_number = value

    @property
    def organization(self):
        if not hasattr(self, '_organization'):
            return None
        return self._organization

    @organization.setter
    def organization(self, value):
        self._organization = value

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        if not d:
            return obj
        buffer = {}
        for item in [
            AttributeNames.CostCenter,
            AttributeNames.Department,
            AttributeNames.Division,
            AttributeNames.EmployeeNumber,
            AttributeNames.Organization,
        ]:
            if item in d:
                buffer[item] = d.get(item)
        for key, value in buffer.items():
            setattr(obj, key, value)
        return obj

    def to_dict(self):
        d = {}
        if self.cost_center:
            d[AttributeNames.CostCenter] = self.cost_center
        if self.department:
            d[AttributeNames.Department] = self.department
        if self.division:
            d[AttributeNames.Division] = self.division
        if self.employee_number:
            d[AttributeNames.EmployeeNumber] = self.employee_number
        if self.organization:
            d[AttributeNames.Organization] = self.organization
        return d
