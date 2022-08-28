import socket
import netifaces
from netaddr import IPNetwork


# 현 컴퓨터의 네트워크 인터페이스들을 list로 리턴
ifaces = netifaces.interfaces() 
print("ifaces:",ifaces)


addr_list = []
subnets = []

# ifaces(인터페이스) -> infos(dict로 변환) -> info(IPv4) -> addr, mask

for myiface in ifaces:
    infos = netifaces.ifaddresses(myiface) # 네트워크 인터페이스에 대한 정보 dict
    # ip, mac 주소, 마스크 등의 정보 (netifaces.address_families를 참고)
    
    print("infos:",infos)

    if socket.AF_INET not in infos: continue # IPv4를 지원하지 않는 인터페이스이면 패스

    info = infos[socket.AF_INET][0] # IPv4 주소, 마스크, 브로드케스트에 대한 dict

    addr = info['addr']
    mask = info['netmask']

    if mask != '255.255.255.0': continue # mask가 255.255.255.0가 아니면 패스

    cidr = IPNetwork("{}/{}".format(addr, mask)) # CIDR 표기 주소를 지닌 객체 생성

    subnets.append(cidr)
    addr_list.append(addr)

possible_addr = []
for cidr in subnets:
    for ip in cidr:
        ip_4 = str(ip).split('.')[3]
        if  ip_4 == '0' or ip_4 =='255': continue
        possible_addr.append(str(ip))
        
print(possible_addr)
# for subnet, mask in subnets:
#     for ip in IPNetwork
