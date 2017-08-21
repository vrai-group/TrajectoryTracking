from Tkinter import *
import datetime

class Map(Canvas):
    def __init__(self, master, scale=1, **kw):
        Canvas.__init__(self, master, **kw)
        self.scale = scale
        # Rightside Log
        self.T = Text(self, height=35, width=45)
        self.T.place(x=830, y=30)
        self.T.config(state="disabled")

    def create_circle(self, x, y, r, color):
        "Disegna un cerchio sul canvas"
        return self.create_oval(x - r, y - r, x + r, y + r, fill=color)

    def draw_aoi(self, aoi, color, text=""):
        "Disegna il rettangolo relativo alla regione aoi sul canvas"

        self.create_rectangle(aoi.x_min * self.scale, aoi.y_max * self.scale,
                              aoi.x_max * self.scale, aoi.y_min * self.scale,
                              fill=color)
        self.create_text((aoi.x_min + aoi.x_max) * self.scale / 2,
                         (aoi.y_max + aoi.y_min) * self.scale / 2,
                         text=text)

    def generate_eps(self):
        self.postscript(file=datetime.datetime.now().isoformat() + " - screenshot.eps")

    def draw_trajectory(self, trajectory, color):
        "Disegna una traiettoria sulla mappa"
        xlast, ylast = None, None
        for p in trajectory.points:
            # Disegna un punto
            self.create_circle(p[0] * self.scale, p[1] * self.scale, 3, color)
            # Disegna un segmento
            if xlast is not None and ylast is not None:
                self.create_line(xlast * self.scale, ylast * self.scale, p[0] * self.scale,
                                 p[1] * self.scale, smooth=True)
            xlast = p[0]
            ylast = p[1]

    def draw_init(self, aois, origin, controls):
        "Inizializza i disegni di aree di interesse, origine e controllo"

        # Resetta la mappa
        self.delete("all")

        # Disegna le aree di interesse
        for aoi in aois:
            self.draw_aoi(aoi, color="#D3D3D3", text=aoi.id)

        # Disegna l'area di origine
        self.draw_aoi(origin, color="peachpuff", text="ORIGIN")

        # Disegna le aree di controllo
        for c in controls:
            self.draw_aoi(controls[c], color="peachpuff", text=c)

    def log(self, txt):
        self.T.config(state="normal")
        self.T.insert(END, txt)
        self.T.config(state="disabled")

    def clear_log(self):
        self.T.config(state="normal")
        self.T.delete(1.0, END)
        self.T.config(state="disabled")
