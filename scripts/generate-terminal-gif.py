#!/usr/bin/env python3
"""Generate the looping terminal animation used by the profile README."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1000, 610
MARGIN_X, TOP = 42, 78
LINE_HEIGHT = 24
BACKGROUND = "#070b16"
PANEL = "#0d1117"
TEXT = "#d8e0ef"
MUTED = "#8791b8"
CYAN = "#5ad1ff"
MINT = "#7affd9"
PURPLE = "#c9a7ff"
YELLOW = "#f0c36a"
GREEN = "#7ee787"

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
font = ImageFont.truetype(FONT_PATH, 16)
bold = ImageFont.truetype(BOLD_PATH, 16)
small = ImageFont.truetype(FONT_PATH, 13)

commands = [
    (
        "whoami",
        [
            ("Lê Nguyễn Quang Đức  /  leduc121", TEXT),
            ("Backend & Mobile Developer · Ho Chi Minh City, Vietnam", MUTED),
        ],
    ),
    (
        "cat career.json",
        [
            ('{ "role": "Backend Developer",', PURPLE),
            ('  "community": "FCAJ Ambassador · AWS Study Group",', CYAN),
            ('  "focus": "AWS Solutions Architect" }', MINT),
        ],
    ),
    (
        "./stack --list",
        [
            ("languages   C# · TypeScript · Dart · Swift", TEXT),
            ("frameworks  .NET · ASP.NET Core · NestJS · React", TEXT),
            ("mobile      Flutter · SwiftUI", TEXT),
            ("data        SQL Server · PostgreSQL · Redis", TEXT),
            ("cloud       AWS · Azure · Docker · GitHub Actions", TEXT),
        ],
    ),
    (
        "system-check --developer",
        [
            ("[ OK ] scalable backend systems", GREEN),
            ("[ OK ] clean architecture & microservices", GREEN),
            ("[ OK ] cloud learning & hands-on projects", GREEN),
            ("[RUN ] building · learning · sharing", YELLOW),
        ],
    ),
    (
        'echo "Build. Learn. Share. Repeat."',
        [("Build. Learn. Share. Repeat.", CYAN)],
    ),
]


def base_frame(frame_index: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    # Subtle moving aurora behind the terminal glass.
    offset = (frame_index * 7) % 500
    draw.ellipse((560 + offset - 250, -190, 1130 + offset - 250, 390), fill="#10245c")
    draw.ellipse((720 - offset // 2, 250, 1180 - offset // 2, 720), fill="#302078")
    draw.rounded_rectangle((10, 10, WIDTH - 10, HEIGHT - 10), radius=18, fill=PANEL, outline="#355082", width=2)
    draw.rectangle((11, 11, WIDTH - 11, 55), fill="#111725")
    draw.ellipse((28, 27, 42, 41), fill="#ff5f57")
    draw.ellipse((52, 27, 66, 41), fill="#febc2e")
    draw.ellipse((76, 27, 90, 41), fill="#28c840")
    draw.text((WIDTH // 2, 34), "leduc121 — zsh — profile", font=small, fill=MUTED, anchor="mm")
    return image


def render(lines, typed_command, cursor, frame_index):
    image = base_frame(frame_index)
    draw = ImageDraw.Draw(image)
    y = TOP

    for value, color, is_prompt in lines:
        if is_prompt:
            draw.text((MARGIN_X, y), "➜", font=bold, fill=MINT)
            draw.text((MARGIN_X + 28, y), "~", font=bold, fill=CYAN)
            draw.text((MARGIN_X + 52, y), value, font=font, fill=color)
        else:
            draw.text((MARGIN_X + 22, y), value, font=font, fill=color)
        y += LINE_HEIGHT

    if typed_command is not None:
        draw.text((MARGIN_X, y), "➜", font=bold, fill=MINT)
        draw.text((MARGIN_X + 28, y), "~", font=bold, fill=CYAN)
        draw.text((MARGIN_X + 52, y), typed_command, font=font, fill=TEXT)
        if cursor:
            cursor_x = MARGIN_X + 52 + draw.textlength(typed_command, font=font) + 3
            draw.rectangle((cursor_x, y + 2, cursor_x + 9, y + 18), fill=CYAN)

    draw.text((WIDTH - 28, HEIGHT - 26), "github.com/leduc121", font=small, fill=MUTED, anchor="rs")
    return image


frames = []
durations = []
history = []
frame_index = 0

for command, output in commands:
    for index in range(len(command) + 1):
        frames.append(render(history, command[:index], True, frame_index))
        durations.append(42)
        frame_index += 1

    history.append((command, TEXT, True))
    for value, color in output:
        history.append((value, color, False))
        frames.append(render(history, None, False, frame_index))
        durations.append(240)
        frame_index += 1

    durations[-1] += 420

for blink in range(8):
    frames.append(render(history, "", blink % 2 == 0, frame_index))
    durations.append(280)
    frame_index += 1

# Pause on the completed terminal, then loop back to the first command.
durations[-1] = 1600
output_path = Path(__file__).resolve().parents[1] / "terminal-demo.gif"
frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Generated {output_path.name}: {len(frames)} frames, {WIDTH}x{HEIGHT}")
