import re

from collections import OrderedDict

RE_VPN_STATE = re.compile(r'\s+>> state: (?P<state>[a-zA-Z]+)')
RE_VPN_STATE_NOTICE = re.compile(r'\s+>> notice: (?P<notice>[\w -.]+)')
RE_VPN_HOST = re.compile(r'\s+> (?P<host>[a-z0-9-.]+).*')

VPN_STATS = OrderedDict([
    ('Duration', re.compile('\s+Duration:\s+(?P<connction_duration>[0-9:]+)')),
    ('Session Disconnect', re.compile('\s+Session Disconnect:\s+(?P<session_disconnect>[\w ]+)')),
    ('Client Address', re.compile('\s+Client Address \(IPv4\):\s+(?P<client_ip>[0-9.]+)')),
    ('Bytes Sent', re.compile('\s+Bytes Sent:\s+(?P<bytes_sent>[\d]+)')),
    ('Bytes Received', re.compile('\s+Bytes Received:\s+(?P<bytes_recv>[\d]+)')),
    ('Packets Sent', re.compile('\s+Packets Sent:\s+(?P<packets_sent>[\d]+)')),
    ('Packets Received', re.compile('\s+Packets Received:\s+(?P<packets_recv>[\d]+)')),
])
