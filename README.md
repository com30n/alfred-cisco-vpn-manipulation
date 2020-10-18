# Alfred Cisco Anyconnect manipulator
Afred workflow to connect, disconnect and reconnect to the Cisco Anyconnect

## How to

- add your password into keychain with name *LDAP*
- add your MFA secret in base32 string into keychain with name *2Factor* 
- type 
    - *vpn* for main menu, 
    - *vpnh* for hosts selection window,
    - *vpnc* for quick connect to last host, 
    - *vpnd* for quick disconnect from vpn,
    - *vpnr* for quick connect to last host.

## Prerequisites

- Install Cisco Anyconnect application
- Install `oathtool` via `brew install oath-toolkit`
- Keychain
