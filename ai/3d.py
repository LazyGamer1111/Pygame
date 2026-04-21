import json
import math
import socket
import sys
import pygame
import numpy as np

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 120
FOV = math.pi / 3
MAX_DEPTH = 20
RAY_STEP = 0.2
COLLISION_BUFFER = 0.2
PORT = 5055

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CEILING = (50, 50, 50)

GAME_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

MAP_WIDTH = len(GAME_MAP[0])
MAP_HEIGHT = len(GAME_MAP)


class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 5.0
        self.rotation_speed = 2.5

    def is_wall(self, x, y):
        if not (0 <= int(x) < MAP_WIDTH and 0 <= int(y) < MAP_HEIGHT):
            return True
        return GAME_MAP[int(y)][int(x)] == 1

    def can_move_to(self, x, y):
        for offset_x in [-COLLISION_BUFFER, 0, COLLISION_BUFFER]:
            for offset_y in [-COLLISION_BUFFER, 0, COLLISION_BUFFER]:
                if self.is_wall(x + offset_x, y + offset_y):
                    return False
        return True

    def handle_input(self, keys, deltatime):
        new_x, new_y = self.x, self.y

        if keys[pygame.K_w]:
            new_x += np.cos(self.angle) * self.speed * deltatime
            new_y += np.sin(self.angle) * self.speed * deltatime
        if keys[pygame.K_s]:
            new_x -= np.cos(self.angle) * self.speed * deltatime
            new_y -= np.sin(self.angle) * self.speed * deltatime

        if keys[pygame.K_a]:
            new_x += np.cos(self.angle - np.pi / 2) * self.speed * deltatime
            new_y += np.sin(self.angle - np.pi / 2) * self.speed * deltatime
        if keys[pygame.K_d]:
            new_x += np.cos(self.angle + np.pi / 2) * self.speed * deltatime
            new_y += np.sin(self.angle + np.pi / 2) * self.speed * deltatime

        if self.can_move_to(new_x, new_y):
            self.x = new_x
            self.y = new_y

        if keys[pygame.K_q]:
            self.angle -= self.rotation_speed * deltatime
        if keys[pygame.K_e]:
            self.angle += self.rotation_speed * deltatime

    def cast_ray(self, angle):
        sin_a = np.sin(angle)
        cos_a = np.cos(angle)
        distance = 0.0

        while distance < MAX_DEPTH:
            distance += RAY_STEP
            x = self.x + cos_a * distance
            y = self.y + sin_a * distance

            if not (0 <= int(x) < MAP_WIDTH and 0 <= int(y) < MAP_HEIGHT):
                return distance
            if GAME_MAP[int(y)][int(x)] == 1:
                return distance

        return MAX_DEPTH

    def render_world(self, screen):
        screen.fill(CEILING)

        for col in range(SCREEN_WIDTH):
            ray_angle = self.angle - FOV / 2 + (col / SCREEN_WIDTH) * FOV
            distance = self.cast_ray(ray_angle)
            distance *= np.cos(self.angle - ray_angle)
            distance = max(distance, 0.1)

            wall_height = min(int(SCREEN_HEIGHT / distance), SCREEN_HEIGHT)
            shade = max(50, 255 - int((distance / MAX_DEPTH) * 200))
            color = (shade, shade, shade)

            wall_top = (SCREEN_HEIGHT - wall_height) // 2
            wall_bottom = wall_top + wall_height

            pygame.draw.line(screen, color, (col, wall_top), (col, wall_bottom), 1)

            if wall_bottom < SCREEN_HEIGHT:
                floor_shade = max(30, 100 - int((distance / MAX_DEPTH) * 80))
                pygame.draw.line(
                    screen,
                    (floor_shade, floor_shade, floor_shade),
                    (col, wall_bottom),
                    (col, SCREEN_HEIGHT),
                    1,
                )


class NetworkSession:
    def __init__(self, is_host, host_ip, port):
        self.is_host = is_host
        self.host_ip = host_ip
        self.port = port
        self.conn = None
        self.server_socket = None
        self.recv_buffer = ""
        self.remote_state = {"x": 12.0, "y": 4.5, "angle": np.pi, "shots": 0}

    def connect(self, screen, clock, font):
        if self.is_host:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(1)
            self.server_socket.setblocking(False)

            connected = False
            while not connected:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return False

                try:
                    self.conn, _addr = self.server_socket.accept()
                    connected = True
                except BlockingIOError:
                    pass

                screen.fill(BLACK)
                t1 = font.render(f"Hosting on port {self.port}", True, GREEN)
                t2 = font.render("Waiting for player... (ESC to cancel)", True, WHITE)
                screen.blit(t1, (40, 200))
                screen.blit(t2, (40, 240))
                pygame.display.flip()
                clock.tick(60)
        else:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.settimeout(0.2)

            connected = False
            while not connected:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return False

                try:
                    self.conn.connect((self.host_ip, self.port))
                    connected = True
                except (TimeoutError, ConnectionRefusedError, OSError):
                    pass

                screen.fill(BLACK)
                t1 = font.render(f"Joining {self.host_ip}:{self.port}", True, BLUE)
                t2 = font.render("Trying to connect... (ESC to cancel)", True, WHITE)
                screen.blit(t1, (40, 200))
                screen.blit(t2, (40, 240))
                pygame.display.flip()
                clock.tick(60)

        self.conn.setblocking(False)
        return True

    def send_state(self, state):
        if not self.conn:
            return
        payload = (json.dumps(state) + "\n").encode("utf-8")
        try:
            self.conn.sendall(payload)
        except OSError:
            pass

    def receive_messages(self):
        if not self.conn:
            return

        while True:
            try:
                data = self.conn.recv(4096)
                if not data:
                    return
                self.recv_buffer += data.decode("utf-8", errors="ignore")
            except BlockingIOError:
                break
            except OSError:
                break

        while "\n" in self.recv_buffer:
            line, self.recv_buffer = self.recv_buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                if isinstance(msg, dict):
                    self.remote_state = msg
            except json.JSONDecodeError:
                continue

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except OSError:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass


def render_remote_player(screen, viewer, remote_state, color):
    dx = remote_state["x"] - viewer.x
    dy = remote_state["y"] - viewer.y
    dist = np.sqrt(dx * dx + dy * dy)

    if dist < 0.1 or dist > MAX_DEPTH:
        return

    angle_to_target = np.arctan2(dy, dx)
    angle_diff = angle_to_target - viewer.angle

    while angle_diff > np.pi:
        angle_diff -= 2 * np.pi
    while angle_diff < -np.pi:
        angle_diff += 2 * np.pi

    if abs(angle_diff) > FOV / 2:
        return

    wall_distance = viewer.cast_ray(angle_to_target)
    if wall_distance + 0.1 < dist:
        return

    col = int(SCREEN_WIDTH / 2 + (angle_diff / (FOV / 2)) * (SCREEN_WIDTH / 2))
    sprite_height = min(int(SCREEN_HEIGHT / dist), SCREEN_HEIGHT)
    top = (SCREEN_HEIGHT - sprite_height) // 2
    sprite_width = max(2, int(SCREEN_WIDTH * 0.22 / (dist + 0.1)))

    pygame.draw.rect(screen, color, (col - sprite_width // 2, top, sprite_width, sprite_height))


def draw_crosshair(screen):
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    pygame.draw.line(screen, WHITE, (cx - 8, cy), (cx + 8, cy), 1)
    pygame.draw.line(screen, WHITE, (cx, cy - 8), (cx, cy + 8), 1)


def menu_screen(screen, clock, font, big_font):
    mode = None
    ip_text = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None

                if mode is None:
                    if event.key == pygame.K_h:
                        return "host", None
                    if event.key == pygame.K_j:
                        mode = "join"
                else:
                    if event.key == pygame.K_RETURN and ip_text.strip():
                        return "join", ip_text.strip()
                    if event.key == pygame.K_BACKSPACE:
                        ip_text = ip_text[:-1]
                    else:
                        ch = event.unicode
                        if ch and (ch.isdigit() or ch == ".") and len(ip_text) < 21:
                            ip_text += ch

        screen.fill(BLACK)
        title = big_font.render("Online Multiplayer", True, YELLOW)
        screen.blit(title, (40, 50))

        if mode is None:
            l1 = font.render("Press H to Host", True, GREEN)
            l2 = font.render("Press J to Join", True, BLUE)
            l3 = font.render("ESC to Exit", True, WHITE)
            screen.blit(l1, (40, 140))
            screen.blit(l2, (40, 180))
            screen.blit(l3, (40, 220))
        else:
            l1 = font.render("Enter Host IP and press ENTER:", True, WHITE)
            box = pygame.Rect(40, 190, 320, 38)
            pygame.draw.rect(screen, WHITE, box, 2)
            l2 = font.render(ip_text or "192.168.1.20", True, BLUE)
            l3 = font.render("ESC to cancel", True, WHITE)
            screen.blit(l1, (40, 150))
            screen.blit(l2, (50, 200))
            screen.blit(l3, (40, 245))

        pygame.display.flip()
        clock.tick(60)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("3D Online Multiplayer")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    big_font = pygame.font.Font(None, 52)

    mode, host_ip = menu_screen(screen, clock, font, big_font)
    if mode is None:
        pygame.quit()
        sys.exit()

    is_host = mode == "host"
    net = NetworkSession(is_host, host_ip, PORT)
    if not net.connect(screen, clock, font):
        pygame.quit()
        sys.exit()

    local_player = Player(4.0, 4.5, 0.0) if is_host else Player(12.0, 4.5, math.pi)
    remote_color = BLUE if is_host else GREEN

    shots = 0
    running = True
    while running:
        deltatime = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_RETURN:
                    shots += 1

        keys = pygame.key.get_pressed()
        local_player.handle_input(keys, deltatime)

        local_state = {
            "x": local_player.x,
            "y": local_player.y,
            "angle": local_player.angle,
            "shots": shots,
        }
        net.send_state(local_state)
        net.receive_messages()

        local_player.render_world(screen)
        render_remote_player(screen, local_player, net.remote_state, remote_color)
        draw_crosshair(screen)

        role_text = "HOST" if is_host else "CLIENT"
        hud1 = font.render(f"Role: {role_text}", True, WHITE)
        hud2 = font.render("Move: WASD | Turn: Q/E | Shoot: ENTER | ESC: Quit", True, WHITE)
        hud3 = font.render(f"Your shots: {shots} | Peer shots: {net.remote_state.get('shots', 0)}", True, WHITE)
        screen.blit(hud1, (12, 10))
        screen.blit(hud2, (12, 38))
        screen.blit(hud3, (12, 66))

        pygame.display.flip()

    net.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
