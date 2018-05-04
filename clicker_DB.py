import sqlite3

#  wont need this later
def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


class clickerDB:
	def __init__(self):
		print("Connecting...")
		self.connection = sqlite3.connect("admin.db")
		self.connection.row_factory = dict_factory
		self.cursor = self.connection.cursor()
		print("init finished")

	def __del__(self):
		self.connection.close()
		print("disconnecting...")

	def createNewRecord(self, fName, lName, username, password):
		self.cursor.execute("INSERT INTO adminList (fName, lName, username, password) VAlUES (?, ?, ?, ?)",
			[fName, lName, username, password])
		self.connection.commit()

	def getAllRecords(self):
		self.cursor.execute("SELECT * FROM adminList")
		return self.cursor.fetchall()

	def getRecord(self, adminID):
		self.cursor.execute("SELECT * FROM adminList WHERE ID = ?", [adminID])
		return self.cursor.fetchone()

	def deleteRecord(self, adminID):
		self.cursor.execute("DELETE FROM adminList WHERE ID = ?", [adminID])
		self.connection.commit()
		return 

	def updateRecord(self, fName, lName, username, password, value):
		self.cursor.execute("UPDATE adminList  SET fName = ?, lName = ?, username = ?, password = ? WHERE ID = ?",
			[fName, lName, username, password, value])
		self.connection.commit()
		
		return
	def checkUsername(self, username):
		self.cursor.execute("SELECT * FROM adminList WHERE username = ?", [username])
		rows = self.cursor.fetchall()
		return rows

	def createNewTopic(self, topic):
		self.cursor.execute("INSERT INTO TopicList (topic) VAlUES (?)",
			[topic])
		self.connection.commit()

	def createNewQuestion(self, question, topic, a, b, c, d):
		self.cursor.execute("INSERT INTO questionList (question, topicID, choiceA, choiceB, choiceC, choiceD) VAlUES (?,?,?,?,?,?)",
			[question, topic, a, b, c, d])
		self.connection.commit()

	def getAllTopics(self):
		self.cursor.execute("SELECT * FROM TopicList")
		return self.cursor.fetchall()

	def getAllQuestions(self, topicId):
		print(topicId)
		self.cursor.execute("SELECT * FROM questionList WHERE topicID = ?", [topicId])
		return self.cursor.fetchall()

	def getTopic(self, topicId):
		self.cursor.execute("SELECT * FROM TopicList WHERE ID = ?", [topicId])
		return self.cursor.fetchone()

	def getQuestion(self, questionId):
		self.cursor.execute("SELECT * FROM questionList WHERE ID = ?", [questionId])
		return self.cursor.fetchone()

	def deleteTopic(self, topidId):
		self.cursor.execute("DELETE FROM TopicList WHERE ID = ?", [topidId])
		self.connection.commit()
		self.cursor.execute("DELETE FROM questionList WHERE topicID = ?", [topidId])
		self.connection.commit()
		return 

	def deleteQuestion(self, questionId):
		self.cursor.execute("DELETE FROM questionList WHERE ID = ?", [questionId])
		self.connection.commit()
		return 

	def updateQuestion(self, question, value):
		self.cursor.execute("UPDATE questionList  SET question = ? WHERE ID = ?",
			[question, value])
		self.connection.commit()
		return




