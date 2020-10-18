# encoding: utf-8
import os
import sys
from workflow import Workflow3

import vpn
import constants

log = None


def main(wf):
    vpn_state = vpn.get_state()
    vpn_state_notice = vpn.get_notice()

    for action in constants.ACTIONS:
        it = wf.add_item(
            title='%s' % action['title'],
            subtitle='State: %s, Notice: %s' % (vpn_state, vpn_state_notice),
            autocomplete=True,
            arg='vpnh' if wf.getvar('connection_type') else '',
            valid=True,
            icon='icon.icns'
        )
        it.setvar('connection_type', action['arg'])

    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    log.debug("settings: %s" % wf.settings)
    log.debug("args: %s" % wf.args)
    log.debug("args len: %s" % len(wf.args))
    if len(wf.args) > 0 and wf.args[0] != u'':
        query = wf.args[0]
        log.debug("query: %s" % query)
        wf.settings["chosen_host"] = query
    else:
        query = None

    vpn_host = wf.settings.get('chosen_host')
    log.debug("vpn_host: %s " %vpn_host)
    if not vpn_host:
        it = wf.add_item(title='Select a host', valid=True)
        it.setvar('set_host', 'true')
        wf.send_feedback()
        sys.exit()

    connection_type = os.getenv('connection_type')
    log.debug(connection_type)
    log.debug(vpn_host)
    if (connection_type and vpn_host) or connection_type == 'disconnection':
        func = None
        for action in constants.ACTIONS:
            if connection_type == action['arg']:
                func = action['func']
                func(vpn_host)
                break
    else:
        sys.exit(wf.run(main))
