
import os
import json
import time
import re
import redis
import sys
from slackclient import SlackClient
from flask import Flask, request, make_response, Response
# initialize Redis datastore
r = redis.Redis(
  host='127.0.0.1',
  port=6379)


dogs = dict({})
# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
# # Your app's Slack bot user token
# SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
# SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
# # Slack client for Web API requests
# slack_client = SlackClient(SLACK_BOT_TOKEN)
# # Flask web server for incoming traffic from Slack
# app = Flask(__name__)
# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
REQUEST = "watch"
TIME = "time"
ASK = "fetch"
LIST = "see"
global DOG_NAME
# Dictionary to store coffee orders. In the real world, you'd want an actual key-value store
DOGS = {}
user_id = "U0CAV5XME"
def parse_bot_commands(slack_events):
  """
    Parses a list of events coming from the Slack RTM API to find bot commands.
    If a bot command is found, this function returns a tuple of command and channel.
    If its not found, then this function returns None, None.
  """
  for event in slack_events:
    if event["type"] == "message" and not "subtype" in event:
      user_id, message = parse_direct_mention(event["text"])
      if user_id == starterbot_id:
        return message, event["channel"]
  return None, None
def parse_direct_mention(message_text):
  """
    Finds a direct mention (a mention that is at the beginning) in message text
    and returns the user ID which was mentioned. If there is no direct mention, returns None
  """
  matches = re.search(MENTION_REGEX, message_text)
  # the first group contains the username, the second group contains the remaining message
  return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    DOG_NAME = command[6:]
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)
    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!

    if REQUEST in command:
        # DOG_NAME = command[6:]
        # response = "Let's get someone to watch " + DOG_NAME
        user_payload = command.split()

        user_name = user_payload[3]
        print type(user_name)
        puppy = user_payload[1]
        time = user_payload[-1]
        avail = True
        response = "Let's get someone to watch :dog: " + puppy + " at " + time + ", " + user_name
        r.set(user_name, [puppy,time])
        dogs[puppy] = [user_name, time, avail]
        # print(dogs[0])
        print(dogs)
        print(dogs[puppy])
        print(dogs[puppy][0])
        print(dogs[puppy][1])
        print(dogs[puppy][2])
        # sys.stdout.write(dogs)
        slack_client.api_call(
          "chat.postMessage",
          channel=channel,
          text= response 
        )
    elif ASK in command:
        user_payload = command.split()
        user_name = user_payload[1]
        puppy = user_payload[-1]
        response = ""
        if dogs[puppy][2]:
            response = "You are now signed up to watch " + puppy + " at " + dogs[puppy][1] + " for " + dogs[puppy][0]
            dogs[puppy][2] = False 

        else:
            response = "Sorry, someone else is already watching that very good pup. Maybe try another!"

        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text= response 
        )
    elif LIST in command:
        response = ""
        # response = dogs.viewkeys()
        for pup in dogs:
            print(dogs[pup][2])
            if dogs[pup][2]:
                respone = ""
                temp = "%s" % pup
                response += temp + "\n"   
                
        
        if not response:
            response = "There aren't any pups that need a sitter right now. Try again later!"
        else:
            response = "These good pups could use a sitter: \n" + response
        # for pups in dogs.iteritems() :
        #     response += convert(dogs)
        # for i in range(0, len(dogs)):
        #     response = dogs[i]

        # for doggos in dogs.iter_items():
        #     response = doggos  + doggos#+ " owned by " + doggos[0] + "\n" 
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text= response 
        )

  #   dog_order = slack_client.api_call(
  #     "chat.postMessage",
  #       as_user=True,
  #       channel=channel,
  #       text="I am WorkDogBot ::dog::, and I\'m here to help you find a dogsitter."
  #       # attachments=[{
  #       #   "text": "",
  #       #   "callback_id": "dog_sitter_form",
  #       #   "color": "#3AA3E3",
  #       #   "attachment_type": "default",
  #       #   "actions": [{
  #       #   "name": "dog_needs_sitter",
  #       #   "text": ":dog: Find me a dogsitter",
  #       #   "type": "button",
  #       #   "value": "dog_sitter_order"
  #       # }]
  #     # }]
  #   )
  #   # open_dialog = slack_client.api_call(
  #   #   "dialog.open",
  #   #   trigger_id=message_action["trigger_id"],
  #   #   dialog={
  #   #     "title": "Request a coffee",
  #   #     "submit_label": "Submit",
  #   #     "callback_id": "coffee_order_form",
  #   #     "elements": [
  #   #       {
  #   #         "label": "Coffee Type",
  #   #         "type": "select",
  #   #         "name": "meal_preferences",
  #   #         "placeholder": "Select a drink",
  #   #         "options": [
  #   #           {
  #   #             "label": "Cappuccino",
  #   #             "value": "cappuccino"
  #   #           },
  #   #           {
  #   #             "label": "Latte",
  #   #             "value": "latte"
  #   #           },
  #   #           {
  #   #             "label": "Pour Over",
  #   #             "value": "pour_over"
  #   #           },
  #   #           {
  #   #             "label": "Cold Brew",
  #   #             "value": "cold_brew"
  #   #           }
  #   #         ]
  #   #       }
  #   #     ]
  #   #   }
  #   # )
  #   # print(open_dialog)
  # DOGS[user_id] = {
  #   "order_channel":dog_order["channel"],
  #   "message_ts":"",
  #   "order":{}
    
  # }
  
# def message_actions():
#   # Parse the request payload
#   message_action = json.loads(request.form["payload"])
#   user_id = message_action["user"]["id"]
#   slack_client.api_call(
#       "chat.postMessage",
#       channel=channel,
#       text= response + "Test 1"
#     )
#   # if message_action["type"] == "interactive_message":
#   #   # Add the message_ts to the user's order info
#   #   DOGS[user_id]["message_ts"] = message_action["message_ts"]
#     # Show the ordering dialog to the user
    
#     slack_client.api_call(
#       "chat.update",
#       channel=channel,
#       ts=message_action["message_ts"],
#       text=":pencil: Taking your order...",
#       attachments=[]
#     )
#   elif message_action["type"] == "dialog_submission":
#     coffee_order = DOGS[user_id]
#     # Update the message to show that we're in the process of taking their order
#     slack_client.api_call(
#       "chat.update",
#       channel=channel,
#       ts=coffee_order["message_ts"],
#       text=":white_check_mark: Order received!",
#       attachments=[]
#     )
#   return make_response("", 200)

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


if __name__ == "__main__":
  if slack_client.rtm_connect(with_team_state=False):
    print("Starter Bot connected and running!")
    # Read bot's user ID by calling Web API method `auth.test`
    starterbot_id = slack_client.api_call("auth.test")["user_id"]
    while True:
      command, channel = parse_bot_commands(slack_client.rtm_read())
      if command:
        handle_command(command, channel)
      time.sleep(RTM_READ_DELAY)
  else:
    print("Connection failed. Exception traceback printed above.")
