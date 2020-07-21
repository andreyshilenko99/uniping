from socket import *
from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902

community_string = 'SWITCH'  # From file
ip_address_host = '192.168.0.102'  # From file
port_snmp = 161
OID_sysName = '.1.3.6.1.4.1.25728.8900.1.1.3.1'  # From SNMPv2-MIB hostname/sysname

check_oids = {'npThermoValue.n': '.1.3.6.1.4.1.25728.8800.1.1.2.1',
              'npThermoStatus.n': '.1.3.6.1.4.1.25728.8800.1.1.3.1',
              'npRelHumSensorValueT': '.1.3.6.1.4.1.25728.8400.2.4.0',
              'npRelHumSensorStatusH': '.1.3.6.1.4.1.25728.8400.2.5.0'}

control_oids = {'warm': '.1.3.6.1.4.1.25728.8900.1.1.3.1', 'wind': '.1.3.6.1.4.1.25728.8900.1.1.3.2',
                'control_wind': '.1.3.6.1.4.1.25728.8900.1.1.2.9'}


def snmp_get(community, ip, port, oid):  # опрос uniping
    getcmd = getCmd(SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((ip, port)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid)))

    error_indication, error_status, error_index, var_binds = next(getcmd)
    for name, val in var_binds:
        return val.prettyPrint()


# code section

name = (snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('control_wind')))
print('answer= ' + name)


# посмотреть errors во вкладке

def snmp_send(community, ip, port, oid):
    cmdGen = cmdgen.CommandGenerator()
    cmdGen.setCmd(
        cmdgen.CommunityData(community, mpModel=1),
        cmdgen.UdpTransportTarget((ip, port)),
        (oid, rfc1902.Integer(-1)),
    )


def main():
    while True:
        temp = int(snmp_get(community_string, ip_address_host, port_snmp, check_oids.get('npThermoStatus.n')))
        wetness = int(snmp_get(community_string, ip_address_host, port_snmp, check_oids.get('npRelHumSensorStatusH')))
        # print(temp)
        # print(wetness)
        if temp == 0:
            print("no termo sense")  # прописать исключения
        elif temp == 1:
            if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('warm'))) == 0:
                snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('warm'))
            if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('wind'))) == 1:
                snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('wind'))
        elif temp == 3:
            if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('wind'))) == 0:
                snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('wind'))
            if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('control_wind'))) == 1:
                # snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('control_wind'))
                print("ok")
            else:
                print("doesnt work cooler")
            if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('warm'))) == 1:
                snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('warm'))
        elif temp == 2:
            if wetness == 0:
                print("no wetness sense")
            elif wetness == 3:
                if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('warm'))) == 0:
                    snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('warm'))
                if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('wind'))) == 0:
                    snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('wind'))
                if int(snmp_get(community_string, ip_address_host, port_snmp,
                                control_oids.get('control_wind'))) == 1:
                    # snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('control_wind'))
                    print("ok")
                else:
                    print("doesnt work cooler")
            elif wetness == 2:
                if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('warm'))) == 1:
                    snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('warm'))
                if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('wind'))) == 1:
                    snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('wind'))
                break


if __name__ == "__main__":
    main()
