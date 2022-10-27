import socket
import threading
import requests

# host = 'localhost'
host = '3.34.210.37'
ports = {}
rooms = {}

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
            # server_socket.close() # 유저가 접속을 끊으면 서버도 같이 끊어질때.
            print("Keyboard interrupt")
            break
        user = client_socket.recv(1024).decode('utf-8')
        rooms[str(i)][user] = client_socket

        receive_thread = threading.Thread(target=handle_receive, args=(client_socket, user, i))
        receive_thread.daemon = True
        receive_thread.start()


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



def accept_func():
    for i in ports.values():
        thread = threading.Thread(target=main, args=(i,))
        thread.start()


if __name__ == '__main__':
    # 1.
    res = requests.get('http://127.0.0.1:5000/game/port/').json()
    for school_code in res['school_codes']:
        ports[school_code] = get_open_port()
    print(ports)
    requests.post('http://127.0.0.1:5000/game/port/', json=ports)
    # 2.
    for i in ports.values():
        rooms[str(i)] = {}
    # 3.
    accept_func()
