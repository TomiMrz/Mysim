# from time import time_ns,sleep
import matplotlib.pyplot as plt
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

def exponencial(random):
    U = 1-random
    return -math.log(U)/35

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


def analizar_metricas(T, llegadas, servicios):
    NT = len(llegadas)
    servidor_ocupado_hasta = 0
    tiempo_total_ocupado = 0
    tiempos_espera = []
    tiempos_sistema = []
    ocupacion_por_hora = [0] * (T+1)

    eventos = sorted([(t, 'llegada', i) for i, t in enumerate(llegadas)])
    for i, llegada in enumerate(llegadas):
        servicio = servicios[i]
        inicio_atencion = max(llegada, servidor_ocupado_hasta)
        fin_atencion = inicio_atencion + servicio
        espera = inicio_atencion - llegada

        tiempos_espera.append(espera)
        tiempos_sistema.append(fin_atencion - llegada)
        tiempo_total_ocupado += servicio
        servidor_ocupado_hasta = fin_atencion
        
        # TODO: Chequear si esto está bien
        h = int(inicio_atencion)
        if int(inicio_atencion) != int(inicio_atencion + servicio):
            # Si el servicio no termina en la misma hora,
            # se distribuye el tiempo de servicio en dos horas
            ocupacion_por_hora[h] += servicio - (inicio_atencion - h)
            ocupacion_por_hora[h + 1] += (inicio_atencion + servicio) - (h + 1)
        else:
            ocupacion_por_hora[h] += servicio

    for h in ocupacion_por_hora:
        h *= 100

    # Evolución de la cola
    eventos = sorted([(t, 'llegada') for t in llegadas] + [(t, 'salida') for t in 
                [max(llegadas[i], sum(servicios[:i])) + servicios[i] for i in range(NT)]])
    en_cola = 0
    tiempos, valores = [], []
    for t, tipo in eventos:
        tiempos.append(t)
        if tipo == 'llegada':
            en_cola += 1
        else:
            en_cola -= 1
        valores.append(en_cola)

    # Métricas
    tiempo_promedio_sistema = sum(tiempos_sistema) / NT
    porcentaje_ocupado = (tiempo_total_ocupado / T) * 100

    print(f"Tiempo promedio en el sistema: {tiempo_promedio_sistema*3600:.2f} segundos")
    print(f"Porcentaje del tiempo que el servidor está ocupado: {porcentaje_ocupado:.2f}%")

    # Gráficos
    plt.figure(figsize=(12, 10))

    plt.subplot(2, 3, 1)
    plt.plot(range(T+1), ocupacion_por_hora, label="Utilización por hora")
    plt.xlabel("Hora")
    plt.ylabel("Utilización")
    plt.title("Tasa de utilización por hora")
    plt.grid(True)

    plt.subplot(2, 3, 2)
    plt.hist([t*3600 for t in tiempos_espera], bins=30, color='skyblue')
    plt.xlabel("Tiempo de espera (s)")
    plt.title("Distribución de los tiempos de espera")

    plt.subplot(2, 3, 3)
    plt.plot(tiempos, valores, drawstyle='steps-post')
    plt.xlabel("Tiempo (h)")
    plt.ylabel("Longitud de la cola")
    plt.title("Evolución de la cola")

    plt.subplot(2, 3, 4)
    plt.hist([t*3600 for t in tiempos_sistema], bins=30, color='orange')
    plt.xlabel("Tiempo en el sistema (s)")
    plt.title("Histograma del tiempo en el sistema")

    plt.subplot(2, 3, 5)
    interarribos = [(llegadas[i+1] - llegadas[i])*3600 for i in range(NT-1)]
    plt.hist(interarribos, bins=30, color='green')
    plt.xlabel("Tiempo entre arribos (s)")
    plt.title("Distribución de tiempo entre arribos")

    plt.subplot(2, 3, 6)
    plt.hist([s*3600 for s in servicios], bins=30, color='purple')
    plt.xlabel("Tiempo de servicio (s)")
    plt.title("Distribución de tiempos de servicio")

    plt.tight_layout()
    plt.show()


def main():
    T = 48  # duración total en horas
    seed = SEED
    NT, llegadas = Poisson_no_homogeneo_adelgazamiento(T, seed, random_xorshift)

    # Generar tiempos de servicio
    servicios = []
    for _ in range(NT):
        u = random_xorshift(seed)
        seed = update_seed(u)
        servicios.append(exponencial(u))

    analizar_metricas(T, llegadas, servicios)

if __name__ == "__main__":
    main()