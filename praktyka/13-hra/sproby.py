"""Робота 13, крок 1: перевірка передбачень. Вікно не відкривається — усе рахується «в памʼяті».

Запускайте ТІЛЬКИ після того, як записали передбачення в peredbachennia.md:
    python praktyka/13-hra/sproby.py
"""
import os
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

pygame.init()
ekran = pygame.display.set_mode((200, 100))

# A — без fill
for i in range(3):
    pygame.draw.rect(ekran, (255, 0, 0), pygame.Rect(i * 50, 30, 40, 40))
    pygame.display.flip()
chervonykh = sum(1 for x in range(200) for y in range(100) if ekran.get_at((x, y))[:3] == (255, 0, 0))
print("A  квадрат 40×40 тричі зсунули на 50 px, fill не викликали")
print(f"   → червоних пікселів на екрані: {chervonykh} (один квадрат — 1600)\n")

# B — tick(10)
hodynnyk = pygame.time.Clock()
t, kadriv = time.perf_counter(), 0
while time.perf_counter() - t < 1:
    hodynnyk.tick(10)
    kadriv += 1
print("B  цикл з hodynnyk.tick(10), рахуємо проходи за 1 секунду")
print(f"   → проходів: {kadriv}\n")

# C — дотик
a, b = pygame.Rect(0, 0, 40, 40), pygame.Rect(40, 0, 40, 40)
print("C  Rect(0, 0, 40, 40).colliderect(Rect(40, 0, 40, 40)) — квадрати стоять впритул")
print(f"   → {a.colliderect(b)}\n")

# D — півпікселя
r = pygame.Rect(0, 0, 40, 40)
for _ in range(10):
    r.x += 0.5
print("D  десять разів rect.x += 0.5")
print(f"   → rect.x = {r.x}\n")

# E — вісь y
r = pygame.Rect(100, 100, 40, 40)
r.y -= 5
print("E  rect.y -= 5 — квадрат рухається вгору чи вниз?")
print(f"   → y був 100, став {r.y}; верх екрана — y = 0\n")
pygame.quit()
