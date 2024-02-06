import os
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
from .data import *


class GamePad:

    def __init__(self, gamepad_number: int = 0):
        import pygame
        pygame.init()
        pygame.joystick.init()
        self.gamepad_count = pygame.joystick.get_count()
        if self.gamepad_count <= gamepad_number:
            print("no Joystick found")
            exit(1)
        self.gamepad_data = GamepadData()
        self.done = False
        self.clock = pygame.time.Clock()
        self.gamepad_number = gamepad_number
        self.gamepad = pygame.joystick.Joystick(self.gamepad_number)
        self.axis_count = self.gamepad.get_numaxes()
        self.buttons_count = self.gamepad.get_numbuttons()
        self.name = self.gamepad.get_name()
        self.hats_count = self.gamepad.get_numhats()
        print("gamepad %i found: %i axis, %i buttons, %i hats" % (self.gamepad_number, self.axis_count, self.buttons_count, self.hats_count))
        self.handlers = []
        self.thread = None

    def add_handler(self, update_type, index, handler):
        while update_type >= len(self.handlers):
            self.handlers.append([])
        while index >= len(self.handlers[update_type]):
            self.handlers[update_type].append(None)
        self.handlers[update_type][index] = handler

    def __get_handler__(self, update: GamepadUpdate):
        if update.t < len(self.handlers) and update.i < len(self.handlers[update.t]):
            return self.handlers[update.t][update.i]
        else:
            return None

    def __process_updates__(self, updates: GamepadUpdates):
        for u in updates:
            handler = self.__get_handler__(u)
            if handler:
                handler(u.v)

    def update(self) -> bool:
        import pygame
        pygame.event.get()
        cur_gamepad_data = GamepadData()
        for i in range(self.axis_count):
            cur_gamepad_data.axes.append(int(self.gamepad.get_axis(i) * 32767))
        for i in range(self.buttons_count):
            cur_gamepad_data.buttons.append(self.gamepad.get_button(i))
        for i in range(self.hats_count):
            cur_gamepad_data.hats.append(Hat(self.gamepad.get_hat(i)))
        updates = self.gamepad_data.get_updates(cur_gamepad_data)
        self.__process_updates__(updates)
        self.gamepad_data.apply_updates(updates)
        self.clock.tick(20)
        return not self.done

    def wait(self, time_out: float = 1):
        from datetime import datetime
        if self.done:
            return False
        start = datetime.now()
        while (datetime.now()-start).total_seconds() < time_out:
            if not self.update():
                return False
        return True

    def __del__(self):
        import pygame
        pygame.quit()

    def __process__(self):
        while self.update():
            pass

    def start(self):
        from threading import Thread
        self.thread = Thread(target=self.__process__)
        self.thread.start()


if __name__ == "__main__":
    gamepad = GamePad()

    def axis0(value):
        print(value)

    def hat0(value):
        print(value)

    gamepad.add_handler(UpdateType.Axis, 0, axis0)
    gamepad.add_handler(UpdateType.Hat, 0, hat0)
    gamepad.__process__()


