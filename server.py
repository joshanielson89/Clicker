from http.server import BaseHTTPRequestHandler, HTTPServer
import random
import json
import urllib.parse 
from clicker_DB import * 
import sys
from passlib.hash import bcrypt


gAnswerCountA = 0
gAnswerCountB = 0
gAnswerCountC = 0
gAnswerCountD = 0
gSessionID = 12113  #something unguessable
gSessionCount = 0
gCurrentQuestion = {}



class MyRequestHandler(BaseHTTPRequestHandler):
	def do_OPTIONS(self):
		self.send_response(200)
		self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		self.send_header("Access-Control-Allow-Headers", "Content-type")
		self.end_headers()

	def do_GET(self):
		parsedPath = splitPath(self.path)
		if parsedPath[0] == "admin":
			self.handleAdminLIST()
		elif parsedPath[0] == "currentQuestion":
			self.handleReturnQuestion()
		elif parsedPath[0] == "topics":
			self.handleTopicLIST()
		elif parsedPath[0] == "setQuestion":
			self.handleSetCurrentQuestion(parsedPath[1])
		elif parsedPath[0] == "getQuestion":
			self.handleGetCurrentQuestion()
		elif parsedPath[0] == "questions":
			self.handleQuestionList(parsedPath[1])
		elif parsedPath[0] == "getAnswers":
			self.handleAnswerReturn()
		elif parsedPath[1] == "cSessionID":
			self.handleGetSessionID()
		else:
			self.send404()

	def do_POST(self):
		if self.path =="/admin":
			self.handleAdminPOST()
		elif self.path == "/topics":
			self.handleTopicPOST()
		elif self.path == "/answer":
			self.handleAnswerPOST()
		elif self.path == "/question":
			self.handleQuestionPOST()
		elif splitPath(self.path)[1] == "sessions":
			self.handleLogin()
		else:
			self.send404()

	def do_DELETE(self):
		parsedPath = splitPath(self.path)
		if parsedPath[0] == "admin":
			db = clickerDB()
			if db.getRecord(parsedPath[1]):
				self.handleAdminDELETE(parsedPath)
			else:
				self.send404()
		elif parsedPath[0] == "topics":
			db = clickerDB()
			if db.getTopic(parsedPath[1]):
				self.handleTopicDELETE(parsedPath)
			else:
				self.send404()
		elif parsedPath[0] == "question":
			db = clickerDB()
			if db.getQuestion(parsedPath[1]):
				self.handleQuestionDELETE(parsedPath)
			else:
				self.send404()
		else:
			self.send404()

	def do_PUT(self): ## UPDATE
		parsedPath = splitPath(self.path)
		if parsedPath[0] == "admin" and parsedPath[1] is not None:  
			self.handleAdminPUT(parsedPath)
		elif parsedPath[0] == "topics" and parsedPath[1] is not None:
			self.handleQuestionPUT(parsedPath)
		elif splitPath(self.path)[1] == "reset":
			self.handleChangePassword()
		else:
			self.send404()
		return


	# ******* ADMINISTRATOR REQUEST HANDLERS **********
	def handleAdminLIST(self):
		db = clickerDB()
		self.getInit()
		lines = db.getAllRecords()
		lines = json.dumps(lines)
		self.wfile.write(bytes(lines, "utf-8"))
		return

	def handleAdminRETRIEVE(self, parsedPath):
		db = clickerDB()
		lines = db.getRecord(parsedPath[1])
		if lines != None:
			self.getInit()
			lines = json.dumps(lines)
			self.wfile.write(bytes(lines, "utf-8"))
		else:
			self.send404()
			return
		return

	def handleAdminPOST(self):
		db = clickerDB()
		length = int(self.headers["Content-length"]) 
		body = self.rfile.read(length).decode("utf-8")
		parsed_body = dict(urllib.parse.parse_qsl(body))
		print("body is: ", body)
		print("parsed body is: ", parsed_body)

		fname = parsed_body["fname"]
		lname = parsed_body["lname"]
		username = parsed_body["username"]
		password = bcrypt.encrypt(parsed_body["password"])
		print(len(db.checkUsername(username)))
		if len(db.checkUsername(username)) == 0:
			print("starting new admin....")
			rowId = db.createNewRecord(fname, lname, username, password)

			self.send_response(201)
			self.send_header("Content-Type", "text/plain")
			self.end_headers()
			self.wfile.write(bytes(str(fname) + str(lname) + "was registered successfully.", "utf-8"))
		else:
			self.send_response(422)
			self.send_header("Content-Type", "text/plain")
			self.end_headers()
			self.wfile.write(bytes("This email is already registered.", "utf-8"))
		return

	def handleAdminDELETE(self, parsedPath):
		db = clickerDB()
		db.deleteRecord(int(parsedPath[1]))
		self.send_response(200) #200 means "ok"
		self.send_header("Content-type", "application/json")
		self.end_headers()
		return

	def handleAdminPUT(self, parsedPath):
		db = clickerDB()
		length = int(self.headers["Content-length"]) #every header describes the content and it's length
		body = self.rfile.read(length).decode("utf-8")
		parsed_body = dict(urllib.parse.parse_qsl(body))
		print("body is: ", body)
		print("parsed body is: ", parsed_body)

		#this is what the user input
		fName = parsed_body["fname"]
		lName = parsed_body["lname"]
		username = parsed_body["username"]
		thisId = parsed_body["ID"]

		arr = db.checkUsername(username)
		print(db.checkUsername(username))
		if len(arr) > 0:
			print(arr)
			arr = arr[0]
			userData = {
				'id': arr['ID'],
				'FirstName': arr['fName'],
				'LastName': arr['lName'],
				'username': arr['username'],
				'Password': arr['password']
			}

			db.updateRecord(fName, lName, username, userData['Password'], userData['id'])
		else:
			print("fist if")
			self.handle401()

	# ****** QUESTION REQUEST HANDLERS *************
	def handleTopicLIST(self):
		db = clickerDB() 
		self.getInit()
		lines = db.getAllTopics()
		lines = json.dumps(lines)
		self.wfile.write(bytes(lines, "utf-8"))
		return

	def handleQuestionList(self, topicId):
		db = clickerDB()
		self.getInit()
		lines = db.getAllQuestions(topicId)
		print(lines)
		lines = json.dumps(lines)
		print(lines)
		self.wfile.write(bytes(lines, "utf-8"))
		return

	def handleTopicPOST(self):
		db = clickerDB()
		length = int(self.headers["Content-length"]) 
		body = self.rfile.read(length).decode("utf-8")
		parsed_body = dict(urllib.parse.parse_qsl(body))
		print("body is: ", body)
		print("parsed body is: ", parsed_body)

		question = parsed_body["question"]
		
		db.createNewTopic(question)
		self.send_response(201)
		self.end_headers()
		return

	def handleQuestionPOST(self):
		db = clickerDB()
		length = int(self.headers["Content-length"])
		body = self.rfile.read(length).decode("utf-8")
		parsed_body = dict(urllib.parse.parse_qsl(body))
		print("body is: ", body)
		print("parsed body is: ", parsed_body)

		question = parsed_body["question"]
		topic = parsed_body["topic"]
		choice1 = parsed_body["choiceA"]
		choice2 = parsed_body["choiceB"]
		choice3 = parsed_body["choiceC"]
		choice4 = parsed_body["choiceD"]

		
		db.createNewQuestion(question, topic, choice1, choice2, choice3, choice4)
		self.send_response(201)
		self.end_headers()
		return

	def handleTopicDELETE(self, parsedPath):
		db = clickerDB()
		db.deleteTopic(int(parsedPath[1]))
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		return

	def handleQuestionDELETE(self, parsedPath):
		db = clickerDB()
		db.deleteQuestion(int(parsedPath[1]))
		self.send_response(200) 
		self.send_header("Content-type", "application/json")
		self.end_headers()
		return

	# ****** Other Handlers ********
	# This will return a question
	def handleProjectQuesion(self):
		db = clickerDB()
		self.getInit()
		line = db.getQuestion()
		line = json.dumps(line)
		global gCurrentQuestion
		global gAnswerCountA
		global gAnswerCountB
		global gAnswerCountC
		global gAnswerCountD
		gAnswerCountA = 0
		gAnswerCountB = 0
		gAnswerCountC = 0
		gAnswerCountD = 0
		gCurrentQuestion = line
		self.wfile.write(bytes(lines, "utf-8"))

	def handleSetCurrentQuestion(self, qID):
		db = clickerDB()
		self.getInit()
		changeSessionID()
		lines = db.getQuestion(qID)
		global gCurrentQuestion
		lines = json.dumps(lines)
		gCurrentQuestion = lines
		print("response: " , gCurrentQuestion)
		self.wfile.write(bytes(lines, "utf-8"))
		return 

	def handleGetCurrentQuestion(self):
		self.getInit()
		global gCurrentQuestion
		lines = json.dumps(gCurrentQuestion)
		self.wfile.write(bytes(lines, "utf-8"))
		return 

	def handleGetSessionID(self):
		self.getInit()
		global gSessionID
		lines = json.dumps(gSessionID)
		self.wfile.write(bytes(lines, "utf-8"))
		return 

	def handleReturnQuestion(self):
		self.getInit()
		global gCurrentQuestion
		if gCurrentQuestion != {}:
			line = gCurrentQuestion
		self.wfile.write(bytes(line, "utf-8"))

	def handleAnswerReturn(self):
		self.getInit()
		global gAnswerCountA
		global gAnswerCountB
		global gAnswerCountC
		global gAnswerCountD
		answers = {}
		answers["A"] = gAnswerCountA
		answers["B"] = gAnswerCountB
		answers["C"] = gAnswerCountC
		answers["D"] = gAnswerCountD
		answers = json.dumps(answers)
		self.wfile.write(bytes(answers, "utf-8"))
		gAnswerCountA = 0
		gAnswerCountB = 0
		gAnswerCountC = 0
		gAnswerCountD = 0

	def handleAnswerPOST(self):
		length = int(self.headers["Content-length"])
		body = self.rfile.read(length).decode("utf-8")
		parsed_body = dict(urllib.parse.parse_qsl(body))
		print("body is: ", body)
		print("parsed body is: ", parsed_body)

		answer = parsed_body["answer"]
		global gAnswerCountA
		global gAnswerCountB
		global gAnswerCountC
		global gAnswerCountD

		if answer == "A":
			gAnswerCountA += 1
		elif answer == "B":
			gAnswerCountB += 1
		elif answer == "C":
			gAnswerCountC += 1
		else:
			gAnswerCountD += 1

		print("A: " + str(gAnswerCountA) + "\n" + "B: " + str(gAnswerCountB) + "\n" + "C: " + str(gAnswerCountC) + "\n" + "D: " + str(gAnswerCountD) + "\n")
		self.send_response(201) 
		self.end_headers()
		return


	def handleLogin(self):
		db = clickerDB()
		length = int(self.headers["Content-length"])
		body = self.rfile.read(length).decode("utf-8")
		parsed_body = dict(urllib.parse.parse_qsl(body))
		print("body is: ", body)
		print("parsed body is: ", parsed_body)

		#this is what the user input
		username = parsed_body["username"]
		password = parsed_body["password"]

		arr = db.checkUsername(username)
		print(db.checkUsername(username))
		if len(arr) > 0:
			print(arr)
			arr = arr[0]
			userData = {
				'id': arr['ID'],
				'FirstName': arr['fName'],
				'LastName': arr['lName'],
				'username': arr['username'],
				'Password': arr['password']
			}

			if bcrypt.verify(password, userData['Password']): 
				self.send_response(200)
				self.send_header("Content-Type", "text/plain")
				self.end_headers()
				self.wfile.write(bytes(str(userData["FirstName"]) + " " + str(userData["LastName"]) + " logged in successfully.", "utf-8"))
			else:
				self.handle401()
		else:
			print("fist if")
			self.handle401()

	def handleChangePassword(self):
		db = clickerDB()
		length = int(self.headers["Content-length"]) 
		body = self.rfile.read(length).decode("utf-8")
		parsed_body = dict(urllib.parse.parse_qsl(body))
		print("body is: ", body)
		print("parsed body is: ", parsed_body)

		#this is what the user input
		username = parsed_body["username"]
		password = parsed_body["password"]
		newPassword = bcrypt.encrypt(parsed_body["newPassword"])

		arr = db.checkUsername(username)
		print(db.checkUsername(username))
		if len(arr) > 0:
			print(arr)
			arr = arr[0]
			userData = {
				'id': arr['ID'],
				'FirstName': arr['fName'],
				'LastName': arr['lName'],
				'username': arr['username'],
				'Password': arr['password']
			}

			if bcrypt.verify(password, userData['Password']): 
				self.session["userId"] = userData["id"]
				self.send_response(200)
				db.updateRecord(userData['FirstName'], userData['LastName'], userData['username'], newPassword, userData['id'])
				self.send_header("Content-Type", "text/plain")
				self.end_headers()
				self.wfile.write(bytes("User has been updated" , "utf-8"))
			else:
				self.handle401()
		else:
			self.handle401()


	def getInit(self):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		return

	def send404(self):
		self.send_response(404)
		self.end_headers()
		self.wfile.write(bytes("Content not found", "utf-8"))
		return

	def end_headers(self):
		self.send_header('Access-Control-Allow-Origin', "*")
		self.send_header('Access-Control-Allow-Credentials', 'true')
		BaseHTTPRequestHandler.end_headers(self)

	def handle401(self):
		self.send_response(401)
		self.send_header("Content-Type", "text/plain")
		self.end_headers()
		self.wfile.write(bytes("You are not authorized for this request.", "utf-8"))

def changeSessionID():
	global gSessionID
	randNum = random.randrange(1000,10000)
	gSessionID = randNum
	print (gSessionID)
	return

def splitPath(path):
	newList = path.split("/")
	newList = newList[1:]
	return newList


def main():
	listen = ("127.0.0.1", 8081)
	server = HTTPServer(listen ,MyRequestHandler)

	print("Listening...")
	server.serve_forever()

main()

