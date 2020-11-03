import binascii
import math
import mmap
import os
import time
from numba import njit


@njit
def _modular_add(a, b):
    return (a + b) % 2 ** 32


@njit
def _rotate_left(x, n):
    return (x << n) | (x >> (32 - n))


@njit
def _calc_f(b, c, d) -> int:
    return (b & c) | (~b & d)


@njit
def _calc_g(b, c, d) -> int:
    return (b & d) | (c & ~d)


@njit
def _calc_h(b, c, d) -> int:
    return b ^ c ^ d


@njit
def _calc_i(b, c, d) -> int:
    return c ^ (b | ~d)


class MD5:

    def __init__(self, string: str = None, file_path: str = None):

        if string is None and file_path is None:
            raise AttributeError()
        elif string is not None:
            self._string = string
        else:
            self._file_path = file_path

        self._T = [math.floor(pow(2, 32) * abs(math.sin(i + 1))) for i in range(64)]
        self._S = [[7, 12, 17, 22], [5, 9, 14, 20], [4, 11, 16, 23], [6, 10, 15, 21]]
        self._init_buffer()

    def _init_buffer(self) -> None:
        """
        initial values of the buffer
        """
        self._buffer = {
            'A': 0x67452301,
            'B': 0xEFCDAB89,
            'C': 0x98BADCFE,
            'D': 0x10325476,
        }

    def _append_padding_bytes(self, string) -> bytearray:
        # print(type(string))
        if isinstance(string, bytearray):
            byte_array = string
        else:
            byte_array = bytearray(string, encoding='utf-8')
        byte_array.append(128)

        ost = len(byte_array) % 64

        if ost > 56:
            byte_array.extend([0] * (64 - ost + 56))
        elif ost < 56:
            byte_array.extend([0] * (56 - ost))

        return byte_array

    def _append_length(self, array: bytearray, length: int) -> bytearray:
        """
        Add 64 bits
        """
        byte_array = array.copy()
        byte_array.extend(length.to_bytes(8, byteorder='little'))

        return byte_array

    def _process_block(self, block: bytearray) -> None:

        a, b, c, d = self._buffer['A'], self._buffer['B'], self._buffer['C'], self._buffer['D']

        X = [int.from_bytes(block[j * 4:j * 4 + 4], byteorder='little') for j in range(16)]

        temp, k = 0, 0

        for j in range(64):
            mod16 = j // 16
            if mod16 == 0:
                k = j
                temp = _calc_f(b, c, d)
            elif mod16 == 1:
                k = (5 * j + 1) % 16
                temp = _calc_g(b, c, d)
            elif mod16 == 2:
                k = (3 * j + 5) % 16
                temp = _calc_h(b, c, d)
            elif mod16 == 3:
                k = (7 * j) % 16
                temp = _calc_i(b, c, d)

            temp = (_rotate_left((temp + X[k] + self._T[j] + a) % 2 ** 32, self._S[mod16][j % 4]) + b) % 2 ** 32

            a, b, c, d = d, temp, b, c

        self._buffer['A'] = _modular_add(self._buffer['A'], a)
        self._buffer['B'] = _modular_add(self._buffer['B'], b)
        self._buffer['C'] = _modular_add(self._buffer['C'], c)
        self._buffer['D'] = _modular_add(self._buffer['D'], d)

    def _result(self) -> str:
        res = ''
        for v in self._buffer.values():
            res += "{0:08x}".format(int.from_bytes(binascii.unhexlify("{0:08x}".format(v)), byteorder='little'))
        return res

    def _hash_file(self) -> str:

        file_size = os.path.getsize(self._file_path)
        block_number = file_size // 64
        last_block_size = file_size - block_number * 64

        from_time = time.time()
        with open(self._file_path, mode='r+b') as file_obj:
            with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
                for i in range(block_number):
                    arr = bytearray(mmap_obj.read(64))
                    self._process_block(arr)
                arr = bytearray(mmap_obj.read(last_block_size))
                last_block = self._append_length(self._append_padding_bytes(arr), file_size * 8)
                if len(last_block) == 64:
                    self._process_block(last_block)
                else:
                    print('hi')
                    self._process_block(last_block[0:64])
                    self._process_block(last_block[64:128])
                print(time.time() - from_time)
                return self._result()

    def _hash_string(self) -> str:
        size = (len(self._string) * 8) % pow(2, 64)
        m = self._append_length(self._append_padding_bytes(self._string), size)
        # print(''.join(format(byte, '08b') for byte in m))
        block_number = len(m) // 64
        self._init_buffer()

        for i in range(block_number):
            self._process_block(m[i * 64:i * 64 + 64])

        return self._result()

    def hash(self) -> str:

        self._init_buffer()
        if '_string' in self.__dict__:
            return self._hash_string()
        else:
            return self._hash_file()


