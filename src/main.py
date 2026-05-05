import machine
import time

PIR_PIN = 16
BUZZER_PIN = 22
SDA_PIN = 20
SCL_PIN = 21
DS1307_ADDR = 0x68
LED_R = 10
LED_G = 11
LED_B = 12

ALARME_INICIO = 18
ALARME_FIM = 6

led_r = machine.Pin(LED_R, machine.Pin.OUT)
led_g = machine.Pin(LED_G, machine.Pin.OUT)
led_b = machine.Pin(LED_B, machine.Pin.OUT)

pir = machine.Pin(PIR_PIN, machine.Pin.IN)
buzzer = machine.Pin(BUZZER_PIN, machine.Pin.OUT)

i2c = machine.I2C(0, sda=machine.Pin(SDA_PIN), scl=machine.Pin(SCL_PIN), freq=100000)

# Estados do alarme
INATIVO = 0
ATIVO = 1
DISPARADO = 2

estado_atual = INATIVO
ultimo_log = time.ticks_ms()
inicio_disparo = 0
buzzer_ligado = False

def set_cor(r, g, b):
    # LED ânodo comum: 0 liga, 1 desliga
    led_r.value(r)
    led_g.value(g)
    led_b.value(b)

def bcd_to_dec(val):
    return ((val // 16) * 10) + (val % 16)

def ler_hora():
    try:
        dados = i2c.readfrom_mem(DS1307_ADDR, 0x00, 3)
        segundo = bcd_to_dec(dados[0] & 0x7F)
        minuto = bcd_to_dec(dados[1])
        hora = bcd_to_dec(dados[2] & 0x3F)
        return hora, minuto, segundo
    except OSError:
        return 0, 0, 0

def alarme_deve_estar_ativo(hora):
    if ALARME_INICIO < ALARME_FIM:
        return ALARME_INICIO <= hora < ALARME_FIM
    return hora >= ALARME_INICIO or hora < ALARME_FIM

print("Sistema configurado!")

while True:
    agora = time.ticks_ms()
    hora, min, seg = ler_hora()
    
    deve_ativar = alarme_deve_estar_ativo(hora)
    
    # Atualiza o estado com base no horário
    if not deve_ativar:
        estado_atual = INATIVO
    elif estado_atual == INATIVO and deve_ativar:
        estado_atual = ATIVO
        
    if estado_atual == INATIVO:
        set_cor(0, 1, 1) # vermelho
        
        # loga a cada 1 segundo pra não floodar o terminal
        if time.ticks_diff(agora, ultimo_log) >= 1000:
            print(f"{hora:02d}:{min:02d}:{seg:02d} - Alarme desativado")
            ultimo_log = agora
            
    elif estado_atual == ATIVO:
        set_cor(1, 0, 1) # verde
        
        if pir.value() == 1:
            estado_atual = DISPARADO
            inicio_disparo = agora
            buzzer.value(1)
            buzzer_ligado = True
            print(f"Alerta! Movimento as {hora:02d}:{min:02d}:{seg:02d}")
            
    elif estado_atual == DISPARADO:
        set_cor(1, 0, 1) # mantém verde
        
        tempo_disparo = time.ticks_diff(agora, inicio_disparo)
        
        # desliga o som depois de 500ms
        if buzzer_ligado and tempo_disparo >= 500:
            buzzer.value(0)
            buzzer_ligado = False
            
        # volta a vigiar depois de 2 segundos (cooldown)
        if tempo_disparo >= 2000:
            estado_atual = ATIVO
            
    time.sleep_ms(10)