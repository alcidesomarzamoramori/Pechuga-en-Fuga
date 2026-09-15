# -*- coding: utf-8 -*-
"""
PECHUGA EN FUGA
Un juego estilo Flappy Bird donde un pollito debe escapar
de un horno esquivando el fuego y el carbón.

Controles:
  ESPACIO o CLICK -> saltar / iniciar / reintentar
  ESC             -> salir
"""

import pygame
import random
import sys

pygame.init()

# --------------------- CONFIGURACIÓN GENERAL ----------------------
ANCHO, ALTO = 400, 650
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pechuga en fuga")
RELOJ = pygame.time.Clock()
FPS = 60

FUENTE_GRANDE = pygame.font.SysFont("arialblack", 38)
FUENTE_MEDIA = pygame.font.SysFont("arial", 24, bold=True)
FUENTE_CHICA = pygame.font.SysFont("arial", 18)

# Colores
NEGRO = (20, 15, 15)
BLANCO = (255, 255, 255)
AMARILLO = (255, 200, 40)
AMARILLO_ALA = (230, 170, 30)
NARANJA = (255, 120, 20)
ROJO = (210, 40, 20)
ROJO_OSCURO = (110, 20, 10)
GRIS_CARBON = (45, 45, 48)
GRIS_CARBON_OSCURO = (25, 25, 27)
GRIS_METAL = (90, 90, 95)

GRAVEDAD = 0.45
FUERZA_SALTO = -8.2
VELOCIDAD_INICIAL = 3.2
VELOCIDAD_MAXIMA = 7.5
HUECO = 165           # espacio vertical entre el obstáculo de arriba y el de abajo
ANCHO_OBST = 70
MARGEN_HUECO = 70
ALTO_PISO = 60
INTERVALO_SPAWN = 95  # frames entre obstáculos


# --------------------- EL POLLO (JUGADOR) ----------------------
class Pollo:
    def __init__(self):
        self.x = ANCHO * 0.28
        self.y = ALTO / 2
        self.vel = 0
        self.ancho = 48
        self.alto = 40
        self.angulo = 0
        self.superficie = self._crear_superficie()

    def _crear_superficie(self):
        """Dibuja al pollito sobre una superficie transparente."""
        surf = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        # Cuerpo
        pygame.draw.ellipse(surf, AMARILLO, (4, 14, 30, 22))
        # Ala
        pygame.draw.ellipse(surf, AMARILLO_ALA, (8, 20, 16, 12))
        # Cabeza
        pygame.draw.circle(surf, AMARILLO, (32, 16), 10)
        # Cresta
        pygame.draw.polygon(surf, ROJO, [(26, 10), (29, 2), (32, 10)])
        pygame.draw.polygon(surf, ROJO, [(30, 9), (34, 1), (36, 10)])
        # Pico
        pygame.draw.polygon(surf, NARANJA, [(40, 14), (47, 17), (40, 20)])
        # Ojo
        pygame.draw.circle(surf, NEGRO, (35, 14), 2)
        return surf

    def saltar(self):
        self.vel = FUERZA_SALTO

    def actualizar(self):
        self.vel += GRAVEDAD
        self.y += self.vel
        self.angulo = max(-30, min(90, -self.vel * 4))

    def dibujar(self, ventana):
        rotada = pygame.transform.rotate(self.superficie, self.angulo)
        rect = rotada.get_rect(center=(self.x, self.y))
        ventana.blit(rotada, rect.topleft)

    def obtener_hitbox(self):
        return pygame.Rect(int(self.x - 14), int(self.y - 12), 28, 24)


# --------------------- OBSTÁCULOS: FUEGO Y CARBÓN ----------------------
class Obstaculo:
    def __init__(self, x):
        self.x = x
        self.tipo = random.choice(["fuego", "carbon"])
        self.y_hueco = random.randint(
            MARGEN_HUECO + HUECO // 2,
            ALTO - MARGEN_HUECO - HUECO // 2 - ALTO_PISO,
        )
        self.ancho = ANCHO_OBST
        self.ya_puntuo = False

    @property
    def alto_superior(self):
        return self.y_hueco - HUECO // 2

    @property
    def y_inferior(self):
        return self.y_hueco + HUECO // 2

    def actualizar(self, velocidad):
        self.x -= velocidad

    def fuera_de_pantalla(self):
        return self.x + self.ancho < 0

    def obtener_hitboxes(self):
        superior = pygame.Rect(int(self.x), 0, self.ancho, int(self.alto_superior))
        inferior = pygame.Rect(
            int(self.x), int(self.y_inferior), self.ancho,
            int(ALTO - self.y_inferior - ALTO_PISO),
        )
        return superior, inferior

    def dibujar(self, ventana):
        superior, inferior = self.obtener_hitboxes()
        if self.tipo == "fuego":
            self._dibujar_fuego(ventana, superior, inferior)
        else:
            self._dibujar_carbon(ventana, superior, inferior)

    def _dibujar_fuego(self, ventana, superior, inferior):
        pygame.draw.rect(ventana, ROJO_OSCURO, superior)
        pygame.draw.rect(ventana, ROJO_OSCURO, inferior)
        # Llamas colgando desde el bloque de arriba
        for i in range(0, self.ancho - 10, 14):
            h = random.randint(10, 22)
            puntos = [
                (self.x + i, superior.height),
                (self.x + i + 7, superior.height - h),
                (self.x + i + 14, superior.height),
            ]
            pygame.draw.polygon(ventana, NARANJA, puntos)
        # Llamas subiendo desde el bloque de abajo
        for i in range(0, self.ancho - 10, 14):
            h = random.randint(10, 22)
            puntos = [
                (self.x + i, inferior.y),
                (self.x + i + 7, inferior.y + h),
                (self.x + i + 14, inferior.y),
            ]
            pygame.draw.polygon(ventana, AMARILLO, puntos)

    def _dibujar_carbon(self, ventana, superior, inferior):
        pygame.draw.rect(ventana, GRIS_METAL, superior)
        pygame.draw.rect(ventana, GRIS_METAL, inferior)
        for i in range(6, self.ancho - 6, 16):
            cx = int(self.x + i)
            cy = int(superior.height - 10)
            pygame.draw.circle(ventana, GRIS_CARBON, (cx, cy), 9)
            pygame.draw.circle(ventana, GRIS_CARBON_OSCURO, (cx, cy), 9, 2)
        for i in range(6, self.ancho - 6, 16):
            cx = int(self.x + i)
            cy = int(inferior.y + 10)
            pygame.draw.circle(ventana, GRIS_CARBON, (cx, cy), 9)
            pygame.draw.circle(ventana, GRIS_CARBON_OSCURO, (cx, cy), 9, 2)


# --------------------- FONDO: EL HORNO ----------------------
def dibujar_fondo(ventana, frame):
    for y in range(0, ALTO, 2):
        proporcion = y / ALTO
        r = int(70 + 90 * (1 - proporcion))
        g = int(20 + 30 * (1 - proporcion))
        b = 15
        pygame.draw.line(ventana, (r, g, b), (0, y), (ANCHO, y), 2)

    for x in range(0, ANCHO, 50):
        pygame.draw.line(ventana, (50, 25, 15), (x, 0), (x, ALTO), 1)

    # Brasas parpadeantes (usa un generador propio para no alterar
    # la aleatoriedad del resto del juego)
    rng = random.Random(frame // 5)
    for _ in range(10):
        ex = rng.randint(0, ANCHO)
        ey = rng.randint(0, ALTO)
        radio = rng.randint(1, 3)
        pygame.draw.circle(ventana, NARANJA, (ex, ey), radio)


def dibujar_piso(ventana):
    piso = pygame.Rect(0, ALTO - ALTO_PISO, ANCHO, ALTO_PISO)
    pygame.draw.rect(ventana, GRIS_METAL, piso)
    for x in range(0, ANCHO, 20):
        pygame.draw.line(ventana, GRIS_CARBON_OSCURO, (x, ALTO - ALTO_PISO), (x, ALTO), 3)
    for x in range(10, ANCHO, 30):
        pygame.draw.circle(ventana, NARANJA, (x, ALTO - 15), 4)


def texto_centrado(ventana, texto, fuente, color, y, sombra=True):
    if sombra:
        surf_sombra = fuente.render(texto, True, NEGRO)
        rect_sombra = surf_sombra.get_rect(center=(ANCHO // 2 + 2, y + 2))
        ventana.blit(surf_sombra, rect_sombra)
    surf = fuente.render(texto, True, color)
    rect = surf.get_rect(center=(ANCHO // 2, y))
    ventana.blit(surf, rect)


# --------------------- PUNTAJE MÁXIMO (se guarda en un archivo local) ----
def cargar_puntaje_maximo():
    try:
        with open("puntaje_maximo.txt", "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def guardar_puntaje_maximo(puntaje):
    try:
        with open("puntaje_maximo.txt", "w") as f:
            f.write(str(puntaje))
    except Exception:
        pass


# --------------------- BUCLE PRINCIPAL DEL JUEGO ----------------------
def main():
    estado = "menu"  # menu, jugando, fin
    pollo = Pollo()
    obstaculos = []
    puntaje = 0
    puntaje_maximo = cargar_puntaje_maximo()
    velocidad = VELOCIDAD_INICIAL
    frame = 0
    temporizador_spawn = 0

    def reiniciar():
        nonlocal pollo, obstaculos, puntaje, velocidad, temporizador_spawn, estado
        pollo = Pollo()
        obstaculos = []
        puntaje = 0
        velocidad = VELOCIDAD_INICIAL
        temporizador_spawn = 0
        estado = "jugando"

    corriendo = True
    while corriendo:
        frame += 1

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
                if evento.key == pygame.K_SPACE:
                    if estado in ("menu", "fin"):
                        reiniciar()
                    else:
                        pollo.saltar()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if estado in ("menu", "fin"):
                    reiniciar()
                else:
                    pollo.saltar()

        dibujar_fondo(VENTANA, frame)

        if estado == "jugando":
            pollo.actualizar()

            temporizador_spawn += 1
            if temporizador_spawn >= INTERVALO_SPAWN:
                obstaculos.append(Obstaculo(ANCHO + 20))
                temporizador_spawn = 0

            for obs in obstaculos:
                obs.actualizar(velocidad)
            obstaculos = [o for o in obstaculos if not o.fuera_de_pantalla()]

            hitbox_pollo = pollo.obtener_hitbox()
            perdio = False
            for obs in obstaculos:
                superior, inferior = obs.obtener_hitboxes()
                if hitbox_pollo.colliderect(superior) or hitbox_pollo.colliderect(inferior):
                    perdio = True
                if not obs.ya_puntuo and obs.x + obs.ancho < pollo.x:
                    obs.ya_puntuo = True
                    puntaje += 1
                    velocidad = min(velocidad + 0.12, VELOCIDAD_MAXIMA)

            if pollo.y - 12 < 0 or pollo.y + 12 > ALTO - ALTO_PISO:
                perdio = True

            if perdio:
                estado = "fin"
                if puntaje > puntaje_maximo:
                    puntaje_maximo = puntaje
                    guardar_puntaje_maximo(puntaje_maximo)

        for obs in obstaculos:
            obs.dibujar(VENTANA)
        dibujar_piso(VENTANA)
        pollo.dibujar(VENTANA)

        if estado == "menu":
            texto_centrado(VENTANA, "PECHUGA EN FUGA", FUENTE_GRANDE, AMARILLO, 150)
            texto_centrado(VENTANA, "Presiona ESPACIO o CLICK", FUENTE_MEDIA, BLANCO, 380)
            texto_centrado(VENTANA, "para escapar del horno", FUENTE_MEDIA, BLANCO, 410)
            texto_centrado(VENTANA, "Esquiva el fuego y el carbon", FUENTE_CHICA, BLANCO, 460)
        elif estado == "jugando":
            texto_centrado(VENTANA, str(puntaje), FUENTE_GRANDE, BLANCO, 60)
        elif estado == "fin":
            texto_centrado(VENTANA, "TE ASASTE!", FUENTE_GRANDE, ROJO, 180)
            texto_centrado(VENTANA, f"Puntaje: {puntaje}", FUENTE_MEDIA, BLANCO, 250)
            texto_centrado(VENTANA, f"Mejor puntaje: {puntaje_maximo}", FUENTE_MEDIA, AMARILLO, 285)
            texto_centrado(VENTANA, "Presiona ESPACIO para reintentar", FUENTE_CHICA, BLANCO, 340)

        pygame.display.flip()
        RELOJ.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
