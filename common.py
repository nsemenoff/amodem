import cStringIO
import numpy as np

import logging
log = logging.getLogger(__name__)

Fs = 32e3
Ts = 1.0 / Fs

frequencies = (np.arange(4) + 8) * 1e3
carrier_index = len(frequencies)/2
Fc = frequencies[carrier_index]
Tc = 1.0 / Fc

Tsym = 1e-3
Nsym = int(Tsym / Ts)
baud = int(1/Tsym)

scaling = 32000.0  # out of 2**15
SATURATION_THRESHOLD = 1.0

LENGTH_FORMAT = '<I'

def to_bits(bytes_list):
    for val in bytes_list:
        for i in range(8):
            mask = 1 << i
            yield (1 if (val & mask) else 0)

bit_weights = [1 << i for i in range(8)]
def to_byte(bits):
    assert len(bits) == 8
    byte = int(np.dot(bits, bit_weights))
    return chr(byte)

def load(fname):
    data = open(fname, 'rb').read()
    return loads(data)

def loads(data):
    x = np.fromstring(data, dtype='int16')
    x = x / scaling
    t = np.arange(len(x)) / Fs
    return t, x

def dumps(sym, n=1):
    sym = sym.imag * scaling
    sym = sym.astype('int16')
    data = sym.tostring()
    return data * n

def norm(x):
    return np.sqrt(np.dot(x.conj(), x).real)


def iterate(data, bufsize, offset=0, advance=1, func=None):
    assert bufsize > 0
    assert offset >= 0
    assert advance > 0
    buf = np.zeros(bufsize)
    buf_index = 0
    for data_index, value in enumerate(data):
        if data_index < offset:
            continue

        buf[buf_index] = value
        buf_index += 1

        if buf_index == bufsize:
            result = func(buf) if func else buf
            yield offset, result
            buf[:-advance] = buf[advance:]
            buf_index = max(0, buf_index - advance)
            offset += advance

if __name__ == '__main__':

    import pylab
    def plot(f):
        t = pylab.linspace(0, Tsym, 1e3)
        x = pylab.sin(2 * pylab.pi * f * t)
        pylab.plot(t / Tsym, x)
        t = pylab.linspace(0, Tsym, Nsym + 1)
        x = pylab.sin(2 * pylab.pi * f * t)
        pylab.plot(t / Tsym, x, '.k')

    plot(Fc)
    pylab.show()