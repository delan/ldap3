# Created on 2013.05.23
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.
from time import sleep
from sys import version
from os import environ, remove
from os.path import join
from random import SystemRandom
from tempfile import gettempdir

from ldap3 import SIMPLE, SYNC, ROUND_ROBIN, IP_V6_PREFERRED, IP_SYSTEM_DEFAULT, Server, Connection, ServerPool, SASL, \
    NONE, ASYNC, RESTARTABLE, REUSABLE, MOCK_SYNC, MOCK_ASYNC, NTLM, AUTO_BIND_TLS_BEFORE_BIND, AUTO_BIND_NO_TLS, ALL, ANONYMOUS
from ldap3.protocol.schemas.edir888 import edir_8_8_8_schema, edir_8_8_8_dsa_info
from ldap3.protocol.schemas.ad2012R2 import ad_2012_r2_schema, ad_2012_r2_dsa_info
from ldap3.protocol.schemas.slapd24 import slapd_2_4_schema, slapd_2_4_dsa_info
from ldap3.protocol.rfc4512 import SchemaInfo, DsaInfo
from ldap3.utils.log import OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED, set_library_log_detail_level, get_detail_level_name

test_strategy = SYNC  # possible choices: SYNC, ASYNC, RESTARTABLE, REUSABLE (not used on TRAVIS - look at .travis.yml)
test_server_mode = IP_V6_PREFERRED

test_logging = False
test_log_detail = EXTENDED

test_pooling_strategy = ROUND_ROBIN
test_pooling_active = 20
test_pooling_exhaust = 15

test_fast_decoder = True  # True uses internal 10x faster than pyasn1 decoder
test_port = 389  # ldap port
test_port_ssl = 636  # ldap secure port
test_authentication = SIMPLE  # authentication type
test_check_names = True  # check attribute names in operations
test_get_info = ALL  # get info from DSA
test_usage = True
test_receive_timeout = None
test_auto_escape = False

try:
    location = environ['USERDOMAIN']
except KeyError:
    location = 'UNKNOWN'

test_server_type = 'EDIR'  # possible choices: EDIR (Novell eDirectory), AD (Microsoft Active Directory), SLAPD (OpenLDAP)

test_lazy_connection = False

if 'TRAVIS,' in location:
    _, strategy, lazy = location.split(',')
    test_strategy = strategy
    test_lazy_connection = bool(int(lazy))

location += '-' + test_server_type

if location.startswith('TRAVIS'):
    # test in the cloud
    test_server_context = 'o=resources'  # used in Novell eDirectory extended operations
    if test_server_type == 'EDIR':
        test_server = 'labldap02.cloudapp.net'
        test_server_edir_name = 'SLES1'
    elif test_server_type == 'AD':
        test_server = 'labldap01.cloudapp.net'
        test_server_edir_name = ''
    else:
        raise NotImplementedError('Cloud lab not implemented for ' + test_server_type)

    test_root_partition = ''
    test_base = 'o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'loginGraceLimit'
    test_user = 'cn=testLAB,o=resources'  # the user that performs the tests
    test_password = 'Rc1234pfop'  # user password
    test_secondary_user = 'cn=testLAB,o=resources'
    test_secondary_password = 'Rc1234pfop'
    test_sasl_user = 'testLAB.resources'
    test_sasl_password = 'Rc1234pfop'
    test_sasl_user_dn = 'cn=testLAB,o=resources'
    test_sasl_realm = None
    test_sasl_secondary_user = 'testLAB.resources'
    test_sasl_secondary_password = 'Rc1234pfop'
    test_sasl_secondary_user_dn = 'cn=testLAB,o=resources'
    test_ca_cert_file = 'test/lab-edir-ca-cert.pem'
    test_user_cert_file = 'test/lab-edir-testlab-cert.pem'
    test_user_key_file = 'test/lab-edir-testlab-key.pem'
    test_ntlm_user = 'xxx\\yyy'
    test_ntlm_password = 'zzz'
    test_logging_filename = 'ldap3.log'
    test_valid_names = ['EDIR-TEST', 'labldap02.cloudapp.net', 'WIN1.FOREST.LAB']
elif location == 'ELITE10GC-EDIR':
    # test notepbook - eDirectory (EDIR)
    # test_server = ['edir1.hyperv',
    #               'edir2.hyperv']  # ldap server where tests are executed, if a list is given a pool will be created
    test_server = 'edir1.hyperv'
    test_server_type = 'EDIR'
    test_root_partition = ''
    test_base = 'ou=fixtures,o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'loginGraceLimit'
    test_server_context = 'o=resources'  # used in novell eDirectory extended operations
    test_server_edir_name = 'edir1'  # used in novell eDirectory extended operations
    test_user = 'cn=test_admin_user,ou=bind,o=test'  # the user that performs the tests
    test_password = 'password1'  # user password
    test_secondary_user = 'cn=test_bind_user,ou=bind,o=test'
    test_secondary_password = 'password2'
    test_sasl_user = 'test_bind_sasl_user.bind.test'
    test_sasl_password = 'password3'
    test_sasl_user_dn = 'cn=test_bind_sasl_user,ou=bind,o=test'
    test_sasl_secondary_user = 'test_bind_sasl2_user.bind.test'
    test_sasl_secondary_password = 'password4'
    test_sasl_secondary_user_dn = 'cn=test_bind_sasl2_user,ou=bind,o=test'
    test_sasl_realm = None
    test_ca_cert_file = 'local-edir-ca-cert.pem'
    test_user_cert_file = 'local-edir-test_admin-cert.pem'
    test_user_key_file = 'local-edir-test_admin-key.pem'
    test_ntlm_user = 'xxx\\yyy'
    test_ntlm_password = 'zzz'
    test_logging_filename = join(gettempdir(), 'ldap3.log')
    test_valid_names = ['192.168.137.101', '192.168.137.102']
elif location == 'ELITE10GC-AD':
    # test notebook - Active Directory (AD)
    # test_server = ['win1',
    #                'win2']
    test_server = 'win1.hyperv'
    test_server_type = 'AD'
    test_domain_name = 'FOREST.LAB'  # Active Directory Domain name
    test_root_partition = 'DC=' + ',DC='.join(test_domain_name.split('.'))  # partition to use in DirSync
    test_base = 'OU=test,' + test_root_partition  # base context where test objects are created
    test_moved = 'ou=moved,OU=test,' + test_root_partition  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'logonCount'
    test_server_context = ''  # used in novell eDirectory extended operations
    test_server_edir_name = ''  # used in novell eDirectory extended operations
    test_user = 'CN=Administrator,CN=Users,' + test_root_partition  # the user that performs the tests
    test_password = 'Rc6666pfop'  # user password
    test_secondary_user = 'CN=testLAB,CN=Users,' + test_root_partition
    test_secondary_password = 'Rc999pfop'  # user password
    test_sasl_user = 'CN=testLAB,CN=Users,' + test_root_partition
    test_sasl_password = 'Rc999pfop'
    test_sasl_user_dn = 'cn=testLAB,o=resources'
    test_sasl_secondary_user = 'CN=testLAB,CN=Users,' + test_root_partition
    test_sasl_secondary_password = 'Rc999pfop'
    test_sasl_secondary_user_dn = 'cn=testSASL,o=services'
    test_sasl_realm = None
    test_ca_cert_file = 'local-forest-lab-ca.pem'
    test_user_cert_file = ''  # 'local-forest-lab-administrator-cert.pem'
    test_user_key_file = ''  # 'local-forest-lab-administrator-key.pem'
    test_ntlm_user = test_domain_name.split('.')[0] + '\\Administrator'
    test_ntlm_password = 'Rc6666pfop'
    test_logging_filename = join(gettempdir(), 'ldap3.log')
    test_valid_names = ['192.168.137.108', '192.168.137.109', 'WIN1.' + test_domain_name, 'WIN2.' + test_domain_name]
elif location == 'ELITE10GC-SLAPD':
    # test notebook - OpenLDAP (SLAPD)
    test_server = 'openldap.hyperv'
    test_server_type = 'SLAPD'
    test_root_partition = ''
    test_base = 'o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'gidNumber'
    test_server_context = ''  # used in novell eDirectory extended operations
    test_server_edir_name = ''  # used in novell eDirectory extended operations
    test_user = 'cn=admin,o=test'  # the user that performs the tests
    test_password = 'password'  # user password
    test_secondary_user = 'cn=testSASL,o=test'  # the user that performs the tests
    test_secondary_password = 'password'  # user password
    test_sasl_user = 'cn=testSASL,o=test'
    test_sasl_password = 'password'
    test_sasl_user_dn = 'cn=testSASL,o=test'
    test_sasl_secondary_user = 'cn=testSASL,o=test'
    test_sasl_secondary_password = 'password'
    test_sasl_secondary_user_dn = 'cn=testSASL,o=test'
    test_sasl_realm = 'openldap.hyperv'
    test_ca_cert_file = 'local-openldap-ca-cert.pem'
    test_user_cert_file = ''
    test_user_key_file = ''
    test_ntlm_user = 'xxx\\yyy'
    test_ntlm_password = 'zzz'
    test_logging_filename = join(gettempdir(), 'ldap3.log')
    test_valid_names = ['192.168.137.104']
elif location == 'W10GC9227-EDIR':
    # test camera
    # test_server = ['sl08',
    #               'sl09',
    #               'sl10']  # the ldap server where tests are executed, if a list is given a pool will be created
    test_server = 'sl10'
    test_server_type = 'EDIR'
    # test_server = 'nova01.amm.intra.camera.it'
    # test_server_type = 'AD'
    test_root_partition = ''
    test_base = 'ou=fixtures,o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'loginGraceLimit'
    test_server_context = 'o=risorse'  # used in novell eDirectory extended operations
    test_server_edir_name = 'sl10'  # used in novell eDirectory extended operations
    test_user = 'cn=test_admin_user,ou=bind,o=test'  # the user that performs the tests
    test_password = 'password'  # user password
    test_secondary_user = 'cn=test_user,ou=bind,o=test'  # the user that performs the tests
    test_secondary_password = 'password2'  # user password
    test_sasl_user = 'test_sasl_user.bind.test'
    test_sasl_password = 'password3'
    test_sasl_user_dn = 'cn=test_sasl_user,ou=bind,o=test'
    test_sasl_secondary_user = 'test_sasl2_user.services'
    test_sasl_secondary_password = 'password4'
    test_sasl_secondary_user_dn = 'cn=test_sasl2_user,ou=bind,o=test'
    test_sasl_realm = None
    test_ca_cert_file = 'local-edir-ca-cert.pem'
    test_user_cert_file = 'local-edir-test_admin-cert.pem'
    test_user_key_file = 'local-edir-test_admin-key.pem'
    test_ntlm_user = 'AMM\\Administrator'
    test_ntlm_password = 'xxx'
    test_logging_filename = join(gettempdir(), 'ldap3.log')
    test_valid_names = ['sl10.intra.camera.it']
else:
    raise Exception('testing location ' + location + ' is not valid')

if test_logging:
    try:
        remove(test_logging_filename)
    except OSError:
        pass

    import logging
    logging.basicConfig(filename=test_logging_filename, level=logging.DEBUG)
    set_library_log_detail_level(test_log_detail)

print('Testing location:', location)
print('Test server:', test_server)
print('Python version:', version)
print('Strategy:', test_strategy, '- Lazy:', test_lazy_connection, '- Check names:', test_check_names, '- Collect usage:', test_usage)
print('Logging:', 'False' if not test_logging else test_logging_filename, '- Log detail:', get_detail_level_name(test_log_detail) if test_logging else 'None')


def random_id():
    return '[' + str(SystemRandom().random())[-8:] + ']'


def generate_dn(base, batch_id, name):
    return test_name_attr + '=' + batch_id + name + ',' + base


def get_connection(bind=None,
                   use_ssl=None,
                   check_names=None,
                   lazy_connection=None,
                   authentication=None,
                   sasl_mechanism=None,
                   sasl_credentials=None,
                   ntlm_credentials=(None, None),
                   get_info=None,
                   usage=None,
                   fast_decoder=None,
                   simple_credentials=(None, None),
                   receive_timeout=None,
                   auto_escape=None):
    if bind is None:
        bind = True
    if check_names is None:
        check_names = test_check_names
    if lazy_connection is None:
        lazy_connection = test_lazy_connection
    if authentication is None:
        authentication = test_authentication
    if get_info is None:
        get_info = test_get_info
    if usage is None:
        usage = test_usage
    if fast_decoder is None:
        fast_decoder = test_fast_decoder
    if receive_timeout is None:
        receive_timeout = test_receive_timeout
    if auto_escape is None:
        auto_escape = test_auto_escape

    if test_server_type == 'AD' and use_ssl is None:
        use_ssl = True  # Active directory forbids Add operations in cleartext

    if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
        # define real server
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy,
                                active=test_pooling_active,
                                exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host,
                                  use_ssl=use_ssl,
                                  port=test_port_ssl if use_ssl else test_port,
                                  allowed_referral_hosts=('*', True),
                                  get_info=get_info,
                                  mode=test_server_mode))
        else:
            server = Server(host=test_server,
                            use_ssl=use_ssl,
                            port=test_port_ssl if use_ssl else test_port,
                            allowed_referral_hosts=('*', True),
                            get_info=get_info,
                            mode=test_server_mode)
    else:
        if test_server_type == 'EDIR':
            schema = SchemaInfo.from_json(edir_8_8_8_schema)
            info = DsaInfo.from_json(edir_8_8_8_dsa_info, schema)
            server = Server.from_definition('MockSyncServer', info, schema)
        elif test_server_type == 'AD':
            schema = SchemaInfo.from_json(ad_2012_r2_schema)
            info = DsaInfo.from_json(ad_2012_r2_dsa_info, schema)
            server = Server.from_definition('MockSyncServer', info, schema)
        elif test_server_type == 'SLAPD':
            schema = SchemaInfo.from_json(slapd_2_4_schema)
            info = DsaInfo.from_json(slapd_2_4_dsa_info, schema)
            server = Server.from_definition('MockSyncServer', info, schema)

    if authentication == SASL:
        connection = Connection(server,
                                auto_bind=bind,
                                version=3,
                                client_strategy=test_strategy,
                                authentication=SASL,
                                sasl_mechanism=sasl_mechanism,
                                sasl_credentials=sasl_credentials,
                                lazy=lazy_connection,
                                pool_name='pool1',
                                check_names=check_names,
                                collect_usage=usage,
                                fast_decoder=fast_decoder,
                                receive_timeout=receive_timeout,
                                auto_escape=auto_escape)
    elif authentication == NTLM:
        connection = Connection(server,
                                auto_bind=bind,
                                version=3,
                                client_strategy=test_strategy,
                                user=ntlm_credentials[0],
                                password=ntlm_credentials[1],
                                authentication=NTLM,
                                lazy=lazy_connection,
                                pool_name='pool1',
                                check_names=check_names,
                                collect_usage=usage,
                                fast_decoder=fast_decoder,
                                receive_timeout=receive_timeout,
                                auto_escape=auto_escape)
    elif authentication == ANONYMOUS:
        connection = Connection(server,
                                auto_bind=bind,
                                version=3,
                                client_strategy=test_strategy,
                                user=None,
                                password=None,
                                authentication=ANONYMOUS,
                                lazy=lazy_connection,
                                pool_name='pool1',
                                check_names=check_names,
                                collect_usage=usage,
                                fast_decoder=fast_decoder,
                                receive_timeout=receive_timeout,
                                auto_escape=auto_escape)
    else:
        connection = Connection(server,
                                auto_bind=bind,
                                version=3,
                                client_strategy=test_strategy,
                                user=simple_credentials[0] or test_user,
                                password=simple_credentials[1] or test_password,
                                authentication=authentication,
                                lazy=lazy_connection,
                                pool_name='pool1',
                                check_names=check_names,
                                collect_usage=usage,
                                fast_decoder=fast_decoder,
                                receive_timeout=receive_timeout,
                                auto_escape=auto_escape)

    if test_strategy in [MOCK_SYNC, MOCK_ASYNC]:
        # create authentication identities for testing mock strategies
        connection.strategy.add_entry(test_user, {'objectClass': 'inetOrgPerson', 'userPassword': test_password})
        connection.strategy.add_entry(test_secondary_user, {'objectClass': 'inetOrgPerson', 'userPassword': test_secondary_password})
        connection.strategy.add_entry(test_sasl_user_dn, {'objectClass': 'inetOrgPerson', 'userPassword': test_sasl_password})
        connection.strategy.add_entry(test_sasl_secondary_user_dn, {'objectClass': 'inetOrgPerson', 'userPassword': test_sasl_secondary_password})
        # connection.strategy.add_entry(test_ntlm_user, {'objectClass': 'inetOrgPerson', 'userPassword': test_ntlm_password})
        if bind:
            connection.bind()

    return connection


def drop_connection(connection, dn_to_delete=None):
    if dn_to_delete:
        for dn in dn_to_delete:
            done = False
            counter = 30
            while not done:  # waits at maximum for 120 seconds
                operation_result = connection.delete(dn[0])
                result = get_operation_result(connection, operation_result)
                if result['description'] == 'success':
                    done = True
                elif result['description'] == 'busy':
                    counter -= 1
                    if counter >= 0:
                        sleep(4)  # wait and retry
                    else:
                        print('unable to delete object ' + dn[0] + ': ' + str(result))
                        done = True
                else:
                    print('unable to delete object ' + dn[0] + ': ' + str(result))
                    break
    connection.unbind()
    if connection.strategy.pooled:
        connection.strategy.terminate()


def get_operation_result(connection, operation_result):
    if not connection.strategy.sync:
        _, result = connection.get_response(operation_result)
    else:
        result = connection.result

    return result


def add_user(connection, batch_id, username, password=None, attributes=None):
    if password is None:
        password = 'Rc2597pfop'

    if attributes is None:
        attributes = dict()

    if test_server_type == 'EDIR':
        attributes.update({'objectClass': 'inetOrgPerson',
                           'sn': username})
    elif test_server_type == 'AD':
        attributes.update({'objectClass': ['person', 'user', 'organizationalPerson', 'top', 'inetOrgPerson'],
                           'sn': username,
                           'sAMAccountName': (batch_id[1: -1] + username)[-20:],  # 20 is the maximum user name length in AD
                           'userPrincipalName': (batch_id[1: -1] + username)[-20:] + '@' + test_domain_name,
                           'displayName': (batch_id[1: -1] + username)[-20:],
                           'unicodePwd': ('"%s"' % password).encode('utf-16-le'),
                           'userAccountControl': 512})
    elif test_server_type == 'SLAPD':
        attributes.update({'objectClass': ['inetOrgPerson', 'posixGroup', 'top'], 'sn': username, 'gidNumber': 0})
    else:
        attributes.update({'objectClass': 'inetOrgPerson', 'sn': username})
    dn = generate_dn(test_base, batch_id, username)
    operation_result = connection.add(dn, None, attributes)
    result = get_operation_result(connection, operation_result)
    if not result['description'] == 'success':
        raise Exception('unable to create user ' + dn + ': ' + str(result))

    return dn, result


def add_group(connection, batch_id, groupname, members=None):
    if members is None:
        members = list()
    dn = generate_dn(test_base, batch_id, groupname)
    operation_result = connection.add(dn, [], {'objectClass': 'groupOfNames', 'member': [member[0] for member in members]})
    result = get_operation_result(connection, operation_result)
    if not result['description'] == 'success':
        raise Exception('unable to create group ' + groupname + ': ' + str(result))

    return dn, result
