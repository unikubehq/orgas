import uuid

from django.db import models
from django_extensions.db.models import TimeStampedModel


class OrganizationMemberInvitation(TimeStampedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE)
    email = models.EmailField()

    # None = no decision taken, True = accepted, False = rejected
    accepted = models.NullBooleanField()
    expired = models.BooleanField(default=False)
    # expiry date is calculated by the cleanup task

    class Meta:
        unique_together = (
            "organization",
            "email",
        )
