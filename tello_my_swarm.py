import threading 
import socket
import time
import netifaces


#전송할 메세지 (텔로에게 시킬 동작)
common_msg1 = "command"
common_msg2 = "takeoff"
move_msg = "forward 100,back 100,cw 360,flip b,flip f,flip l,flip r,land".split(",")

# <<Tello의 명령어>>
# c: command
# ta: takeoff \t la: land
# f: forward \t b: back
# l: left \t r: right
# u: up \t d: down
# cw, ccw
# end\n



# 텔로들의 주소 리스트
tello_address = list()
tello_address.append(('192.168.221.188',8889)) # 모바일에 접속한 텔로
tello_address.append(('192.168.221.211',8889)) # 모바일에 접속한 텔로
tello_address.append(('192.168.221.181',8889)) # 모바일에 접속한 텔로
# tello_address.append(('192.168.137.198',8889)) # 노트북에 접속한 텔로
# tello_address.append(('192.168.137.88',8889)) # 노트북에 접속한 텔로



# ====함수 정의 공간=============================================================================

# 텔로의 신호를 받아오는 함수(항상 실행)
def recv():
    global wait
    while True: 
        try:
            response, ip = my_socket.recvfrom(1518)
            print(ip," : ",response)
            wait+=1
        except Exception:
            print ('\nExit . . .\n')
            break

# 모든 텔로가 동작을 마칠 때까지 대기하도록 하는 함수
def join(tello_num):
    global wait
    while(wait!=tello_num): continue
    wait = 0
    time.sleep(1)


# ====실행 코드 공간===============================================================================

print("---Tello Edu swarm test---")

# UDP socket 생성 및 포트 지정
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.bind(('',8889))


#recv를 실행할 thread 생성
recvThread = threading.Thread(target=recv)
recvThread.start()

wait = 0

try:
    print("1: command")
    for i in range(len(tello_address)):
        my_socket.sendto(common_msg1.encode("utf-8"), tello_address[i])
    
    join(len(tello_address))

    print("2: takeoff")
    for i in range(len(tello_address)):
        my_socket.sendto(common_msg2.encode("utf-8"), tello_address[i])

    join(len(tello_address))

    n = len(tello_address)
    for cur_msg in move_msg:
        print("{}: {}".format(n,cur_msg))
        n+=1
        for cur_addr in tello_address:
            my_socket.sendto(cur_msg.encode("utf-8"), cur_addr)
        join(len(tello_address))
        

except KeyboardInterrupt:
    print ('\n . . .\n')
    my_socket.close()  




# 지원되는 네트워크 인터페이스들을 list로 리턴 '{4E90B6B6-D601-4ADA-AA5B-ACC215C2B151}', '{0C62F66A-E7A3-11EC-9E1F-806E6F6E6963}'
ifaces = netifaces.interfaces()

# 
netifaces.interfaces()
['lo', 'eth0', 'wlan0']
netifaces.ifaddresses('wlan0')