from peewee import *

# Data Base File (SQLite)
db = SqliteDatabase('database/sqlite/testset.db')


class BaseModel(Model):
    class Meta:
        database = db


class Aoi(BaseModel):
    "Regioni di interesse che costituiscono la mappa"
    id = IntegerField(primary_key=True)
    x_min = FloatField()
    x_max = FloatField()
    y_min = FloatField()
    y_max = FloatField()


class Cart(BaseModel):
    "Istanze che descrivono la posizione di un carrello"
    id = IntegerField(primary_key=True)
    tag_id = CharField()
    time_stamp = DateTimeField()
    x = FloatField()
    y = FloatField()

    def inside(self, aoi):
        return self.x > aoi.x_min and self.x < aoi.x_max and self.y > aoi.y_min and self.y < aoi.y_max

    def multinside(self, aois):
        for aoi in aois.values():
            if self.inside(aoi):
                return True
        return False
