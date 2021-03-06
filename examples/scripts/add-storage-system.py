#!/usr/bin/env python3
###
# (C) Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###
import sys
if sys.version_info < (3, 2):
    raise Exception('Must use Python 3.2 or later')

import hpOneView as hpov
from ast import literal_eval
from pprint import pprint


def acceptEULA(con):
    # See if we need to accept the EULA before we try to log in
    con.get_eula_status()
    try:
        if con.get_eula_status() is True:
            print('EULA display needed')
            con.set_eula('no')
    except Exception as e:
        print('EXCEPTION:')
        print(e)


def login(con, credential):
    # Login with givin credentials
    try:
        con.login(credential)
    except:
        print('Login failed')


def getsto(sto):
    systems = sto.get_storage_systems()
    for sys in systems:
        pprint(sys)


def delsto(sto):
    systems = sto.get_storage_systems()
    for sys in systems:
        print('Removing Storage System: ', sys['serialNumber'])
        sto.remove_storage_system(sys)


def addsto(sto, ip, usr, pas, domain):
    TB = 1000 * 1000 * 1000 * 1000
    ret = sto.add_storage_system(ip, usr, pas)
    retdict = literal_eval(ret)
    print('Adding Storage System: ', retdict['ip_hostname'])
    found = False
    systems = sto.get_storage_systems()
    uri = ''
    conSys = None
    for sys in systems:
        if sys['credentials']['ip_hostname'] == ip:
            conSys = sys

    if not conSys:
        print('Unable to locale a connected system')
        sys.exit()

    for port in reversed(conSys['unmanagedPorts']):
        if port['actualNetworkUri'] != 'unknown':
            conSys['managedPorts'].append(port)
            conSys['unmanagedPorts'].remove(port)
    for port in conSys['managedPorts']:
        port['expectedNetworkUri'] = port['actualNetworkUri']
        port['groupName'] = 'Auto'
    for dom in reversed(conSys['unmanagedDomains']):
        if dom == domain:
            conSys['managedDomain'] = dom
            conSys['unmanagedDomains'].remove(dom)
            found = True
    if not found:
        print('Storage Domain ', domain, ' not found. Verify the domain '
              'exsits on the storage system')
        sys.exit()
    found = False
    for pool in reversed(conSys['unmanagedPools']):
        if pool['domain'] == domain:
            conSys['managedPools'].append(pool)
            conSys['unmanagedPools'].remove(pool)
            found = True
    if not found:
        print('Could not locate storage pool for domain:"', domain, '" Verify'
              ' the pool exsits on the storage system')
        sys.exit()

    ret = sto.update_storage_system(conSys)
    print()
    print('Status:        ', conSys['status'])
    print('Name:          ', conSys['name'])
    print('Serial Number: ', conSys['serialNumber'])
    print('Model:         ', conSys['model'])
    print('WWN:           ', conSys['wwn'])
    print('Firmware:      ', conSys['firmware'])
    print()
    print('Total:         ', format(int(conSys['totalCapacity']) / TB, '.0f'), 'TB')
    print('Allocated:     ', format(int(conSys['allocatedCapacity']) / TB, '.0f'), 'TB')
    print('Free:          ', format(int(conSys['freeCapacity']) / TB, '.0f'), 'TB')
    print()
    print('uri: ', conSys['uri'])


def main():
    parser = argparse.ArgumentParser(add_help=True, description='Usage')
    parser.add_argument('-a', '--appliance', dest='host', required=True,
                        help='HP OneView Appliance hostname or IP')
    parser.add_argument('-u', '--user', dest='user', required=False,
                        default='Administrator', help='HP OneView Username')
    parser.add_argument('-p', '--pass', dest='passwd', required=False,
                        help='HP OneView Password')
    parser.add_argument('-c', '--certificate', dest='cert', required=False,
                        help='Trusted SSL Certificate Bundle in PEM '
                        '(Base64 Encoded DER) Format')
    parser.add_argument('-r', '--proxy', dest='proxy', required=False,
                        help='Proxy (host:port format')
    parser.add_argument('-su', '--sto_user', dest='stousr', required=False,
                        help='Administrative username for the storage system')
    parser.add_argument('-sp', '--sto_pass', dest='stopass', required=False,
                        help='Administrative password for the storage system')
    parser.add_argument('-sd', '--sto_dom', dest='stodom', required=False, default='NewDomain',
                        help='Storage Domain on the storage system')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', dest='storage',
                       help='IP address of the storage system to add')
    group.add_argument('-d', dest='delete',
                       action='store_true', help='Remove ALL storage systems and exit')
    group.add_argument('-g', dest='get',
                       action='store_true', help='Get storage systems and exit')

    args = parser.parse_args()
    credential = {'userName': args.user, 'password': args.passwd}

    con = hpov.connection(args.host)
    sto = hpov.storage(con)

    if args.proxy:
        con.set_proxy(args.proxy.split(':')[0], args.proxy.split(':')[1])
    if args.cert:
        con.set_trusted_ssl_bundle(args.cert)

    login(con, credential)
    acceptEULA(con)

    if args.get:
        getsto(sto)
        sys.exit()

    if args.delete:
        delsto(sto)
        sys.exit()

    addsto(sto, args.storage, args.stousr, args.stopass, args.stodom)

if __name__ == '__main__':
    import sys
    import argparse
    sys.exit(main())

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
