from Tkinter import Canvas
from peewee_models import Aoi


class Map(Canvas):
    def __init__(self, master, scale=1, **kw):
        Canvas.__init__(self, master, **kw)
        self.scale = scale

    # Disegna un cerchio sul canvas
    def create_circle(self, x, y, r, color):
        return self.create_oval(x - r, y - r, x + r, y + r, fill=color)

    # Disegna il rettangolo relativo alla regione aoi sul canvas
    def draw_aois(self, o_limit, color):
        for aoi in Aoi.select():
            self.create_rectangle(
                aoi.p0_x * self.scale,
                aoi.p0_y * self.scale,
                aoi.p3_x * self.scale,
                aoi.p3_y * self.scale,
                fill=color
        )
            self.create_text((aoi.p0_x + aoi.p3_x) * self.scale / 2, (aoi.p0_y + aoi.p3_y) * self.scale / 2,
                             text=aoi.shelf)
        # Origine
        self.create_rectangle(o_limit[0] * self.scale, o_limit[2] * self.scale, o_limit[1] * self.scale, o_limit[3] *
                              self.scale, fill="white")
        self.create_text((o_limit[0] + o_limit[1]) * self.scale / 2, (o_limit[2] + o_limit[3]) * self.scale / 2,
                         text="ORIGINE")
        self.create_line(850, 0, 850, 680)

        # Punti di controllo
        self.create_rectangle(41.18 * self.scale, 19.53 * self.scale, 44.23 * self.scale, 21.49 *
                              self.scale, fill="white")
        self.create_rectangle(31.13 * self.scale, 19.53 * self.scale, 34.28 * self.scale, 21.49 *
                              self.scale, fill="white")
        self.create_rectangle(31.13 * self.scale, 9.55 * self.scale, 34.24 * self.scale, 12.43 *
                              self.scale, fill="white")
        self.create_rectangle(41.26 * self.scale, 9.55 * self.scale, 44.22 * self.scale, 12.43 *
                              self.scale, fill="white")
        self.create_rectangle(0.74 * self.scale, 18.74 * self.scale, 4.4 * self.scale, 22.00 *
                              self.scale, fill="white")
        self.create_rectangle(8.1 * self.scale, 18.74 * self.scale, 11.15 * self.scale, 22.00 *
                              self.scale, fill="white")
        self.create_rectangle(8.1 * self.scale, 9.08 * self.scale, 11.88 * self.scale, 12.03 *
                              self.scale, fill="white")
        self.create_rectangle(19.08 * self.scale, 9.08 * self.scale, 22.12 * self.scale, 11.35 *
                              self.scale, fill="white")

    # Disegna una rilevazione del carrello cart scelto sul canvas
    def draw_cart(self, cart, radius, color):
        self.create_circle(cart.x * self.scale, cart.y * self.scale, radius, color)

    # Disegna la corsa relativa al carrello cart
    def draw_run(self, cart_array):
        self.create_text(900, 50, text='Carrello preso in esame:    ' + str(cart_array[0].tag_id))
        self.create_text(900, 100, text='Inizio della corsa alle:    ' + str(cart_array[0].time_stamp))
        self.create_text(900, 150,
                         text='Fine della corsa alle:     ' + str(cart_array[len(cart_array) - 1].time_stamp))
        self.create_text(900, 200, text='Numero di rilevazioni:     ' + str(len(cart_array)))
        index = 0

        # disegna i punti relativi al carrello scelto nella lista 'cart' e le traiettorie che li congiungono
        while index < len(cart_array) - 1:
            pointX = cart_array[index].x * self.scale
            pointY = cart_array[index].y * self.scale
            pointXX = cart_array[index - 1].x * self.scale
            pointYY = cart_array[index - 1].y * self.scale
            self.draw_cart(cart_array[index], 3, "red")
            self.create_line(pointX, pointY, pointXX, pointYY)
            index = index + 1
