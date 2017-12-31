import telnetlib
import re
from errors import *
import Function


class HuaweiSwitch(object):
    def __init__(self, host=None, password=None, username=None, super_password=None):
        self.host = host
        self.username = username
        self.password = password
        self.super_password = super_password

        self.connected = False
        self._connection = None
        self.hostname = None

        if self.username == '':
            self.username = None

    def connect(self, host=None, port=23, timeout=2):
        if host is None:
            host = self.host

        self._connection = telnetlib.Telnet(host, port, timeout)
        self._authenticate()
        self._get_hostname()
        self._super()
        self.cmd("screen-length 0 temporary")

        self.connected = True

    def disconnect(self):
        if self._connection is not None:
            self._connection.write('quit' + '\n')
            self._connection.close()

        self._connection = None
        self.connected = False

    def _authenticate(self):
        idx, match, text = self.expect(['sername:', 'assword:'], 5)

        if match is None:
            raise AuthenticationError("Unable to get a username or password prompt when trying to authenticate.", text)
        elif match.group().count(b'assword:'):
            self.write(self.password + "\n")

            # Another password prompt means a bad password
            idx, match, text = self.expect(['assword', '>', '#'], 5)
            if match.group() is not None and match.group().count(b'assword'):
                raise AuthenticationError("Incorrect login password")
        elif match.group().count(b'sername') > 0:
            if self.username is None:
                raise AuthenticationError("A username is required but none is supplied.")
            else:
                self.write(self.username + "\n")
                idx, match, text = self.expect(['assword:'], 5)

                if match is None:
                    raise AuthenticationError("Unexpected text when trying to enter password", text)
                elif match.group().count(b'assword'):
                    self.write(self.password + "\n")

                # Check for an valid login
                idx, match, text = self.expect(['#', '>', "Login invalid", "Authentication failed"], 2)
                if match is None:
                    raise AuthenticationError("Unexpected text post-login", text)
                elif b"invalid" in match.group() or b"failed" in match.group():
                    raise AuthenticationError("Unable to login. Your username or password are incorrect.")
        else:
            raise AuthenticationError("Unable to get a login prompt")

    def _get_hostname(self):
        self.write("\n")

        idx, match, text = self.expect(['>'], 2)

        if match is not None:
            tmp = text.replace('<','').strip()
            self.hostname = tmp.replace('>', '').strip()

        else:
            raise HuaweiError("Unable to get device hostname")

    def _super(self, password=None):
        if password is not None:
            self.super_password = password
        self.write('\n')
        self.read_until_prompt()

        self.write("super"+'\n')

        idx, match, text = self.expect(['>', 'assword:'], 1)

        if match is None:
            raise HuaweiError("I tried to enable, but didn't get a command nor a password prompt")
        else:
            if 'privilege is 3' in text:
                return
            elif 'assword' in text:
                self.write(self.super_password + "\n")

        idx, match, text = self.expect([">", 'assword:'], 1)
        print match.group()
        if match is None:
            raise HuaweiError("Unexpected output when trying to enter super mode", text=None)
        elif match.group().count(b'assword') > 0:
            self.write("\n\n\n")
            raise HuaweiError("Incorrect super password")
        elif 'privilege is 3' in text:
            return

    def expect(self, asearch, timeout=2):

        idx, match, result = self._connection.expect([needle.encode('ascii') for needle in asearch], timeout)
        return idx, match, result

    def write(self, text):
        """ Do a raw write on the telnet connection. No newline implied. """

        if self._connection is None:
            self.connect()
            raise HuaweiError("Not connected")

        self._connection.write(text.encode('ascii'))

    def read_until_prompt(self, prompt=None, timeout=5):
        thost = self.hostname

        if thost is None:
            raise HuaweiError("The Hostname of the Device is None", text=None)

        if prompt is None:
            expect = [thost + ">"]
        else:
            expect = [thost + prompt]

        idx, match, ret_text = self.expect(expect, timeout)

        return ret_text

    def cmd(self, cmd_text):
        """ Send a command to the switch and return the resulting text. Given
            command should NOT have a newline in it."""

        self.write(cmd_text + "\n")
        text = self.read_until_prompt()

        # Get rid of the prompt (the last line)
        ret_text = ""
        for a in text.split('\n')[:-1]:
            ret_text += a + "\n"

        # If someone changed the hostname, we need to update that
        if 'hostname' in cmd_text:
            self._get_hostname()

        if "Error" in ret_text:
            raise InvalidCommand(cmd_text)

        return ret_text

    def get_arp_table(self):
        """
        Returns the ARP table from the device as a list of dicts.
        Only retreives IP and ARPA addresses at the moment.

        {ip,mac}
        """
        re_text = '(?P<ip>\d+\.\d+\.\d+\.\d+)\s+((?:\d|\w){4}\-(?:\d|\w){4}\-(?:\d|\w){4}|Incomplete)\s+.+\r?\n?'

        table = []
        result = self.cmd("display arp")
        items = re.findall(re_text, result)
        for item in items:
            table.append({
                "ip": item[0],
                "mac": item[1],
            })

        return table

    def get_mac_address_table(self):
        """
        Returns the Mac Address table  from the device as a list of dicts.
        Only retreives MAC and Interface at the moment.

        {device_name,mac,interface}
        """
        re_text = '((?:\d|\w){4}\-(?:\d|\w){4}\-(?:\d|\w){4})\s+(\d+/-)\s+(.+?)\s+(dynamic|sticky)\s+.+\r?\n?'
        table = []
        result = self.cmd("display mac-address")
        items  = re.findall(re_text,result)
        for item in items:
            table.append({
                "hostname":self.hostname,
                "mac": item[0],
                "vlan": item[1],
                "interface": Function.function.change_int_name(item[2]),
                "type": item[3],
            })


        return table
