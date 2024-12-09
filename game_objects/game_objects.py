import os
import random
import pygame
from pygame import mixer
from utils import data_master
from random import choice
import threading

cwd = os.getcwd()
enemy_map = {"enemy_1.png": {"health": 6, "speed": 3},
             "enemy_2.png": {"health": 5, "speed": 3},
             "enemy_3.png": {"health": 5, "speed": 3},
             "enemy_4.png": {"health": 5, "speed": 4},
             "enemy_5.png": {"health": 3, "speed": 3}}


class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, frames, speed):
        pygame.sprite.Sprite.__init__(self)
        self.frames = frames
        self.cur_frame = 0
        self.image = frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.speed = speed
        self.destroyed = False

    def update_animation(self, group):
        if self.cur_frame < len(self.frames) - 1 and self.destroyed:
            self.cur_frame += 1
            self.image = self.frames[self.cur_frame]
        elif self.destroyed:
            group.remove(self)
            self.sound.set_volume(0.5)
            self.sound.play()

    def move(self, vector=1):
        self.rect.y += self.speed * vector

    def check_collision(self, objects):
        if not pygame.sprite.spritecollideany(self, objects):
            return True
        return False


class Player(BasicSprite):
    def __init__(self, plane_data, width, height):
        self.plane_images = [(os.path.join(cwd, 'data', 'planes', f"{i}", plane_data[2])) for i in
                             range(7)]

        self.neutral_frame = pygame.image.load(self.plane_images[0])
        self.right_frames = [pygame.image.load(img) for img in self.plane_images[1:4]]
        self.left_frames = [pygame.image.load(img) for img in self.plane_images[4:]]

        BasicSprite.__init__(self,
                             [pygame.image.load(os.path.join(cwd, 'data', 'planes', '0', plane_data[2]))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))],
                             plane_data[5])

        self.bullets = plane_data[9]
        self.bombs = int(plane_data[8])
        self.rockets = int(plane_data[10])
        self.hits = int(plane_data[6])
        self.explosion = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))
        self.explosion.set_volume(0.5)
        self.down = False
        self.exploding = False
        self.turning_r = 0
        self.turning_l = 0
        self.rect.x = int(width * 0.5)
        self.rect.y = int(height * 0.5)

    def move_up(self):
        if self.rect.y <= 0:
            self.rect.y = 0
        else:
            self.rect.y -= self.speed

    def move_down(self, height):
        if self.rect.y >= height - self.rect.height:
            self.rect.y = height - self.rect.height
        else:
            self.rect.y += self.speed

    def move_left(self):
        if self.rect.x <= 0:
            self.rect.x = 0
        else:
            self.rect.x -= self.speed
            self.turning_r = 0
            self.turning_l += 1
            self.update_on_turn()

    def move_right(self, width):
        if self.rect.x >= width - self.rect.width:
            self.rect.x = width - self.rect.width
        else:
            self.rect.x += self.speed
            self.turning_l = 0
            self.turning_r += 1
            self.update_on_turn()

    def update(self, group, player_data, plane_data, score):
        if self.down and self.cur_frame < len(self.frames) - 1 and self.exploding:
            self.turning_r = 0
            self.turning_l = 0
            self.cur_frame += 1
            self.image = self.frames[self.cur_frame]
        elif self.down:
            self.exploding = False
            group.remove(self)
        if self.down and not self.exploding:
            group.remove(self)
            mixer.stop()

            add_points = threading.Thread(target=data_master.change_score_money(player_data, int(int(plane_data[11])
                                                                                                 * score)))
            add_points.start()
            _, user_data = data_master.check_player(player_data[0], player_data[1])
            data_master.show_info(user_data)

    def update_on_turn(self):
        if self.turning_r > 0:
            self.image = self.right_frames[min(max(self.turning_r - 4, 0) // 4, 2)]
        elif self.turning_l > 0:
            self.image = self.left_frames[min(max(self.turning_l - 4, 0) // 4, 2)]
        else:
            self.image = self.neutral_frame

    def shoot(self, group):
        if self.bullets > 0:
            bullet = Bullet(pygame.image.load(os.path.join(cwd, 'data', 'arms', 'bullet.png')), self.speed,
                            self.rect.midtop)
            group.add(bullet)
            self.bullets -= 1

    def drop_bomb(self, bombs):
        if self.bombs >= 1:
            bmb = Bomb(self.rect.midbottom, self.speed)
            bombs.add(bmb)
            self.bombs -= 1

    def shoot_rocket(self, rockets):
        if self.rockets >= 1:
            rocket = AARocket(self.rect.x + 25, self.rect.midtop[1] - 50)
            rockets.add(rocket)
            rocket.chase()
            self.rockets -= 1

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.hits = 0
            self.down = True
            self.exploding = True
            self.explosion.play()
            mixer.stop()

    def add_bombs(self):
        self.bombs += 1

    def add_bullets(self):
        self.bullets += 1

    def check_collision(self, objects):
        collided = pygame.sprite.spritecollideany(self, objects)
        if collided and not collided.destroyed:
            collided.kill()
            self.hit()

    def check_plane_collision(self, objects):
        collided = pygame.sprite.spritecollideany(self, objects)
        if collided and not collided.destroyed:
            collided.kill()
            self.kill()

    def shot(self, bullets):
        collided = pygame.sprite.spritecollideany(self, bullets)
        if collided:
            bullets.remove(collided)
            self.hit()

    def not_turning(self, vector):
        if self.turning_l > 0 and vector == -1:
            self.turning_l -= 4
            self.update_on_turn()
        if self.turning_r > 0 and vector == 1:
            self.turning_r -= 4
            self.update_on_turn()

    def kill(self):
        self.down = True
        self.exploding = True

    def win(self, score, group, player_data, plane_data):
        group.remove(self)
        mixer.stop()

        add_points = threading.Thread(target=data_master.change_score_money(player_data, int(int(plane_data[11])
                                                                                             * score)))
        add_points.start()
        _, user_data = data_master.check_player(player_data[0], player_data[1])
        data_master.show_info(user_data)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, speed, px):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = int(px[0]) - 10
        self.rect.y = int(px[1])
        self.hit = False
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'bullet.wav'))
        self.sound.set_volume(0.8)
        self.sound.play()

    def update(self, vector=1):
        self.rect.y -= self.speed * 2 * vector


class Bomb(BasicSprite):
    def __init__(self, mid_bottom, speed):
        BasicSprite.__init__(self, [pygame.image.load(os.path.join(cwd, 'data', 'arms', 'bomb.png'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))],
                             speed * 0.5)
        self.rect.x = mid_bottom[0] - 10
        self.rect.y = mid_bottom[1] - 60
        self.size_x = 20
        self.size_y = 36
        self.hit = False
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'bomb.wav'))
        self.explosion = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))
        self.explosion.set_volume(0.5)
        self.sound.set_volume(0.5)
        self.sound.play(1)

    def update(self, group):
        if not self.hit and self.size_x >= 10:
            self.rect.y += self.speed
            self.size_x *= 0.99
            self.size_y *= 0.99
            self.image = pygame.transform.smoothscale(self.image, (int(self.size_x), int(self.size_y)))
        elif not self.hit:
            self.hit = True
            self.explosion.play()
        elif self.hit and self.cur_frame < len(self.frames) - 1:
            self.cur_frame += 1
            self.image = self.frames[self.cur_frame]
        else:
            group.remove(self)


class EnemyBase(BasicSprite):
    def __init__(self, speed, base_pos):
        BasicSprite.__init__(self, [pygame.image.load(os.path.join(cwd, 'data', 'backgrounds', 'enemy_base.png'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))],
                             speed * 0.5)
        self.rect.x = base_pos[0]
        self.rect.y = base_pos[1]
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))

    def bombed(self, bmbs):
        collided = pygame.sprite.spritecollideany(self, bmbs)
        if collided:
            if collided.size_x <= 10:
                collided.sound.stop()
                bmbs.remove(collided)
                self.destroyed = True
                return True
        return False


class AARocket(BasicSprite):
    def __init__(self, x, height, speed=14):
        BasicSprite.__init__(self, [pygame.image.load(os.path.join(cwd, 'data', 'arms', 'aa_rocket.png'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))],
                             speed)
        self.rect.x = x
        self.rect.y = height
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))
        self.sound.set_volume(0.5)

    def chase(self):
        if not self.destroyed:
            start = mixer.Sound(os.path.join(cwd, 'data', 'music', 'missile.wav'))
            start.set_volume(0.4)
            start.play()

    def exploded(self):
        self.destroyed = True


class Enemy(BasicSprite):
    def __init__(self, enemy_pos):
        self.enemy_type = random.choice(
            [f'enemy_{i}.png' for i in range(1, 6)])
        self.health = enemy_map[self.enemy_type]["health"]
        self.speed = enemy_map[self.enemy_type]["speed"]
        BasicSprite.__init__(self, [
            pygame.image.load(os.path.join(cwd, 'data', 'planes', 'enemies', f'{self.enemy_type}'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))], self.speed)
        self.rect.x = enemy_pos[0]
        self.rect.y = enemy_pos[1]
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))

    def shot(self, bullets, damage):
        collided = pygame.sprite.spritecollideany(self, bullets)
        if collided:
            bullets.remove(collided)
            self.health -= damage
            if self.health <= 0:
                self.destroyed = True
                return True
        return False

    def shoot(self, group):
        bullet = Bullet(pygame.image.load(os.path.join(cwd, 'data', 'arms', 'bullet.png')), self.speed,
                        self.rect.midbottom)
        group.add(bullet)

    def kill(self):
        self.destroyed = True


class Decorations(BasicSprite):
    def __init__(self, speed, x, y, level=1, dec_type=1):
        if level == 2:
            decoration = choice([str(i) for i in range(1, 11)])
            frames = [pygame.image.load(os.path.join(cwd, 'data', 'backgrounds', 'clouds', f"{decoration}.png"))] + [
                pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))]
        else:
            if dec_type == 1:
                decoration = choice(['building1', 'building2', 'building3', 'building4', 'building5', 'building6',
                                     'building7'])
                frames = [pygame.image.load(
                    os.path.join(cwd, 'data', 'backgrounds', decoration, 'image1.png'))] + [pygame.image.load(
                    os.path.join(cwd, 'data', 'backgrounds', decoration, 'image4.png'))]
            else:
                decoration = choice([str(i) for i in range(1, 13)])
                frames = [pygame.image.load(os.path.join(cwd, 'data', 'backgrounds', 'trees', f"{decoration}.png"))] + [
                    pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))]

        if level == 1:
            BasicSprite.__init__(self, frames, speed * 0.5)
        elif level == 2:
            BasicSprite.__init__(self, frames, speed * 0.8)

        self.rect.x = x
        self.rect.y = y

    def update(self, bmbs):
        collided = pygame.sprite.spritecollideany(self, bmbs)

        if collided:
            if collided.size_x <= 10:
                collided.sound.stop()
                if self.cur_frame < len(self.frames) - 1:
                    self.cur_frame += 1
        self.image = self.frames[self.cur_frame]


class Background:
    def __init__(self, img, speed, level_k=1):
        self.bgimage = pygame.image.load(os.path.join(cwd, img))
        self.rectBGimg = self.bgimage.get_rect()

        self.bgY1 = 0
        self.bgX1 = 0

        self.bgY2 = -self.rectBGimg.height
        self.bgX2 = 0

        self.moving_speed = int(abs(speed) * 0.5 * level_k)

    def update(self):
        self.bgY1 += self.moving_speed
        self.bgY2 += self.moving_speed
        if self.bgY1 >= self.rectBGimg.height:
            self.bgY1 = -self.rectBGimg.height
        if self.bgY2 >= self.rectBGimg.height:
            self.bgY2 = -self.rectBGimg.height

    def render(self, screen):
        screen.blit(self.bgimage, (self.bgX1, self.bgY1))
        screen.blit(self.bgimage, (self.bgX2, self.bgY2))


class BossHelicopter(pygame.sprite.Sprite):
    def __init__(self, enemy_pos):
        pygame.sprite.Sprite.__init__(self)
        self.normal_frames = [pygame.image.load(os.path.join(cwd, 'data', 'helicopters', 'boss', f"{i}.png")) for i in range(6)]
        self.explosion_frames = [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png'))
                                 for i in range(1, 7)] + \
                                [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))]
        self.current_frame = 0
        self.destroyed = False
        self.exploding = False
        self.speed = 3
        self.vector = random.choice([-1, 1])
        self.health = 400

        self.image = self.normal_frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=enemy_pos)

        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))
        self.sound.set_volume(0.5)

        self.timing = 0
        self.forward = 0

    def update_animation(self, group):
        if self.exploding:
            if self.current_frame < len(self.explosion_frames) - 1:
                self.current_frame += 1
                self.image = self.explosion_frames[self.current_frame]
            else:
                self.destroyed = True
                group.remove(self)
                self.sound.play()
        else:
            self.current_frame = (self.current_frame + 1) % len(self.normal_frames)
            self.image = self.normal_frames[self.current_frame]

    def move(self):
        if 0 <= self.rect.x + self.speed * self.vector <= 1200 - self.rect.width:
            self.rect.x += self.speed * self.vector
        else:
            self.vector *= -1

        self.timing += 1
        if self.timing == 60:
            self.vector = random.choice([-1, 1])
            self.timing = 0

        if self.forward < 30:
            self.rect.y += self.speed
            self.forward += 1

    def check_collision(self, objects):
        return not pygame.sprite.spritecollideany(self, objects)

    def shot(self, bullets, damage):
        collided = pygame.sprite.spritecollideany(self, bullets)
        if collided:
            bullets.remove(collided)
            self.health -= damage
            if self.health <= 0 and not self.exploding:
                self.exploding = True
                self.current_frame = 0
            return True
        return False

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.exploding = True


    def shoot(self, group):
        bullet_image = pygame.image.load(os.path.join(os.getcwd(), 'data', 'arms', 'bullet.png')).convert_alpha()
        bullet = Bullet(bullet_image, self.speed, self.rect.midbottom)
        group.add(bullet)

    def kill(self):
        self.destroyed = True

    def is_dead(self):
        return self.destroyed

    def get_health(self):
        return self.health
