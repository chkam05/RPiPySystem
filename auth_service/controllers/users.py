from typing import Any, Dict, Optional
from flask import request, jsonify
from utils.auto_swag import (
    auto_swag, ok, created, bad_request, conflict, not_found,
    request_body_json, qparam, unauthorized
)
from utils.base_controller import BaseController

from auth_service.models.user import User
from auth_service.storage.users_storage import UsersStorage
from auth_service.utils.auth_guard import AuthGuard


class UsersController(BaseController):
    def __init__(self, *, url_prefix: str = '/api/auth/user', users: Optional[UsersStorage] = None) -> None:
        self.storage = users or UsersStorage()
        self.auth = AuthGuard(self.storage)
        super().__init__('auth_users', __name__, url_prefix=url_prefix)
    
    @auto_swag(
        tags=['user'],
        summary='Add user (Admin/Root)',
        request_body=request_body_json(User.schema_add_request()),
        responses={
            201: created(User.schema_public()),
            400: bad_request('Invalid payload'),
            401: unauthorized('Unauthorized'),
            403: bad_request('Forbidden'),
            409: conflict('User exists'),
        }
    )
    def add_user(self):
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
        level = data.get(User.FIELD_LEVEL) or User.LEVEL_USER

        if not isinstance(name, str) or not name or not isinstance(password, str) or not password:
            return jsonify({'message': 'invalid payload'}), 400

        # Admin cannot create Root-level users
        # (only Root has permission to create another Root account)
        if self.auth.is_admin(actor) and level == User.LEVEL_ROOT:
            return jsonify({'message': 'forbidden: admin cannot create Root'}), 403

        try:
            user = self.storage.add_user(name=name, raw_password=password, level=level)
        except ValueError as e:
            if str(e) == 'user_exists':
                return jsonify({'message': 'user exists'}), 409
            raise
        return jsonify(user.to_public()), 201

    @auto_swag(
        tags=['user'],
        summary='List users (User/Admin/Root)',
        parameters=[qparam('q', {'type': 'string'}, 'Optional name filter (contains)')],
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

        users = [u.to_public() for u in self.storage.list_users()]
        return jsonify(users), 200

    @auto_swag(
        tags=['user'],
        summary='Get user by id (User/Admin/Root)',
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

        user = self.storage.get_user_by_id(id)
        if not user:
            return jsonify({'message': 'not found'}), 404
        return jsonify(user.to_public()), 200

    @auto_swag(
        tags=['user'],
        summary='Remove user (User: only self; Admin: not Root; Root: any)',
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

        target = self.storage.get_user_by_id(id)
        if not target:
            return jsonify({'message': 'not found'}), 404

        # --- User rule ---
        # Regular user can only delete their own account (self-removal).
        if self.auth.is_user(actor) and actor.id != id:
            return jsonify({'message': 'forbidden: user can only remove self'}), 403

        # --- Admin rule ---
        # Admin can delete other users, but not Root accounts.
        if self.auth.is_admin(actor) and target.level == User.LEVEL_ROOT:
            return jsonify({'message': 'forbidden: admin cannot remove Root'}), 403

        # --- Root rule ---
        # Root can delete any user (no restriction).
        if not self.storage.remove_user(id):
            return jsonify({'message': 'not found'}), 404
        return jsonify({'removed': True}), 200

    @auto_swag(
        tags=['user'],
        summary='Update user (User: self & cannot change level; Admin: non-Root target, no level=Root; Root: any)',
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

        target = self.storage.get_user_by_id(id)
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
            if target.level == User.LEVEL_ROOT:
                return jsonify({'message': 'forbidden: cannot update Root user'}), 403
            if isinstance(new_level, str) and new_level == User.LEVEL_ROOT:
                return jsonify({'message': 'forbidden: cannot assign Root level'}), 403

        # --- Root rule ---
        # Root can update any user freely (no restriction).
        try:
            updated = self.storage.update_user(
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

    # region --- Endpoint registration ---

    def register_routes(self) -> 'UsersController':
        self.add_url_rule('/add', view_func=self.add_user, methods=['POST'])
        self.add_url_rule('/list', view_func=self.list_users, methods=['GET'])
        self.add_url_rule('/<id>', view_func=self.get_user, methods=['GET'])
        self.add_url_rule('/<id>', view_func=self.update_user, methods=['PATCH'])
        self.add_url_rule('/<id>', view_func=self.remove_user, methods=['DELETE'])
        return self

    # endregion --- Endpoint registration ---
