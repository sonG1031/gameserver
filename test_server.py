import socket
import argparse
import threading
import requests
# import time

host = 'localhost'
port = 4000
ports = {}
rooms = {}
# notice_flag = 0

def get_open_port(): # 사용가능한 포트 얻는 함수
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port

def main(i):
    # IPv4 체계, TCP 타입 소켓 객체를 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 포트를 사용 중 일때 에러를 해결하기 위한 구문
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # ip주소와 port번호를 함께 socket에 바인드 한다.
    # 포트의 범위는 1-65535 사이의 숫자를 사용할 수 있다.
    server_socket.bind((host, i))

    # 서버가 최대 5개의 클라이언트의 접속을 허용한다.
    server_socket.listen(5)

    while 1:
        try:
            # 클라이언트 함수가 접속하면 새로운 소켓을 반환한다.
            client_socket, addr = server_socket.accept()
        except KeyboardInterrupt:
            for user, con in rooms[str(i)]:
                con.close()
            # server_socket.close()
            print("Keyboard interrupt")
            break
        user = client_socket.recv(1024).decode('utf-8')
        rooms[str(i)][user] = client_socket

        # accept()함수로 입력만 받아주고 이후 알고리즘은 핸들러에게 맡긴다.
        # notice_thread = threading.Thread(target=handle_notice, args=(client_socket, addr, user))
        # notice_thread.daemon = True
        # notice_thread.start()

        receive_thread = threading.Thread(target=handle_receive, args=(client_socket, user, i))
        receive_thread.daemon = True
        receive_thread.start()
        # receive_thread.join()
        # handle_receive(client_socket, user, i)

def msg_func(msg, i):
    print(msg)
    for con in rooms[str(i)].values():
        try:
            con.send(msg.encode('utf-8'))
        except:
            print("연결이 비 정상적으로 종료된 소켓 발견")


def handle_receive(client_socket, user, i):
    msg = "---- %s님이 들어오셨습니다. ----"%user
    msg_func(msg, i)
    while 1:
        data = client_socket.recv(1024)
        string = data.decode('utf-8')

        if "/종료" in string:
            msg = "---- %s님이 나가셨습니다. ----"%user
            print(rooms[str(i)][user])
            #유저 목록에서 방금 종료한 유저의 정보를 삭제
            del rooms[str(i)][user]
            msg_func(msg, i)
            break
        string = "%s : %s"%(user, string)
        msg_func(string, i)
    client_socket.close()


# def handle_notice(client_socket, addr, user):
#     pass


def accept_func():
    for i in ports.values():
        thread = threading.Thread(target=main, args=(i,))
        # thread.daemon = True
        thread.start()
        # thread.join()


if __name__ == '__main__':
    #parser와 관련된 메서드 정리된 블로그 : https://docs.python.org/ko/3/library/argparse.html
    #description - 인자 도움말 전에 표시할 텍스트 (기본값: none)
    #help - 인자가 하는 일에 대한 간단한 설명.

    res = requests.get('http://127.0.0.1:5000/game/port/').json()
    for school_code in res['school_codes']:
        ports[school_code] = get_open_port()
    requests.post('http://127.0.0.1:5000/game/port/', json=ports)

    for i in ports.values():
        rooms[str(i)] = {}


    parser = argparse.ArgumentParser(description="\nJoo's server\n-p port\n")
    parser.add_argument('-p', help="port")

    args = parser.parse_args()
    try:
        port = int(args.p)
    except:
        pass
    accept_func()
