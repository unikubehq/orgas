import uuid
from typing import Optional

from commons.keycloak.abstract_models import KeycloakResource
from django.db import models
from django_extensions.db.models import TimeStampedModel, TitleSlugDescriptionModel

from organization.resource_handler import OrganizationResourceHandler
from organization.utils import random_token


def get_default_avatar_image():
    return None


class Organization(TitleSlugDescriptionModel, TimeStampedModel, KeycloakResource):
    resource_handler = OrganizationResourceHandler

    secret_token = models.CharField(max_length=300, blank=True)

    on_trial = models.BooleanField()

    avatar_image = models.FileField(blank=True, null=True, default=get_default_avatar_image)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.secret_token:
            self.secret_token = random_token()
        super(Organization, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Organization, self).delete(*args, **kwargs)

    def get_keycloak_name(self) -> Optional[str]:
        return self.slug

    def create_keycloak_groups(self, associate_perms=False):
        super(Organization, self).create_keycloak_groups(associate_perms=False)
        # add admin permissions to admin group
        self.associate_permission(
            f"Edit {self._meta.model_name} {self.get_keycloak_name()}",
            scopes=[
                self.resource_handler.EDIT,
                self.resource_handler.PROJECTS_VIEW,
                self.resource_handler.PROJECTS_ADD,
                self.resource_handler.MEMBERS_ADD,
                self.resource_handler.MEMBERS_DELETE,
            ],
            group_ids=[self.get_group_id(self.ADMINS)],
        )
        # add member permission to member group
        self.associate_permission(
            f"View {self._meta.model_name} {self.get_keycloak_name()}",
            scopes=[self.resource_handler.PROJECTS_VIEW, self.resource_handler.PROJECTS_ADD],
            group_ids=[self.get_group_id(self.MEMBERS)],
        )
