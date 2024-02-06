from json_cpp import JsonList, JsonObject


class UpdateType:
    Axis = 0
    Button = 1
    Hat = 2


class GamepadUpdate(JsonObject):

    def __init__(self, update_type: int = UpdateType.Axis, index: int = 0,  value: int = 0):
        self.t = update_type
        self.i = index
        self.v = value


class GamepadUpdates(JsonList):

    def __init__(self):
        JsonList(self, list_type=GamepadUpdate)


class Hat(JsonObject):

    def __init__(self, t: tuple = None, x: int = 0, y: int = 0):
        if t:
            self.x = t[0]
            self.y = t[1]
        else:
            self.x = x
            self.y = y
        JsonObject.__init__(self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class GamepadData (JsonObject):

    def __init__(self, axes: JsonList = None, buttons: JsonList = None, hats: JsonList = None):
        if not axes:
            axes = JsonList(list_type=int)
        self.axes = axes
        if not buttons:
            buttons = JsonList(list_type=int)
        self.buttons = buttons
        if not hats:
            hats = JsonList(list_type=Hat)
        self.hats = hats
        JsonObject.__init__(self)

    def get_updates(self, other) -> GamepadUpdates:
        updates = JsonList(list_type=GamepadUpdate)
        for i, a in enumerate(other.axes):
            if i >= len(self.axes) or a != self.axes[i]:
                updates.append(GamepadUpdate(update_type=UpdateType.Axis, index=i, value=other.axes[i]))

        for i, b in enumerate(other.buttons):
            if i >= len(self.buttons) or b != self.buttons[i]:
                updates.append(GamepadUpdate(update_type=UpdateType.Button, index=i, value=other.buttons[i]))

        for i, b in enumerate(other.hats):
            if i >= len(self.hats) or b != self.hats[i]:
                updates.append(GamepadUpdate(update_type=UpdateType.Hat, index=i, value=other.hats[i]))

        return updates

    def apply_updates(self, updates: GamepadUpdates):
        for u in updates:
            if u.t == UpdateType.Axis:
                while u.i >= len(self.axes):
                    self.axes.append(0)
                self.axes[u.i] = u.v
            elif u.t == UpdateType.Button:
                while u.i >= len(self.buttons):
                    self.buttons.append(0)
                self.buttons[u.i] = u.v
            elif u.t == UpdateType.Hat:
                while u.i >= len(self.hats):
                    self.hats.append(Hat())
                self.hats[u.i] = u.v

