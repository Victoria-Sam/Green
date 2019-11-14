import socket
sock = socket.socket()
sock.connect(('wgforge-srv.wargaming.net', 443))


def send_action_and_recieve_response(type='Login', **kwargs):
    sock.send(b'\x01\x00\x00\x00\x10\x00\x00\x00{"name":"Boris"}')
    result_code = sock.recv(4)
    msg_length = int.from_bytes(sock.recv(4), byteorder='little')
    data = bytearray()
    while len(data) < msg_length:
        packet = sock.recv(msg_length - len(data))
        if not packet:
            break
        data.extend(packet)
    return [result_code, msg_length, data.decode('utf-8')]


result = send_action_and_recieve_response()
print("Result code:", int.from_bytes(result[0], byteorder='little'))
print("Message length:", result[1])
print("Message:")
print(result[2])
sock.close()
