from flask import request, jsonify
from utils.auto_swag import auto_swag, ok, created, bad_request, conflict, not_found, request_body_json, qparam
from utils.base_controller import BaseController
from auth_service.models.user import User
from auth_service.storage.users_storage import UsersStorage


class UserController(BaseController):
    def __init__(self, *, url_prefix: str = '/api/auth/user', storage: UsersStorage | None = None) -> None:
        self.storage = storage or UsersStorage()
        super().__init__('auth_users', __name__, url_prefix=url_prefix)
    
    @auto_swag(
        tags=['user'],
        summary='Add user',
        request_body=request_body_json(User.schema_add_request()),
        responses={201: created(User.schema_public()), 400: bad_request('Invalid payload'), 409: conflict('User exists')}
    )
    def add_user(self):
        data = request.get_json(silent=True) or {}
        name = data.get(User.FIELD_NAME)
        password = data.get('password')
        if not isinstance(name, str) or not name or not isinstance(password, str) or not password:
            return jsonify({'message': 'invalid payload'}), 400
        try:
            user = self.storage.add(name=name, raw_password=password)
        except ValueError as e:
            if str(e) == 'user_exists':
                return jsonify({'message': 'user exists'}), 409
            raise
        return jsonify(user.to_public()), 201

    @auto_swag(
        tags=['user'],
        summary='List users',
        parameters=[qparam('q', {'type': 'string'}, 'Optional name filter (contains)')],
        responses={200: ok({'type': 'array', 'items': User.schema_public()})}
    )
    def list_users(self):
        q = request.args.get('q', type=str)
        users = [u.to_public() for u in self.storage.list_users()]
        if q:
            users = [u for u in users if q.lower() in u[User.FIELD_NAME].lower()]
        return jsonify(users), 200

    @auto_swag(
        tags=['user'],
        summary='Get user by id',
        responses={200: ok(User.schema_public()), 404: not_found('User not found')}
    )
    def get_user(self, id: str):
        user = self.storage.get_by_id(id)
        if not user:
            return jsonify({'message': 'not found'}), 404
        return jsonify(user.to_public()), 200

    @auto_swag(
        tags=['user'],
        summary='Remove user',
        responses={200: ok({'type': 'object', 'properties': {'removed': {'type': 'boolean', 'example': True}}}),
                   404: not_found('User not found')}
    )
    def remove_user(self, id: str):
        if not self.storage.remove(id):
            return jsonify({'message': 'not found'}), 404
        return jsonify({'removed': True}), 200

    @auto_swag(
        tags=['user'],
        summary='Update user',
        request_body=request_body_json(User.schema_update_request(), required=False),
        responses={200: ok(User.schema_public()), 400: bad_request('Nothing to update'),
                   404: not_found('User not found'), 409: conflict('User exists')}
    )
    def update_user(self, id: str):
        data = request.get_json(silent=True) or {}
        name = data.get(User.FIELD_NAME)
        password = data.get('password')
        if name is None and password is None:
            return jsonify({'message': 'nothing to update'}), 400
        try:
            updated = self.storage.update(id, name=name if isinstance(name, str) else None,
                                               raw_password=password if isinstance(password, str) else None)
        except ValueError as e:
            if str(e) == 'user_exists':
                return jsonify({'message': 'user exists'}), 409
            raise
        if not updated:
            return jsonify({'message': 'not found'}), 404
        return jsonify(updated.to_public()), 200

    def register_routes(self) -> 'UsersController':
        self.add_url_rule('/add', view_func=self.add_user, methods=['POST'])
        self.add_url_rule('/list', view_func=self.list_users, methods=['GET'])
        self.add_url_rule('/<id>', view_func=self.get_user, methods=['GET'])
        self.add_url_rule('/remove/<id>', view_func=self.remove_user, methods=['DELETE'])
        self.add_url_rule('/update/<id>', view_func=self.update_user, methods=['PATCH'])
        return self