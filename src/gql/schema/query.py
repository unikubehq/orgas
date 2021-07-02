import graphene
from commons.graphql.nodes import page_field_factory, resolve_page
from commons.keycloak.abstract_models import KeycloakResource
from commons.keycloak.groups import GroupHandler
from graphene import UUID, ObjectType
from graphene_django import DjangoObjectType
from graphene_federation import extend, external, key
from graphql import GraphQLError

from organization.models import Organization, OrganizationMemberInvitation


@extend(fields="id")
class UserNode(ObjectType):
    id = external(UUID(required=True))


class OrganizationMember(ObjectType):
    user = graphene.Field(UserNode)
    role = graphene.String()


@key("id")
class OrganizationNode(DjangoObjectType):
    avatar_image = graphene.String()
    members = graphene.List(OrganizationMember)

    class Meta:
        model = Organization
        fields = ("id", "title", "description", "created")

    def resolve_avatar_image(self, info):
        if self.avatar_image:
            return self.avatar_image.url
        else:
            return None

    def resolve_members(self, info, **kwargs):
        if info.context.permissions.has_permission(str(self.id)):
            member_list = []
            gh = GroupHandler()
            admin_group = self.keycloak_data["groups"].get(KeycloakResource.ADMINS)
            member_group = self.keycloak_data["groups"].get(KeycloakResource.MEMBERS)
            admins = gh.members(admin_group)
            for a in admins:
                member_list.append(OrganizationMember(user=UserNode(id=a["id"]), role="admin"))
            members = gh.members(member_group)
            for m in members:
                member_list.append(OrganizationMember(user=UserNode(id=m["id"]), role="member"))
            return member_list
        else:
            return None

    def __resolve_reference(self, info, **kwargs):
        if info.context.permissions.has_permission(str(self.id)):
            return Organization.objects.get(id=self.id)
        # this user has no access to this orga, title is public field
        orga = Organization.objects.get(id=self.id)
        return Organization(title=orga.title)


class OrganizationInvitationNode(DjangoObjectType):
    class Meta:
        model = OrganizationMemberInvitation
        fields = ("id", "organization", "email")


class Query(graphene.ObjectType):

    all_organizations = page_field_factory(OrganizationNode)
    organization = graphene.Field(OrganizationNode, id=graphene.UUID(required=True))
    user_invitations = page_field_factory(OrganizationInvitationNode)
    all_organization_invitations = page_field_factory(OrganizationInvitationNode, id=graphene.UUID(required=True))

    @resolve_page
    def resolve_all_organizations(self, info):
        allowed_organizations = info.context.permissions.get_resource_id_by_scope("organization:*")
        return Organization.objects.filter(id__in=allowed_organizations)

    def resolve_organization(self, info, id):
        allowed_organizations = info.context.permissions.get_resource_id_by_scope("organization:*")
        # TODO better error handling
        return Organization.objects.filter(id__in=allowed_organizations).get(id=id)

    @resolve_page
    def resolve_user_invitations(self, info):
        return OrganizationMemberInvitation.objects.filter(
            email=info.context.kcuser["email"], expired=False, accepted=None
        )

    @resolve_page
    def resolve_all_organization_invitations(self, info, id):
        allowed_organizations = info.context.permissions.get_resource_id_by_scope("organization:members:*")
        if str(id) in allowed_organizations:
            # return undecided and still valid invitations
            return OrganizationMemberInvitation.objects.filter(organization__id=id, expired=False, accepted=None)
        else:
            raise GraphQLError("This user does not have permission to list all organization member invitations.")
