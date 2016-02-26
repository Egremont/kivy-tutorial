from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import random

class PauseMenu(Widget):
    pause_popup = Popup(title='Pause menu',
                        content=Label(text='Game paused, press Esc to continue'),\
                        size_hint=(.4, .2), auto_dismiss=False)
    def handler(self, game_id, is_paused):
        if not(is_paused):
            self.pause_popup.open()
            Clock.unschedule(game_id.update)
        else:
            self.pause_popup.dismiss()
            Clock.schedule_interval(game_id.update, 1.0 / 60.0)
        return not(is_paused)

class PongPaddle(Widget):
    score = NumericProperty(0)
    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongGame(Widget):
    is_paused = False
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    paused = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def check_paddle_border(self, player_id, border_id):
        if player_id==1:
            player_center = self.player1.center_y
            player_height = self.player1.height
        elif player_id==2:
            player_center = self.player2.center_y
            player_height = self.player2.height
        if border_id=='top':
            return player_center + player_height/2 < self.top
        elif border_id=='bottom':
            return player_center - player_height/2 > self.y

    def update(self, dt):
        self.ball.move()

        #CPU player as player2: player2 paddle tracks vertical position of ball
        # controls how much cpu paddle moves during each tick
        cpu_paddle_speed = 2+random.randint(1,4) # increase -> more difficult
        # cpu decides to move based on difference between its paddle's y
        # position and that of the ball
        cpu_detect_motion = 100 # decrease -> more difficult
        if self.player2.center_y - self.ball.y < -cpu_detect_motion:
            # check paddle is not at upper border
            if self.check_paddle_border( player_id=2, border_id='top'):
                #paddle below ball, move up
                self.player2.center_y += cpu_paddle_speed
        elif self.player2.center_y - self.ball.y > cpu_detect_motion:
            # check paddle is not at lower border
            if self.check_paddle_border( player_id=2, border_id='bottom'):
                #paddle above ball, move down
                self.player2.center_y -= cpu_paddle_speed

        #bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        #bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        #went off to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

    # using keyboard controls so commented out touch methods
    #def on_touch_move(self, touch):
    #    if touch.x < self.width / 3:
    #        self.player1.center_y = touch.y
    #    # player2 is cpu player
    #    #if touch.x > self.width - self.width / 3:
    #    #    self.player2.center_y = touch.y

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        move_on_press = 50
        if keycode[1] == 'w':
            # check paddle is not at upper border
            if self.check_paddle_border( player_id=1, border_id='top'):
                self.player1.center_y += move_on_press
        elif keycode[1] == 's':
            # check paddle is not at lower border
            if self.check_paddle_border( player_id=1, border_id='bottom'):
                self.player1.center_y -= move_on_press
        elif keycode[1] == 'escape':
            self.is_paused = self.paused.handler(self, self.is_paused)

        # player2 is cpu player
        #elif keycode[1] == 'up':
        #    self.player2.center_y += move_on_press
        #elif keycode[1] == 'down':
        #    self.player2.center_y -= move_on_press
        return True

class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__=='__main__':
    PongApp().run()
