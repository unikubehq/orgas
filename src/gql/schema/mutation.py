import graphene
from commons.keycloak.abstract_models import KeycloakResource
from commons.keycloak.users import UserHandler
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError

from gql.schema.query import OrganizationNode
from organization.forms import OrganizationForm
from organization.models import Organization, OrganizationMemberInvitation


class CreateUpdateOrganization(DjangoModelFormMutation):
    organization = graphene.Field(OrganizationNode)

    @classmethod
    def perform_mutate(cls, form, info):
        organization_id = str(form.cleaned_data.get("id"))
        if organization_id and info.context.permissions.has_permission(organization_id, "organization:edit"):
            result = super(CreateUpdateOrganization, cls).perform_mutate(form, info)
        elif organization_id:
            raise GraphQLError("This user does not have permission to edit this organization.")
        else:
            # this is a new organization
            result = super(CreateUpdateOrganization, cls).perform_mutate(form, info)
            # add this user as an administrator of this new orga
            uh = UserHandler()
            admin_group = form.instance.keycloak_data["groups"].get(KeycloakResource.ADMINS)
            uh.join_group(info.context.kcuser["uuid"], admin_group)
        return result

    class Meta:
        form_class = OrganizationForm
        convert_choices_to_enum = True


class OrganizationMemberRoleEnum(graphene.Enum):
    admin = "admin"
    member = "member"


class UpdateOrganizationMember(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()
        user = graphene.UUID()
        role = graphene.Argument(OrganizationMemberRoleEnum)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if info.context.permissions.has_permission(str(kwargs.get("id")), "organization:edit"):
            organization = Organization.objects.get(id=kwargs.get("id"))
            try:
                # first remove user from all groups
                UserHandler().leave_group(
                    str(kwargs.get("user")), organization.keycloak_data["groups"].get(KeycloakResource.ADMINS)
                )
                UserHandler().leave_group(
                    str(kwargs.get("user")), organization.keycloak_data["groups"].get(KeycloakResource.MEMBERS)
                )
                # then, add it to the corresponding group in keycloak
                if kwargs.get("role") == OrganizationMemberRoleEnum.admin:
                    UserHandler().join_group(
                        str(kwargs.get("user")), organization.keycloak_data["groups"].get(KeycloakResource.ADMINS)
                    )
                    return cls(ok=True)
                elif kwargs.get("role") == OrganizationMemberRoleEnum.member:
                    UserHandler().join_group(
                        str(kwargs.get("user")), organization.keycloak_data["groups"].get(KeycloakResource.MEMBERS)
                    )
                    return cls(ok=True)
                else:
                    return cls(ok=False)
            except Exception:
                raise GraphQLError("Could not add this user to organization.")
        else:
            raise GraphQLError("This user does not have permission to add a user to this organization.")


class DeleteOrganizationMember(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()
        user = graphene.UUID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if info.context.permissions.has_permission(str(kwargs.get("id")), "organization:members:delete"):
            organization = Organization.objects.get(id=kwargs.get("id"))
            try:
                UserHandler().leave_group(
                    str(kwargs.get("user")), organization.keycloak_data["groups"].get(KeycloakResource.ADMINS)
                )
                UserHandler().leave_group(
                    str(kwargs.get("user")), organization.keycloak_data["groups"].get(KeycloakResource.MEMBERS)
                )
                return cls(ok=True)
            except Exception:
                raise GraphQLError("Could not remove this user from organization.")
        else:
            raise GraphQLError("This user does not have permission to remove a user from this organization.")


class CreateOrganizationMemberInvitation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()
        email = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        organization_id = str(kwargs.get("id"))
        if info.context.permissions.has_permission(organization_id, "organization:members:add"):
            invitation_mail = kwargs.get("email").strip().lower()
            organization = Organization.objects.get(id=kwargs.get("id"))
            try:
                invitation, created = OrganizationMemberInvitation.objects.get_or_create(
                    organization=organization, email=invitation_mail
                )
                if not created:
                    if invitation.expired:
                        # this invitation was expired, set it active again
                        invitation.expired = False
                    if invitation.accepted is not None:
                        # todo handle cases correctly
                        # case 1: user is already part of the organization and gets invited again -> raise error
                        # case 2: user left organization in the past -> reset organization
                        invitation.accepted = None
                    invitation.save()
            except ValidationError as e:
                raise GraphQLError("ValidationError: " + e.message)
            except IntegrityError as e:
                raise GraphQLError("IntegrityError: " + e.message)
            return cls(ok=True)
        else:
            raise GraphQLError("This user does not have permission to invite a user to this organization.")


class RevokeOrganizationMemberInvitation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        invitation_id = str(kwargs.get("id"))
        try:
            invitation = OrganizationMemberInvitation.objects.get(accepted=None, expired=False, id=invitation_id)
        except OrganizationMemberInvitation.DoesNotExist:
            raise GraphQLError("This invitation does not exist.")
        if info.context.permissions.has_permission(str(invitation.organization.id), "organization:members:add"):
            invitation.expired = True
            invitation.save()
            return cls(ok=True)
        else:
            raise GraphQLError("This user does not have permission to invite a user to this organization.")


class UpdateOrganizationMemberInvitation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID()
        accepted = graphene.Boolean()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        invitation_id = str(kwargs.get("id"))
        try:
            invitation = OrganizationMemberInvitation.objects.get(accepted=None, expired=False, id=invitation_id)
        except OrganizationMemberInvitation.DoesNotExist:
            raise GraphQLError("This invitation does not exist.")

        # TODO what happens when user changes email
        if info.context.kcuser["email"] != invitation.email:
            raise GraphQLError("This invitation does not exist.")

        accepted = kwargs.get("accepted")
        invitation.accepted = accepted
        if accepted:
            # add user to member group the orga
            UserHandler().join_group(
                str(info.context.kcuser["uuid"]),
                invitation.organization.keycloak_data["groups"].get(KeycloakResource.MEMBERS),
            )
        invitation.save()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_update_organization = CreateUpdateOrganization.Field()
    create_invitation = CreateOrganizationMemberInvitation.Field()
    revoke_invitation = RevokeOrganizationMemberInvitation.Field()
    answer_invitation = UpdateOrganizationMemberInvitation.Field()
    update_organization_member = UpdateOrganizationMember.Field()
    remove_organization_member = DeleteOrganizationMember.Field()
