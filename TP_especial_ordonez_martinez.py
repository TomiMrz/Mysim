from time import time_ns,sleep
from random import random
import math

SEED = 1234567890
M32 = 0xFFFFFFFF # Máscara para enteros de 32 bits
MOD = 2**31 - 1
MAX_XORSHIFT = 2**32 - 1

def random_minstd(seed):
    """ Generar un número aleatorio usando el generador minstd """
    x = seed & M32
    x = (x * 16807) % MOD
    return x/MOD

def random_xorshift(seed):
    """ Generar un número aleatorio usando el generador xorshift """
    x = seed & M32
    x ^= (x << 1) & 0xFFFFFFFF
    x ^= (x >> 3)
    x ^= (x << 10) & 0xFFFFFFFF
    return x/MAX_XORSHIFT

def random_midsquare(seed):
    """ Generar un número aleatorio usando el generador de Von Neumann """
    x = seed % 10000000000
    x = (x**2 // 100000) % 10000000000
    return x/10000000000

#def random_list(seed,n,method):
#    values = []
#    for _ in range(n):
#        result = method(seed) 
#        values.append(result)
#        seed = int(result * 10000000000)
#    return values

# def random_gen(list, method):
#    index = time_ns() % len(list)
#    seed = int(list[index] * 10000000000)
#    sleep(0.000000001)
#    return method(seed)

def update_seed(value):
    """ Actualiza el seed basado en el valor generado """
    return int(value * 10000000000)

def lamda_t(t):
    return 20 + 10*math.cos((math.pi * t) / 12)

def Poisson_no_homogeneo_adelgazamiento(T,seed,random):
    'Devuelve el numero de eventos NT y los tiempos en Eventos'
    'lamda_t(t): intensidad, lamda_t(t)<=lamda'
    lamda = 30
    NT = 0
    Eventos = []
    U = 1 - random(seed)
    seed = update_seed(U)
    t = -math.log(U) / lamda
    while t <= T:
        V = random(seed)
        seed = update_seed(V)
        if V < lamda_t(t) / lamda:
            NT += 1
            Eventos.append(t)
        random_value = random(seed)
        t += -math.log(1 - random_value) / lamda
        seed = update_seed(random_value)
    return NT, Eventos

def main():
    T = 20
    NT, Eventos = Poisson_no_homogeneo_adelgazamiento(T, SEED, random_midsquare)
    print(f"Numero de eventos NT: {NT}")
    print("Tiempos de los eventos:", Eventos)

if __name__ == "__main__":
    main()