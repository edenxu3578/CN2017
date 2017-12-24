#!/usr/bin/env python3
import sys
import socket
import time
import packet


SENDER_ADDR = ('localhost', 50000)
AGENT_ADDR = ('localhost', 50002)
PACKET_SIZE = 1024
TIME_OUT_BOUND = 1.0


def send(sock,  src_filename):
    #   Open source file
    try:
        src_file = open(src_filename, 'rb')
        #print('source file opened')
    except:
        print('Cannot open source file!')
        return

    #   Gather information e.g. filename extension
    extension = src_filename.split('.')[-1].encode('utf-8')
    info = packet.combine(0, extension)

    #   Make packets
    packets = []
    packets.append(info)
    seq_num = 1

    while True:
        content = src_file.read(PACKET_SIZE)
        if not content:
            break
        packets.append(packet.combine(seq_num, content))
        seq_num = seq_num + 1
    num_of_packets = len(packets)
    src_file.close()

    base = 0
    next_seq_num = 0
    window_size = 1
    threshold = 16
    time_out = False

    while base < num_of_packets:
        #   Send packets
        if not time_out:
            while next_seq_num < base + window_size and next_seq_num < num_of_packets:
                sock.sendto(packets[next_seq_num], AGENT_ADDR)
                print('send\tdata\t#%d,\twinSize = %d' %
                      (next_seq_num, window_size))
                next_seq_num += 1

        # Resend
        else:
            threshold = max(1, window_size / 2)
            window_size = 1
            sock.sendto(packets[base], AGENT_ADDR)
            print('time\tout,\t\tthreshold = %d\nresnd\tdata\t#%d,\twinSize = 1' % (
                threshold, base))
            next_seq_num = base + 1
            time_out = False

        start_time = time.time()

        #   Recieve ack
        while base < next_seq_num:
            try:
                recv_packet, _ = sock.recvfrom(1024)
                ack, _ = packet.separate(recv_packet)
                print('recv\tack\t#%d' % ack)
                if ack == base:
                    base += 1
            except:
                #   Timeout
                if time.time() - start_time >= TIME_OUT_BOUND:
                    time_out = True
                    break

        #   Set window size
        if not time_out:
            if window_size >= threshold:
                window_size += 1
            else:
                window_size *= 2

    #   Send fin
    sock.setblocking(True)
    sock.sendto(packet.combine(-1, b'fin'), AGENT_ADDR)
    print('send\tfin')
    recv_packet, _ = sock.recvfrom(1024)
    print('recv\tfinack')

    return


def set_config():
    global SENDER_ADDR
    global AGENT_ADDR
    global PACKET_SIZE
    global TIME_OUT_BOUND

    try:
        config_file = open('./config', 'r')

        count = 0

        for config in config_file:
            if count > 3:
                break
            if config[0] != '#':
                config = config.split(',')
                if config[0] == 'SENDER_ADDR':
                    SENDER_ADDR = (config[1], int(config[2]))
                    count += 1
                elif config[0] == 'AGENT_ADDR':
                    AGENT_ADDR = (config[1], int(config[2]))
                    count += 1
                elif config[0] == 'PACKET_SIZE':
                    PACKET_SIZE = int(config[1])
                    count += 1
                elif config[0] == 'TIME_OUT_BOUND':
                    TIME_OUT_BOUND = float(config[1])
                    count += 1
    except:
        pass

    return


def main():
    if len(sys.argv) != 2:
        print('usage: sender.py path_of_source_file')
        sys.exit()

    src_filename = sys.argv[1]

    set_config()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)
    sock.setblocking(False)

    send(sock, src_filename)

    sock.close()

    return


if __name__ == '__main__':
    main()
