from math import *
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise


class Trajectory():
    globID = 0

    def __init__(self, run, gti):
        self.id = Trajectory.globID
        Trajectory.globID += 1

        self.run = list(run)
        self.points = []
        self.gti = gti
        self.ci = -1
        self.prefixSum = [0.0]

        self.build()

    def clean(self, param=0.9, dist=3.):
        "Filtra la corsa eliminando i punti che sono troppo vicini tra di loro"
        run = self.getPoints()
        i = 0
        while i < len(run) - 1:
            ii = i + 1
            dist_i = 0
            while ii < len(run) - 1:
                dist_i_ii = euclid_dist(run[i], run[ii])
                # dist_ii = euclid_dist(run[ii-1], run[ii])
                # dist_i += dist_ii
                if dist_i_ii < param:
                    self.points.remove(run[ii])
                ii += 1
            i += 1
        # Aggiorna la lunghezza della corsa
        self.setPrefixSum()

    def filter(self):
        "Filtra la corsa attraverso un filtro di Kalman"
        # Crea il filtro di Kalman
        f = KalmanFilter(dim_x=2, dim_z=2)
        # Inizializza il filtro
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

    def build(self):
        "Costruisce i punti della traiettoria"
        for cart in self.run:
            self.addPoint((cart.x, cart.y))
        # Aggiorna la lunghezza della corsa
        self.setPrefixSum()

    def setPrefixSum(self):
        "Calcola e aggiorna la lunghezza della traiettoria"
        self.prefixSum = [0.0]
        if len(self.points) > 0:
            index = 0
            while index < len(self.points) - 1:
                self.prefixSum.append(self.prefixSum[len(self.prefixSum) - 1] +
                                      euclid_dist(self.points[index + 1], self.points[index]))
                index += 1

    def getPrefixSum(self):
        return self.prefixSum

    def addPoint(self, p):
        self.points.append(p)

    def getPoints(self):
        return self.points

    def groundTruth(self):
        return self.gti

    def getClusterIdx(self):
        return self.ci

    def setClusterIdx(self, ci):
        self.ci = ci

    def length(self):
        return self.prefixSum[len(self.prefixSum) - 1]

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

    ##################
    ## DA ELIMINARE ##
    ##################

    # Filtra la corsa eliminando i punti che sono troppo vicini tra di loro
    def clean_run(self, param=0.5):
        index = len(self.run) - 1
        while index > 0:
            dist = euclid_dist((self.run[index].x, self.run[index].y), (self.run[index - 1].x, self.run[index - 1].y))
            if dist <= param:
                self.run.remove(self.run[index])
            index -= 1

    # Filtra la corsa attraverso un filtro di Kalman
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
    assert (len(p1) == len(p2))
    return sqrt(sum([((p1[i] - p2[i])) ** 2 for i in range(len(p1))]))
