from django import forms

from organization.models import Organization


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"
        exclude = ["secret_token", "keycloak_data"]
