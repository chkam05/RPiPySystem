from __future__ import annotations

from flask import jsonify, request
from typing import ClassVar

from bluetooth_service.models.bt_connect_request import BtConnectRequest
from bluetooth_service.models.bt_connection_info import BtConnectionInfo
from bluetooth_service.models.bt_disconnect_response import BtDisconnectResponse
from bluetooth_service.models.bt_message import BtMessage
from bluetooth_service.models.bt_message_pair import BtMessagePair
from bluetooth_service.models.bt_received_count_response import BtReceivedCountResponse
from bluetooth_service.models.bt_send_message_request import BtSendMessageRequest
from bluetooth_service.utilities.bt_connection_manager import BtConnectionManager
from core.api.auto_swag import auto_swag, ok, pparam, request_body_json, response
from core.api.flask_api_service import FlaskApiService
from core.api.mid_auth_controller import MidAuthController
from core.authorization.models.auth_check_result import AuthCheckResult
from core.data.error_response import ErrorResponse


class ConnectionsController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'Connections'
    _CONTROLLER_PATH: ClassVar[str] = 'connections'

    def __init__(
            self,
            service: FlaskApiService,
            connection_manager: BtConnectionManager,
            auth_url: str,
            url_prefix_base: str
        ) -> None:
        if not connection_manager:
            raise ValueError('"connection_manager" component is required.')
        if not isinstance(auth_url, str) or not auth_url.strip():
            raise ValueError('"auth_url" argument is required.')
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('"url_prefix_base" argument is required.')

        self._connection_manager = connection_manager
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, auth_url, url_prefix)

    def register_routes(self) -> ConnectionsController:
        self.add_url_rule('/connect', view_func=self.connect, methods=['POST'])
        self.add_url_rule('/disconnect/<connection_id>', view_func=self.disconnect, methods=['POST'])
        self.add_url_rule('/<connection_id>', view_func=self.get_connection, methods=['GET'])
        self.add_url_rule('/list', view_func=self.list_connections, methods=['GET'])
        self.add_url_rule('/<connection_id>/send_and_receive_message', view_func=self.send_and_receive_message, methods=['POST'])
        self.add_url_rule('/<connection_id>/send_message', view_func=self.send_message, methods=['POST'])
        self.add_url_rule('/<connection_id>/receive_message', view_func=self.receive_message, methods=['POST'])
        self.add_url_rule('/<connection_id>/received_count', view_func=self.get_received_count, methods=['GET'])
        self.add_url_rule('/<connection_id>/received_list', view_func=self.get_received_list, methods=['POST'])
        return self

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    def _get_required_connection(self, connection_id: str):
        connection = self._connection_manager.get_connection(connection_id)
        if not connection:
            return None, (jsonify(ErrorResponse(
                message='Connection not found.',
                code=404,
                details=f'Bluetooth connection "{connection_id}" was not found.',
            ).to_public()), 404)

        return connection, None

    # --------------------------------------------------------------------------------
    # ENDPOINTS
    # --------------------------------------------------------------------------------

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Connect Bluetooth Device - Admin/Root Only',
        request_body=request_body_json(BtConnectRequest.schema_public(), {'address': '00:11:22:33:44:55', 'port': 1}),
        responses={
            200: ok(BtConnectionInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def connect(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        data = request.get_json(silent=True) or {}
        connect_request = BtConnectRequest.from_dict(data)
        connection = self._connection_manager.connect(
            connect_request.address,
            port=connect_request.port,
            connection_id=connect_request.connection_id,
            name=connect_request.name,
        )
        return jsonify(connection.to_info().to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Disconnect Bluetooth Device - Admin/Root Only',
        parameters=[pparam('connection_id', {'type': 'string', 'example': 'hc05'}, 'Connection ID.')],
        responses={
            200: ok(BtDisconnectResponse.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def disconnect(self, connection_id: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(BtDisconnectResponse(
            disconnected=self._connection_manager.disconnect(connection_id)
        ).to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Bluetooth Connection - Admin/Root Only',
        parameters=[pparam('connection_id', {'type': 'string', 'example': 'hc05'}, 'Connection ID.')],
        responses={
            200: ok(BtConnectionInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Connection not found.', ErrorResponse.schema_public('not_found', 404, 'Connection not found.')),
        },
    )
    def get_connection(self, connection_id: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        connection, error = self._get_required_connection(connection_id)
        if error:
            return error
        return jsonify(connection.to_info().to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='List Bluetooth Connections - Admin/Root Only',
        responses={
            200: ok(BtConnectionInfo.schema_public_list()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def list_connections(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(BtConnectionInfo.to_public_list(self._connection_manager.get_connection_list())), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Send And Receive Bluetooth Message - Admin/Root Only',
        parameters=[pparam('connection_id', {'type': 'string', 'example': 'hc05'}, 'Connection ID.')],
        request_body=request_body_json(
            BtSendMessageRequest.schema_public(),
            {'message': 'ping\\n', 'timeout': 5},
        ),
        responses={
            200: ok(BtMessagePair.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Connection not found.', ErrorResponse.schema_public('not_found', 404, 'Connection not found.')),
        },
    )
    def send_and_receive_message(self, connection_id: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        connection, error = self._get_required_connection(connection_id)
        if error:
            return error
        send_request = BtSendMessageRequest.from_dict(request.get_json(silent=True) or {})
        return jsonify(connection.send_and_receive(send_request.to_message(), send_request.timeout).to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Send Bluetooth Message - Admin/Root Only',
        parameters=[pparam('connection_id', {'type': 'string', 'example': 'hc05'}, 'Connection ID.')],
        request_body=request_body_json(
            BtSendMessageRequest.schema_public(),
            {'bytes': [112, 105, 110, 103, 10]},
        ),
        responses={
            200: ok(BtMessage.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Connection not found.', ErrorResponse.schema_public('not_found', 404, 'Connection not found.')),
        },
    )
    def send_message(self, connection_id: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        connection, error = self._get_required_connection(connection_id)
        if error:
            return error
        send_request = BtSendMessageRequest.from_dict(request.get_json(silent=True) or {})
        return jsonify(connection.send_message(send_request.to_message()).to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Receive Bluetooth Message - Admin/Root Only',
        parameters=[pparam('connection_id', {'type': 'string', 'example': 'hc05'}, 'Connection ID.')],
        responses={
            200: ok({**BtMessage.schema_public(), 'nullable': True}),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Connection not found.', ErrorResponse.schema_public('not_found', 404, 'Connection not found.')),
        },
    )
    def receive_message(self, connection_id: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        connection, error = self._get_required_connection(connection_id)
        if error:
            return error
        message = connection.receive_message()
        return jsonify(message.to_public() if message else None), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Received Bluetooth Message Count - Admin/Root Only',
        parameters=[pparam('connection_id', {'type': 'string', 'example': 'hc05'}, 'Connection ID.')],
        responses={
            200: ok(BtReceivedCountResponse.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Connection not found.', ErrorResponse.schema_public('not_found', 404, 'Connection not found.')),
        },
    )
    def get_received_count(self, connection_id: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        connection, error = self._get_required_connection(connection_id)
        if error:
            return error
        return jsonify(BtReceivedCountResponse(count=connection.get_received_count()).to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get And Clear Received Bluetooth Messages - Admin/Root Only',
        parameters=[pparam('connection_id', {'type': 'string', 'example': 'hc05'}, 'Connection ID.')],
        responses={
            200: ok(BtMessage.schema_public_list()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Connection not found.', ErrorResponse.schema_public('not_found', 404, 'Connection not found.')),
        },
    )
    def get_received_list(self, connection_id: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        connection, error = self._get_required_connection(connection_id)
        if error:
            return error
        return jsonify(BtMessage.to_public_list(connection.get_received_list())), 200
