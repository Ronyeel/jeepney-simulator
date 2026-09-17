class Passenger:
    WALK_SPEED = 3.0
    BOARD_SPEED = 4.0
    RADIUS = 5

    def __init__(self, canvas, spawn_x, spawn_y, queue_x, queue_y, color):
        self.canvas = canvas
        self.x = float(spawn_x)
        self.y = float(spawn_y)
        self.target_x = float(queue_x)
        self.target_y = float(queue_y)
        self.color = color
        self.state = "walking"  
        self.seat_x = None
        self.seat_y = None

        r = self.RADIUS
        self.item_id = canvas.create_oval(
            self.x - r, self.y - r, self.x + r, self.y + r,
            fill=self.color, outline="#000000", width=1
        )

    def update(self):
        if self.state == "queued" or self.state == "seated":
            return

        r = self.RADIUS

        if self.state == "walking":
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < self.WALK_SPEED:
                self.x = self.target_x
                self.y = self.target_y
                self.state = "queued"
            else:
                inv = self.WALK_SPEED / dist
                self.x += dx * inv
                self.y += dy * inv
            self.canvas.coords(self.item_id, self.x - r, self.y - r, self.x + r, self.y + r)

        elif self.state == "boarding":
            if self.seat_x is not None:
                dx = self.seat_x - self.x
                dy = self.seat_y - self.y
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < self.BOARD_SPEED:
                    self.state = "seated"
                    self.canvas.delete(self.item_id)
                    self.item_id = None
                else:
                    inv = self.BOARD_SPEED / dist
                    self.x += dx * inv
                    self.y += dy * inv
                    self.canvas.coords(self.item_id, self.x - r, self.y - r, self.x + r, self.y + r)

    def destroy(self):
        if self.item_id:
            self.canvas.delete(self.item_id)
            self.item_id = None
