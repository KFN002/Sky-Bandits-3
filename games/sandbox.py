from game_objects.game_objects import Player, EnemyBase, AARocket, Decorations, Background
import pygame
import random


def play(plane_data, player_data):
    pygame.init()
    k_spawn = 0
    k_spawn_dec_b = 0
    k_spawn_dec_t = 0
    score = 0
    size = width, height = 1200, 800

    screen = pygame.display.set_mode(size)
    img_path = random.choice(['./data/backgrounds/jungles.png',
                              './data/backgrounds/forest.png',
                              './data/backgrounds/mountains.png'])
    font = pygame.font.Font('./data/fonts/font.ttf', 30)

    enemies = pygame.sprite.Group()
    players = pygame.sprite.Group()
    decorations = pygame.sprite.Group()
    bombs = pygame.sprite.Group()

    background = Background(img_path, plane_data[5])
    player = Player(plane_data, width, height)
    players.add(player)

    running = True
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
                    player.drop_bomb(bombs)

            if event.type == pygame.QUIT:
                running = False

        enemy_base = EnemyBase(plane_data[5], [random.randint(0, width - 150), -100])
        if enemy_base.check_collision(enemies) and k_spawn == 10 and enemy_base.check_collision(decorations):
            enemies.add(enemy_base)

        decor_b = Decorations(plane_data[5], *[random.randint(0, width - 150), -100])
        if decor_b.check_collision(decorations) and k_spawn_dec_b == 30 and decor_b.check_collision(enemies):
            decorations.add(decor_b)

        decor_t = Decorations(plane_data[5], *[random.randint(0, width - 150), -100], dec_type=2)
        if decor_t.check_collision(decorations) and k_spawn_dec_t == 10 and decor_t.check_collision(enemies):
            decorations.add(decor_t)

        for dec in decorations:
            dec.move()
            dec.update(bombs)

        for enemy in enemies:
            enemy.move()
            if enemy.bombed(bombs):
                score += 1
                player.add_bombs()
            enemy.update_animation(enemies)

        for bmb in bombs:
            bmb.update(bombs)

        for gamer in players:
            gamer.update(players, player_data, plane_data, score)

        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        bomb_text = font.render(f'Bombs: {player.bombs}', True, (255, 255, 255))
        health_text = font.render(f'Health: {player.hits}', True, (255, 255, 255))

        score_rect = score_text.get_rect()
        bomb_rect = bomb_text.get_rect()
        health_rect = health_text.get_rect()

        health_rect.center = (width - 100, 110)
        bomb_rect.center = (width - 100, 80)
        score_rect.center = (width - 100, 50)

        background.update()
        background.render(screen)

        decorations.draw(screen)
        enemies.draw(screen)
        bombs.draw(screen)
        players.draw(screen)

        screen.blit(score_text, score_rect)
        screen.blit(bomb_text, bomb_rect)
        screen.blit(health_text, health_rect)

        pygame.display.flip()
        clock.tick(fps)
        k_spawn = (k_spawn + 1) % 11
        k_spawn_dec_t = (k_spawn_dec_t + 1) % 11
        k_spawn_dec_b = (k_spawn_dec_b + 1) % 31

    pygame.quit()
