from typing import List

from commons.keycloak.resources import ResourceHandler


class OrganizationResourceHandler(ResourceHandler):
    """
    Organizations support the following scopes:
        organization:projects:view
        organization:projects:add
        organization:edit
        organization:member:add
        organization:member:delete
    """

    ADD = "add"
    DELETE = "delete"
    PROJECTS_VIEW = f"projects{ResourceHandler.SCOPE_SEP}{ResourceHandler.VIEW}"
    PROJECTS_ADD = f"projects{ResourceHandler.SCOPE_SEP}{ADD}"
    MEMBERS_ADD = f"members{ResourceHandler.SCOPE_SEP}{ADD}"
    MEMBERS_DELETE = f"members{ResourceHandler.SCOPE_SEP}{DELETE}"

    def get_available_scopes(self, content_type: str) -> List[str]:
        return [
            self._scope(content_type, self.PROJECTS_VIEW),
            self._scope(content_type, self.PROJECTS_ADD),
            self._scope(content_type, self.EDIT),
            self._scope(content_type, self.MEMBERS_ADD),
            self._scope(content_type, self.MEMBERS_DELETE),
        ]
