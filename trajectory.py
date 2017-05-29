from peewee_models import Cart


class Trajectory():
    run = []

    def __init__(self, r):
        self.run = r
