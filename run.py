import flask
import os
import json
from flask_pymongo import PyMongo
from flask import jsonify
from flask import request
from bson.json_util import dumps
from flask import Response

app = flask.Flask(__name__)
app.config["MONGO_URI"] = "MONGO_URI" ## PUT YOUR MONGODB CREDENTIALS
app.config["DEBUG"] = False
mongo = PyMongo(app)
screens = mongo.db.tickets

# API to show details of all screens
@app.route('/', methods=['GET'])
def home():
	output = screens.find()
	return dumps(output)

# API to accept details of a movie screen
@app.route('/screens', methods=['POST'])
def add_screen():
  data = json.loads(request.data)
  try:
  	bookedSeatInfo = {}

  	for i in data['seatInfo']:
  		row_seats_info = {}
  		for j in range(data['seatInfo'][i]['numberOfSeats']):
  			row_seats_info[str(j)] = 0

  		bookedSeatInfo[i] = row_seats_info
  		
  	data['bookedSeatInfo'] = bookedSeatInfo 
  	#print(data)
  	screens.insert(data)
  	return jsonify({'result' : 'success'})
  except Exception as e:
  	return jsonify({'result' : str(e)})

# API to reserve tickets for given seats in a given screen
@app.route('/screens/<screen_name>/reserve', methods=['POST'])
def reserve_tickets(screen_name):
  data = json.loads(request.data)
  try:
  	screen_data = screens.find_one({'name':screen_name})
  	flag = 0
  	for k in data['seats']:
  		for i in data['seats'][k]:
  			if k not in screen_data['bookedSeatInfo'] :
  				flag = 1
  				break
  			if screen_data['bookedSeatInfo'][k][str(i)] == 1:
  				flag = 1
  				break
  		if flag == 1:
  			break

  	if flag == 0:
  		for k in data['seats']:
  			for i in data['seats'][k]:
  				screen_data['bookedSeatInfo'][k][str(i)] = 1
  		## Insert updated data
  		screens.insert(screen_data)
  		return jsonify({'result' : 'success'}),200
  	else:
  		return jsonify({'result' : 'failure'}),500
  	
  except Exception as e:
  	return jsonify({'result' : str(e)}),500


# API to get the available seats for a given screen
@app.route('/screens/<screen_name>/seats', methods=['GET'])
def available_seats(screen_name):

    if 'status' in request.args:
    	try:
    		screen_data = screens.find_one({'name':screen_name})
    		result = {}
    		row_seats_dict = {}
    		for k in screen_data['bookedSeatInfo']:
    			seat_list = []
    			for i in screen_data['bookedSeatInfo'][k]:
    				if screen_data['bookedSeatInfo'][k][str(i)] == 0:
    					seat_list.append(i)
    			row_seats_dict[k] = seat_list

    		result["seats"] = row_seats_dict
    		return jsonify(result)
    	except Exception as e:
    		return jsonify({'result' : str(e)}),500

    elif ('numSeats' in request.args) and ('choice' in request.args):
    	try:
    		numSeats = request.args['numSeats']
    		row_choice = request.args['choice'][0:1]
    		seat_choice = request.args['choice'][1:]
    		screen_data = screens.find_one({'name':screen_name})
    		result = {}
    		row_seats_dict = {}

    		for i in range(screen_data['seatInfo'][row_choice]['numberOfSeats']):
    			
    			seat_list = []
    			for j in range(i, i+int(numSeats)):
    				if (str(j) in screen_data['bookedSeatInfo'][row_choice]) and (screen_data['bookedSeatInfo'][row_choice][str(j)] == 0):
    					seat_list.append(j)
    				else:
    					break

    			if (len(seat_list) == int(numSeats)) and (int(seat_choice) in seat_list):
    				row_seats_dict[row_choice] = seat_list
    				break


    		result["availableSeats"] = row_seats_dict
    		if len(row_seats_dict) == 0:
    			return jsonify({'result' : 'no available tickets of your choice'}),404
    		return jsonify(result)
    	except Exception as e:
    		return jsonify({'result' : str(e)}),500



  

if __name__ == '__main__':
	port = int(os.environ.get('PORT',9090))
	app.run(port=port)
