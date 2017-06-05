from math import *
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise


class Trajectory():
    globID = 0

    def __init__(self, r, gti):
        self.id = Trajectory.globID
        Trajectory.globID += 1

        self.run = r
        self.points = []
        self.gti = gti
        self.ci = -1
        self.prefixSum = [0.0]

    # filtra la corsa eliminando i punti che sono troppo vicini tra di loro - DA ELIMINARE
    def clean_run(self, param=0.5):
        index = len(self.run) - 1
        while index > 0:
            dist = euclid_dist((self.run[index].x, self.run[index].y), (self.run[index - 1].x, self.run[index - 1].y))
            if dist <= param:
                self.run.remove(self.run[index])
            index -= 1

    # filtra la corsa eliminando i punti che sono troppo vicini tra di loro
    def clean(self, param=0.5):
        run = self.getPoints()
        index = len(run) - 1
        while index > 0:
            dist = euclid_dist(run[index], run[index - 1])
            if dist <= param:
                self.points.remove(run[index])
            index -= 1

    # filtra la corsa attraverso un filtro di Kalman - DA ELIMINARE
    def kalman_filter(self):
        # crea il filtro di Kalman
        f = KalmanFilter(dim_x=2, dim_z=2)
        # inizializza il filtro
        f.x = np.array([self.run[0].x, self.run[0].y])
        index = 0
        while index < len(self.run) - 1:
            f.F = np.array([[1, 0], [0, 1]])  # state transition matrix
            f.H = np.array([[1, 0], [0, 1]])  # Measurement function
            f.P *= 1000.  # covariance matrix
            f.R = np.array([[1, 0], [0, 1]])  # state uncertainty
            f.Q = Q_discrete_white_noise(2, 1., 1.)  # process uncertainty
            f.predict()
            f.update([self.run[index + 1].x, self.run[index + 1].y])
            self.run[index + 1].x = f.x[0]
            self.run[index + 1].y = f.x[1]
            index += 1

    # filtra la corsa attraverso un filtro di Kalman
    def filter(self):
        # crea il filtro di Kalman
        f = KalmanFilter(dim_x=2, dim_z=2)
        # inizializza il filtro
        f.x = np.array(self.points[0])
        index = 0
        while index < len(self.points) - 1:
            f.F = np.array([[1, 0], [0, 1]])  # state transition matrix
            f.H = np.array([[1, 0], [0, 1]])  # Measurement function
            f.P *= 1000.  # covariance matrix
            f.R = np.array([[1, 0], [0, 1]])  # state uncertainty
            f.Q = Q_discrete_white_noise(2, 1., 1.)  # process uncertainty
            f.predict()
            f.update(self.points[index + 1])
            self.points[index + 1] = f.x
            index += 1

    def addPoint(self, p):
        self.points.append(p)

    def setPrefixSum(self):
        if len(self.points) > 0:
            index = 0
            while index < len(self.points) - 1:
                self.prefixSum.append(self.prefixSum[len(self.prefixSum) - 1] +
                                      euclid_dist(self.points[index + 1], self.points[index]))
                index += 1

    def getPoints(self):
        return self.points

    def getPrefixSum(self):
        return self.prefixSum

    def groundTruth(self):
        return self.gti

    def getClusterIdx(self):
        return self.ci

    def setClusterIdx(self, ci):
        self.ci = ci

    def length(self):
        return self.prefixSum[len(self.prefixSum) - 1]

    def draw(self, widget, color):
        xlast, ylast = None, None
        for p in self.points:
            # paint a point
            widget.create_oval(p[0] * widget.scale - 3, p[1] * widget.scale - 3, p[0] * widget.scale + 3,
                               p[1] * widget.scale + 3, fill=color)
            # paint a line
            if xlast is not None and ylast is not None:
                widget.create_line(xlast * widget.scale, ylast * widget.scale, p[0] * widget.scale, p[1] * widget.scale,
                                   smooth=True)
            xlast = p[0]
            ylast = p[1]

    @staticmethod
    def decGlobID():
        Trajectory.globID -= 1

    @staticmethod
    def resetGlobID():
        Trajectory.globID = 0

    def __str__(self):
        str = "=== Trajectory ===\n"
        str += "ground truth: %d\n" % self.gti
        str += "cluster: %d\n" % self.ci
        for p in self.points:
            str += repr(p) + ", "
        str += "\n"
        return str

    def __len__(self):
        return len(self.points)


if __name__ == "__main__":
    # Test prefix sum
    t1 = Trajectory(0)

    t1.addPoint((0, 0))
    t1.addPoint((1, 1))
    t1.addPoint((2, 2))
    t1.addPoint((3, 3))

    ps = [i * sqrt(2) for i in range(4)]
    assert (ps == t1.prefixSum)

    l = t1.length()
    assert (l == 3 * sqrt(2))

    print("TEST END")


# calcola la distanza euclidea tra due punti p1 e p2
def euclid_dist(p1, p2):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
