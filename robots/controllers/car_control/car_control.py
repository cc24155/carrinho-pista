# Júlio Pacheco Stein
# 24137


import struct
import socket
import _thread

from controller import Robot, Camera, Display

status_sentido = False

# dados para criar um servidor socjet para receber mensagens
def get_porta():
    return 9001

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    return IP

def on_new_client(socket, addr):
    global status_sentido
    while True:
        msg = socket.recv(1024)
        if msg:
            print('olha a mensagem')
            break
        else:
            break
    req = msg.decode()
    if req.__contains__('anda'):
        status_sentido = True
    print(req)
    socket.close()
    return

# define o servidor
def servidor(https, hport):
    sockHttp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sockHttp.bind((https, hport))
    except:
        sockHttp.bind(('', hport))
    
    sockHttp.listen(1)
    print(f'Iniciou o servidor em {get_ip()} na porta {get_porta()}')
    while True:
        client, addr = sockHttp.accept()
        _thread.start_new_thread(on_new_client, (client, addr))
        
# inicializa a thread do socket servidor
_thread.start_new_thread(servidor, (get_ip(), get_porta()))


# programacao de movimento e sensores

robot = Robot()

timestep = int(robot.getBasicTimeStep())

print("iniciando rodas")

motorE = robot.getDevice('motorE')
motorE.setPosition(float('inf'))
motorE.setVelocity(0.0)

motorE2 = robot.getDevice('motorE2')
motorE2.setPosition(float('inf'))
motorE2.setVelocity(0.0)


motorD = robot.getDevice('motorD')
motorD.setPosition(float('inf'))
motorD.setVelocity(0.0)

motorD2 = robot.getDevice('motorD2')
motorD2.setPosition(float('inf'))
motorD2.setVelocity(0.0)

ds = robot.getDevice('DS')
dse = robot.getDevice('DSE')
dsd = robot.getDevice('DSD')

ds.enable(timestep)
dse.enable(timestep)
dsd.enable(timestep)


camera = robot.getDevice('camera')
refresh_rate_ms = 64
camera.enable(refresh_rate_ms)
display = robot.getDevice('display')

sentido = False
vini_e = 0
vini_d = 0



v_maxima = 5.0

# Julio 
# 24137

while robot.step(timestep) != -1:    
    ve = round(dse.getValue(), 2)
    vd = round(dsd.getValue(), 2)
    
    e_preto = ve >= 5 
    d_preto = vd >= 5 
    
    # maquina de escapar circulos 2.0    
    if e_preto and d_preto:
        # Quando os dois sensores pegam preto
        # Gira para um lado para ir por um dos lados e 
        # não acabar indo reto e fora do caminho
        motorE.setVelocity(v_maxima)
        motorE2.setVelocity(v_maxima)
        motorD.setVelocity(-v_maxima * 0.5)
        motorD2.setVelocity(-v_maxima * 0.5)

    # curvas esquerda
    elif e_preto and not d_preto:
        # Roda esquerda gira para tras e roda direita para frente
        # Resulta numa curva bem fechada, gira no proprio eixo
        motorE.setVelocity(-v_maxima)
        motorE2.setVelocity(-v_maxima)
        motorD.setVelocity(v_maxima)
        motorD2.setVelocity(v_maxima)
                
    # curvas direita
    elif d_preto and not e_preto:
        # Direita para tras e esquerda para frente
        motorE.setVelocity(v_maxima)
        motorE2.setVelocity(v_maxima)
        motorD.setVelocity(-v_maxima)
        motorD2.setVelocity(-v_maxima)
        
    # lihna reta ------
    else: 
        # ambos sensores no branco -> anda reto
        motorE.setVelocity(v_maxima)
        motorE2.setVelocity(v_maxima)
        motorD.setVelocity(v_maxima)
        motorD2.setVelocity(v_maxima)

    # Processamento da câmera
    image = camera.getImage()
    if display and image:
        img_ref = display.imageNew(image, Display.BGRA, camera.getWidth(), camera.getHeight())
        display.imagePaste(img_ref, 0, 0, False)
        display.imageDelete(img_ref)
    