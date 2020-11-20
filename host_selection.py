# encoding: utf-8

import sys

import vpn

from workflow import Workflow3


def main(wf):
    clear_cache = wf.getvar('clear_cache')

    if clear_cache:
        wf.clear_cache('vpn_hosts')
        wf.settings['chosen_host'] = None

    hosts = wf.cached_data('vpn_hosts', vpn.get_hosts, max_age=0)

    for host in hosts:
        it = wf.add_item(
            title='Host: %s' % host,
            arg=host,
            valid=True,
            icontype='fileicon',
            icon='/Applications/Cisco/Cisco AnyConnect Secure Mobility Client.app'
        )
        it.setvar('chosen_host', host)
        it.setvar('connection_type', 'reconnection')

    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
