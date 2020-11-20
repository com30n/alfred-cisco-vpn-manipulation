# encoding: utf-8

import re
import subprocess

import regexes

from workflow import Workflow3
from workflow.notify import notify

WF = Workflow3()
logger = WF.logger

VPN_BASE_CMD = '/opt/cisco/anyconnect/bin/vpn -s'
KEYCHAIN_BASE_CMD = '/usr/bin/security find-generic-password -wl '

PASSWORD_KEYCHAIN_NAME = 'LDAP'
MFA_SECRET_KEYCHAIN_NAME = '2Factor'


def _run_subprocess_and_return_output(cmd):
    logger.debug("Running shell command: \"%s\"" % cmd)
    process = subprocess.Popen(
        cmd,
        shell=True,
        executable="/bin/bash",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.wait()
    output = process.stdout.read()
    returncode = process.returncode
    # logger.debug("Command \"%s\" run finished.\r\nOutput: %s\r\nReturn code: %s" % (
    #     cmd, output, returncode
    # ))

    return output, returncode


def _get_password_from_keychain(secret_name):
    logger.debug("Getting password \"%s\" from keychain." % secret_name)
    keychain_cmd = KEYCHAIN_BASE_CMD + secret_name.strip()
    output, returncode = _run_subprocess_and_return_output(keychain_cmd)
    if returncode == 0:
        logger.debug("Password \"%s\" got from keychain" % secret_name)
    else:
        pass
        # logger.debug("Cannot get password \"%s\" got from keychain.\r\nOutput: %s\r\nReturn code: %s" % (
        #     secret_name, output, returncode
        # ))
    return output


def _re_search_output(re_compile, output):
    regex = re.search(re_compile, output)

    if regex:
        return regex.groupdict()
    return False


def _re_findall_output(re_compile, output):
    match = re.findall(re_compile, output)

    if match:
        return match
    return False


def generate_totp_key(mfa_secret):
    logger.debug("Generating the TOTP code...")
    cmd = "/usr/local/bin/oathtool --totp --base32 %s" % mfa_secret
    output, returncode = _run_subprocess_and_return_output(cmd)
    if returncode == 0:
        logger.debug("TOTP code successfully generated")
        return output.strip()
    else:
        logger.debug("Cannot generate TOTP code.\r\nOutput: %s\r\nReturn code: %s" % (output, returncode))
    return False


def run_vpn_command(cmd):
    logger.debug("Running vpn command...")
    vpn_cmd_prefix = 'printf "%s\nexit" |' % cmd.strip()
    run_cmd = vpn_cmd_prefix + VPN_BASE_CMD
    output, returncode = _run_subprocess_and_return_output(run_cmd)
    # logger.debug("Running vpn command finished.\r\nOutput: %s\r\nReturn code: %s" % (output, returncode))
    return output


def run_ui():
    logger.debug("Running VPN UI...")
    output, returncode = _run_subprocess_and_return_output('open -a "Cisco AnyConnect Secure Mobility Client.app"')
    if returncode == 0:
        logger.debug("VPN UI started")
    else:
        logger.debug("VPN UI Not started.\r\nOutput: %s\r\nReturn code: %s" % (output, returncode))
    return returncode


def kill_ui():
    logger.debug("Killing VPN UI...")
    output, returncode = _run_subprocess_and_return_output('pkill -x "Cisco AnyConnect.*"')
    if returncode == 0:
        logger.debug("VPN UI Killed")
    else:
        logger.debug("VPN UI Not killed.\r\nOutput: %s\r\nReturn code: %s" % (output, returncode))
    return returncode


def auth():
    logger.debug("Getting an auth creds...")
    ldap_password = _get_password_from_keychain(PASSWORD_KEYCHAIN_NAME)
    mfa_secret = _get_password_from_keychain(MFA_SECRET_KEYCHAIN_NAME).strip()
    totp_code = generate_totp_key(mfa_secret)
    logger.debug("Auth creds got.")
    return ldap_password, totp_code


def get_state():
    logger.debug("Getting VPN state")
    state = _re_search_output(regexes.RE_VPN_STATE, run_vpn_command('state'))
    logger.debug("VPN State got.")
    if state:
        return state['state']
    return False


def get_notice():
    logger.debug("Getting VPN notice")
    notice = _re_search_output(regexes.RE_VPN_STATE_NOTICE, run_vpn_command('state'))
    logger.debug("VPN notice got")
    if notice:
        return notice
    return False


def get_hosts():
    logger.debug("Getting VPN hosts")
    hosts = _re_findall_output(regexes.RE_VPN_HOST, run_vpn_command('host'))
    logger.debug("VPN hosts got")
    if hosts:
        return hosts
    return False


def check_connection():
    logger.debug('Checking VPN connection...')
    state = get_state()
    logger.debug('State: %s' % state)
    if state == 'Connected':
        logger.debug('VPN connected')
        return True
    logger.debug('VPN disconnected')
    return False


def check_ui_running():
    logger.debug("Check VPN UI running...")
    output, returncode = _run_subprocess_and_return_output('pgrep "Cisco AnyConnect .*"')
    if returncode == 0:
        logger.debug("VPN UI is running")
        return True
    logger.debug("VPN UI is not running")
    return False


def disconnect(*args, **kwargs):
    logger.debug("Disconnecting VPN...")
    notify("Disconnecting VPN")
    output = ""
    if check_connection():
        output = run_vpn_command('disconnect')
    if check_ui_running():
        notify("Killing UI")
        kill_ui()

    logger.debug("VPN disconnection result: %s" % output)
    notify("VPN disconnected")
    return True, "VPN Disconnected", ""


def connect(vpn_server, vpn_group_index=0, ui=True, *args, **kwargs):
    logger.debug("Trying to connect to VPN...\r\nvpn_server:%s\r\nvpn_group_index:%s" % (vpn_server, vpn_group_index))
    notify("Connecting to %s" % vpn_server)
    if check_connection():
        notify("VPN Already connected")
        return True
    if check_ui_running():
        kill_ui()

    notify("Getting creds")
    ldap, mfa_code = auth()
    credentials = "printf '\\n\\n" + ldap + mfa_code + "\\ny'"
    notify("Running 'vpn connect' command")
    vpn_cmd = "/opt/cisco/anyconnect/bin/vpn -s connect '" + vpn_server + "'"
    cmd = credentials + " | " + vpn_cmd

    output, returncode = _run_subprocess_and_return_output(cmd)
    if returncode == 0 and check_connection():
        notify("Running UI")
        run_ui()
        notify("VPN Connected")
        return True
    logger.warn("VPN is not run\r\nOutput: %s\r\nReturn code: %s" % (output, returncode))
    notify("VPN Not connected", "Check workflow logs")
    return False


def reconnect(vpn_server, vpn_group_index=0, *args, **kwargs):
    if check_connection():
        disconnect()

    return connect(vpn_server, vpn_group_index)
