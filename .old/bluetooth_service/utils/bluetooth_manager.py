from datetime import datetime
from typing import Dict, List, Optional, Tuple
import bluetooth  # PyBluez
import pexpect
import sys
import time

sys.path.append('/usr/lib/python3/dist-packages')
from pydbus import SystemBus

from bluetooth_service.exceptions.bluetooth_authentication_error import BluetoothAuthenticationError
from bluetooth_service.exceptions.bluetooth_error import BluetoothError
from bluetooth_service.models.bluetooth_connection import BluetoothConnection
from bluetooth_service.models.bluetooth_connection_info import BluetoothConnectionInfo
from bluetooth_service.models.bluetooth_device_info import BluetoothDeviceInfo


class BluetoothManager:
    """High-level manager for Bluetooth operations using BlueZ D-Bus."""

    def __init__(self, scan_timeout: int = 5, adapter_name: str = "hci0") -> None:
        self.scan_timeout = scan_timeout
        self.adapter_name = adapter_name

        # Hint for name -> MAC (but still verified in BlueZ).
        self._devices_cache: Dict[str, str] = {}

        # Active RFCOMM calls (this is the only state maintained between calls).
        self._connections: Dict[str, BluetoothConnection] = {}
    
    # --------------------------------------------------------------------------
    # --- INTERNAL: D-BUS / BLUEZ HELPERS (stateless) ---
    # --------------------------------------------------------------------------

    def _get_bus(self) -> SystemBus:
        """
        Returns a fresh SystemBus on each call.
        """
        return SystemBus()
    
    def _get_bluez_root(self):
        bus = self._get_bus()
        return bus, bus.get("org.bluez", "/")
    
    @property
    def _adapter_path(self) -> str:
        return f"/org/bluez/{self.adapter_name}"

    def _get_adapter(self):
        """
        Gets the adapter from a new SystemBus each time.
        """
        bus = self._get_bus()
        try:
            adapter = bus.get("org.bluez", self._adapter_path)
        except Exception as e:
            raise BluetoothError(
                f"Bluetooth adapter {self.adapter_name} not found on D-Bus: {e}"
            ) from e
        return adapter
    
    def _get_managed_objects(self) -> Dict[str, dict]:
        """
        Fresh snapshot of all BlueZ objects.
        """
        bus, bluez = self._get_bluez_root()
        return bluez.GetManagedObjects()
    
    # --------------------------------------------------------------------------
    # --- DEVICE PATH RESOLUTION ---
    # --------------------------------------------------------------------------

    def _find_device_entries(self) -> Dict[str, Tuple[str, dict]]:
        """
        Returns an address -> (path, props) map for all Device1.
        """
        objs = self._get_managed_objects()
        result: Dict[str, Tuple[str, dict]] = {}

        for path, ifaces in objs.items():
            dev_props = ifaces.get("org.bluez.Device1")
            if not dev_props:
                continue
            # Only devices under our adapter.
            if not path.startswith(self._adapter_path + "/dev_"):
                continue

            addr = dev_props.get("Address")
            if not addr:
                continue

            result[addr.upper()] = (path, dev_props)

        return result

    def _resolve_device_to_addr(self, device: str) -> str:
        """
        Accepts:
            - MAC (with ':') -> returns MAC (uppercase).
            - name/alias -> converts to MAC based on the current BlueZ state.
        If necessary, performs a quick scan().
        """
        device = device.strip()
        if ":" in device:
            return device.upper()

        # Try with cache (hint).
        cached = self._devices_cache.get(device)
        if cached:
            return cached

        # Try BlueZ's current properties.
        addr = self._resolve_name_in_bluez(device)
        if addr:
            return addr

        # If not found – scan, update status, try again.
        self.scan()
        addr = self._resolve_name_in_bluez(device)
        if addr:
            return addr

        raise BluetoothError(f"Unknown device: {device}")

    def _resolve_name_in_bluez(self, device_name: str) -> Optional[str]:
        """
        Search by Name/Alias ​​(case-insensitive) in current Device1.
        """
        entries = self._find_device_entries()
        device_name_lower = device_name.lower()

        # Exact match Name.
        for addr, (_path, props) in entries.items():
            name = props.get("Name")
            if name and name.lower() == device_name_lower:
                self._devices_cache[name] = addr
                return addr

        # Alias.
        for addr, (_path, props) in entries.items():
            alias = props.get("Alias")
            if alias and alias.lower() == device_name_lower:
                self._devices_cache[alias] = addr
                return addr

        return None

    def _get_device_path_and_props(self, addr: str) -> Tuple[str, dict]:
        """
        Find the path and properties for a device with a given MAC based on the current BlueZ snapshot.
        """
        addr = addr.upper()
        entries = self._find_device_entries()
        if addr not in entries:
            raise BluetoothError(
                f"Device {addr} not present in BlueZ managed objects (not visible)"
            )
        return entries[addr]

    def _get_device_proxy(self, addr: str):
        """
        Returns a proxy to Device1 based on addr, always on a fresh SystemBus.
        Does not maintain this proxy between calls.
        """
        path, _props = self._get_device_path_and_props(addr)
        bus = self._get_bus()
        try:
            return bus.get("org.bluez", path)
        except Exception as e:
            raise BluetoothError(f"Device {addr} not found on D-Bus (path={path}): {e}") from e
    
    # --------------------------------------------------------------------------
    # --- ADAPTER MANAGEMENT ---
    # --------------------------------------------------------------------------

    def is_enabled(self) -> bool:
        """
        Return True if Bluetooth adapter is powered on.
        """
        try:
            adapter = self._get_adapter()
            props = adapter.GetAll("org.bluez.Adapter1")
        except Exception:
            return False

        return bool(props.get("Powered", False))

    def enable_bt(self) -> None:
        """
        Enable Bluetooth adapter.
        """
        adapter = self._get_adapter()
        try:
            adapter.Set("org.bluez.Adapter1", "Powered", True)
        except Exception as e:
            raise BluetoothError(f"Failed to enable Bluetooth adapter: {e}") from e

    def disable_bt(self) -> None:
        """
        Disable Bluetooth adapter.
        """
        adapter = self._get_adapter()
        try:
            adapter.Set("org.bluez.Adapter1", "Powered", False)
        except Exception as e:
            raise BluetoothError(f"Failed to disable Bluetooth adapter: {e}") from e
    
    # --------------------------------------------------------------------------
    # --- SCAN & GET_DEVICE_INFO ---
    # --------------------------------------------------------------------------

    def scan(self, scan_timeout: Optional[int] = None) -> List[BluetoothDeviceInfo]:
        """
        Scan for nearby Bluetooth devices (stateless).
        """
        if not scan_timeout:
            scan_timeout = self.scan_timeout

        adapter = self._get_adapter()

        try:
            adapter.StartDiscovery()
        except Exception as e:
            raise BluetoothError(f"Failed to start discovery: {e}") from e

        time.sleep(scan_timeout)

        try:
            adapter.StopDiscovery()
        except Exception:
            pass

        entries = self._find_device_entries()
        devices: List[BluetoothDeviceInfo] = []
        self._devices_cache.clear()
        now = datetime.now()

        for addr, (_path, props) in entries.items():
            name = props.get("Name")
            alias = props.get("Alias")
            paired = props.get("Paired", False)
            connected = props.get("Connected", False)
            trusted = props.get("Trusted", False)
            blocked = props.get("Blocked", False)
            rssi = props.get("RSSI")
            uuids = list(props.get("UUIDs", []))

            manufacturer_id: Optional[int] = None
            manufacturer_spec_data: List[int] = []
            manuf = props.get("ManufacturerData") or {}
            if manuf:
                manufacturer_id, manufacturer_spec_data = next(iter(manuf.items()))

            info = BluetoothDeviceInfo(
                address=addr,
                name=name,
                alias=alias,
                paired=paired,
                trusted=trusted,
                connected=connected,
                blocked=blocked,
                rssi=rssi,
                manufacturer_id=manufacturer_id,
                manufacturer_spec_data=manufacturer_spec_data,
                uuids=uuids,
                last_seen=now,
            )
            devices.append(info)

            if name:
                self._devices_cache[name] = addr
            if alias:
                self._devices_cache[alias] = addr

        return devices

    def get_device_info(self, device: str) -> BluetoothDeviceInfo:
        """
        Get detailed info about device (name or address), na bazie aktualnego stanu BlueZ.
        """
        addr = self._resolve_device_to_addr(device)
        _path, props = self._get_device_path_and_props(addr)

        manufacturer_id: Optional[int] = None
        manufacturer_spec_data: List[int] = []
        manuf = props.get("ManufacturerData") or {}
        if manuf:
            manufacturer_id, manufacturer_spec_data = next(iter(manuf.items()))

        return BluetoothDeviceInfo(
            address=props.get("Address", addr),
            name=props.get("Name"),
            alias=props.get("Alias"),
            paired=props.get("Paired", False),
            trusted=props.get("Trusted", False),
            blocked=props.get("Blocked", False),
            connected=props.get("Connected", False),
            rssi=props.get("RSSI"),
            manufacturer_id=manufacturer_id,
            manufacturer_spec_data=manufacturer_spec_data,
            uuids=list(props.get("UUIDs", [])),
            last_seen=datetime.now(),
        )
    
    # --------------------------------------------------------------------------
    # --- PAIR / UNPAIR / CONNECTED STATE ---
    # --------------------------------------------------------------------------

    _BLUETOOTHCTL_PROMPT = r'\[bluetooth[^\]]*\]>'

    def _pair_with_pin_via_bluetoothctl(self, addr: str, pin: str, timeout: int = 30) -> None:
        """
        Pair with device using bluetoothctl in an interactive session, automatically providing PIN when requested.
        Designed for HC-06 / HC-05 style modules.
        """
        child = pexpect.spawn("bluetoothctl", encoding="utf-8", timeout=timeout)

        try:
            # Main prompt.
            child.expect(self._BLUETOOTHCTL_PROMPT)

            # Make sure there is an agent.
            child.sendline("agent KeyboardOnly")
            # These commands can return different messages, so there is no expectation for a specific one.
            child.expect(self._BLUETOOTHCTL_PROMPT)

            child.sendline("default-agent")
            child.expect(self._BLUETOOTHCTL_PROMPT)

            # Start pairing.
            child.sendline(f"pair {addr}")

            # Waiting for one of several events:
            idx = child.expect([
                r"Enter PIN code:",              # 0 – PIN.
                r"Failed to pair",               # 1 – Fail.
                r"Authentication Failed",        # 2 – Fail.
                r"Pairing successful",           # 3 – Success.
                r"AlreadyExists",                # 4 – Already paired.
                pexpect.EOF,                     # 5
                pexpect.TIMEOUT,                 # 6
            ])

            if idx == 0:
                # There is a request for a PIN.
                child.sendline(pin)
                # After entering the PIN, wait for the result.
                idx2 = child.expect([
                    r"Pairing successful",
                    r"Failed to pair",
                    r"Authentication Failed",
                    r"AlreadyExists",
                    pexpect.EOF,
                    pexpect.TIMEOUT,
                ])
                if idx2 == 0 or idx2 == 3:
                    return
                elif idx2 in (1, 2):
                    raise BluetoothAuthenticationError(
                        f"Pairing failed with {addr}: authentication failed (PIN={pin})"
                    )
                else:
                    raise BluetoothError(
                        f"Pairing with {addr} did not complete (EOF/TIMEOUT after PIN)."
                    )

            elif idx == 3 or idx == 4:
                # Pairing successful / AlreadyExists.
                return

            elif idx in (1, 2):
                raise BluetoothAuthenticationError(
                    f"Pairing failed with {addr}: authentication failed (no PIN accepted)."
                )

            else:
                raise BluetoothError(
                    f"Pairing with {addr} did not complete (EOF/TIMEOUT)."
                )

        finally:
            # Always try to clear the session.
            try:
                child.sendline("quit")
            except Exception:
                pass
            child.close()

    def is_paired(self, device: str) -> bool:
        """
        Return True if device (name or address) is paired (na bazie Device1.Paired).
        """
        info = self.get_device_info(device)
        return bool(info.paired)

    def is_connected(self, device: str) -> bool:
        """
        Return True if device (name or address) is connected (Device1.Connected).
        """
        info = self.get_device_info(device)
        return bool(info.connected)

    def pair(self, device: str, pin: Optional[str] = None, trust: bool = True) -> None:
        """
        Pair with device (name or address) via BlueZ Device1.Pair().
        Requires a running BlueZ system agent if device requires PIN/confirm.
        """
        addr = self._resolve_device_to_addr(device)

        if pin:
            # Path for devices with PIN
            self._pair_with_pin_via_bluetoothctl(addr, pin=pin)
        else:
            # Pure D-Bus Pair() path for JustWorks devices / with system agent
            # Make sure BlueZ sees the device; if not, do a quick scan.
            try:
                self._get_device_path_and_props(addr)
            except BluetoothError:
                self.scan()
                self._get_device_path_and_props(addr)

            dev = self._get_device_proxy(addr)

            try:
                dev.Pair()
            except Exception as e:
                msg = str(e)
                if "org.bluez.Error.AuthenticationFailed" in msg:
                    raise BluetoothAuthenticationError(
                        f"Pairing failed with {addr}: authentication failed ({e})"
                    ) from e
                raise BluetoothError(f"Pairing failed with {addr}: {e}") from e

        # After successful pairing, an attempt to mark the device as trusted.
        if trust:
            try:
                if hasattr(dev, "Trust"):
                    dev.Trust()
                else:
                    dev.Set("org.bluez.Device1", "Trusted", True)
            except Exception:
                # Trust is not critical to operation.
                pass

    def unpair(self, device: str) -> None:
        """
        Unpair device (name or address) via Adapter1.RemoveDevice().
        """
        addr = self._resolve_device_to_addr(device)
        path, _props = self._get_device_path_and_props(addr)
        adapter = self._get_adapter()

        try:
            adapter.RemoveDevice(path)
        except Exception as e:
            raise BluetoothError(f"Failed to unpair device {addr}: {e}") from e
    
    # --------------------------------------------------------------------------
    # --- CONNECT / DISCONNECT / CONNECTIONS ---
    # --------------------------------------------------------------------------

    def connect(self, device: str) -> BluetoothConnection:
        """
        Connect to device (name or address) and return BluetoothConnection.
        """
        addr = self._resolve_device_to_addr(device)

        # Link-level connect via BlueZ.
        try:
            dev = self._get_device_proxy(addr)
            try:
                dev.Connect()
            except Exception as e:
                msg = str(e)
                # SPP modules often give: org.bluez.Error.NotAvailable: br-connection-profile-unavailable
                if "org.bluez.Error.NotAvailable" in msg or "br-connection-profile-unavailable" in msg:
                    # For pure RFCOMM devices this process can be safely ignored.
                    pass
                else:
                    raise BluetoothError(f"Failed to connect to {addr} via BlueZ: {e}") from e
        except BluetoothError:
            # If BlueZ link connect failed entirely, it *might* be able to do RFCOMM.
            pass

        # Find RFCOMM via PyBluez.
        name = bluetooth.lookup_name(addr, timeout=self.scan_timeout)
        rfcomm_port: Optional[int] = None

        for _ in range(3):
            services = bluetooth.find_service(address=addr)
            for svc in services:
                if svc.get("protocol") == "RFCOMM":
                    rfcomm_port = svc.get("port")
                    break
            if rfcomm_port is not None:
                break
            time.sleep(1)

        if rfcomm_port is None:
            raise BluetoothError(f"No RFCOMM service found on device {addr}.")

        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        try:
            sock.connect((addr, rfcomm_port))
        except OSError as e:
            raise BluetoothError(f"RFCOMM connect to {addr}:{rfcomm_port} failed: {e}") from e

        connection_id = name or addr
        conn = BluetoothConnection(
            address=addr,
            port=rfcomm_port,
            sock=sock,
            name=name,
            connection_id=connection_id,
        )

        self._connections[addr] = conn
        return conn

    def disconnect(self, device: str) -> None:
        """
        Disconnect device (name or address).
        """
        addr = self._resolve_device_to_addr(device)

        # Local RFCOMM
        conn = self._connections.get(addr)
        if conn:
            conn.disconnect()
            del self._connections[addr]

        # Link-level disconnect (ignore error if already disconnected).
        try:
            dev = self._get_device_proxy(addr)
            dev.Disconnect()
        except Exception:
            pass

    def active_connections(self) -> List[BluetoothConnectionInfo]:
        """
        Return list of active connections info.
        """
        infos: List[BluetoothConnectionInfo] = []
        for conn in self._connections.values():
            infos.append(conn.info)
        return infos

    def disconnect_all(self) -> None:
        """
        Disconnect all active connections.
        """
        addrs = list(self._connections.keys())
        for addr in addrs:
            conn = self._connections.get(addr)
            if conn:
                conn.disconnect()
        self._connections.clear()