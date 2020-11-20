import vpn

ACTIONS = [
    {'arg': 'connection', 'title': 'Connect', 'func': vpn.connect},
    {'arg': 'disconnection', 'title': 'Disconnect', 'func': vpn.disconnect},
    {'arg': 'reconnection', 'title': 'Reconnect', 'func': vpn.reconnect},
]
