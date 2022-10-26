import requests
import socket
res = requests.get('http://127.0.0.1:5000/game/port/').json()
ports = {}

def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port

print(res['school_codes'])

for school_code in res['school_codes']:
    ports[school_code] = get_open_port()
print(ports)
send_db = requests.post('http://127.0.0.1:5000/game/port/', json=ports)



