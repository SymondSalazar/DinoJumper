import pygame
import sys
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    COLOR_WHITE,
    COLOR_BLACK,
    SPEED_START,
    MAX_SPEED,
    ACCELERATION,
    GROUND_Y_POS,
    SPRITE_SHEET_PATH,
    get_day_night_distance,
)
from dinosaur import Dinosaur
from controller import InputHandler
from obstacles import ObstacleManager
from sprite_sheet import SpriteSheet

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Jumper")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)


def reset_game(
    player: Dinosaur, obstacle_manager: ObstacleManager, input_handler: InputHandler
) -> tuple[float, float, bool, bool, tuple[int, int, int], tuple[int, int, int], int]:
    """Resetea el juego sin crear nuevas instancias"""
    player.__init__()
    obstacle_manager.obstacles.clear()
    obstacle_manager.last_spawn_time = 0
    input_handler.reset()

    return (
        0,
        SPEED_START,
        False,
        True,
        COLOR_WHITE,
        COLOR_BLACK,
        get_day_night_distance(),
    )


def main() -> None:
    player = Dinosaur()
    input_handler = InputHandler()
    obstacle_manager = ObstacleManager()

    sheet = SpriteSheet(SPRITE_SHEET_PATH)
    ground_img = sheet.get_image(2, 104, 2400, 24)
    ground_x = 0
    ground_y = GROUND_Y_POS + 10

    game_speed = SPEED_START
    score = 0.0
    game_over = False

    bg_color = COLOR_WHITE
    fg_color = COLOR_BLACK
    is_day = True
    next_day_night_switch = get_day_night_distance()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                input_handler.close()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    (
                        score,
                        game_speed,
                        game_over,
                        is_day,
                        bg_color,
                        fg_color,
                        next_day_night_switch,
                    ) = reset_game(player, obstacle_manager, input_handler)
                    ground_x = 0

        input_handler.update()

        input_handler.set_game_over(game_over)

        if game_over and input_handler.is_hand_raised_just_now():
            (
                score,
                game_speed,
                game_over,
                is_day,
                bg_color,
                fg_color,
                next_day_night_switch,
            ) = reset_game(player, obstacle_manager, input_handler)
            ground_x = 0

        if not game_over:
            if game_speed < MAX_SPEED:
                game_speed += ACCELERATION

            player.update(input_handler)
            obstacle_manager.update(game_speed, int(score))

            score += 0.15 * (game_speed / SPEED_START)

            ground_x -= game_speed
            if ground_x <= -ground_img.get_width():
                ground_x = 0

            if score >= next_day_night_switch:
                is_day = not is_day

                if is_day:
                    bg_color = COLOR_WHITE
                    fg_color = COLOR_BLACK
                else:
                    bg_color = COLOR_BLACK
                    fg_color = COLOR_WHITE

                next_day_night_switch = score + get_day_night_distance()

            player_rect = player.rect.inflate(-20, -15)
            for obs in obstacle_manager.obstacles:
                obs_rect = obs.rect.inflate(-15, -15)
                if player_rect.colliderect(obs_rect):
                    game_over = True

        screen.fill(bg_color)

        camera_frame = input_handler.get_camera_frame()
        if camera_frame is not None:
            camera_surface = pygame.surfarray.make_surface(camera_frame)
            camera_width, camera_height = 320, 240
            camera_surface = pygame.transform.scale(
                camera_surface, (camera_width, camera_height)
            )

            camera_x = 10
            camera_y = 10

            border_color = (255, 0, 255) if game_over else fg_color
            pygame.draw.rect(
                screen,
                border_color,
                (camera_x - 2, camera_y - 2, camera_width + 4, camera_height + 4),
                3,
            )

            screen.blit(camera_surface, (camera_x, camera_y))

        screen.blit(ground_img, (ground_x, ground_y))
        screen.blit(ground_img, (ground_x + ground_img.get_width(), ground_y))

        player.draw(screen)
        obstacle_manager.draw(screen)

        score_surface = font.render(f"Pts {int(score):05d}", True, fg_color)
        screen.blit(score_surface, (SCREEN_WIDTH - 150, 20))

        if game_over:
            go_text = font.render("Levanta la mano para reiniciar", True, fg_color)
            rect = go_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(go_text, rect)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
