from __future__ import annotations
from flask import jsonify, request
from typing import Any, ClassVar, Dict

from core.api.auth_guard_controller import AuthGuardController
from core.api.auto_swag import auto_swag, bad_request, conflict, created, not_found, ok, qparam, request_body_json, unauthorized
from core.api.flask_api_service import FlaskApiService
from core.authorization.auth_guard import AuthGuard
from core.authorization.enums.access_level import AccessLevel
from core.authorization.models.user import User
from core.authorization.storage.user_storage import UserStorage
from core.data.error_response import ErrorResponse
from core.data.removed_response import RemovedResponse


class UsersController(AuthGuardController):
    _CONTROLLER_NAME: ClassVar[str] = 'users'
    _CONTROLLER_PATH: ClassVar[str] = 'users'
    _LIST_USERS_F_NAME: ClassVar[str] = 'name_filter'
    _LIST_USERS_F_LEVEL: ClassVar[str] = 'level_filter'

    def __init__(
            self,
            service: FlaskApiService,
            auth_guard: AuthGuard,
            url_prefix_base: str) -> None:
        
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        super().__init__(
            service,
            auth_guard,
            self._CONTROLLER_NAME,
            __name__,
            url_prefix)
    
    def register_routes(self) -> UsersController:
        self.add_url_rule('/create', view_func=self.create_user, methods=['POST'])
        self.add_url_rule('/list', view_func=self.list_users, methods=['GET'])
        self.add_url_rule('/<id>', view_func=self.get_user, methods=['GET'])
        self.add_url_rule('/<id>', view_func=self.update_user, methods=['PATCH'])
        self.add_url_rule('/<id>', view_func=self.remove_user, methods=['DELETE'])
        return self
    
    # --------------------------------------------------------------------------------
    # PROPERTIES (shortcuts)
    # --------------------------------------------------------------------------------
    
    @property
    def _user_storage(self) -> UserStorage:
        """Return the AuthGuard component."""
        return self._auth_guard.user_storage

    # --------------------------------------------------------------------------------
    # ENDPOINTS
    # --------------------------------------------------------------------------------

    @auto_swag(
        tags=['users'],
        summary='Create User (Admin/Root)',
        description='Creates a new user account; Requires Admin or Root privileges.',
        request_body=request_body_json(User.schema_add_request()),
        responses={
            201: created(User.schema_public()),
            400: bad_request(ErrorResponse.schema_public('invalid payload', 400, 'Invalid username or password.')),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            403: bad_request(ErrorResponse.schema_public('forbidden', 403, 'Forbidden.')),
            409: conflict(ErrorResponse.schema_public('user exists', 409, 'User exists.')),
        }
    )
    def create_user(self):
        # Require valid access token
        try:
            actor, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

        # Only Admins and Root users can add new users
        if not (self.auth.is_admin(actor) or self.auth.is_root(actor)):
            return jsonify(ErrorResponse('forbidden', 403, details='You do not have permission to perform this action.')), 403

        data = request.get_json(silent=True) or {}
        username = data.get(User.FIELD_NAME)
        password = data.get('password')
        level = data.get(User.FIELD_LEVEL) or AccessLevel.USER.value

        if not isinstance(username, str) or not username:
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing username.')), 400

        if not isinstance(password, str) or not password:
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing password.')), 400

        # Admin cannot create Root-level users
        # (only Root has permission to create another Root account)
        if self.auth.is_admin(actor) and level == AccessLevel.ROOT:
            return jsonify(ErrorResponse('forbidden', 403, details='You do not have permission to perform this action (Admin cannot create Root).')), 403

        try:
            user = self._user_storage.add_user(name=username, raw_password=password, level=level)
        except ValueError as e:
            if str(e) == 'user_exists':
                return jsonify(ErrorResponse('user exists', 409, details=f'User with name {username} already exists.')), 409
            raise
        return jsonify(user.to_public()), 201
    
    @auto_swag(
        tags=['users'],
        summary='List Users (User/Admin/Root)',
        description='Returns a list of users; Available to all roles.',
        parameters=[
            qparam(_LIST_USERS_F_NAME, {'type': 'string'}, 'Optional name filter (contains)'),
            qparam(_LIST_USERS_F_LEVEL, {'type': 'string'}, 'Optional level filter (equal)')
        ],
        responses={
            200: ok({'type': 'array', 'items': User.schema_public()}),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.'))
        }
    )
    def list_users(self):
        # Any authenticated user can view the list of users.
        # There are no restrictions, since "list" itself is non-destructive.
        try:
            _, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401
        
        f_name = request.args.get(self._LIST_USERS_F_NAME, type=str)
        f_level = request.args.get(self._LIST_USERS_F_LEVEL, type=str)

        users = [u.to_public() for u in 
                 self._user_storage.list_users(f_name, f_level)]
        return jsonify(users), 200
    
    @auto_swag(
        tags=['users'],
        summary='Get User by ID (User/Admin/Root)',
        description='Returns user details by ID; Available to all roles.',
        parameters=[{
            "in": "path",
            "name": "id",
            "schema": {"type": "string", "example": "uuid"},
            "required": True,
            "description": "User ID"
        }],
        responses={
            200: ok(User.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: not_found(ErrorResponse.schema_public('not found', 404, 'User not exists.'))
        }
    )
    def get_user(self, id: str):
        # Any authenticated user can fetch user info.
        # For now, there’s no privacy restriction — every user can view all accounts.
        try:
            _, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

        user = self._user_storage.get_user_by_id(id)
        if not user:
            return jsonify(ErrorResponse('not found', 404, f'User with id "{id}" not found.')), 404
        return jsonify(user.to_public()), 200
    
    @auto_swag(
        tags=['users'],
        summary='Remove User (User: itself; Admin: not Root; Root: any)',
        description='Removes a User; Users may delete only themselves, Admins cannot delete Root, and Root may delete any user.',
        parameters=[{
            "in": "path",
            "name": "id",
            "schema": {"type": "string", "example": "uuid"},
            "required": True,
            "description": "User ID"
        }],
        responses={
            200: ok(RemovedResponse.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            403: bad_request(ErrorResponse.schema_public('forbidden', 403, 'Forbidden.')),
            404: not_found(ErrorResponse.schema_public('not found', 404, 'User not exists.'))
        }
    )
    def remove_user(self, id: str):
        # Require valid access token
        try:
            actor, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

        target = self._user_storage.get_user_by_id(id)
        if not target:
            return jsonify(ErrorResponse('not found', 404, f'User with id "{id}" not found.')), 404

        # --- User rule ---
        # Regular user can only delete their own account (self-removal).
        if self.auth.is_user(actor) and actor.id != id:
            return jsonify(ErrorResponse('forbidden', 403, details='You do not have permission to perform this action (User can only remove self).')), 403

        # --- Admin rule ---
        # Admin can delete other users, but not Root accounts.
        if self.auth.is_admin(actor) and target.level == AccessLevel.ROOT:
            return jsonify(ErrorResponse('forbidden', 403, details='You do not have permission to perform this action (Admin can not remove Root).')), 403

        # --- Root rule ---
        # Root can delete any user (no restriction).
        if not self._user_storage.remove_user(id):
            return jsonify(ErrorResponse('not found', 404, f'User with id "{id}" not found.')), 404
        return jsonify(RemovedResponse(True)), 200
    
    @auto_swag(
        tags=['users'],
        summary='Update user (User: itself; Admin: not Root; Root: any)',
        description='Updates a User; Users may update only themselves and cannot change level, Admins may update non-Root users without setting level=Root, and Root may update any user.',
        parameters=[{
            "in": "path",
            "name": "id",
            "schema": {"type": "string", "example": "uuid"},
            "required": True,
            "description": "User ID"
        }],
        request_body=request_body_json(User.schema_update_request(), required=False),
        responses={
            200: ok(User.schema_public()),
            400: bad_request(ErrorResponse.schema_public('nothing to update', 400, 'Nothing to update.')),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            403: bad_request(ErrorResponse.schema_public('forbidden', 403, 'Forbidden.')),
            404: not_found(ErrorResponse.schema_public('not found', 404, 'User not exists.')),
            409: conflict(ErrorResponse.schema_public('user exists', 409, 'User exists.'))
        }
    )
    def update_user(self, id: str):
        # Require valid access token
        try:
            actor, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        username = data.get(User.FIELD_NAME)
        password = data.get('password')
        new_level = data.get(User.FIELD_LEVEL)

        if username is None and password is None and new_level is None:
            return jsonify(ErrorResponse('nothing to update', 400, details='Nothing to update.')), 400

        target = self._user_storage.get_user_by_id(id)
        if not target:
            return jsonify(ErrorResponse('not found', 404, f'User with id "{id}" not found.')), 404

        # --- User rule ---
        # Regular users can only update themselves and cannot change their access level.
        if self.auth.is_user(actor):
            if actor.id != id:
                return jsonify(ErrorResponse('forbidden', 403, details='You do not have permission to perform this action (User can only update self).')), 403
            new_level = None  # block privilege escalation

        # --- Admin rule ---
        # Admin can modify other users, but cannot:
        # - update Root accounts (to avoid privilege reduction of highest authority)
        # - set level=Root (to avoid unauthorized privilege escalation)
        elif self.auth.is_admin(actor):
            if target.level == AccessLevel.ROOT:
                return jsonify(ErrorResponse('forbidden', 403, details='You do not have permission to perform this action (Admin cannot update Root user).')), 403
            if isinstance(new_level, str) and new_level == AccessLevel.ROOT.value:
                return jsonify(ErrorResponse('forbidden', 403, details='You do not have permission to perform this action (Admin cannot assign Root level).')), 403

        # --- Root rule ---
        # Root can update any user freely (no restriction).
        try:
            updated = self._user_storage.update_user(
                id,
                name=username if isinstance(username, str) else None,
                raw_password=password if isinstance(password, str) else None,
                level=new_level if isinstance(new_level, str) else None
            )
        except ValueError as e:
            if str(e) == 'user_exists':
                return jsonify(ErrorResponse('user exists', 409, details=f'User with name {username} already exists.')), 409
            if str(e) == 'invalid_level':
                return jsonify(ErrorResponse('invalid payload', 400, details='Invalid "level".')), 400
            raise

        if not updated:
            return jsonify(ErrorResponse('nothing to update', 404, details='The data has not been updated.')), 404
        return jsonify(updated.to_public()), 200
