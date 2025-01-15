import game_objects
from game_objects.game_objects import Player, Enemy, Background, Decorations
import pygame
import random


def play(plane_data, player_data):  # босс-вертолет
    pygame.init()
    k_shoot = 0
    score = 0
    k_spawn_dec = 0
    size = width, height = 1200, 800
    win_timer = 0
    won = False
    paused = False

    screen = pygame.display.set_mode(size)
    img_path = random.choice(['./data/backgrounds/jungles.png',
                              './data/backgrounds/forest.png',
                              './data/backgrounds/mountains.png'])
    font = pygame.font.Font('./data/fonts/font.ttf', 30)

    enemies = pygame.sprite.Group()
    players = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    player_rockets = pygame.sprite.Group()
    decorations = pygame.sprite.Group()

    boss = game_objects.game_objects.BossHelicopter([random.randint(0, width - 150), 0])
    enemies.add(boss)
    boss_max_health = boss.get_health()
    boss_health = boss.get_health()
    background = Background(img_path, plane_data[5], level_k=0.5)

    player = Player(plane_data, width, height)
    players.add(player)

    running = True
    screen.fill('white')
    fps = 60
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
            elif event.type == pygame.MOUSEBUTTONDOWN and not paused:
                if pygame.mouse.get_pressed()[0]:
                    player.shoot(player_bullets)
                elif pygame.mouse.get_pressed()[2]:
                    player.shoot_rocket(player_rockets)

        if paused:
            pause_text = font.render("Paused - Press P to Resume", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(width // 2, height // 2))
            screen.fill((0, 0, 0))
            screen.blit(pause_text, pause_rect)
            pygame.display.flip()
            clock.tick(fps)
            continue

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
            player.move_up()
        if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
            player.move_down(height)
        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            player.move_left()
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            player.move_right(width)
        if not (key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]):
            player.not_turning(-1)
        if not (key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]):
            player.not_turning(1)

        decor = Decorations(plane_data[5] * 0.4, *[random.randint(0, width - 150), -100], 2)
        if decor.check_collision(decorations) and k_spawn_dec == 20 and decor.check_collision(enemies):
            decorations.add(decor)

        for enemy in enemies:
            boss_health = enemy.get_health()
            enemy.move()
            if k_shoot == 60:
                enemy.shoot(enemy_bullets)
            if enemy.shot(player_bullets, plane_data[7]):
                player.add_bullets()
            enemy.update_animation(enemies)
            if enemy.is_dead():
                score += 1998
                win_timer = 0
                won = True

        for gamer in players:
            gamer.update(players, player_data, plane_data, score)
            gamer.check_plane_collision(enemies)
            gamer.shot(enemy_bullets)

        for rocket in player_rockets:
            rocket.move(-1)
            rocket.update_animation(player_rockets)
            collided = pygame.sprite.spritecollideany(rocket, enemies)
            if collided and not rocket.destroyed:
                rocket.exploded()
                collided.hit(20)

        for bullet in player_bullets:
            bullet.update()

        for enemy_bullet in enemy_bullets:
            enemy_bullet.update(-1)

        for dec in decorations:
            dec.move()

        if won and win_timer >= 120:
            for gamer in players:
                gamer.win(score, players, player_data, plane_data)

        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        health_text = font.render(f'Health: {player.hits}', True, (255, 255, 255))
        bullets_text = font.render(f'Bullets: {player.bullets}', True, (255, 255, 255))
        rockets_text = font.render(f'Rockets: {player.rockets}', True, (255, 255, 255))
        boss_label_text = font.render("Boss kover-vertolet", True, (255, 255, 255))

        bullets_rect = bullets_text.get_rect()
        score_rect = score_text.get_rect()
        health_rect = health_text.get_rect()
        rockets_rect = rockets_text.get_rect()
        boss_label_rect = boss_label_text.get_rect()

        score_rect.center = (width - 100, 50)
        bullets_rect.center = (width - 100, 80)
        rockets_rect.center = (width - 100, 110)
        health_rect.center = (width - 100, 140)
        boss_label_rect.center = (width // 2, 60)

        background.update()
        background.render(screen)
        decorations.draw(screen)
        players.draw(screen)
        enemies.draw(screen)
        enemy_bullets.draw(screen)
        player_bullets.draw(screen)
        player_rockets.draw(screen)
        screen.blit(score_text, score_rect)
        screen.blit(bullets_text, bullets_rect)
        screen.blit(health_text, health_rect)
        screen.blit(rockets_text, rockets_rect)
        screen.blit(boss_label_text, boss_label_rect)

        boss_health_width = int((boss_health / boss_max_health) * 400)
        pygame.draw.rect(screen, (255, 0, 0), (width // 2 - (boss_max_health // 2),
                                               20, boss_health_width, 20))
        pygame.draw.rect(screen, (255, 255, 255), (width // 2 - (boss_max_health // 2),
                                                   20, boss_max_health, 20), 2)

        clock.tick(fps)
        win_timer += 1
        k_shoot = (k_shoot + 1) % 61
        k_spawn_dec = (k_spawn_dec + 1) % 21
        pygame.display.flip()
    pygame.quit()
