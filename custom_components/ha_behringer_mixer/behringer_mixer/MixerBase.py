import re
import asyncio
import logging
import threading
import time
from .errors import MixerError
from typing import Optional, Union
from .utils import fader_to_db, db_to_fader
from .mixer_osc import OSCClientServer
from pythonosc.dispatcher import Dispatcher


class MixerBase:
    """Handles the communication with the mixer via the OSC protocol"""

    logger = logging.getLogger("behringermixer.behringermixer")

    _CONNECT_TIMEOUT = 0.5

    _info_response = []
    port_number: int = 10023
    delay: float = 0.02
    addresses_to_load = []
    cmd_scene_load = ""
    tasks = set()

    def __init__(self, **kwargs):
        self.ip = kwargs.get("ip")
        self.port = kwargs.get("port") or self.port_number
        self._delay = kwargs.get("delay") or self.delay
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(kwargs.get("logLevel") or logging.WARNING)
        if not self.ip:
            raise MixerError("No valid ip detected")

        self._callback_function = None
        self.subscription = None
        self._state = {}
        self._rewrites = {}
        self._rewrites_reverse = {}
        self.server = None

    async def validate_connection(self):
        """Validate connection to the mixer"""
        await self.send("/xinfo")
        await asyncio.sleep(self._CONNECT_TIMEOUT)
        if not self.info_response:
            raise MixerError(
                "Failed to setup OSC connection to mixer. Please check for correct ip address."
            )
        print(
            f"Successfully connected to {self.info_response[2]} at {self.info_response[0]}."
        )

    @property
    def info_response(self):
        """Return any OSC responses"""
        return self._info_response

    async def connectserver(self):
        """Connect to the server"""
        await self.startup()
        # asyncio.run(self.startup())

    async def startup(self):
        """Startup the server"""
        if not self.server:
            dispatcher = Dispatcher()
            dispatcher.set_default_handler(self.msg_handler)
            self.server = OSCClientServer(
                (self.ip, self.port), dispatcher, asyncio.get_event_loop()
            )
            transport, protocol = await self.server.create_serve_endpoint()
            self.server.register_transport(transport, protocol)
            await self.validate_connection()

    def msg_handler(self, addr, *data):
        """Handle callback response"""
        self.logger.debug(f"received: {addr} {data if data else ''}")
        handling_subscriptions = bool(self._callback_function)
        updates = self._update_state(addr, data, handling_subscriptions)
        if handling_subscriptions:
            for row in updates:
                self._callback_function(row)
        else:
            self._info_response = data[:]

    async def send(self, addr: str, param: Optional[str] = None):
        """Send an OSC message"""
        self.logger.debug(f"sending: {addr} {param if param is not None else ''}")
        self.server.send_message(addr, param)
        self._info_response = None
        await asyncio.sleep(self._delay)

    async def query(self, address):
        """Send an receive the value of an OSC message"""
        await self.send(address)
        return self.info_response

    async def subscribe(self, callback_function):
        await self._subscribe_worker("/xremote", callback_function)

    # async def _subscribe(self, parameter_string, callback_function):
    #    self._subscribe_worker(parameter_string, callback_function)
    #    return True

    async def _subscribe_worker(self, parameter_string, callback_function):
        self._callback_function = callback_function
        await self.send(parameter_string)
        renew_string = "/renew"
        if parameter_string == "/xremote":
            renew_string = "/xremote"
        while self._callback_function:
            await asyncio.sleep(9)
            await self.send(renew_string)
        return True

    async def unsubscribe(self):
        await self.send("/unsubscribe")
        self._callback_function = None
        return True

    async def disconnect(self):
        await self.server.shutdown()
        return True

    def state(self, key=None):
        """Return current mixer state"""
        if key:
            return self._state.get(key)
        return self._state

    async def load_scene(self, scene_number):
        """Return current mixer state"""
        await self.send(self.cmd_scene_load, scene_number)

    async def reload(self):
        """Reload state"""
        self._state = {}
        await self._load_initial()

    async def _load_initial(self):
        """Load initial state"""
        expanded_addresses = []
        for address_row in self.addresses_to_load:
            address = address_row[0]
            rewrite_address = address_row[1] if len(address_row) > 1 else None
            matches = re.search(r"\{(.*?)(:(\d)){0,1}\}", address)
            if matches:
                match_var = matches.group(1)
                max_count = getattr(self, match_var)
                zfill_num = int(matches.group(3) or 0) or len(str(max_count))
                for number in range(1, max_count + 1):
                    new_address = address.replace(
                        "{" + match_var + "}", str(number).zfill(zfill_num)
                    )
                    expanded_addresses.append(new_address)
                    if rewrite_address:
                        new_rewrite_address = rewrite_address.replace(
                            "{" + match_var + "}", str(number).zfill(zfill_num)
                        )
                        self._rewrites[new_address] = new_rewrite_address
            else:
                expanded_addresses.append(address)
                if rewrite_address:
                    self._rewrites[address] = rewrite_address
        for address in expanded_addresses:
            await self.send(address)

    def _update_state(self, address, values, updates_only=False):
        # update internal state representation
        # State looks like
        #    /ch/2/mix_fader = Value
        #    /ch/2/config_name = Value
        rewrite_key = self._rewrites.get(address)
        if rewrite_key:
            address = rewrite_key
        state_key = self._generate_state_key(address)
        value = values[0]
        updates = []
        if state_key:
            if state_key.endswith("_on"):
                value = bool(value)
            state_key = re.sub(r"/0+(\d+)/", r"/\1/", state_key)
            if updates_only and state_key not in self._state:
                # we are processing updates and data captured is not in initial state
                # Therefore we want to ignore data
                return updates
            self._state[state_key] = value
            updates.append({"property": state_key, "value": value})
            if state_key.endswith("_fader"):
                db_val = fader_to_db(value)
                self._state[state_key + "_db"] = db_val
                updates.append({"property": state_key + "_db", "value": db_val})
        return updates

    @staticmethod
    def _generate_state_key(address):
        # generate a key for use by state from the address
        prefixes = [
            r"^/ch/\d+/",
            r"^/bus/\d+/",
            r"^/dca/\d+/",
            r"^/mtx/\d+/",
            r"^/main/[a-z]+/",
        ]
        for prefix in prefixes:
            match = re.match(prefix, address)
            if match:
                key_prefix = address[: match.span()[1]]
                key_string = address[match.span()[1] :]
                key_string = key_string.replace("/", "_")
                return key_prefix + key_string
        return address

    def _build_reverse_rewrite(self):
        # Invert the mapping for self._rewrites
        if not self._rewrites_reverse:
            self._rewrites_reverse = {v: k for k, v in self._rewrites.items()}

    async def set_value(self, address, value):
        """Set the value in the mixer"""
        if address.endswith("_db"):
            address = address.replace("_db", "")
            value = db_to_fader(value)
        if value is False:
            value = 0
        if value is True:
            value = 1
        address = address.replace("_", "/")
        address = self._redo_padding(address)
        self._build_reverse_rewrite()
        rewrite_key = self._rewrites_reverse.get(address)
        if rewrite_key:
            address = rewrite_key
        await self.send(address, value)
        await self.query(address)
        # self._update_state(address, [value])

    def _redo_padding(self, address):
        # Go through address and see if it matches with one of the known address
        # if so, make sure the numbers are padded correctly

        for address_row in self.addresses_to_load:
            initial_address = address_row[0]
            matches = re.search(r"^(.*)/{(num_[a-z]+?)(:(\d)){0,1}}", initial_address)
            if matches:
                init_string = matches.group(1)
                if address.startswith(init_string):
                    max_count = getattr(self, matches.group(2))
                    zfill_num = int(matches.group(4) or 0) or len(str(max_count))
                    sub_match = re.search(r"^" + init_string + r"/(\d+)/", address)
                    num = sub_match.group(1)
                    address = address.replace(
                        f"{init_string}/{num}/",
                        f"{init_string}/" + str(num).zfill(zfill_num) + "/",
                    )
        return address
