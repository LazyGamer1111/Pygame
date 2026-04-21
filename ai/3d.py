import json
import math
import random
import socket
import sys
import time

import numpy as np
import pygame

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 120
FOV = math.pi / 3
MAX_DEPTH = 20
RAY_STEP = 0.2
COLLISION_BUFFER = 0.2
PORT = 5055
MAX_HP = 100
DAMAGE = 25
RESPAWN_SECONDS = 3.0

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 160, 255)
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
SPAWN_POINTS = [
    (4.0, 4.5, 0.0),
    (12.0, 4.5, math.pi),
    (7.5, 2.0, math.pi / 2),
    (7.5, 7.5, -math.pi / 2),
    (2.5, 7.0, 0.2),
    (13.0, 7.0, math.pi - 0.2),
]


class PlayerController:
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
        for ox in [-COLLISION_BUFFER, 0, COLLISION_BUFFER]:
            for oy in [-COLLISION_BUFFER, 0, COLLISION_BUFFER]:
                if self.is_wall(x + ox, y + oy):
                    return False
        return True

    def handle_input(self, keys, deltatime):
        new_x, new_y = self.x, self.y

        # ZQSD scheme for AZERTY keyboards.
        if keys[pygame.K_z]:
            new_x += np.cos(self.angle) * self.speed * deltatime
            new_y += np.sin(self.angle) * self.speed * deltatime
        if keys[pygame.K_s]:
            new_x -= np.cos(self.angle) * self.speed * deltatime
            new_y -= np.sin(self.angle) * self.speed * deltatime
        if keys[pygame.K_q]:
            new_x += np.cos(self.angle - np.pi / 2) * self.speed * deltatime
            new_y += np.sin(self.angle - np.pi / 2) * self.speed * deltatime
        if keys[pygame.K_d]:
            new_x += np.cos(self.angle + np.pi / 2) * self.speed * deltatime
            new_y += np.sin(self.angle + np.pi / 2) * self.speed * deltatime

        if self.can_move_to(new_x, new_y):
            self.x = new_x
            self.y = new_y

        if keys[pygame.K_LEFT]:
            self.angle -= self.rotation_speed * deltatime
        if keys[pygame.K_RIGHT]:
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


def normalize_angle(angle):
    while angle > np.pi:
        angle -= 2 * np.pi
    while angle < -np.pi:
        angle += 2 * np.pi
    return angle


def cast_ray_from_state(px, py, angle):
    sin_a = np.sin(angle)
    cos_a = np.cos(angle)
    distance = 0.0
    while distance < MAX_DEPTH:
        distance += RAY_STEP
        x = px + cos_a * distance
        y = py + sin_a * distance
        if not (0 <= int(x) < MAP_WIDTH and 0 <= int(y) < MAP_HEIGHT):
            return distance
        if GAME_MAP[int(y)][int(x)] == 1:
            return distance
    return MAX_DEPTH


def get_local_ip():
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("8.8.8.8", 80))
        ip = probe.getsockname()[0]
        probe.close()
        return ip
    except OSError:
        return "127.0.0.1"


class HostServer:
    def __init__(self, port):
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("", port))
        self.server.listen(16)
        self.server.setblocking(False)

        self.clients = {}  # sock -> {id, buffer}
        self.next_id = 2
        self.snapshot_interval = 1.0 / 30.0
        self.last_snapshot = 0.0

        x, y, angle = SPAWN_POINTS[0]
        self.players = {
            1: {
                "id": 1,
                "name": "Host",
                "x": x,
                "y": y,
                "angle": angle,
                "hp": MAX_HP,
                "shots": 0,
                "score": 0,
                "alive": True,
                "respawn_at": 0.0,
            }
        }

    def shutdown(self):
        for sock in list(self.clients.keys()):
            try:
                sock.close()
            except OSError:
                pass
        try:
            self.server.close()
        except OSError:
            pass

    def _spawn_for(self, player_id):
        sx, sy, sa = SPAWN_POINTS[player_id % len(SPAWN_POINTS)]
        return sx, sy, sa

    def _send_json(self, sock, obj):
        try:
            sock.sendall((json.dumps(obj) + "\n").encode("utf-8"))
            return True
        except OSError:
            return False

    def _disconnect(self, sock):
        info = self.clients.pop(sock, None)
        if info:
            pid = info["id"]
            if pid in self.players:
                del self.players[pid]
        try:
            sock.close()
        except OSError:
            pass

    def _accept_new_clients(self):
        while True:
            try:
                sock, _addr = self.server.accept()
            except BlockingIOError:
                break
            except OSError:
                break

            sock.setblocking(False)
            pid = self.next_id
            self.next_id += 1
            self.clients[sock] = {"id": pid, "buffer": ""}

            sx, sy, sa = self._spawn_for(pid)
            self.players[pid] = {
                "id": pid,
                "name": f"P{pid}",
                "x": sx,
                "y": sy,
                "angle": sa,
                "hp": MAX_HP,
                "shots": 0,
                "score": 0,
                "alive": True,
                "respawn_at": 0.0,
            }
            self._send_json(sock, {"type": "welcome", "id": pid})

    def _apply_respawns(self, now):
        for p in self.players.values():
            if not p["alive"] and now >= p["respawn_at"]:
                sx, sy, sa = self._spawn_for(p["id"])
                p["x"] = sx
                p["y"] = sy
                p["angle"] = sa
                p["hp"] = MAX_HP
                p["alive"] = True

    def _resolve_shot(self, shooter_id):
        shooter = self.players.get(shooter_id)
        if not shooter or not shooter["alive"]:
            return

        best_target = None
        best_dist = float("inf")

        for target_id, target in self.players.items():
            if target_id == shooter_id or not target["alive"]:
                continue

            dx = target["x"] - shooter["x"]
            dy = target["y"] - shooter["y"]
            dist = np.sqrt(dx * dx + dy * dy)
            if dist < 0.1 or dist > MAX_DEPTH:
                continue

            angle_to_target = np.arctan2(dy, dx)
            angle_diff = normalize_angle(angle_to_target - shooter["angle"])
            if abs(angle_diff) > 0.12:
                continue

            wall_distance = cast_ray_from_state(shooter["x"], shooter["y"], angle_to_target)
            if wall_distance + 0.1 < dist:
                continue

            if dist < best_dist:
                best_dist = dist
                best_target = target

        if best_target is not None:
            best_target["hp"] -= DAMAGE
            if best_target["hp"] <= 0:
                best_target["hp"] = 0
                best_target["alive"] = False
                best_target["respawn_at"] = time.time() + RESPAWN_SECONDS
                shooter["score"] += 1

    def set_host_state(self, x, y, angle, shoot_pressed):
        host = self.players[1]
        host["x"] = x
        host["y"] = y
        host["angle"] = angle
        if shoot_pressed and host["alive"]:
            host["shots"] += 1
            self._resolve_shot(1)

    def _read_clients(self):
        for sock, info in list(self.clients.items()):
            disconnected = False
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        disconnected = True
                        break
                    info["buffer"] += data.decode("utf-8", errors="ignore")
                except BlockingIOError:
                    break
                except OSError:
                    disconnected = True
                    break

            if disconnected:
                self._disconnect(sock)
                continue

            while "\n" in info["buffer"]:
                line, info["buffer"] = info["buffer"].split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(msg, dict):
                    continue

                pid = info["id"]
                p = self.players.get(pid)
                if not p:
                    continue

                if msg.get("type") == "state":
                    p["x"] = float(msg.get("x", p["x"]))
                    p["y"] = float(msg.get("y", p["y"]))
                    p["angle"] = float(msg.get("angle", p["angle"]))
                    if bool(msg.get("shoot", False)) and p["alive"]:
                        p["shots"] += 1
                        self._resolve_shot(pid)

    def _broadcast_snapshot(self):
        payload = {
            "type": "snapshot",
            "players": {str(pid): pdata for pid, pdata in self.players.items()},
        }
        for sock in list(self.clients.keys()):
            if not self._send_json(sock, payload):
                self._disconnect(sock)

    def tick(self):
        now = time.time()
        self._accept_new_clients()
        self._read_clients()
        self._apply_respawns(now)
        if now - self.last_snapshot >= self.snapshot_interval:
            self._broadcast_snapshot()
            self.last_snapshot = now


class ClientSession:
    def __init__(self, host_ip, port):
        self.host_ip = host_ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(0.2)
        self.connected = False
        self.local_id = None
        self.buffer = ""
        self.players = {}

    def connect_with_ui(self, screen, clock, font):
        while not self.connected:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False

            try:
                self.sock.connect((self.host_ip, self.port))
                self.connected = True
            except (TimeoutError, ConnectionRefusedError, OSError):
                pass

            screen.fill(BLACK)
            t1 = font.render(f"Joining {self.host_ip}:{self.port}", True, BLUE)
            t2 = font.render("Connecting... (ESC to cancel)", True, WHITE)
            screen.blit(t1, (40, 220))
            screen.blit(t2, (40, 255))
            pygame.display.flip()
            clock.tick(60)

        self.sock.setblocking(False)
        return True

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass

    def send_state(self, x, y, angle, shoot_pressed):
        msg = {
            "type": "state",
            "x": x,
            "y": y,
            "angle": angle,
            "shoot": bool(shoot_pressed),
        }
        try:
            self.sock.sendall((json.dumps(msg) + "\n").encode("utf-8"))
        except OSError:
            pass

    def poll_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    return False
                self.buffer += data.decode("utf-8", errors="ignore")
            except BlockingIOError:
                break
            except OSError:
                return False

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(msg, dict):
                continue

            mtype = msg.get("type")
            if mtype == "welcome":
                self.local_id = int(msg.get("id", 0))
            elif mtype == "snapshot":
                raw_players = msg.get("players", {})
                new_players = {}
                for pid_str, pdata in raw_players.items():
                    try:
                        pid = int(pid_str)
                    except (ValueError, TypeError):
                        continue
                    if isinstance(pdata, dict):
                        new_players[pid] = pdata
                self.players = new_players

        return True


def render_remote_player(screen, viewer, target, font):
    dx = target["x"] - viewer.x
    dy = target["y"] - viewer.y
    dist = np.sqrt(dx * dx + dy * dy)

    if dist < 0.1 or dist > MAX_DEPTH or not target.get("alive", True):
        return

    angle_to_target = np.arctan2(dy, dx)
    angle_diff = normalize_angle(angle_to_target - viewer.angle)
    if abs(angle_diff) > FOV / 2:
        return

    wall_distance = viewer.cast_ray(angle_to_target)
    if wall_distance + 0.1 < dist:
        return

    col = int(SCREEN_WIDTH / 2 + (angle_diff / (FOV / 2)) * (SCREEN_WIDTH / 2))
    sprite_height = min(int(SCREEN_HEIGHT / dist), SCREEN_HEIGHT)
    top = (SCREEN_HEIGHT - sprite_height) // 2
    sprite_width = max(3, int(SCREEN_WIDTH * 0.22 / (dist + 0.1)))

    body_color = RED
    pygame.draw.rect(screen, body_color, (col - sprite_width // 2, top, sprite_width, sprite_height))

    # Draw hp bar above the visible player sprite.
    hp = int(target.get("hp", MAX_HP))
    hp_ratio = max(0.0, min(1.0, hp / MAX_HP))
    bar_w = max(20, sprite_width)
    bar_h = 6
    bar_x = col - bar_w // 2
    bar_y = max(6, top - 14)
    pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

    name = str(target.get("name", "P?"))
    tag = font.render(f"{name} {hp}HP", True, WHITE)
    screen.blit(tag, (col - tag.get_width() // 2, bar_y - 16))


def draw_crosshair(screen):
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    pygame.draw.line(screen, WHITE, (cx - 8, cy), (cx + 8, cy), 1)
    pygame.draw.line(screen, WHITE, (cx, cy - 8), (cx, cy + 8), 1)


def draw_hud(screen, font, local_id, players, mode_text):
    role = font.render(mode_text, True, WHITE)
    help_line = font.render("Move: ZQSD | Turn: Left/Right | Shoot: ENTER | ESC: Quit", True, WHITE)
    screen.blit(role, (12, 10))
    screen.blit(help_line, (12, 38))

    y = 68
    for pid in sorted(players.keys()):
        p = players[pid]
        marker = ">" if pid == local_id else " "
        alive = "alive" if p.get("alive", True) else "respawn"
        line = f"{marker} {p.get('name', 'P')} HP:{int(p.get('hp', 0))} K:{int(p.get('score', 0))} {alive}"
        color = YELLOW if pid == local_id else WHITE
        surf = font.render(line, True, color)
        screen.blit(surf, (12, y))
        y += 24


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
        title = big_font.render("Online PvP", True, YELLOW)
        screen.blit(title, (40, 50))

        if mode is None:
            host_ip = get_local_ip()
            l1 = font.render("Press H to Host", True, GREEN)
            l2 = font.render("Press J to Join", True, BLUE)
            l3 = font.render(f"Your LAN IP: {host_ip}", True, WHITE)
            l4 = font.render(f"Port: {PORT}", True, WHITE)
            l5 = font.render("ESC to Exit", True, WHITE)
            screen.blit(l1, (40, 140))
            screen.blit(l2, (40, 174))
            screen.blit(l3, (40, 230))
            screen.blit(l4, (40, 264))
            screen.blit(l5, (40, 318))
        else:
            l1 = font.render("Type host IP then ENTER:", True, WHITE)
            box = pygame.Rect(40, 190, 320, 38)
            pygame.draw.rect(screen, WHITE, box, 2)
            l2 = font.render(ip_text or "192.168.1.20", True, BLUE)
            l3 = font.render("ESC to cancel", True, WHITE)
            screen.blit(l1, (40, 150))
            screen.blit(l2, (50, 200))
            screen.blit(l3, (40, 245))

        pygame.display.flip()
        clock.tick(60)


def run_host(screen, clock, font):
    server = HostServer(PORT)
    local_player = PlayerController(*SPAWN_POINTS[0])

    running = True
    while running:
        deltatime = clock.tick(FPS) / 1000.0
        shoot_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_RETURN:
                    shoot_pressed = True

        keys = pygame.key.get_pressed()
        host_data = server.players.get(1)
        if host_data and not host_data.get("alive", True):
            local_player.x = host_data["x"]
            local_player.y = host_data["y"]
            local_player.angle = host_data["angle"]
        else:
            local_player.handle_input(keys, deltatime)

        server.set_host_state(local_player.x, local_player.y, local_player.angle, shoot_pressed)
        server.tick()

        local_player.render_world(screen)
        for pid, pdata in server.players.items():
            if pid == 1:
                continue
            render_remote_player(screen, local_player, pdata, font)

        draw_crosshair(screen)
        draw_hud(screen, font, 1, server.players, "Mode: HOST")
        pygame.display.flip()

    server.shutdown()


def run_client(screen, clock, font, host_ip):
    client = ClientSession(host_ip, PORT)
    if not client.connect_with_ui(screen, clock, font):
        return

    local_player = PlayerController(*SPAWN_POINTS[1])
    running = True
    while running:
        deltatime = clock.tick(FPS) / 1000.0
        shoot_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_RETURN:
                    shoot_pressed = True

        keys = pygame.key.get_pressed()

        if client.local_id and client.local_id in client.players:
            lp = client.players[client.local_id]
            if not lp.get("alive", True):
                local_player.x = lp["x"]
                local_player.y = lp["y"]
                local_player.angle = lp["angle"]
            else:
                local_player.handle_input(keys, deltatime)
        else:
            local_player.handle_input(keys, deltatime)

        client.send_state(local_player.x, local_player.y, local_player.angle, shoot_pressed)
        if not client.poll_messages():
            break

        local_player.render_world(screen)
        local_id = client.local_id if client.local_id is not None else -1
        for pid, pdata in client.players.items():
            if pid == local_id:
                continue
            render_remote_player(screen, local_player, pdata, font)

        draw_crosshair(screen)
        draw_hud(screen, font, local_id, client.players, "Mode: CLIENT")
        pygame.display.flip()

    client.close()


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("3D Online PvP")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    big_font = pygame.font.Font(None, 52)

    mode, host_ip = menu_screen(screen, clock, font, big_font)
    if mode is None:
        pygame.quit()
        sys.exit()

    if mode == "host":
        run_host(screen, clock, font)
    else:
        run_client(screen, clock, font, host_ip)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
