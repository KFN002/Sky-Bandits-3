from game_objects.game_objects import Player, Enemy, Background, Decorations
import pygame
import random


def play(plane_data, player_data):  # аналогично 1 уровню, но с вражескими самолетами
    pygame.init()
    k_spawn = 0
    k_shoot = 0
    score = 0
    k_spawn_dec = 0
    size = width, height = 1200, 800

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

    background = Background(img_path, plane_data[5], level_k=0.5)

    player = Player(plane_data, width, height)
    players.add(player)

    running = True
    screen.fill('white')
    fps = 60
    clock = pygame.time.Clock()

    while running:
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

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    player.shoot(player_bullets)
                elif pygame.mouse.get_pressed()[2]:
                    player.shoot_rocket(player_rockets)

            if event.type == pygame.QUIT:
                running = False

        enemy = Enemy([random.randint(0, width - 150), -100])
        if enemy.check_collision(enemies) and k_spawn == 80:
            enemies.add(enemy)

        decor = Decorations(plane_data[5] * 0.4, *[random.randint(0, width - 150), -100], 2)
        if decor.check_collision(decorations) and k_spawn_dec == 20 and decor.check_collision(enemies):
            decorations.add(decor)

        for enemy in enemies:
            enemy.move()
            if k_shoot == 60:
                enemy.shoot(enemy_bullets)
            if enemy.shot(player_bullets, plane_data[7]):
                score += 1
                player.add_bullets()
            if enemy.shot(player_rockets, 100):
                score += 1
            enemy.update_animation(enemies)

        for gamer in players:
            gamer.update(players, player_data, plane_data, score)
            gamer.check_collision(enemies)
            gamer.shot(enemy_bullets)

        for rocket in player_rockets:
            rocket.move(-1)
            rocket.update_animation(player_rockets)
            if not rocket.check_collision(enemies) and not rocket.destroyed:
                rocket.exploded()

        for bullet in player_bullets:
            bullet.update()

        for enemy_bullet in enemy_bullets:
            enemy_bullet.update(-1)

        for dec in decorations:
            dec.move()

        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        health_text = font.render(f'Health: {player.hits}', True, (255, 255, 255))
        bullets_text = font.render(f'Bullets: {player.bullets}', True, (255, 255, 255))
        rockets_text = font.render(f'Rockets: {player.rockets}', True, (255, 255, 255))

        bullets_rect = bullets_text.get_rect()
        score_rect = score_text.get_rect()
        health_rect = health_text.get_rect()
        rockets_rect = rockets_text.get_rect()

        score_rect.center = (width - 100, 50)
        bullets_rect.center = (width - 100, 80)
        rockets_rect.center = (width - 100, 110)
        health_rect.center = (width - 100, 140)

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

        clock.tick(fps)
        k_spawn = (k_spawn + 1) % 81
        k_shoot = (k_shoot + 1) % 61
        k_spawn_dec = (k_spawn_dec + 1) % 21
        pygame.display.flip()
    pygame.quit()
