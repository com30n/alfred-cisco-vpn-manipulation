# encoding: utf-8
import os
import sys
from workflow import Workflow3

import vpn
import constants

log = None


def get_vpn_host(wf):
    log.debug("Getting VPN host...")

    # Do not rewrite settings with empty string
    # by default wf.args consist non empty list: wf.args[u'']
    if len(wf.args) > 0 and wf.args[0] != u'':
        host = wf.args[0]
        log.debug("Update VPN host in settings: %s" % host)
        # If main.py script was called after host_selection.py,
        # that means it have to update settings with the new host
        wf.settings["chosen_host"] = host

    vpn_host = wf.settings.get("chosen_host")
    log.debug("VPN Host: %s" % vpn_host)
    return vpn_host


def select_vpn_host(wf):
    it = wf.add_item(title="Select VPN host", valid=True)
    it.setvar("set_host", "true")
    wf.send_feedback()
    return


def manage_connection(connection_type, vpn_host):
    for action in constants.ACTIONS:
        if connection_type == action["arg"]:
            func = action["func"]
            func(vpn_host)
            return


def get_connection_info():
    return {'state': vpn.get_state(), 'notice': vpn.get_notice()}


def generate_connection_options(wf, connection_info):
    for action in constants.ACTIONS:
        it = wf.add_item(
            title="%s" % action["title"],
            subtitle="State: %s, Notice: %s" % (connection_info['state'], connection_info['notice']),
            autocomplete=True,
            valid=True,
            icon="icon.icns"
        )
        it.setvar("connection_type", action["arg"])
    return wf


def main(wf):
    vpn_host = get_vpn_host(wf)

    # If vpn_host is empty in the settings, the workflow should show
    # the VPN hosts to select the connection.
    if not vpn_host:
        return select_vpn_host(wf)

    # If main.py is running as a connection manager (after a choice of the connection type)
    # just run one of functions: connect, disconnect or reconnect
    connection_type = os.getenv("connection_type")
    if (connection_type and vpn_host) or connection_type == "disconnection":
        return manage_connection(connection_type, vpn_host)

    # If main.py is running as a main menu, it will show you every
    # connection options with some additional info

    # Gather additional info
    connection_info = get_connection_info()

    # Add every items with all connection options
    wf = generate_connection_options(wf, connection_info)

    # Show main menu with all connection options
    wf.send_feedback()
    return


if __name__ == u"__main__":
    wf = Workflow3(update_settings={
        # Your username and the workflow's repo's name.
        "github_slug": "com30n/alfred-cisco-vpn-manipulation",

        # Optional number of days between checks for updates.
        "frequency": 1,
    })
    log = wf.logger

    if wf.update_available:
        # Download new version and tell Alfred to install it
        log.info("Workflow update available. Updating...")
        wf.start_update()

    sys.exit(wf.run(main))
