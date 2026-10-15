
import math


def handle_paddle_collision(puck, paddle, previous_x=None, previous_y=None):
    radius = puck.radius + paddle.radius

    if previous_x is None:
        previous_x = puck.x
    if previous_y is None:
        previous_y = puck.y

    move_x = puck.x - previous_x
    move_y = puck.y - previous_y
    length_sq = move_x * move_x + move_y * move_y

    if length_sq > 0:
        t = (
            (paddle.x - previous_x) * move_x
            + (paddle.y - previous_y) * move_y
        ) / length_sq
        t = max(0.0, min(1.0, t))

        closest_x = previous_x + t * move_x
        closest_y = previous_y + t * move_y
    else:
        closest_x = puck.x
        closest_y = puck.y

    dx = closest_x - paddle.x
    dy = closest_y - paddle.y
    distance = math.hypot(dx, dy)

    if distance > radius:
        return False

    if distance > 0.000001:
        nx = dx / distance
        ny = dy / distance
    else:
        speed = math.hypot(puck.vx, puck.vy)

        if speed > 0.000001:
            nx = -puck.vx / speed
            ny = -puck.vy / speed
        else:
            nx, ny = -1.0, 0.0

    puck.x = paddle.x + nx * (radius + 0.5)
    puck.y = paddle.y + ny * (radius + 0.5)

    velocity_dot_normal = puck.vx * nx + puck.vy * ny

    if velocity_dot_normal < 0:
        puck.vx -= 2 * velocity_dot_normal * nx
        puck.vy -= 2 * velocity_dot_normal * ny

    return True
