# ============================================================================
#  Sonar Visual — tela de sonar para o Radar Ultrassônico (Arduino)
#
#  Como usar:
#    python sonar_visual.py            -> tenta a porta padrão
#    python sonar_visual.py COM3       -> usa a porta COM3 (Windows)
#    python sonar_visual.py sim        -> modo simulação (sem Arduino)
#
#  Precisa de: pygame e pyserial  ->  pip install -r requirements.txt
# ============================================================================

import sys
import math
import random
import pygame

# ----- Configuração ----------------------------------------------------------
PORTA_PADRAO     = "COM9"
VELOCIDADE       = 9600
DISTANCIA_MAX    = 100
DISTANCIA_ALERTA = 50
LARGURA, ALTURA  = 900, 620

# ----- Cores -----------------------------------------------------------------
COR_FUNDO     = (2, 10, 6)
COR_GRADE     = (0, 80, 42)
COR_GRADE_DIM = (0, 45, 24)
COR_ANEL_EXT  = (0, 160, 80)
COR_VARREDURA = (60, 255, 130)
COR_TEXTO     = (100, 255, 160)
COR_TEXTO_DIM = (35, 110, 65)
COR_OBJETO    = (255, 50, 50)
COR_ALERTA    = (255, 90, 90)

# ----- Geometria (igual ao original) -----------------------------------------
CX   = LARGURA // 2
CY   = ALTURA - 80
RAIO = min(CX - 40, CY - 40)


# ---------- Pré-renderiza a grade (só uma vez) --------------------------------
def build_grade(fonte_xs):
    surf = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    # anéis
    for cm in range(25, DISTANCIA_MAX + 1, 25):
        r = int((cm / DISTANCIA_MAX) * RAIO)
        bright = cm == DISTANCIA_MAX
        cor = COR_ANEL_EXT if bright else COR_GRADE
        esp = 2 if bright else 1
        pygame.draw.arc(surf, cor, (CX - r, CY - r, r * 2, r * 2), 0, math.pi, esp)
        # rótulo de distância
        txt = fonte_xs.render(f"{cm}cm", True, COR_TEXTO_DIM)
        surf.blit(txt, (CX + 5, CY - r - 14))

    # linhas de ângulo principais (a cada 30°)
    for ang in range(0, 181, 30):
        fim = _ponto(ang, DISTANCIA_MAX)
        pygame.draw.line(surf, COR_GRADE, (CX, CY), fim, 1)
        # rótulo de ângulo
        px, py = _ponto(ang, DISTANCIA_MAX + 10)
        txt = fonte_xs.render(f"{ang}°", True, COR_TEXTO_DIM)
        surf.blit(txt, txt.get_rect(center=(px, py)))

    # marcações finas a cada 10°
    for ang in range(0, 181, 10):
        if ang % 30 == 0:
            continue
        fim = _ponto(ang, DISTANCIA_MAX)
        pre = _ponto(ang, DISTANCIA_MAX - 7)
        pygame.draw.line(surf, COR_GRADE_DIM, pre, fim, 1)

    # linha de base
    pygame.draw.line(surf, COR_ANEL_EXT,
                     _ponto(0, DISTANCIA_MAX), _ponto(180, DISTANCIA_MAX), 2)

    # ponto central
    pygame.draw.circle(surf, COR_ANEL_EXT, (CX, CY), 5)
    pygame.draw.circle(surf, COR_FUNDO,    (CX, CY), 2)

    return surf


def _ponto(angulo, distancia):
    r   = (distancia / DISTANCIA_MAX) * RAIO
    rad = math.radians(angulo)
    return int(CX + r * math.cos(rad)), int(CY - r * math.sin(rad))


# Alias público
def ponto_no_radar(angulo, distancia):
    return _ponto(angulo, distancia)


# ---------- Varredura com glow ------------------------------------------------
_CAUDA_GRAUS = 50   # quantos graus de rastro atrás do feixe

def desenha_varredura(tela, historico):
    if not historico:
        return

    ang_atual = historico[-1]
    camada    = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    # Fatia preenchida: vários triângulos finos cobrindo a cauda
    # Cada triângulo vai do centro até dois pontos consecutivos no arco
    passos = 60                         # suavidade da fatia
    for i in range(passos):
        t   = i / passos                # 0 = cauda apagada, 1 = feixe brilhante
        ang = ang_atual - _CAUDA_GRAUS * (1 - t)
        ang_prox = ang_atual - _CAUDA_GRAUS * (1 - (i + 1) / passos)

        if ang < 0 or ang_prox > 180:   # fora do semicírculo
            continue

        p1 = _ponto(max(0, min(180, ang)),      DISTANCIA_MAX)
        p2 = _ponto(max(0, min(180, ang_prox)), DISTANCIA_MAX)

        alfa = int(90 * (t ** 1.8))     # curva de potência: sobe rápido perto do feixe
        pygame.draw.polygon(camada, (*COR_VARREDURA, alfa),
                            [(CX, CY), p1, p2])

    tela.blit(camada, (0, 0))

    # Linha do feixe atual: glow largo + linha fina brilhante
    fim = _ponto(ang_atual, DISTANCIA_MAX)
    glow = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    pygame.draw.line(glow, (*COR_VARREDURA, 40), (CX, CY), fim, 10)
    pygame.draw.line(glow, (*COR_VARREDURA, 80), (CX, CY), fim, 5)
    tela.blit(glow, (0, 0))
    pygame.draw.line(tela, COR_VARREDURA,      (CX, CY), fim, 2)
    pygame.draw.line(tela, (220, 255, 235),    (CX, CY), fim, 1)


# ---------- Objetos detectados -----------------------------------------------
def desenha_objetos(tela, objetos, agora):
    if not objetos:
        return

    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    for obj in objetos:
        vida = 1.0 - (agora - obj["tempo"]) / 3000
        if vida <= 0:
            continue
        x, y = _ponto(obj["angulo"], obj["distancia"])

        # pulse: raio externo oscila
        pulso = 1 + 0.3 * math.sin((agora - obj["tempo"]) * 0.006)
        for r, a in ((int(20 * pulso), 18), (13, 55), (8, 120)):
            pygame.draw.circle(camada, (*COR_OBJETO, int(a * vida)), (x, y), r)

        # núcleo brilhante
        pygame.draw.circle(camada, (255, 210, 210, int(255 * vida)), (x, y), 4)

    tela.blit(camada, (0, 0))


# ---------- Painel de texto (mesmo posicionamento do original) ---------------
def desenha_painel(tela, fonte_g, fonte_m, fonte_sm,
                   angulo, distancia, detectou, agora):
    # título
    titulo = fonte_g.render("SONAR ULTRASSONICO", True, COR_TEXTO)
    tela.blit(titulo, (20, 14))

    # dados
    for i, linha in enumerate([
        f"Angulo:    {angulo:>3} °",
        f"Distancia: {distancia:>5.1f} cm" if distancia > 0 else "Distancia:    ---",
        f"Alerta:  < {DISTANCIA_ALERTA} cm",
    ]):
        tela.blit(fonte_sm.render(linha, True, COR_TEXTO), (20, 54 + i * 22))

    # status central embaixo — pisca quando detecta
    if detectou and (agora // 400) % 2 == 0:
        aviso = fonte_m.render("!! OBJETO DETECTADO !!", True, COR_OBJETO)
    else:
        aviso = fonte_m.render("area livre", True, COR_GRADE)
    tela.blit(aviso, aviso.get_rect(center=(CX, ALTURA - 28)))


# ---------- Overlay de scanlines (efeito monitor antigo) ---------------------
def build_scanlines():
    surf = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    for y in range(0, ALTURA, 4):
        pygame.draw.line(surf, (0, 0, 0, 22), (0, y), (LARGURA, y), 1)
    return surf


# ---------- Serial -----------------------------------------------------------
def le_do_arduino(porta, buffer):
    leituras = []
    dados = porta.read(512)
    if dados:
        buffer[0] += dados.decode(errors="ignore")
        while "\n" in buffer[0]:
            linha, buffer[0] = buffer[0].split("\n", 1)
            par = _analisa(linha)
            if par:
                leituras.append(par)
    return leituras


def _analisa(linha):
    try:
        a, d = linha.strip().split(",")
        return int(a), float(d)
    except ValueError:
        return None


def passo_simulacao(estado):
    estado["ang"] += estado["dir"]
    if estado["ang"] >= 180 or estado["ang"] <= 0:
        estado["dir"] *= -1
    ang = estado["ang"]
    distancia = 0.0
    for obj_ang, obj_dist in estado["objetos"]:
        if abs(ang - obj_ang) <= 2:
            distancia = obj_dist + random.uniform(-1.5, 1.5)
    return ang, max(0.0, distancia)


# ---------- Main -------------------------------------------------------------
def main():
    arg  = sys.argv[1] if len(sys.argv) > 1 else PORTA_PADRAO
    porta = None if arg == "sim" else _cria_porta(arg)
    sim = {
        "ang": 0, "dir": 1,
        "objetos": [(40, 30), (90, 65), (135, 22), (65, 45)],
    }

    pygame.init()
    tela    = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Sonar Ultrassonico")
    relogio = pygame.time.Clock()

    fonte_g  = pygame.font.SysFont("consolas", 24, bold=True)
    fonte_m  = pygame.font.SysFont("consolas", 20, bold=True)
    fonte_sm = pygame.font.SysFont("consolas", 16)
    fonte_xs = pygame.font.SysFont("consolas", 13)

    grade     = build_grade(fonte_xs)
    scanlines = build_scanlines()

    historico = []
    objetos   = []
    buffer    = [""]
    angulo, distancia = 0, 0.0

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                rodando = False

        leituras = le_do_arduino(porta, buffer) if porta else [passo_simulacao(sim)]

        agora = pygame.time.get_ticks()
        for ang, dist in leituras:
            angulo, distancia = ang, dist
            historico.append(ang)
            if 0 < dist <= DISTANCIA_ALERTA:
                objetos.append({"angulo": ang, "distancia": dist, "tempo": agora})

        historico = historico[-70:]
        objetos   = [o for o in objetos if agora - o["tempo"] < 3000]
        detectou  = 0 < distancia <= DISTANCIA_ALERTA

        tela.fill(COR_FUNDO)
        tela.blit(grade, (0, 0))
        desenha_varredura(tela, historico)
        desenha_objetos(tela, objetos, agora)
        desenha_painel(tela, fonte_g, fonte_m, fonte_sm, angulo, distancia, detectou, agora)
        tela.blit(scanlines, (0, 0))

        pygame.display.flip()
        relogio.tick(60)

    if porta:
        porta.close()
    pygame.quit()


def _cria_porta(nome_porta):
    try:
        import serial
        porta = serial.Serial(nome_porta, VELOCIDADE, timeout=0)
        print(f"Conectado ao Arduino em {nome_porta}.")
        return porta
    except Exception as erro:
        print(f"Nao foi possivel abrir {nome_porta} ({erro}).")
        print("Entrando em modo de simulacao.")
        return None


if __name__ == "__main__":
    main()
