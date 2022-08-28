import socket
# 메뉴얼: https://docs.python.org/ko/3/library/socket.html


# Tello의 접속모드를 변경하기 위한 함수 (AP 모드 -> station 모드)
def set_ap(SSID, PW):
    # SSID: Service Set IDentifier (e.g. Wi-Fi 이름)
    # PW: the password of the network (e.g. Wi-Fi 비밀번호)


    #소켓 생성 및 포트 연결
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    my_socket.bind(('', 8889)) #'': 모든 host / 8889: 연결할 포트

    '''
    socket(): 소켓을 생성하는 함수
        SOCKET socket(int family=AF_INET,int type=SOCK_STREAM,int proto=0);
        실패 시: -1(SOCKET_ERROR) 반환
        family: 네트워크 주소 체계
            #define AF_INET       2         //IPv4
            #define AF_INET6      23        //IPv6
        type: 소켓 타입
            #define SOCK_STREAM   1         //스트림 , TCP 프롤토콜의 전송 방식
            #define SOCK_DGRAM    2         //데이터 그램, UDP 프로토콜의 전송 방식
            #define SOCK_RAW      3         //RAW 소켓, 가공하지 않은 소켓
        proto: 프로토콜
            #define IPPROTO_TCP   6         //TCP 프로토콜
            #define IPPROTO_UDP   17        //UDP 프로토콜
            #define IPPROTO_RAW   255       //RAW
    '''
    
    #텔로의 주소 (텔로에 접속했을 때 텔로의 IP, 포트)
    tello_address = ('192.168.10.1', 8889)
    

    #Tello에게 송신- SDK 모드에 진입하기 위해, command 명령어 전송
    cmd_str = 'command'
    my_socket.sendto(cmd_str.encode('utf-8'), tello_address)
    

    #Tello로부터 수신
    response, ip = my_socket.recvfrom(100) #받을 길이(bytes) 지정
    print('from %s: %s' % (ip, response))

    
    #Tello에게 송신- 접속모드를 station모드로 변경하기 위해, ap SSID PW 명령어 전송
    cmd_str = 'ap %s %s' % (SSID, PW)
    my_socket.sendto(cmd_str.encode('utf-8'), tello_address)
    
    
    #Tello로부터 수신
    response, ip = my_socket.recvfrom(100) #받을 길이(bytes) 지정
    print('from %s: %s' % (ip, response))


#실행
set_ap('LUC', 'LUCLUCLUC')


