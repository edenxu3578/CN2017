#!/usr/bin/python3
import socket
import time
import string


config = open('./config', 'r')
chan = config.readline()
channel = chan.split('\'', 2)[1]
config.close()


ircsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = 'irc.freenode.net'
nickname = 'Uvuvwevwevwe'
adminname = 'EdenXu'
exitcommand = 'cy@' + ' ' + nickname
# channel = '#cn_test'


def login():
    ircsocket.send(bytes(('USER %s %s %s %s\n' %
                          (nickname, nickname, nickname, nickname)), 'utf-8'))
    ircsocket.send(bytes(('NICK ' + nickname + '\n'), 'utf-8'))


def sendmsg(msg, target=channel):
    ircsocket.send(bytes(('PRIVMSG ' + target + ' :' + msg + '\n'), 'utf-8'))
    time.sleep(0.8)


def join():
    ircsocket.send(bytes(('JOIN ' + channel + '\n'), 'utf-8'))
    sendmsg('Hello, I\'m Uvuvwevwevwe Onyetenyevwe Ugwemuhwem Osas')
    sendmsg('@repeat Anybot home?')
    ircmsg = ''
    while ircmsg.find('End of /NAMES list.') == -1:
        ircmsg = ircsocket.recv(4096).decode('utf-8')
        ircmsg = ircmsg.strip('\r')
        print(ircmsg)


def ping():
    ircsocket.send(bytes('PONG :pingis\n', 'UTF-8'))


def check(ip):
    return str(int(ip)) == ip and int(ip) >= 0 and int(ip) <= 255


def addrcalculator(tail):
    if tail.find(' ') == -1:
        if len(tail) < 4 or len(tail) > 12:
            sendmsg('0')
        else:
            ans = []
            for i in range(1, 4):
                for j in range(1, 4):
                    for k in range(1, 4):
                        if i + j + k < len(tail):
                            ip1 = tail[0:i]
                            ip2 = tail[i:i + j]
                            ip3 = tail[i + j:i + j + k]
                            ip4 = tail[i + j + k:]
                            ip = ip1 + '.' + ip2 + '.' + ip3 + '.' + ip4
                            if check(ip1) and check(ip2) and check(ip3) and check(ip4):
                                ans.append(ip)
            sendmsg(str(len(ans)))
            for i in range(0, len(ans)):
                sendmsg(ans[i])
                # for j in range(0, 100000):
                #    print('%d 隻羊，' % j)


def main():
    while True:
        ircmsg = ircsocket.recv(4096).decode('utf-8')
        ircmsg.strip('\r\n')
        print(ircmsg)

        if ircmsg.find('PRIVMSG') != -1:
            name = ircmsg.split('!', 1)[0][1:]
            message = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
            if message[0] == '@':
                order = message.split(' ', 1)[0].split('@')[1]
                order.strip('\r\n')
                if order.find('help') != -1:
                    sendmsg('@repeat <Message>')
                    sendmsg('@convert <Number>')
                    sendmsg('@ip <String>')
                    print('helped')
                elif order.find('repeat') != -1:
                    tail = message.split(' ', 1)[1].split('\r', 1)[0]
                    sendmsg(tail)
                    print('repeated')
                elif order.find('convert') != -1:
                    tail = message.split(' ', 1)[1].split('\r', 1)[0]
                    if tail.find('0x') != -1 and all(c in string.hexdigits for c in tail.split('x', 1)[1]):
                        sendmsg(str(int(tail, 0)))
                    elif tail.isdigit():
                        sendmsg(hex(int(tail)))
                    else:
                        sendmsg('UCCU, Little Bad Guy')
                    print('converted')
                elif order.find('ip') != -1:
                    tail = message.split(' ', 1)[1].split('\r', 1)[0]
                    if tail.isdigit():
                        addrcalculator(tail)
                        print('calculated')
                    else:
                        sendmsg('UCCU, Little Bad Guy')
                else:
                    sendmsg('I have no idea what are you talking about.')
                    sendmsg('Maybe you can try "@help"')
            elif message.find(exitcommand) != -1 and name.lower() == adminname.lower():
                sendmsg('She why at shine')
                ircsocket.send(bytes("QUIT \n", "UTF-8"))
                return
        else:
            if ircmsg.find('PING :') != -1:
                ping()


ircsocket.connect((server, 6667))
login()
join()
main()
