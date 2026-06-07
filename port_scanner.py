import socket

def check_port(host, port):
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        result = sock.connect_ex((host,port))

        sock.close()

        return result == 0
    
    except:
        return False