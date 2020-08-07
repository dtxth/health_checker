
from peewee import *
from db.db import init_db

db = init_db()
print(db)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = db

class HealthCheckModel(BaseModel):
    # memid = AutoField() 
    url = CharField()
    duration = FloatField()
    response_code = IntegerField()
    date = DateTimeField()

    class Meta:
    	table_name = 'health_check'

try:
	HealthCheckModel.create_table()
except Exception as e:
	print(e)


