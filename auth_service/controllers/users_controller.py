from typing import Any, ClassVar, Dict, Optional

from flask import jsonify, request

from auth_service.models.access_level import AccessLevel
from auth_service.models.user import User
from auth_service.storage.users_storage import UsersStorage
from auth_service.utils.auth_guard import AuthGuard
from utils.auto_swag import (
    auto_swag, bad_request, conflict, created, not_found, ok, 
    qparam, request_body_json, unauthorized
)
from utils.base_controller import BaseController
from utils.flask_api_service import FlaskApiService


class UsersController(BaseController):
    _CONTROLLER_NAME: ClassVar[str] = 'auth_users'
    _CONTROLLER_PATH: ClassVar[str] = 'users'

    def __init__(
            self,
            url_prefix_base: str,
            auth_guard: AuthGuard,
            users_storage: UsersStorage,
            *,
            service: Optional[FlaskApiService] = None) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        if not auth_guard:
            raise ValueError('auth_guard is required')
        if not users_storage:
            raise ValueError('users_storage is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        self.auth = auth_guard
        self.users_storage = users_storage
        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, service=service)
    
    def register_routes(self) -> 'UsersController':
        self.add_url_rule('/create', view_func=self.create_user, methods=['POST'])
        self.add_url_rule('/list', view_func=self.list_users, methods=['GET'])
        self.add_url_rule('/<id>', view_func=self.get_user, methods=['GET'])
        self.add_url_rule('/<id>', view_func=self.update_user, methods=['PATCH'])
        self.add_url_rule('/<id>', view_func=self.remove_user, methods=['DELETE'])
        return self
    
    # --- ENDPOINTS ---

    @auto_swag(
        tags=['user'],
        summary='Create User (Admin/Root)',
        description='Creates a new user account; Requires Admin or Root privileges.',
        request_body=request_body_json(User.schema_add_request()),
        responses={
            201: created(User.schema_public()),
            400: bad_request('Invalid payload'),
            401: unauthorized('Unauthorized'),
            403: bad_request('Forbidden'),
            409: conflict('User exists'),
        }
    )
    def create_user(self):
        # Require valid access token
        try:
            actor, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({'message': str(e)}), 401

        # Only Admins and Root users can add new users
        if not (self.auth.is_admin(actor) or self.auth.is_root(actor)):
            return jsonify({'message': 'forbidden'}), 403

        data = request.get_json(silent=True) or {}
        name = data.get(User.FIELD_NAME)
        password = data.get('password')
        level = data.get(User.FIELD_LEVEL) or AccessLevel.USER.value

        if not isinstance(name, str) or not name or not isinstance(password, str) or not password:
            return jsonify({'message': 'invalid payload'}), 400

        # Admin cannot create Root-level users
        # (only Root has permission to create another Root account)
        if self.auth.is_admin(actor) and level == AccessLevel.ROOT:
            return jsonify({'message': 'forbidden: admin cannot create Root'}), 403

        try:
            user = self.users_storage.add_user(name=name, raw_password=password, level=level)
        except ValueError as e:
            if str(e) == 'user_exists':
                return jsonify({'message': 'user exists'}), 409
            raise
        return jsonify(user.to_public()), 201
    
    @auto_swag(
        tags=['user'],
        summary='List Users (User/Admin/Root)',
        description='Returns a list of users; Available to all roles.',
        parameters=[qparam('name_filter', {'type': 'string'}, 'Optional name filter (contains)')],
        responses={
            200: ok({'type': 'array', 'items': User.schema_public()}),
            401: unauthorized('Unauthorized')
        }
    )
    def list_users(self):
        # Any authenticated user can view the list of users.
        # There are no restrictions, since "list" itself is non-destructive.
        try:
            _, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({'message': str(e)}), 401
        
        name_filter = request.args.get('name_filter', type=str)

        users = [u.to_public() for u in self.users_storage.list_users(name_filter)]
        return jsonify(users), 200
    
    @auto_swag(
        tags=['user'],
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
            401: unauthorized('Unauthorized'),
            404: not_found('User not found')
        }
    )
    def get_user(self, id: str):
        # Any authenticated user can fetch user info.
        # For now, there’s no privacy restriction — every user can view all accounts.
        try:
            _, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({'message': str(e)}), 401

        user = self.users_storage.get_user_by_id(id)
        if not user:
            return jsonify({'message': 'not found'}), 404
        return jsonify(user.to_public()), 200
    
    @auto_swag(
        tags=['user'],
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
            200: ok({'type': 'object', 'properties': {'removed': {'type': 'boolean', 'example': True}}}),
            401: unauthorized('Unauthorized'),
            403: bad_request('Forbidden'),
            404: not_found('User not found')
        }
    )
    def remove_user(self, id: str):
        # Require valid access token
        try:
            actor, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({'message': str(e)}), 401

        target = self.users_storage.get_user_by_id(id)
        if not target:
            return jsonify({'message': 'not found'}), 404

        # --- User rule ---
        # Regular user can only delete their own account (self-removal).
        if self.auth.is_user(actor) and actor.id != id:
            return jsonify({'message': 'forbidden: user can only remove self'}), 403

        # --- Admin rule ---
        # Admin can delete other users, but not Root accounts.
        if self.auth.is_admin(actor) and target.level == AccessLevel.ROOT:
            return jsonify({'message': 'forbidden: admin cannot remove Root'}), 403

        # --- Root rule ---
        # Root can delete any user (no restriction).
        if not self.users_storage.remove_user(id):
            return jsonify({'message': 'not found'}), 404
        return jsonify({'removed': True}), 200
    
    @auto_swag(
        tags=['user'],
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
            400: bad_request('Nothing to update'),
            401: unauthorized('Unauthorized'),
            403: bad_request('Forbidden'),
            404: not_found('User not found'),
            409: conflict('User exists')
        }
    )
    def update_user(self, id: str):
        # Require valid access token
        try:
            actor, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({'message': str(e)}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        name = data.get(User.FIELD_NAME)
        password = data.get('password')
        new_level = data.get(User.FIELD_LEVEL)

        if name is None and password is None and new_level is None:
            return jsonify({'message': 'nothing to update'}), 400

        target = self.users_storage.get_user_by_id(id)
        if not target:
            return jsonify({'message': 'not found'}), 404

        # --- User rule ---
        # Regular users can only update themselves and cannot change their access level.
        if self.auth.is_user(actor):
            if actor.id != id:
                return jsonify({'message': 'forbidden: user can only update self'}), 403
            new_level = None  # block privilege escalation

        # --- Admin rule ---
        # Admin can modify other users, but cannot:
        # - update Root accounts (to avoid privilege reduction of highest authority)
        # - set level=Root (to avoid unauthorized privilege escalation)
        elif self.auth.is_admin(actor):
            if target.level == AccessLevel.ROOT:
                return jsonify({'message': 'forbidden: cannot update Root user'}), 403
            if isinstance(new_level, str) and new_level == AccessLevel.ROOT.value:
                return jsonify({'message': 'forbidden: cannot assign Root level'}), 403

        # --- Root rule ---
        # Root can update any user freely (no restriction).
        try:
            updated = self.users_storage.update_user(
                id,
                name=name if isinstance(name, str) else None,
                raw_password=password if isinstance(password, str) else None,
                level=new_level if isinstance(new_level, str) else None
            )
        except ValueError as e:
            if str(e) == 'user_exists':
                return jsonify({'message': 'user exists'}), 409
            if str(e) == 'invalid_level':
                return jsonify({'message': 'invalid level'}), 400
            raise

        if not updated:
            return jsonify({'message': 'not found'}), 404
        return jsonify(updated.to_public()), 200