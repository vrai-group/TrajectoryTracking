from peewee import *

# Data Base File (SQLite)
db = SqliteDatabase('database/trajectory_tracking.db')


class BaseModel(Model):
    class Meta:
        database = db


class Aoi(BaseModel):
    "Regioni di interesse che costituiscono la mappa"
    shelf = IntegerField(primary_key=True)
    p0_x = FloatField()
    p0_y = FloatField()
    p1_x = FloatField()
    p1_y = FloatField()
    p2_x = FloatField()
    p2_y = FloatField()
    p3_x = FloatField()
    p3_y = FloatField()

    class Meta:
        database = db


class Cart(BaseModel):
    "Istanze che descrivono la posizione di un carrello"
    id = IntegerField(primary_key=True)
    tag_id = CharField()
    time_stamp = DateTimeField()
    x = FloatField()
    y = FloatField()

    class Meta:
        database = db
