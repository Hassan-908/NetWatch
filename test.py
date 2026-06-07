from port_scanner import check_port

host = "www.google.com"
ports = [80, 443, 22]

for port in ports:
    if check_port(host,port):
        print(f"{port}: OPEN")
    else:
        print(F"{port}: CLOSED")