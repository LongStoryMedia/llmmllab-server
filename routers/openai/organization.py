from fastapi import APIRouter
from typing import Optional
from server.models.openai.admin_api_key import AdminApiKey
from server.models.openai.api_key_list import ApiKeyList
from server.models.openai.certificate import Certificate
from server.models.openai.create_group_body import CreateGroupBody
from server.models.openai.create_group_user_body import CreateGroupUserBody
from server.models.openai.delete_certificate_response import DeleteCertificateResponse
from server.models.openai.deleted_role_assignment_resource import DeletedRoleAssignmentResource
from server.models.openai.group_deleted_resource import GroupDeletedResource
from server.models.openai.group_list_resource import GroupListResource
from server.models.openai.group_resource_with_success import GroupResourceWithSuccess
from server.models.openai.group_response import GroupResponse
from server.models.openai.group_role_assignment import GroupRoleAssignment
from server.models.openai.group_user_assignment import GroupUserAssignment
from server.models.openai.group_user_deleted_resource import GroupUserDeletedResource
from server.models.openai.invite import Invite
from server.models.openai.invite_delete_response import InviteDeleteResponse
from server.models.openai.invite_list_response import InviteListResponse
from server.models.openai.invite_project_group_body import InviteProjectGroupBody
from server.models.openai.invite_request import InviteRequest
from server.models.openai.list_audit_logs_response import ListAuditLogsResponse
from server.models.openai.list_certificates_response import ListCertificatesResponse
from server.models.openai.modify_certificate_request import ModifyCertificateRequest
from server.models.openai.project import Project
from server.models.openai.project_api_key import ProjectApiKey
from server.models.openai.project_api_key_delete_response import ProjectApiKeyDeleteResponse
from server.models.openai.project_api_key_list_response import ProjectApiKeyListResponse
from server.models.openai.project_create_request import ProjectCreateRequest
from server.models.openai.project_group import ProjectGroup
from server.models.openai.project_group_deleted_resource import ProjectGroupDeletedResource
from server.models.openai.project_group_list_resource import ProjectGroupListResource
from server.models.openai.project_list_response import ProjectListResponse
from server.models.openai.project_rate_limit import ProjectRateLimit
from server.models.openai.project_rate_limit_list_response import ProjectRateLimitListResponse
from server.models.openai.project_rate_limit_update_request import (
    ProjectRateLimitUpdateRequest,
)
from server.models.openai.project_service_account import ProjectServiceAccount
from server.models.openai.project_service_account_create_request import (
    ProjectServiceAccountCreateRequest,
)
from server.models.openai.project_service_account_create_response import (
    ProjectServiceAccountCreateResponse,
)
from server.models.openai.project_service_account_delete_response import (
    ProjectServiceAccountDeleteResponse,
)
from server.models.openai.project_service_account_list_response import (
    ProjectServiceAccountListResponse,
)
from server.models.openai.project_update_request import ProjectUpdateRequest
from server.models.openai.project_user import ProjectUser
from server.models.openai.project_user_create_request import ProjectUserCreateRequest
from server.models.openai.project_user_delete_response import ProjectUserDeleteResponse
from server.models.openai.project_user_list_response import ProjectUserListResponse
from server.models.openai.project_user_update_request import ProjectUserUpdateRequest
from server.models.openai.public_assign_organization_group_role_body import (
    PublicAssignOrganizationGroupRoleBody,
)
from server.models.openai.public_create_organization_role_body import (
    PublicCreateOrganizationRoleBody,
)
from server.models.openai.public_role_list_resource import PublicRoleListResource
from server.models.openai.public_update_organization_role_body import (
    PublicUpdateOrganizationRoleBody,
)
from server.models.openai.role import Role
from server.models.openai.role_deleted_resource import RoleDeletedResource
from server.models.openai.role_list_resource import RoleListResource
from server.models.openai.toggle_certificates_request import ToggleCertificatesRequest
from server.models.openai.update_group_body import UpdateGroupBody
from server.models.openai.upload_certificate_request import UploadCertificateRequest
from server.models.openai.usage_response import UsageResponse
from server.models.openai.user import User
from server.models.openai.user_delete_response import UserDeleteResponse
from server.models.openai.user_list_resource import UserListResource
from server.models.openai.user_list_response import UserListResponse
from server.models.openai.user_role_assignment import UserRoleAssignment
from server.models.openai.user_role_update_request import UserRoleUpdateRequest


router = APIRouter(prefix="/organization", tags=["Organization"])


@router.get("/admin_api_keys")
async def admin_api_keys_list() -> ApiKeyList:
    """Operation ID: admin-api-keys-list"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/admin_api_keys")
async def admin_api_keys_create() -> AdminApiKey:
    """Operation ID: admin-api-keys-create"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/admin_api_keys/{key_id}")
async def admin_api_keys_delete(key_id: str) -> dict:
    """Operation ID: admin-api-keys-delete"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/admin_api_keys/{key_id}")
async def admin_api_keys_get(key_id: str) -> AdminApiKey:
    """Operation ID: admin-api-keys-get"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/audit_logs")
async def list_audit_logs() -> ListAuditLogsResponse:
    """Operation ID: list-audit-logs"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/certificates")
async def listOrganizationCertificates() -> ListCertificatesResponse:
    """Operation ID: listOrganizationCertificates"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/certificates")
async def uploadCertificate(body: UploadCertificateRequest) -> Certificate:
    """Operation ID: uploadCertificate"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/certificates/activate")
async def activateOrganizationCertificates(
    body: ToggleCertificatesRequest,
) -> ListCertificatesResponse:
    """Operation ID: activateOrganizationCertificates"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/certificates/deactivate")
async def deactivateOrganizationCertificates(
    body: ToggleCertificatesRequest,
) -> ListCertificatesResponse:
    """Operation ID: deactivateOrganizationCertificates"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/certificates/{certificate_id}")
async def deleteCertificate(certificate_id: str) -> DeleteCertificateResponse:
    """Operation ID: deleteCertificate"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/certificates/{certificate_id}")
async def getCertificate(certificate_id: str) -> Certificate:
    """Operation ID: getCertificate"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/certificates/{certificate_id}")
async def modifyCertificate(
    certificate_id: str, body: ModifyCertificateRequest
) -> Certificate:
    """Operation ID: modifyCertificate"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/costs")
async def usage_costs() -> UsageResponse:
    """Operation ID: usage-costs"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/groups")
async def list_groups() -> GroupListResource:
    """Operation ID: list-groups"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/groups")
async def create_group(body: CreateGroupBody) -> GroupResponse:
    """Operation ID: create-group"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/groups/{group_id}")
async def delete_group(group_id: str) -> GroupDeletedResource:
    """Operation ID: delete-group"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/groups/{group_id}")
async def update_group(
    group_id: str, body: UpdateGroupBody
) -> GroupResourceWithSuccess:
    """Operation ID: update-group"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/groups/{group_id}/roles")
async def list_group_role_assignments(group_id: str) -> RoleListResource:
    """Operation ID: list-group-role-assignments"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/groups/{group_id}/roles")
async def assign_group_role(
    group_id: str, body: PublicAssignOrganizationGroupRoleBody
) -> GroupRoleAssignment:
    """Operation ID: assign-group-role"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/groups/{group_id}/roles/{role_id}")
async def unassign_group_role(
    group_id: str, role_id: str
) -> DeletedRoleAssignmentResource:
    """Operation ID: unassign-group-role"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/groups/{group_id}/users")
async def list_group_users(group_id: str) -> UserListResource:
    """Operation ID: list-group-users"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/groups/{group_id}/users")
async def add_group_user(
    group_id: str, body: CreateGroupUserBody
) -> GroupUserAssignment:
    """Operation ID: add-group-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/groups/{group_id}/users/{user_id}")
async def remove_group_user(group_id: str, user_id: str) -> GroupUserDeletedResource:
    """Operation ID: remove-group-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/invites")
async def list_invites() -> InviteListResponse:
    """Operation ID: list-invites"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/invites")
async def inviteUser(body: InviteRequest) -> Invite:
    """Operation ID: inviteUser"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/invites/{invite_id}")
async def delete_invite(invite_id: str) -> InviteDeleteResponse:
    """Operation ID: delete-invite"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/invites/{invite_id}")
async def retrieve_invite(invite_id: str) -> Invite:
    """Operation ID: retrieve-invite"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects")
async def list_projects() -> ProjectListResponse:
    """Operation ID: list-projects"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects")
async def create_project(body: ProjectCreateRequest) -> Project:
    """Operation ID: create-project"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}")
async def retrieve_project(project_id: str) -> Project:
    """Operation ID: retrieve-project"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}")
async def modify_project(project_id: str, body: ProjectUpdateRequest) -> Project:
    """Operation ID: modify-project"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/api_keys")
async def list_project_api_keys(project_id: str) -> ProjectApiKeyListResponse:
    """Operation ID: list-project-api-keys"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/projects/{project_id}/api_keys/{key_id}")
async def delete_project_api_key(
    project_id: str, key_id: str
) -> ProjectApiKeyDeleteResponse:
    """Operation ID: delete-project-api-key"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/api_keys/{key_id}")
async def retrieve_project_api_key(project_id: str, key_id: str) -> ProjectApiKey:
    """Operation ID: retrieve-project-api-key"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}/archive")
async def archive_project(project_id: str) -> Project:
    """Operation ID: archive-project"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/certificates")
async def listProjectCertificates(project_id: str) -> ListCertificatesResponse:
    """Operation ID: listProjectCertificates"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}/certificates/activate")
async def activateProjectCertificates(
    project_id: str, body: ToggleCertificatesRequest
) -> ListCertificatesResponse:
    """Operation ID: activateProjectCertificates"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}/certificates/deactivate")
async def deactivateProjectCertificates(
    project_id: str, body: ToggleCertificatesRequest
) -> ListCertificatesResponse:
    """Operation ID: deactivateProjectCertificates"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/groups")
async def list_project_groups(project_id: str) -> ProjectGroupListResource:
    """Operation ID: list-project-groups"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}/groups")
async def add_project_group(
    project_id: str, body: InviteProjectGroupBody
) -> ProjectGroup:
    """Operation ID: add-project-group"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/projects/{project_id}/groups/{group_id}")
async def remove_project_group(
    project_id: str, group_id: str
) -> ProjectGroupDeletedResource:
    """Operation ID: remove-project-group"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/rate_limits")
async def list_project_rate_limits(project_id: str) -> ProjectRateLimitListResponse:
    """Operation ID: list-project-rate-limits"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}/rate_limits/{rate_limit_id}")
async def update_project_rate_limits(
    project_id: str, rate_limit_id: str, body: ProjectRateLimitUpdateRequest
) -> ProjectRateLimit:
    """Operation ID: update-project-rate-limits"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/service_accounts")
async def list_project_service_accounts(
    project_id: str,
) -> ProjectServiceAccountListResponse:
    """Operation ID: list-project-service-accounts"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}/service_accounts")
async def create_project_service_account(
    project_id: str, body: ProjectServiceAccountCreateRequest
) -> ProjectServiceAccountCreateResponse:
    """Operation ID: create-project-service-account"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/projects/{project_id}/service_accounts/{service_account_id}")
async def delete_project_service_account(
    project_id: str, service_account_id: str
) -> ProjectServiceAccountDeleteResponse:
    """Operation ID: delete-project-service-account"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/service_accounts/{service_account_id}")
async def retrieve_project_service_account(
    project_id: str, service_account_id: str
) -> ProjectServiceAccount:
    """Operation ID: retrieve-project-service-account"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/users")
async def list_project_users(project_id: str) -> ProjectUserListResponse:
    """Operation ID: list-project-users"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}/users")
async def create_project_user(
    project_id: str, body: ProjectUserCreateRequest
) -> ProjectUser:
    """Operation ID: create-project-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/projects/{project_id}/users/{user_id}")
async def delete_project_user(
    project_id: str, user_id: str
) -> ProjectUserDeleteResponse:
    """Operation ID: delete-project-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/projects/{project_id}/users/{user_id}")
async def retrieve_project_user(project_id: str, user_id: str) -> ProjectUser:
    """Operation ID: retrieve-project-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/projects/{project_id}/users/{user_id}")
async def modify_project_user(
    project_id: str, user_id: str, body: ProjectUserUpdateRequest
) -> ProjectUser:
    """Operation ID: modify-project-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/roles")
async def list_roles() -> PublicRoleListResource:
    """Operation ID: list-roles"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/roles")
async def create_role(body: PublicCreateOrganizationRoleBody) -> Role:
    """Operation ID: create-role"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/roles/{role_id}")
async def delete_role(role_id: str) -> RoleDeletedResource:
    """Operation ID: delete-role"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/roles/{role_id}")
async def update_role(role_id: str, body: PublicUpdateOrganizationRoleBody) -> Role:
    """Operation ID: update-role"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/usage/audio_speeches")
async def usage_audio_speeches() -> UsageResponse:
    """Operation ID: usage-audio-speeches"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/usage/audio_transcriptions")
async def usage_audio_transcriptions() -> UsageResponse:
    """Operation ID: usage-audio-transcriptions"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/usage/code_interpreter_sessions")
async def usage_code_interpreter_sessions() -> UsageResponse:
    """Operation ID: usage-code-interpreter-sessions"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/usage/completions")
async def usage_completions() -> UsageResponse:
    """Operation ID: usage-completions"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/usage/embeddings")
async def usage_embeddings() -> UsageResponse:
    """Operation ID: usage-embeddings"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/usage/images")
async def usage_images() -> UsageResponse:
    """Operation ID: usage-images"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/usage/moderations")
async def usage_moderations() -> UsageResponse:
    """Operation ID: usage-moderations"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/usage/vector_stores")
async def usage_vector_stores() -> UsageResponse:
    """Operation ID: usage-vector-stores"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/users")
async def list_users() -> UserListResponse:
    """Operation ID: list-users"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str) -> UserDeleteResponse:
    """Operation ID: delete-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/users/{user_id}")
async def retrieve_user(user_id: str) -> User:
    """Operation ID: retrieve-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/users/{user_id}")
async def modify_user(user_id: str, body: UserRoleUpdateRequest) -> User:
    """Operation ID: modify-user"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.get("/users/{user_id}/roles")
async def list_user_role_assignments(user_id: str) -> RoleListResource:
    """Operation ID: list-user-role-assignments"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.post("/users/{user_id}/roles")
async def assign_user_role(
    user_id: str, body: PublicAssignOrganizationGroupRoleBody
) -> UserRoleAssignment:
    """Operation ID: assign-user-role"""
    raise NotImplementedError("Endpoint not yet implemented")


@router.delete("/users/{user_id}/roles/{role_id}")
async def unassign_user_role(
    user_id: str, role_id: str
) -> DeletedRoleAssignmentResource:
    """Operation ID: unassign-user-role"""
    raise NotImplementedError("Endpoint not yet implemented")
