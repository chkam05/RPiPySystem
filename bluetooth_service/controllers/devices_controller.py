from __future__ import annotations

from flask import jsonify, request
from typing import ClassVar

from bluetooth_service.models.bt_address_request import BtAddressRequest
from bluetooth_service.models.bt_device import BtDevice
from bluetooth_service.models.bt_pair_request import BtPairRequest
from bluetooth_service.models.bt_unpair_response import BtUnpairResponse
from bluetooth_service.utilities.bt_device_manager import BtDeviceManager
from core.api.auto_swag import auto_swag, ok, pparam, qparam, request_body_json, response
from core.api.flask_api_service import FlaskApiService
from core.api.mid_auth_controller import MidAuthController
from core.authorization.models.auth_check_result import AuthCheckResult
from core.data.error_response import ErrorResponse


class DevicesController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'Devices'
    _CONTROLLER_PATH: ClassVar[str] = 'devices'

    def __init__(
            self,
            service: FlaskApiService,
            device_manager: BtDeviceManager,
            auth_url: str,
            url_prefix_base: str
        ) -> None:
        if not device_manager:
            raise ValueError('"device_manager" component is required.')
        if not isinstance(auth_url, str) or not auth_url.strip():
            raise ValueError('"auth_url" argument is required.')
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('"url_prefix_base" argument is required.')

        self._device_manager = device_manager
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, auth_url, url_prefix)

    def register_routes(self) -> DevicesController:
        self.add_url_rule('/find_nearby', view_func=self.find_nearby, methods=['GET'])
        self.add_url_rule('/<address>', view_func=self.get_device_info, methods=['GET'])
        self.add_url_rule('/paired', view_func=self.get_paired_list, methods=['GET'])
        self.add_url_rule('/pair', view_func=self.pair, methods=['POST'])
        self.add_url_rule('/unpair', view_func=self.unpair, methods=['POST'])
        return self

    # --------------------------------------------------------------------------------
    # ENDPOINTS
    # --------------------------------------------------------------------------------

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Find Nearby Bluetooth Devices - Admin/Root Only',
        parameters=[qparam('timeout', {'type': 'integer', 'example': 8}, 'Scan timeout in seconds.')],
        responses={
            200: ok(BtDevice.schema_public_list()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def find_nearby(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        timeout = request.args.get('timeout', default=None, type=int)
        return jsonify(BtDevice.to_public_list(self._device_manager.find_nearby(timeout))), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Bluetooth Device Info - Admin/Root Only',
        parameters=[pparam('address', {'type': 'string', 'example': '00:11:22:33:44:55'}, 'Bluetooth MAC address.')],
        responses={
            200: ok(BtDevice.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Device not found.', ErrorResponse.schema_public('not_found', 404, 'Device not found.')),
        },
    )
    def get_device_info(self, address: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(self._device_manager.get_device_info(address).to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='List Paired Bluetooth Devices - Admin/Root Only',
        responses={
            200: ok(BtDevice.schema_public_list()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_paired_list(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(BtDevice.to_public_list(self._device_manager.get_paired_devices())), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Pair Bluetooth Device - Admin/Root Only',
        request_body=request_body_json(BtPairRequest.schema_public(), {'address': '00:11:22:33:44:55', 'passkey': '1234'}),
        responses={
            200: ok(BtDevice.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def pair(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        data = request.get_json(silent=True) or {}
        pair_request = BtPairRequest.from_dict(data)
        return jsonify(self._device_manager.pair_device(pair_request.address, pair_request.passkey).to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Unpair Bluetooth Device - Admin/Root Only',
        request_body=request_body_json(BtAddressRequest.schema_public(), {'address': '00:11:22:33:44:55'}),
        responses={
            200: ok(BtUnpairResponse.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def unpair(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        data = request.get_json(silent=True) or {}
        address_request = BtAddressRequest.from_dict(data)
        return jsonify(BtUnpairResponse(
            removed=self._device_manager.unpair_device(address_request.address)
        ).to_public()), 200
