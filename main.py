import pyxel


# 自機・敵・弾・弾幕の基本クラス
class Item:
    def __init__(self):
        self.x = pyxel.rndi(0, 155)
        self.y = -200

        self.width = 8
        self.height = 8

    def reset(self):
        self.x = pyxel.rndi(0, 155)
        self.y = -200

    def update(self):
        dx = 0
        dy = 2
        self.x += dx
        self.y += dy

        # 画面外で消す
        if self.y > 120:
            self.reset()

    def draw(self):
        pyxel.rect(self.x, self.y, 8, 8, 14)  # アイテムを描画
        pyxel.rect(self.x + 1, self.y + 1, 6, 6, 8)  # アイテムの中身を描画
        pyxel.text(self.x + 2, self.y + 2, "P", 7)

class Bullet:
    def __init__(self, x, y, dx, dy, color=8):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.active = True
        self.color = color

    def update(self):
        self.x += self.dx
        self.y += self.dy
        # 画面外で消す
        if self.x < 0 or self.x > 160 or self.y < -30 or self.y > 120:
            self.active = False

    def draw(self):
        pyxel.circ(self.x, self.y, 2, self.color)


class Player:
    def __init__(self):
        self.x = 80
        self.y = 100
        self.power = 0
        self.bullets = []
        self.cooldown = 0

    def add_power(self):
        if self.power < 3:
            self.power += 1
            pyxel.play(0, 0)

    def update(self):
        move_speed = 2

        if pyxel.btn(pyxel.KEY_SHIFT):
            move_speed = 1

        # 移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x = max(self.x - move_speed, 8)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x = min(self.x + move_speed, 152)
        if pyxel.btn(pyxel.KEY_UP):
            self.y = max(self.y - move_speed, 8)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y = min(self.y + move_speed, 112)

        # ショット
        if pyxel.btn(pyxel.KEY_Z) and self.power == 3:
            self.bullets.append(Bullet(self.x, self.y - 8, 0, -6, color=7))
            self.power = 0

        # 弾の更新
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.active]

    def draw(self):
        pyxel.tri(self.x - 5, self.y + 4, self.x + 5, self.y + 4, self.x, self.y - 8, 10)
        pyxel.circ(self.x, self.y, 2, 78)
        for b in self.bullets:
            b.draw()


class Enemy:
    def __init__(self):
        self.x = 80
        self.y = 10
        self.dx = 0
        self.dy = 0
        self.r = 6
        self.timer = 0
        self.move_timer = 0
        self.bullets_pattern1 = []
        self.bullets_pattern2 = []

    def select_destination(self):
        # ランダムな画面上部中央付近の座標を選択
        # 前回の座標から少しずらす
        while True:
            target_x = pyxel.rndi(20, 140)
            target_y = pyxel.rndi(10, 30)
            if abs(target_x - self.x) > 50:
                break
        return target_x, target_y

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def get_player_angle(self, player_x, player_y):
        # プレイヤーの位置から角度を計算
        dx = player_x - self.x
        dy = player_y - self.y
        return pyxel.atan2(dy, dx)

    def update(self, player_x=None, player_y=None):
        if self.timer % 90 == 0:
            target_x, target_y = self.select_destination()
            self.dx = (target_x - self.x) / 90
            self.dy = (target_y - self.y) / 90

        self.move()

        self.timer += 1
        # 一定間隔で弾幕発射
        if self.timer % 8 == 0:
            angle = self.get_player_angle(player_x, player_y)
            for deg in range(0, 360, 30):
                deg = (angle + deg) % 360
                dx = pyxel.cos(deg) * 2.5
                dy = pyxel.sin(deg) * 2.5
                self.bullets_pattern1.append(Bullet(self.x, self.y, dx, dy, color=8))

        if self.timer % 90 == 0:
            for _ in range(18):
                x = pyxel.rndi(1, 159)
                y = pyxel.rndf(-25, 0)
                dx = 0
                dy = pyxel.rndf(0.8, 2.5)
                self.bullets_pattern2.append(Bullet(x, y, dx, dy, color=3))

        for b in self.bullets_pattern1:
            b.update()
        self.bullets_pattern1 = [b for b in self.bullets_pattern1 if b.active]

        for b in self.bullets_pattern2:
            b.update()
        self.bullets_pattern2 = [b for b in self.bullets_pattern2 if b.active]

    def draw(self):
        pyxel.circ(self.x, self.y, self.r, 9)
        for b in self.bullets_pattern1:
            b.draw()
        for b in self.bullets_pattern2:
            b.draw()


class App:
    def __init__(self, debug=False):
        self.width = 160
        self.height = 120
        self.clear_flag = False
        self.debug = debug

        pyxel.init(self.width, self.height, title="Danmaku")
        self.player = Player()
        self.enemy = Enemy()
        self.item = Item()

        if debug:
            self.player.power = 3  # デバッグモードではパワーを最大に

        pyxel.run(self.update, self.draw)

    def update(self):
        if self.clear_flag:
            return  # クリア時は更新しない

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.player.update()
        self.enemy.update(self.player.x, self.player.y)
        self.item.update()

        # 当たり判定（超簡易）
        for b in self.enemy.bullets_pattern1 + self.enemy.bullets_pattern2:
            dist = ((b.x - self.player.x) ** 2 + (b.y - self.player.y) ** 2) ** 0.5
            if dist < 2:
                pyxel.quit()  # 被弾で即終了

        # 当たり判定（アイテム）
        # おかしい
        if (abs(self.item.x - self.player.x) < self.item.width) and (abs(self.item.y - self.player.y) < self.item.height):
            self.player.add_power()
            self.item.reset()

        # プレイヤーの弾を当てるとゲームクリア
        for b in self.player.bullets:
            dist = ((b.x - self.enemy.x) ** 2 + (b.y - self.enemy.y) ** 2) ** 0.5
            if dist < self.enemy.r:
                # 画面を白くして、中央に「クリア」と表示
                self.clear_flag = True
                pyxel.text(70, 50, "CLEAR!", 7)
                pyxel.text(50, 60, "Press Q to exit", 7)

    def draw(self):
        if self.clear_flag:
            return

        pyxel.cls(1)
        self.player.draw()
        self.enemy.draw()
        self.item.draw()

        pyxel.rect(0, self.height - 2, self.width, self.height, 7)
        pyxel.rect(self.enemy.x - self.enemy.r, self.height - 2, self.enemy.r * 2, self.height, 8)

        if self.player.power == 3:
            pyxel.text(5, self.height - 10, f"Power: {self.player.power}", 8)
        else:
            pyxel.text(5, self.height - 10, f"Power: {self.player.power}", 7)

App()  # debug=Trueでデバッグモードを有効に
