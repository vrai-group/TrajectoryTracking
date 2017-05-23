from Tkinter import Canvas


class Map(Canvas):
    def __init__(self, master, scale=1, **kw):
        Canvas.__init__(self, master, **kw)
        self.scale = scale

    def create_circle(self, x, y, r, color):
        return self.create_oval(x - r, y - r, x + r, y + r, fill=color)

    def draw_aoi(self, aoi, color):
        self.create_rectangle(
            aoi.p0_x * self.scale,
            aoi.p0_y * self.scale,
            aoi.p3_x * self.scale,
            aoi.p3_y * self.scale,
            fill=color
        )

    def draw_cart(self, cart, radius, color):
        self.create_circle(cart.x * self.scale, cart.y * self.scale, radius, color)
