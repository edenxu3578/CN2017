#!/usr/bin/env python3
import socket
import random
import packet


SENDER_ADDR = ('localhost', 50000)
RECEIVER_ADDR = ('localhost', 50001)
AGENT_ADDR = ('localhost', 50002)
DROP_PROB = 0.0


def set_config():
    global SENDER_ADDR
    global RECEIVER_ADDR
    global AGENT_ADDR
    global DROP_PROB

    try:
        config_file = open('./config', 'r')

        count = 0

        for config in config_file:
            if count > 3:
                break
            if config[0] != '#':
                config = config.strip('\r\n\t').split(',')
                if config[0] == 'SENDER_ADDR':
                    SENDER_ADDR = (config[1], int(config[2]))
                    count += 1
                elif config[0] == 'RECEIVER_ADDR':
                    RECEIVER_ADDR = (config[1], int(config[2]))
                    count += 1
                elif config[0] == 'AGENT_ADDR':
                    AGENT_ADDR = (config[1], int(config[2]))
                    count += 1
                elif config[0] == 'DROP_PROB':
                    DROP_PROB = float(config[1])
                    count += 1
    except:
        pass

    return


def main():
    set_config()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(AGENT_ADDR)

    num_of_drop = 0.0
    num_of_recv_data = 0.0

    while True:
        recv_packet, _ = sock.recvfrom(2048)
        num, content = packet.separate(recv_packet)

        if num >= 0:
            if content == b'':
                # Ack
                print('get\tack\t#%d' % num)
                sock.sendto(recv_packet, SENDER_ADDR)
                print('fwd\tack\t#%d' % num)
            else:
                # Normal data
                print('get\tdata\t#%d' % num)
                num_of_recv_data += 1

                if random.random() < DROP_PROB:
                    # Drop
                    num_of_drop += 1
                    print('drop\tdata\t#%d,\tloss rate = %f' %
                          (num, num_of_drop / num_of_recv_data))
                else:
                    # Normal case
                    sock.sendto(recv_packet, RECEIVER_ADDR)
                    print('fwd\tdata\t#%d,\tloss rate = %f' %
                          (num, num_of_drop / num_of_recv_data))
        elif num == -1:
            # Fin
            print('get\tfin')
            sock.sendto(recv_packet, RECEIVER_ADDR)
            print('fwd\tfin')
        else:
            # Finack
            print('get\tfinack')
            sock.sendto(recv_packet, SENDER_ADDR)
            print('fwd\tfinack')
            break

    sock.close()

    return


if __name__ == '__main__':
    main()
