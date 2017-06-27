class Track:
    id = -1

    def __init__(self):
        Track.id += 1
        self.trajectories = []
        self.cluster_code = []

    def add_trajectory(self, trajectory):
        self.trajectories.append(trajectory)
        self.cluster_code.append(trajectory.getClusterIdx())
