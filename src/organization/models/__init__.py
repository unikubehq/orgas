# imports can't be relative (e.g. ``from .users [...]``), as ``manage.py test`` won't work with those...
from organization.models.invitation import *
from organization.models.organization import *