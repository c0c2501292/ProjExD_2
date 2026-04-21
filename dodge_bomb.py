import os
import sys
import random  
import pygame as pg
import time  


WIDTH, HEIGHT = 1100, 650

DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0, +5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面内か画面外かを判定する関数
    引数：こうかとんRectまたは爆弾Rect
    戻り値：横方向,縦方向判定結果（True: 画面内,False: 画面外）
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向判定
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:    #ゲームオーバー画面を表示する関数

    black_scr = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(black_scr, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    black_scr.set_alpha(200)

    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2
    black_scr.blit(txt, txt_rct)


    kk_cry = pg.image.load("fig/8.png") 
    black_scr.blit(kk_cry, [WIDTH // 2 - 250, HEIGHT // 2 - 40]) # 左側
    black_scr.blit(kk_cry, [WIDTH // 2 + 200, HEIGHT // 2 - 40]) # 右側

    screen.blit(black_scr, [0, 0])

    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の大きさと加速度を持つ爆弾リストを返す
    戻り値: (爆弾Surfaceのリスト, 加速度のリスト)
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルをキー,rotozoomしたSurfaceを値とした辞書を返す
    """
    kk_img = pg.image.load("fig/3.png")
    # デフォルト（右向き）を基準に反転や回転を行う
    kk_img_flip = pg.transform.flip(kk_img, True, False) # 右向き
    
    kk_dict = {
        ( 0,  0): pg.transform.rotozoom(kk_img, 0, 0.9),      # 静止（左向き）
        (-5,  0): pg.transform.rotozoom(kk_img, 0, 0.9),      # 左
        (-5, -5): pg.transform.rotozoom(kk_img, -45, 0.9),    # 左上
        ( 0, -5): pg.transform.rotozoom(kk_img_flip, 90, 0.9), # 上（右向きを90度）
        (+5, -5): pg.transform.rotozoom(kk_img_flip, 45, 0.9), # 右上
        (+5,  0): pg.transform.rotozoom(kk_img_flip, 0, 0.9),  # 右
        (+5, +5): pg.transform.rotozoom(kk_img_flip, -45, 0.9),# 右下
        ( 0, +5): pg.transform.rotozoom(kk_img_flip, -90, 0.9),# 下
        (-5, +5): pg.transform.rotozoom(kk_img, 45, 0.9),     # 左下
    }
    return kk_dict

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg") 

    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]  # 初期状態の爆弾
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5


    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        idx = min(tmr // 300, 9)  # 300フレームごとに段階を上げる（最大9）
        bb_img = bb_imgs[idx]
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_img = kk_imgs[tuple(sum_mv)]

        kk_rct.move_ip(sum_mv)

        if check_bound(kk_rct) != (True, True): #画面外
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(avx, avy)

        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向
            vx *= -1
        if not tate:  # 縦方向
            vy *= -1
        
        curr_center = bb_rct.center
        bb_rct = bb_img.get_rect()
        bb_rct.center = curr_center
            
        screen.blit(bb_img, bb_rct)  # 爆弾を表示させる
        
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return  #ゲームオーバー
        
        pg.display.update()
        tmr += 1
        clock.tick(50)
       

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
