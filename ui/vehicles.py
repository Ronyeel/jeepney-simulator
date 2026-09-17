from ui.theme import (
    JEEP_GOLD, JEEP_SILVER, JEEP_SEAT, JEEP_SEAT_OCCUPIED,
    JEEP_LIGHT_FRONT, JEEP_LIGHT_REAR,
    CAR_COLORS, FONT_MAP_TINY
)

class SumoCar:
    def __init__(self, canvas, x, lane_y, speed, direction, color=None):
        self.canvas = canvas
        self.x = float(x)
        self.y = float(lane_y)
        self.speed = float(speed) * direction
        self.direction = direction
        self.color = color if color else CAR_COLORS[0]
        self.length = 46
        self.width = 22

        w, h = self.length, self.width
        self.body_id = canvas.create_rectangle(
            self.x - w // 2, self.y - h // 2,
            self.x + w // 2, self.y + h // 2,
            fill=self.color, outline="#000000", width=2
        )
        ws_x = self.x + (w // 2 - 14) * direction
        self.ws_id = canvas.create_rectangle(
            ws_x - 4, self.y - h // 2 + 3,
            ws_x + 4, self.y + h // 2 - 3,
            fill="#0f172a", outline=""
        )

    def update(self):
        self.x += self.speed
        w, h, d = self.length, self.width, self.direction
        self.canvas.coords(
            self.body_id,
            self.x - w // 2, self.y - h // 2,
            self.x + w // 2, self.y + h // 2
        )
        ws_x = self.x + (w // 2 - 14) * d
        self.canvas.coords(
            self.ws_id,
            ws_x - 4, self.y - h // 2 + 3,
            ws_x + 4, self.y + h // 2 - 3
        )

    def set_color(self, color):
        self.color = color
        self.canvas.itemconfig(self.body_id, fill=color)

    def destroy(self):
        self.canvas.delete(self.body_id)
        self.canvas.delete(self.ws_id)

class Tricycle:
    def __init__(self, canvas, x, lane_y, speed, direction=1):
        self.canvas = canvas
        self.x = float(x)
        self.y = float(lane_y)
        self.speed = float(speed) * direction
        self.direction = direction

        d = self.direction
        self.bike_id = canvas.create_rectangle(
            self.x - 14, self.y - 3,
            self.x + 14, self.y + 3,
            fill="#334155", outline="#0f172a", width=1
        )
        self.sidecar_id = canvas.create_rectangle(
            self.x - 11, self.y + 4,
            self.x + 11, self.y + 14,
            fill="#2563eb", outline="#1d4ed8", width=1
        )

    def update(self):
        self.x += self.speed
        self.canvas.coords(
            self.bike_id,
            self.x - 14, self.y - 3,
            self.x + 14, self.y + 3
        )
        self.canvas.coords(
            self.sidecar_id,
            self.x - 11, self.y + 4,
            self.x + 11, self.y + 14
        )

    def destroy(self):
        self.canvas.delete(self.bike_id)
        self.canvas.delete(self.sidecar_id)

class Jeepney:
    W_BODY = 84
    H_BODY = 28

    def __init__(self, canvas, spawn_x, lane_y, bay_x, bay_y, capacity=8):
        self.canvas = canvas
        self.x = float(spawn_x)
        self.y = float(lane_y)
        self.bay_x = float(bay_x)
        self.bay_y = float(bay_y)
        self.lane_y = float(lane_y)
        self.capacity = capacity
        self.passengers_onboard = 0
        self.target_served = capacity
        self.state = "approaching"  
        self.approach_speed = 9.5
        self.depart_speed = 1.0
        self.depart_ticks = 0
        self.prep_ticks = 0

        w, h = self.W_BODY, self.H_BODY

        self.wheel_ids = []
        for wx, wy in [
            (self.x + w // 2 - 20, self.y - h // 2 - 2),
            (self.x + w // 2 - 20, self.y + h // 2),
            (self.x - w // 2 + 14, self.y - h // 2 - 2),
            (self.x - w // 2 + 14, self.y + h // 2),
        ]:
            wh_id = canvas.create_rectangle(wx - 7, wy, wx + 7, wy + 2, fill="#0f172a", outline="")
            self.wheel_ids.append(wh_id)

        self.rear_bumper_id = canvas.create_rectangle(
            self.x - w // 2 - 3, self.y - h // 2 + 2,
            self.x - w // 2, self.y + h // 2 - 2,
            fill=JEEP_SILVER, outline="#64748b", width=1
        )

        self.body_id = canvas.create_rectangle(
            self.x - w // 2, self.y - h // 2,
            self.x + w // 2, self.y + h // 2,
            fill=JEEP_GOLD, outline="#78350f", width=2
        )

        self.front_bumper_id = canvas.create_rectangle(
            self.x + w // 2, self.y - h // 2 + 2,
            self.x + w // 2 + 4, self.y + h // 2 - 2,
            fill=JEEP_SILVER, outline="#64748b", width=1
        )

        ws_x = self.x + w // 2 - 20
        self.ws_id = canvas.create_rectangle(
            ws_x - 3, self.y - h // 2 + 3,
            ws_x + 3, self.y + h // 2 - 3,
            fill="#38bdf8", outline=""
        )

        cabin_x = self.x - w // 2 + 6
        cabin_w = w - 30
        self.cabin_x0 = cabin_x
        self.cabin_w = cabin_w
        self.cabin_id = canvas.create_rectangle(
            cabin_x, self.y - h // 2 + 3,
            cabin_x + cabin_w, self.y + h // 2 - 3,
            fill=JEEP_SEAT, outline=""
        )

        half_cap = max(1, self.capacity // 2)
        seat_w = (cabin_w - 4) / half_cap
        self.seat_ids = []
        for s in range(half_cap):
            sx = cabin_x + 2 + s * seat_w
            top_id = canvas.create_rectangle(
                sx, self.y - h // 2 + 4,
                sx + seat_w - 2, self.y - h // 2 + 9,
                fill="#334155", outline=""
            )
            bot_id = canvas.create_rectangle(
                sx, self.y + h // 2 - 9,
                sx + seat_w - 2, self.y + h // 2 - 4,
                fill="#334155", outline=""
            )
            self.seat_ids.append((top_id, bot_id))

        self.hl_top_id = canvas.create_oval(
            self.x + w // 2 + 1, self.y - h // 2 + 3,
            self.x + w // 2 + 4, self.y - h // 2 + 7,
            fill=JEEP_LIGHT_FRONT, outline=""
        )
        self.hl_bot_id = canvas.create_oval(
            self.x + w // 2 + 1, self.y + h // 2 - 7,
            self.x + w // 2 + 4, self.y + h // 2 - 3,
            fill=JEEP_LIGHT_FRONT, outline=""
        )

        self.tl_top_id = canvas.create_rectangle(
            self.x - w // 2 - 2, self.y - h // 2 + 3,
            self.x - w // 2, self.y - h // 2 + 7,
            fill=JEEP_LIGHT_REAR, outline=""
        )
        self.tl_bot_id = canvas.create_rectangle(
            self.x - w // 2 - 2, self.y + h // 2 - 7,
            self.x - w // 2, self.y + h // 2 - 3,
            fill=JEEP_LIGHT_REAR, outline=""
        )

        self.blinker_id = canvas.create_rectangle(
            self.x + w // 2 - 10, self.y - h // 2 - 1,
            self.x + w // 2 - 4, self.y - h // 2 + 2,
            fill="#78350f", outline=""
        )

    def start_departure(self):
        if self.state in ("waiting", "docking"):
            self.state = "preparing_departure"
            self.prep_ticks = 0
            self.canvas.itemconfigure(self.blinker_id, fill="#f59e0b")

    def update(self):
        w, h = self.W_BODY, self.H_BODY

        if self.state == "approaching":
            target_x = self.bay_x - 10
            dx = target_x - self.x
            slow_zone = 260.0
            spd = self.approach_speed
            if abs(dx) < slow_zone:
                spd = max(2.5, spd * (abs(dx) / slow_zone))
            if abs(dx) < 3.5:
                self.x = target_x
                self.y = self.bay_y
                self.state = "docking"
            else:
                self.x += min(spd, abs(dx))
                if abs(self.x - self.bay_x) < 300:
                    pull = self.bay_y - self.y
                    self.y += pull * 0.10

        elif self.state == "docking":
            dx = self.bay_x - self.x
            if abs(dx) < 2.0:
                self.x = self.bay_x
                self.state = "waiting"
            else:
                self.x += min(2.5, abs(dx))

        elif self.state == "waiting":
            self.canvas.itemconfigure(self.blinker_id, fill="#78350f")

        elif self.state == "preparing_departure":
            self.prep_ticks += 1
            blink_on = (self.prep_ticks // 3) % 2 == 0
            self.canvas.itemconfigure(self.blinker_id, fill="#f59e0b" if blink_on else "#78350f")

            jitter_y = 0.8 if (self.prep_ticks % 2 == 1) else -0.8
            self.y += jitter_y

            if self.prep_ticks >= 20:
                self.state = "departing"
                self.depart_speed = 1.0
                self.depart_ticks = 0

        elif self.state == "departing":
            self.depart_ticks += 1

            if self.depart_ticks <= 30:
                blink_on = (self.depart_ticks // 3) % 2 == 0
                self.canvas.itemconfigure(self.blinker_id, fill="#f59e0b" if blink_on else "#78350f")
            else:
                self.canvas.itemconfigure(self.blinker_id, fill="#78350f")

            if self.depart_speed < 8.0:
                self.depart_speed += 0.18
            self.x += self.depart_speed

            pull = self.lane_y - self.y
            self.y += pull * 0.08

            canvas_w = max(self.canvas.winfo_width(), getattr(self.canvas, "W", 1280))
            rear_bumper_x = self.x - w // 2
            if rear_bumper_x > canvas_w + 50:
                self.state = "done"

        for i, (wx, wy) in enumerate([
            (self.x + w // 2 - 20, self.y - h // 2 - 2),
            (self.x + w // 2 - 20, self.y + h // 2),
            (self.x - w // 2 + 14, self.y - h // 2 - 2),
            (self.x - w // 2 + 14, self.y + h // 2),
        ]):
            self.canvas.coords(self.wheel_ids[i], wx - 7, wy, wx + 7, wy + 2)

        self.canvas.coords(
            self.rear_bumper_id,
            self.x - w // 2 - 3, self.y - h // 2 + 2,
            self.x - w // 2, self.y + h // 2 - 2
        )
        self.canvas.coords(
            self.front_bumper_id,
            self.x + w // 2, self.y - h // 2 + 2,
            self.x + w // 2 + 4, self.y + h // 2 - 2
        )

        self.canvas.coords(
            self.body_id,
            self.x - w // 2, self.y - h // 2,
            self.x + w // 2, self.y + h // 2
        )

        ws_x = self.x + w // 2 - 20
        self.canvas.coords(
            self.ws_id,
            ws_x - 3, self.y - h // 2 + 3,
            ws_x + 3, self.y + h // 2 - 3
        )

        cabin_x = self.x - w // 2 + 6
        self.canvas.coords(
            self.cabin_id,
            cabin_x, self.y - h // 2 + 3,
            cabin_x + self.cabin_w, self.y + h // 2 - 3
        )

        half_cap = max(1, self.capacity // 2)
        seat_w = (self.cabin_w - 4) / half_cap
        for s, (top_id, bot_id) in enumerate(self.seat_ids):
            sx = cabin_x + 2 + s * seat_w
            self.canvas.coords(
                top_id,
                sx, self.y - h // 2 + 4,
                sx + seat_w - 2, self.y - h // 2 + 9
            )
            self.canvas.coords(
                bot_id,
                sx, self.y + h // 2 - 9,
                sx + seat_w - 2, self.y + h // 2 - 4
            )

        self.canvas.coords(
            self.hl_top_id,
            self.x + w // 2 + 1, self.y - h // 2 + 3,
            self.x + w // 2 + 4, self.y - h // 2 + 7
        )
        self.canvas.coords(
            self.hl_bot_id,
            self.x + w // 2 + 1, self.y + h // 2 - 7,
            self.x + w // 2 + 4, self.y + h // 2 - 3
        )

        self.canvas.coords(
            self.tl_top_id,
            self.x - w // 2 - 2, self.y - h // 2 + 3,
            self.x - w // 2, self.y - h // 2 + 7
        )
        self.canvas.coords(
            self.tl_bot_id,
            self.x - w // 2 - 2, self.y + h // 2 - 7,
            self.x - w // 2, self.y + h // 2 - 3
        )

        self.canvas.coords(
            self.blinker_id,
            self.x + w // 2 - 10, self.y - h // 2 - 1,
            self.x + w // 2 - 4, self.y - h // 2 + 2
        )

    def set_occupied(self, count):
        self.passengers_onboard = count
        half_cap = max(1, self.capacity // 2)
        for s, (top_id, bot_id) in enumerate(self.seat_ids):
            occ_top = (s < count)
            occ_bot = (half_cap + s < count)
            self.canvas.itemconfig(top_id, fill=JEEP_SEAT_OCCUPIED if occ_top else "#334155")
            self.canvas.itemconfig(bot_id, fill=JEEP_SEAT_OCCUPIED if occ_bot else "#334155")

    def destroy(self):
        for wid in self.wheel_ids:
            self.canvas.delete(wid)
        self.wheel_ids.clear()
        self.canvas.delete(self.rear_bumper_id)
        self.canvas.delete(self.front_bumper_id)
        self.canvas.delete(self.body_id)
        self.canvas.delete(self.ws_id)
        self.canvas.delete(self.cabin_id)
        self.canvas.delete(self.hl_top_id)
        self.canvas.delete(self.hl_bot_id)
        self.canvas.delete(self.tl_top_id)
        self.canvas.delete(self.tl_bot_id)
        self.canvas.delete(self.blinker_id)
        for top_id, bot_id in self.seat_ids:
            self.canvas.delete(top_id)
            self.canvas.delete(bot_id)
        self.seat_ids.clear()
