from django.db.models.sql import datastructures
from django.core.exceptions import EmptyResultSet

# Waiting new release of drf-extension
# Ref: https://github.com/chibisov/drf-extensions/issues/294
datastructures.EmptyResultSet = EmptyResultSet

