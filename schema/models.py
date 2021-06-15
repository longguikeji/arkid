from django.db import models
import jsonfield
from common.model import BaseModel
from provisioning.models import Config


class Schema(BaseModel):

    MAPPING_TYPE_CHOICES = (
        (0, 'None'),
        (1, 'Direct'),
        (2, 'Constant'),
        # (3, 'Expression'),  # Expression to be supported in ArkID
    )

    APPLY_TYPE_CHOICES = (
        (0, 'Always'),
        (1, 'Only during creation'),
    )

    provisioning_config = models.ForeignKey(Config, on_delete=models.CASCADE, related_name='app_profile_mappings')
    mapping_type = models.IntegerField(choices=MAPPING_TYPE_CHOICES, default=0)
    source_attribute = models.CharField(max_length=256)
    target_attribute = models.CharField(max_length=256)
    default_value = models.CharField(max_length=128, blank=True, null=True)
    constant_value = models.CharField(max_length=128, null=True, blank=True)
    is_used_matching = models.BooleanField(default=False)
    matching_precedence = models.IntegerField(blank=True, null=True, default=-1)
    apply_type = models.IntegerField(choices=APPLY_TYPE_CHOICES, default=0)


class AppProfile(BaseModel):

    ATTR_TYPE_CHOICES = (
        (0, 'Boolean'),
        (1, 'Datetime'),
        (2, 'Integer'),
        (3, 'String'),
        # (4, 'Binary'),
        # (5, 'Reference'),
    )

    provisioning_config = models.ForeignKey(Config, on_delete=models.CASCADE, related_name='app_profile')
    name = models.CharField(max_length=128)
    type = models.IntegerField(choices=ATTR_TYPE_CHOICES, default=0)
    is_primary = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    multi_value = models.BooleanField(default=False)
    exact_case = models.BooleanField(default=False)
    # api_expression = models.CharField(max_length=128)
    # referenced_object_attr = models.CharField(max_length=128)
