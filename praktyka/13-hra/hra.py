"""Робота 13: заготовка гри. Цикл кадрів уже крутиться — додайте гравця, ворога, зіткнення й рахунок.

Потрібен pygame-ce:  python -m pip install pygame-ce
Запуск:     python praktyka/13-hra/hra.py
Перевірка:  python praktyka/13-hra/perevir.py
"""
import pygame

SHYRYNA, VYSOTA = 640, 480

pygame.init()
ekran = pygame.display.set_mode((SHYRYNA, VYSOTA))
pygame.display.set_caption("Моя гра")
hodynnyk = pygame.time.Clock()
shryft = pygame.font.SysFont("arial", 24)

# ← гравець: pygame.Rect(…)
# ← обʼєкт, що рухається сам, і його швидкість
# ← рахунок або життя

pratsiuie = True
while pratsiuie:
    # 1. ввід
    for podiia in pygame.event.get():
        if podiia.type == pygame.QUIT:
            pratsiuie = False
    # ← клавіші: pygame.key.get_pressed()

    # 2. оновити стан: рух обʼєкта, межі екрана, зіткнення й наслідок

    # 3. намалювати кадр
    ekran.fill((30, 30, 40))
    # ← гравець, обʼєкт, текст із рахунком: ekran.blit(shryft.render(…), (10, 10))
    pygame.display.flip()

    # 4. темп
    hodynnyk.tick(60)

pygame.quit()
