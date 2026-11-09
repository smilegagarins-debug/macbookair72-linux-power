#!/usr/bin/env python3
# Minimal Apple SMC port I/O (same protocol as drivers/hwmon/applesmc.c). Requires applesmc unloaded.
import os, sys, time, struct
DATA, CMD = 0x300, 0x304
f = os.open('/dev/port', os.O_RDWR)
def inb(p): os.lseek(f, p, 0); return os.read(f, 1)[0]
def outb(v, p): os.lseek(f, p, 0); os.write(f, bytes([v]))
def wait(val, mask, tmo=0.05):
    t = time.time()
    while time.time() - t < tmo:
        s = inb(CMD)
        if (s & mask) == val: return s
        time.sleep(0.00002)
    raise IOError("timeout status=%#x want %#x/%#x" % (inb(CMD), val, mask))
def send_byte(b, port):
    wait(0, 0x02); wait(0x04, 0x04); outb(b, port)
def send_cmd(c):
    wait(0, 0x02); outb(c, CMD)
def sane():
    try: wait(0, 0x04); return
    except IOError: pass
    send_cmd(0x10); wait(0, 0x04)
def hdr(cmd, key, ln):
    sane(); send_cmd(cmd)
    for ch in key.encode(): send_byte(ch, DATA)
    send_byte(ln, DATA)
def read(key, ln, cmd=0x10):
    hdr(cmd, key, ln); out = []
    for i in range(ln):
        wait(0x05, 0x05); out.append(inb(DATA))
    for i in range(16):
        time.sleep(0.00001)
        if not (inb(CMD) & 0x01): break
        inb(DATA)
    return bytes(out)
def write(key, data):
    hdr(0x11, key, len(data))
    for b in data: send_byte(b, DATA)
    wait(0, 0x04)
def info(key):
    b = read(key, 6, 0x13); return b[0], b[1:5].decode(errors='replace'), b[5]
if __name__ == '__main__':
    op = sys.argv[1]
    if op == 'r':
        ln, typ, fl = info(sys.argv[2]); print(sys.argv[2], typ, ln, read(sys.argv[2], ln).hex())
    elif op == 'w':
        write(sys.argv[2], bytes.fromhex(sys.argv[3])); print('ok')
def key_at(i):
    sane(); send_cmd(0x12)
    for b in struct.pack('>I', i): send_byte(b, DATA)
    send_byte(4, DATA); out=[]
    for j in range(4): wait(0x05,0x05); out.append(inb(DATA))
    return bytes(out).decode(errors='replace')
if len(sys.argv)>1 and sys.argv[1]=='list':
    n = struct.unpack('>I', read('#KEY',4))[0]
    for i in range(n):
        k = key_at(i)
        try:
            ln, typ, fl = info(k); v = read(k, ln).hex() if fl & 0x80 or True else ''
        except Exception as e: typ, ln, v = '?', 0, 'ERR'
        print(k, typ, ln, v)
