from django.db import models
import jsonfield
from common.model import BaseModel
from provisioning.models import Config


class Schema(BaseModel):

    MAPPING_TYPE_CHOICES = (
        ('none', 'None'),
        ('direct', 'Direct'),
        ('constant', 'Constant'),
        # ('expression', 'Expression'),  # Expression to be supported in ArkID
    )

    APPLY_TYPE_CHOICES = (
        ('always', 'Always'),
        ('created', 'Only during creation'),
    )

    provisioning_config = models.ForeignKey(
        Config, on_delete=models.CASCADE, related_name='app_profile_mappings'
    )
    mapping_type = models.CharField(
        max_length=128,
        choices=MAPPING_TYPE_CHOICES,
        default='direct',
    )
    source_attribute = models.CharField(max_length=256)
    target_attribute = models.CharField(max_length=256)
    default_value = models.CharField(max_length=128, blank=True, null=True)
    constant_value = models.CharField(max_length=128, null=True, blank=True)
    is_used_matching = models.BooleanField(default=False)
    matching_precedence = models.IntegerField(blank=True, null=True, default=-1)
    apply_type = models.CharField(
        max_length=128, choices=APPLY_TYPE_CHOICES, default='always'
    )


class AppProfile(BaseModel):

    ATTR_TYPE_CHOICES = (
        ('boolean', 'Boolean'),
        ('datetime', 'Datetime'),
        ('integer', 'Integer'),
        ('string', 'String'),
        # ('binary', 'Binary'),
        # ('referenced', 'Reference'),
    )

    provisioning_config = models.ForeignKey(
        Config, on_delete=models.CASCADE, related_name='app_profile'
    )
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=128, choices=ATTR_TYPE_CHOICES, default='string')
    is_primary = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    multi_value = models.BooleanField(default=False)
    exact_case = models.BooleanField(default=False)
    # api_expression = models.CharField(max_length=128)
    # referenced_object_attr = models.CharField(max_length=128)
