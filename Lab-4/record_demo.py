"""Headless recorder: python record.py <repo_dir> <before|after> <out.mp4>"""
import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
repo, mode, out = sys.argv[1:4]
sys.path.insert(0, repo)
os.chdir(repo)
import pygame, imageio
import numpy as np

clock = [0.0]
pygame.time.get_ticks = lambda: int(clock[0])
pygame.init()
scr = pygame.display.set_mode((800, 450))
from game.game_engine import GameEngine
random.seed(7)
e = GameEngine(800, 450)
if mode == "after":
    e.match_start -= 41000          # demo only: skip ahead so sudden death shows within 10 s

KD, KU = pygame.KEYDOWN, pygame.KEYUP
def ev(t, k): e.handle_event(pygame.event.Event(t, key=k))

# overlapping mash: key i goes down every `gap` frames and is held `hold` frames
def schedule(frame):
    if mode == "before":
        return 3, 10
    if frame < 110: return 5, 8
    if frame < 200: return 14, 16
    if frame < 330: return 4, 7
    return 2, 5

w = imageio.get_writer(out, fps=30, codec="libx264", quality=8, macro_block_size=None)
down = {}            # key -> release frame
nxt, idx = 0, 0
keys = [pygame.K_a, pygame.K_d]
for f in range(600):               # 10 s at 60 fps sim, written at 30 fps
    gap, hold = schedule(f)
    for k, rel in list(down.items()):
        if f >= rel:
            ev(KU, k); del down[k]
    if f >= nxt and f > 20:
        k = keys[idx % 2]; idx += 1
        ev(KD, k); down[k] = f + hold; nxt = f + gap
    if f % 30 == 0: print(f, e.rope.marker_x, e.panic_active, e.sudden_death)
    clock[0] += 1000 / 60
    e.update(); e.render(scr)
    if f % 2 == 0:
        w.append_data(np.ascontiguousarray(pygame.surfarray.array3d(scr).swapaxes(0, 1)))
    if f in (120, 240, 360, 480, 590):
        pygame.image.save(scr, out.replace(".mp4", f"_f{f}.png"))
w.close()
print(mode, "winner:", e.winner, "state:", e.game_state, "marker:", e.rope.marker_x)
