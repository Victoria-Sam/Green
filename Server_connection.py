import socket
sock = socket.socket()
sock.connect(('wgforge-srv.wargaming.net', 443))
actions = {'LOGIN': 1, 'LOGOUT': 2, 'MOVE': 3, 'UPGRADE': 4, 'TURN': 5,
           'PLAYER': 6, 'GAMES': 7, 'MAP': 10}


def message_to_server(action, **kwargs):
    message_code = actions[action]
    action_message = bytearray()
    action_message += message_code.to_bytes(4, byteorder='little')

    if len(kwargs) != 0:
        json_msg = '{'
        for key, value in kwargs.items():
            if value is not None:
                json_msg += '"' + key + '":'
                if isinstance(value, str):
                    json_msg += '"' + str(value) + '", '
                else:
                    json_msg += str(value) + ', '
        json_msg = json_msg[:-2]
        json_msg += '}'
        action_message += len(json_msg).to_bytes(4, byteorder='little')
        action_message.extend(json_msg.encode())
    else:
        action_message += len(kwargs).to_bytes(4, byteorder='little')

    sock.send(action_message)

    result_code = int.from_bytes(sock.recv(4), byteorder='little')
    response_length = int.from_bytes(sock.recv(4), byteorder='little')
    response = sock.recv(response_length, socket.MSG_WAITALL)
    return {"result_code": result_code,
            "response_length": response_length,
            "response": response.decode('utf-8')
            }


result = message_to_server('LOGIN', name="Boris")
print("Result code:", result["result_code"])
print("Response length:", result["response_length"])
print("Response:")
print(result["response"])
result = message_to_server('MAP', layer=0)
print("Result code:", result["result_code"])
print("Response length:", result["response_length"])
print("Response:")
print(result["response"])
result = message_to_server('MAP', layer=1)
print("Result code:", result["result_code"])
print("Response length:", result["response_length"])
print("Response:")
print(result["response"])
result = message_to_server('MAP', layer=10)
print("Result code:", result["result_code"])
print("Response length:", result["response_length"])
print("Response:")
print(result["response"])
result = message_to_server('MAP', layer=10)
print("Result code:", result["result_code"])
print("Response length:", result["response_length"])
print("Response:")
print(result["response"])
result = message_to_server('GAMES')
print("Result code:", result["result_code"])
print("Response length:", result["response_length"])
print("Response:")
print(result["response"])
result = message_to_server('TURN')
print("Result code:", result["result_code"])
print("Response length:", result["response_length"])
print("Response:")
result = message_to_server('UPGRADE', posts=[], trains=[1])
print("Result code:", result["result_code"])
print("Response length:", result["response_length"])
print("Response:")
print(result["response"])
sock.close()
