import socket
from time import sleep
import curses
# curses 메뉴얼: https://docs.python.org/ko/3/howto/curses.html

INTERVAL = 0.05


#cmd 화면에 Tello의 상태를 출력하는 함수
def report(str):
    stdscr.addstr(0, 0, str)
    stdscr.refresh()

if __name__ == "__main__":
    stdscr = curses.initscr() # curses 초기화w
    curses.noecho() # 키를 읽고, 특정 상황에서만 표시하도록 변경
    curses.cbreak() # 엔터를 누르지 않아도 즉시 반응하도록 변경

    # IPv4, UDP 방식의 소켓 생성 후 8890 포트와 연결(수신받을 포트)
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    socket.bind(('', 8890))

    # 8889 포트로 SDK 모드 진입을 위한 command 명령어 송신
    socket.sendto('command'.encode('utf-8'), ('192.168.10.1',8889))

    try:
        while True:
            response, ip = socket.recvfrom(1024)
            if response == 'ok': continue
            
            response = response.decode('utf-8')
            out = response.replace(';', ';\n')
            out = 'Tello State:\n' + out
            report(out)
            sleep(INTERVAL)
    except KeyboardInterrupt: #종료 시, 설정을 다시 원래대로 복구
        curses.echo()
        curses.nocbreak()
        curses.endwin()


