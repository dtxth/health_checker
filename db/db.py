import os
from peewee import PostgresqlDatabase

DATABASE = os.environ.get('DATABASE', '0.0.0.0')

class DbController():
	
	def __init__(self, name, user, pwd, host,port):
		self.name = name
		self.user = user
		self.pwd = pwd
		self.host = host
		self.port = port
		self.db = self._connect()

	def _connect(self):
		return PostgresqlDatabase(self.name, user=self.user, password=self.pwd,
                           host=self.host, port=self.port)

	def createTable(self, table_model):
		with self.db:
			self.db.create_tables(table_model)

def init_db():
	return DbController('hc', 'postgres', 'postgres', DATABASE, 5432).db

