# -*- coding: utf-8 -*-
import socket, struct, time
from hashlib import md5
import os
from threading import Thread
import random
import uuid
from gui import *

#利用ipconfig/all命令获取以太网的网卡和IP地址
FOUNDED = False
txt = os.popen("ipconfig /all").readlines()
for line in txt:
    if FOUNDED:
        if '\xc3\xbd\xcc\xe5\xd2\xd1\xb6\xcf\xbf\xaa\xc1\xac\xbd\xd3' in line:
            FOUNDED = False
            continue
        if '\xce\xef\xc0\xed\xb5\xd8\xd6\xb7' in line:
            mac = eval('0x'+''.join(line.split(':')[1].strip().split('-')))
        if 'IPv4 \xb5\xd8\xd6\xb7' in line:
            host_ip = line.split(':')[1].split('(')[0].strip()
        if '\xca\xca\xc5\xe4\xc6\xf7' in line:
            break
    if ('\xce\xde\xcf\xdf\xbe\xd6\xd3\xf2\xcd\xf8\xca\xca\xc5\xe4\xc6\xf7 WLAN') in line\
        or ('\xce\xde\xcf\xdf\xbe\xd6\xd3\xf2\xcd\xf8\xca\xca\xc5\xe4\xc6\xf7 \xce\xde\xcf\xdf\xcd\xf8\xc2\xe7\xc1\xac\xbd\xd3')in line\
       or ('\xd2\xd4\xcc\xab\xcd\xf8\xca\xca\xc5\xe4\xc6\xf7 \xb1\xbe\xb5\xd8\xc1\xac\xbd\xd3') in line\
       or ('\xd2\xd4\xcc\xab\xcd\xf8\xca\xca\xc5\xe4\xc6\xf7 \xd2\xd4\xcc\xab\xcd\xf8') in line:
        FOUNDED = True
if FOUNDED == False:
    alert('\xce\xb4\xbc\xec\xb2\xe2\xb5\xbd\xcd\xf8\xbf\xa8', '\xb4\xed\xce\xf3')
    sys.exit(2)
#没啥用...获取一下计算机名可以随意设
host_name = socket.gethostname()
host_os = 'Windows 10'
#一些固定设置
server = '10.100.61.3'
CONTROLCHECKSTATUS = '\x20'
ADAPTERNUM = '\x04'
IPDOG = '\x01'
PRIMARY_DNS = '10.10.10.10'
dhcp_server = '0.0.0.0'
AUTH_VERSION = '\x68\x00'
KEEP_ALIVE_VERSION = '\xdc\x02'
#好大一堆我还没看懂。。。
nic_name = ''
bind_ip = '0.0.0.0'


class ChallengeException(Exception):
    def __init__(self):
        pass


class LoginException(Exception):
    def __init__(self):
        pass


def bind_nic():
    try:
        import fcntl
        def get_ip_address(ifname):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', ifname[:15])
            )[20:24])

        return get_ip_address(nic_name)
    except ImportError as e:
        print('Indicate nic feature need to be run under Unix based system.')
        return '0.0.0.0'
    except IOError as e:
        print(nic_name + 'is unacceptable !')
        return '0.0.0.0'
    finally:
        return '0.0.0.0'


if nic_name != '':
    bind_ip = bind_nic()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#给原代码加了这个提示，貌似是其他客户端运行的错误
try:#请检查是否有其他客户端正在运行，错误
    s.bind((bind_ip, 61440))
except Exception:#
    alert('\xc7\xeb\xbc\xec\xb2\xe9\xca\xc7\xb7\xf1\xd3\xd0\xc6\xe4\xcb\xfb\xbf\xcd\xbb\xa7\xb6\xcb\xd5\xfd\xd4\xda\xd4\xcb\xd0\xd0'
          , '\xb4\xed\xce\xf3')
    sys.exit(1)

s.settimeout(3)
SALT = ''

def log(*args, **kwargs):
    s = ' '.join(args)
    print s
    with open('D:/drc.log', 'a') as f:
        f.write(s + '\n')


def challenge(svr, ran):
    while True:
        t = struct.pack("<H", int(ran) % (0xFFFF))
        s.sendto("\x01\x02" + t + "\x09" + "\x00" * 15, (svr, 61440))
        try:
            data, address = s.recvfrom(1024)
            log('[challenge] recv', data.encode('hex'))
        except:
            log('[challenge] timeout, retrying...')
            sys.exit(2)

        if address == (svr, 61440):
            break
        else:
            continue
    log('[DEBUG] challenge:\n' + data.encode('hex'))
    if data[0] != '\x02':
        raise ChallengeException
    log('[challenge] challenge packet sent.')
    return data[4:8]


def md5sum(s):
    m = md5()
    m.update(s)
    return m.digest()


def dump(n):
    s = '%x' % n
    if len(s) & 1:
        s = '0' + s
    return s.decode('hex')

def keep_alive_package_builder(number, random, tail, type=1, first=False):
    data = '\x07' + chr(number) + '\x28\x00\x0b' + chr(type)
    if first:
        data += '\x0f\x27'
    else:
        data += KEEP_ALIVE_VERSION
    data += '\x2f\x12' + '\x00' * 6
    data += tail
    data += '\x00' * 4
    if type == 3:
        foo = ''.join([chr(int(i)) for i in host_ip.split('.')])
        crc = '\x00' * 4
        data += crc + foo + '\x00' * 8
    else:
        data += '\x00' * 16
    return data

def keep_alive2(*args):
    STATUSCHK = 0
    svr = server
    ran = random.randint(0, 0xFFFF)
    ran += random.randint(1, 10)
    svr_num = 0
    packet = keep_alive_package_builder(svr_num, dump(ran), '\x00' * 4, 1, True)
    while True:
        log('[keep-alive2] send1', packet.encode('hex'))
        s.sendto(packet, (svr, 61440))
        data, address = s.recvfrom(1024)
        log('[keep-alive2] recv1', data.encode('hex'))
        if data.startswith('\x07\x00\x28\x00') or data.startswith('\x07' + chr(svr_num) + '\x28\x00'):
            break
        elif data[0] == '\x07' and data[2] == '\x10':
            log('[keep-alive2] recv file, resending..')
            svr_num = svr_num + 1
            packet = keep_alive_package_builder(svr_num, dump(ran), '\x00' * 4, 1, False)
        else:
            log('[keep-alive2] recv1/unexpected', data.encode('hex'))

    ran += random.randint(1, 10)
    packet = keep_alive_package_builder(svr_num, dump(ran), '\x00' * 4, 1, False)
    log('[keep-alive2] send2', packet.encode('hex'))
    s.sendto(packet, (svr, 61440))
    while True:
        data, address = s.recvfrom(1024)
        if data[0] == '\x07':
            svr_num = svr_num + 1
            break
        else:
            log('[keep-alive2] recv2/unexpected', data.encode('hex'))
    log('[keep-alive2] recv2', data.encode('hex'))
    tail = data[16:20]

    ran += random.randint(1, 10)
    packet = keep_alive_package_builder(svr_num, dump(ran), tail, 3, False)
    log('[keep-alive2] send3', packet.encode('hex'))
    s.sendto(packet, (svr, 61440))
    while True:
        data, address = s.recvfrom(1024)
        if data[0] == '\x07':
            svr_num = svr_num + 1
            break
        else:
            log('[keep-alive2] recv3/unexpected', data.encode('hex'))
    log('[keep-alive2] recv3', data.encode('hex'))
    tail = data[16:20]
    log("[keep-alive2] keep-alive2 loop was in daemon.")
    alert(#登陆成功，提示
        '\xb5\xc7\xc2\xbd\xb3\xc9\xb9\xa6'
        , '\xcc\xe1\xca\xbe')
    initWin.Hide()#登陆成功后自动隐藏在后台
    i = svr_num
    while True:
        try:
            ran += random.randint(1, 10)
            packet = keep_alive_package_builder(i, dump(ran), tail, 1, False)
            log('[keep_alive2] send', str(i), packet.encode('hex'))
            s.sendto(packet, (svr, 61440))
            data, address = s.recvfrom(1024)
            log('[keep_alive2] recv', data.encode('hex'))
            tail = data[16:20]

            ran += random.randint(1, 10)
            packet = keep_alive_package_builder(i + 1, dump(ran), tail, 3, False)
            s.sendto(packet, (svr, 61440))
            log('[keep_alive2] send', str(i + 1), packet.encode('hex'))
            data, address = s.recvfrom(1024)
            log('[keep_alive2] recv', data.encode('hex'))
            tail = data[16:20]
            i = (i + 2) % 0xFF
            STATUSCHK == 0
            time.sleep(20)
            keep_alive1(*args)
        except:
            STATUSCHK += 1#网络断开的检查并提示
            if STATUSCHK == 3:
                alert(#网络已断开，请重新登录，错误
                    '\xcd\xf8\xc2\xe7\xd2\xd1\xb6\xcf\xbf\xaa\xa3\xac\xc7\xeb\xd6\xd8\xd0\xc2\xb5\xc7\xc2\xbc'
                    , '\xb4\xed\xce\xf3')
                initWin.Show()
                STATUSCHK = 0
                return 'error'

def ror(md5, pwd):
    ret = ''
    for i in range(len(pwd)):
        x = ord(md5[i]) ^ ord(pwd[i])
        ret += chr(((x<<3)&0xFF) + (x>>5))
    return ret

import re


def checksum(s):
    ret = 1234
    for i in re.findall('....', s):
        ret ^= int(i[::-1].encode('hex'), 16)
    ret = (1968 * ret) & 0xffffffff
    return struct.pack('<I', ret)


def mkpkt(salt, usr, pwd, mac):
    data = '\x03\x01\x00' + chr(len(usr) + 20)#固定格式
    data += md5sum('\x03\x01' + salt + pwd)
    data += usr.ljust(36, '\x00')
    data += CONTROLCHECKSTATUS
    data += ADAPTERNUM
    data += dump(int(data[4:10].encode('hex'), 16) ^ mac).rjust(6, '\x00')
    data += md5sum("\x01" + pwd + salt + '\x00' * 4)
    data += '\x01'
    data += ''.join([chr(int(i)) for i in host_ip.split('.')])#IP地址
    data += '\00' * 4#三个默认为00.00.00.00
    data += '\00' * 4
    data += '\00' * 4
    data += md5sum(data + '\x14\x00\x07\x0b')[:8]
    data += IPDOG
    data += '\x00' * 4
    data += host_name.ljust(32, '\x00')#计算机名
    data += ''.join([chr(int(i)) for i in PRIMARY_DNS.split('.')])#DNS和dhcp服务器
    data += ''.join([chr(int(i)) for i in dhcp_server.split('.')])
    data += '\x00\x00\x00\x00'#下面这一堆都很固定
    data += '\x00' * 8
    data += '\x94\x00\x00\x00'
    data += '\x06\x00\x00\x00'
    data += '\x02\x00\x00\x00'
    data += '\xf0\x23\x00\x00'
    data += '\x02\x00\x00\x00'
    data += '\x44\x72\x43\x4f\x4d\x00\xcf\x07\x68'
    data += '\x00' * 55                                                     #下面这一长串我也不知道有啥用，也没相似的
    data += '\x33\x64\x63\x37\x39\x66\x35\x32\x31\x32\x65\x38\x31\x37\x30\x61\x63\x66\x61\x39\x65\x63\x39\x35\x66\x31\x64\x37\x34\x39\x31\x36\x35\x34\x32\x62\x65\x37\x62\x31'
    data += '\x00' * 24
    data += AUTH_VERSION
    data += '\x00' + chr(len(pwd))#密码长度。。。亏我想半天
    data += ror(md5sum('\x03\x01'+salt+pwd), pwd)
    data += '\x02\x0c'
    data += checksum(data + '\x01\x26\x07\x11\x00\x00' + dump(mac))
    data += '\x00\x00'
    data += dump(mac)
    if (len(pwd) / 4) != 4:
        data += '\x00' * (len(pwd) / 4)#其实这个值好像不影响，但是我还是加了
    data += '\x60\xa2'
    data += '\x00' * 28
    log('[mkpkt]', data.encode('hex'))
    return data


def login(usr, pwd, svr):
    import random
    global SALT
    while True:
        salt = challenge(svr, time.time() + random.randint(0xF, 0xFF))
        SALT = salt
        packet = mkpkt(salt, usr, pwd, mac)
        log('[login] send', packet.encode('hex'))
        s.sendto(packet, (svr, 61440))
        data, address = s.recvfrom(1024)
        log('[login] recv', data.encode('hex'))
        log('[login] packet sent.')
        if address == (svr, 61440):
            if data[0] == '\x04':
                log('[login] loged in')
                break
            else:
                log('[login] login failed.')#这里退出被后面的exception截获
                sys.exit(1)
        else:
            log('[login] exception occured.')
            sys.exit(1)

    log('[login] login sent')
    return data[23:39]


def keep_alive1(salt, tail, pwd, svr):
    foo = struct.pack('!H', int(time.time()) % 0xFFFF)
    data = '\xff' + md5sum('\x03\x01' + salt + pwd) + '\x00\x00\x00'
    data += tail
    data += foo + '\x00\x00\x00\x00'
    log('[keep_alive1] send', data.encode('hex'))

    s.sendto(data, (svr, 61440))
    while True:
        data, address = s.recvfrom(1024)
        if data[0] == '\x07':
            break
        else:
            log('[keep-alive1]recv/not expected', data.encode('hex'))
    log('[keep-alive1] recv', data.encode('hex'))


def empty_socket_buffer():
    log('starting to empty socket buffer')
    try:
        while True:
            data, address = s.recvfrom(1024)
            log('recived sth unexpected', data.encode('hex'))
            if s == '':
                break
    except:
        log('exception in empty_socket_buffer')
        pass
    log('emptyed')


def main(event):
    initWin.Hide()#自动隐藏界面
    try:
        f = open("D:\drcon.txt", "r")#账号密码保存目录
        [username, password] = f.read().split("\n")
        f.close()
    except Exception:#未检测到账号密码，请先点击修改账号后再一键登录，错误
        alert('\xce\xb4\xbc\xec\xb2\xe2\xb5\xbd\xd5\xcb\xba\xc5\xc3\xdc\xc2\xeb\xa3\xac\xc7\xeb\xcf\xc8\xb5\xe3\xbb\xf7\xd0\xde\xb8\xc4\xd5\xcb\xba\xc5\xba\xf3\xd4\xd9\xd2\xbb\xbc\xfc\xb5\xc7\xc2\xbc'
              , '\xb4\xed\xce\xf3')
        initWin.Show()
        return -2

    log("auth svr:" + server + "\nusername:" + username + "\npassword:" + password + "\nmac:" + str(hex(mac)))
    log(bind_ip)
    try:
            package_tail = login(username, password, server)
    except :
        alert(#登录失败，请仔细检查网络是否连通和账号密码,错误
                '\xb5\xc7\xc2\xbc\xca\xa7\xb0\xdc\xa3\xac\xc7\xeb\xd7\xd0\xcf\xb8\xbc\xec\xb2\xe9\xcd\xf8\xc2\xe7\xca\xc7\xb7\xf1\xc1\xac\xcd\xa8\xba\xcd\xd5\xcb\xba\xc5\xc3\xdc\xc2\xeb'
                , '\xb4\xed\xce\xf3')
        initWin.Show()
        return -2
    log('package_tail', package_tail.encode('hex'))
    empty_socket_buffer()
    keep_alive1(SALT, package_tail, password, server)
    bg = Thread(target=keep_alive2, args = (SALT, package_tail, password, server))#并行进程运行否则会影响gui
    bg.setDaemon(True)
    bg.start()

loginButton.Bind(wx.EVT_BUTTON, main)
initWin.Show()
app.MainLoop()