"""
INSTRUCTIONS:
1. pip install twilio
   pip install Flask

2. Download ngrok

3. ./ngrok http 5000
   ^ Will need to have this start up when RPI booted
   ^ As well as this file

4. Get forwarding address from ngrok, and add to twilio

"""

from flask import Flask, request
import twilio.twiml
from twilio.rest import Client
import sys
import pyjokes

# Establish Flask server
app = Flask(__name__)

# Global authentications 
AUTHENTICATION       = 'Activate'
AUTHENTICATIONNUMBER = '4510'
SID = 'AC549920cb425a4ea3443de051f3c6c98d'
AUTHORIZATION_TOKEN = 'fa5054a039327afea5301a0390014d1f'
MYNUMBER = '+19516677255'
REGISTEREDNUMBERS = ['+17854320777']

# Security Vars
WANTACTIVATION  = 0
NUMBERACTIVATED = 0
ATTEMPTNUMBER   = 0
PANIC           = 0
PANICNUMBER     = 0

# Suppress errors to console 
class DevNull:
    def write(self, msg):
        pass

# Global objects
#sys.stderr = DevNull()
smsClient = Client(SID,AUTHORIZATION_TOKEN)

# Server start up message
for registeredNumber in REGISTEREDNUMBERS:
	smsClient.messages.create(to    =  registeredNumber,
			          		  from_ =  MYNUMBER,
			                  body  =  'MQTT Server & Flask Server Running')
 
# Route traffic to /sms
@app.route('/sms', methods=['POST'])

def sms():

	number = request.form['From']
	message_body = request.form['Body']

	global WANTACTIVATION
	global NUMBERACTIVATED
	global ATTEMPTNUMBER
	global PANIC
	global PANICNUMBER

	############        Activated State Machine     ##############

	if NUMBERACTIVATED == 1 and PANICNUMBER != str(number) and message_body == 'Temp':

		smsClient.messages.create(to    =  number,
          		                  from_ =  MYNUMBER,
                                  body  =  'Current Temperature Is: 56 Degrees F')

	elif NUMBERACTIVATED == 1 and PANICNUMBER != str(number) and message_body == 'Joke':

		sendJoke = pyjokes.get_joke()
		smsClient.messages.create(to    =  number,
	                              from_ =  MYNUMBER,
                                  body  =  sendJoke)


	elif NUMBERACTIVATED == 1 and PANICNUMBER != str(number):

		smsClient.messages.create(to    =  number,
  		                          from_ =  MYNUMBER,
                                  body  =  "I'm Not Sure What That Message Means, Please Try Again")

	else:

		pass


	############        Activated State Machine - END    ##############




	############ Authentication State Machine ##############

	if NUMBERACTIVATED == 0 and PANICNUMBER != str(number):

		if str(message_body) == AUTHENTICATION:

			smsClient.messages.create(to    =  number,
							          from_ =  MYNUMBER,
							          body  =  'Enter Authorization Code')

			WANTACTIVATION = 1

		elif (WANTACTIVATION == 1) and (str(message_body) == AUTHENTICATIONNUMBER):

			wantActivationMessage = str(number) + ' ' + 'has been activated!'
			smsClient.messages.create(to    =  number,
					          		  from_ =  MYNUMBER,
					                  body  =  wantActivationMessage)

			NUMBERACTIVATED = 1

		elif (WANTACTIVATION == 1) and (str(message_body) != AUTHENTICATIONNUMBER):

			ATTEMPTNUMBER += 1
			wrongAuthenticationNumberMessage = 'Wrong Activation Number, Attempt Number:' + ' ' + str(ATTEMPTNUMBER)

			smsClient.messages.create(to    =  number,
			          		          from_ =  MYNUMBER,
			                          body  =  wrongAuthenticationNumberMessage)

			if ATTEMPTNUMBER == 3:

				PANIC = 1
				PANICNUMBER = str(number)

		else:

			pass

	elif PANIC == 1 and PANICNUMBER == str(number):

		smsClient.messages.create(to    =  number,
		          		          from_ =  MYNUMBER,
		                          body  =  "You've Exceeded The Number Of Attempts")


	############ Authentication State Machine - END ##############

if __name__ == '__main__':
    app.run()
