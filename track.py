class Track:
    id = -1

    def __init__(self):
        Track.id += 1
        self.trajectories = []
        self.cluster_code = []

    def addTrajectory(self, t):
        self.trajectories.append(t)
        self.cluster_code.append(t.getClusterIdx())