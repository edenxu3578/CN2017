#!/usr/bin/env python3
import sys
import socket
import packet


RECEIVER_ADDR = ('localhost', 50001)
AGENT_ADDR = ('localhost', 50002)
BUFFER_SIZE = 32


def ack(num):
    return packet.combine(num, b'')


def flush(des_file, data):
    des_file.write(data)
    print('flush')


def receive(sock, paht_of_des_file):
    #   Receive information
    recv_packet, _ = sock.recvfrom(2048)
    print('recv\tdata\t#0')
    extension = ''
    packet_num, data = packet.separate(recv_packet)
    if packet_num == 0:
        extension = data.decode('utf-8')
        sock.sendto(ack(0), AGENT_ADDR)  # Ack
        print('send\tack\t#0')

    #   Open destination file
    if paht_of_des_file[-1] == '/':
        des_filename = paht_of_des_file + 'result.' + extension
    else:
        des_filename = paht_of_des_file + '/result.' + extension

    try:
        des_file = open(des_filename, 'wb')
        #print("destination file opened")
    except:
        print("Cannot open destination file!")
        return

    seq_num = 1
    recv_buffer = 0
    data = b''
    fin = False

    while True:
        #   Receive packets
        while recv_buffer <= BUFFER_SIZE:
            recv_packet, _ = sock.recvfrom(2048)
            num, content = packet.separate(recv_packet)
            if num == -1 and content == b'fin':  # Fin
                fin = True
                print('recv\tfin')
                break
            elif num == seq_num:  # Normal case
                print('recv\tdata\t#%d' % num)
                sock.sendto(ack(num), AGENT_ADDR)  # Ack
                print('send\tack\t#%d' % num)
                data += content
                recv_buffer += 1
                seq_num += 1
            else:  # Packet lost
                sock.sendto(ack(seq_num - 1), AGENT_ADDR)
                print('drop\tdata\t#%d\nsend\tack\t#%d' % (num, seq_num - 1))

        if fin:
            sock.sendto(ack(-2), AGENT_ADDR)  # Finack
            print('send\tfinack')
            flush(des_file, data)
            break
        else:
            if recv_buffer > BUFFER_SIZE:
                recv_packet, _ = sock.recvfrom(2048)
                num, content = packet.separate(recv_packet)
                sock.sendto(ack(seq_num - 1), AGENT_ADDR)
                print('drop\tdata\t#%d\nsend\tack\t#%d' % (num, seq_num - 1))
            flush(des_file, data)
            recv_buffer = 0
            data = b''

    return


def set_config():
    global RECEIVER_ADDR
    global AGENT_ADDR
    global BUFFER_SIZE

    try:
        config_file = open('./config', 'r')

        count = 0

        for config in config_file:
            if count > 2:
                break
            if config[0] != '#':
                config = config.split(',')
                if config[0] == 'RECEIVER_ADDR':
                    RECEIVER_ADDR = (config[1], int(config[2]))
                    count += 1
                elif config[0] == 'AGENT_ADDR':
                    AGENT_ADDR = (config[1], int(config[2]))
                    count += 1
                elif config[0] == 'BUFFER_SIZE':
                    BUFFER_SIZE = int(config[1])
                    count += 1
    except:
        pass

    return


def main():
    if len(sys.argv) != 2:
        print("usage: sender.py path_of_destination_file")
        sys.exit()

    paht_of_des_file = sys.argv[1]

    set_config()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    sock.setblocking(True)

    receive(sock, paht_of_des_file)

    sock.close()


if __name__ == '__main__':
    main()
