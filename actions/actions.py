# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from typing import Text, List, Any, Dict


from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# THIS IS NOT CURRENTLY USED AS THE USER IS FREE TO INPUT WHATEVER INGREDIENT
# All the available ingredients (for the banned_ingredients slot)
available_ingredients = ['tomato','cheese','olives','mushrooms','onions','peppers','ham','tuna','egg','fish']
tomato_syn = ['tomato','tomatoes','pomodoro','pomodori']

# All the available cakes
available_cakes = ['tiramisù','cheesecake','apple pie']
tiramisu_syn = ['tiramisu','tiramisù','tiramisú','tiramisù','tiramisou']

# All the available drinks
available_drinks = ['coca cola','sprite','pepsi','water','beer','wine','champagne']
coca_cola_syn = ['coca cola','coca-cola','coca','cola','coke']

# All the available pizzas
vegetarian_pizzas = ['capricciosa', 'marinara','mountain','snowflake','hawaii'] #['margherita', 'capricciosa', 'ortolana', 'boscaiola', 'romana', 'marinara', 'funghi','mountain','snowflake','hawaii']
fish_pizzas = ['king','ocean'] #['king', 'gamberetti','ocean']
meat_pizzas = ['pepperoni','eagle','castle','chicken'] #['diavola', 'wurstel', 'salame', 'salsiccia', 'speck', 'prosciutto', 'calzone','pepperoni','eagle','castle','chicken']
home_specialty = ['radicchiosa']

# Generate the pizza prices
pizza_prices = {}
# This is the easter egg, the answer to the riddle
# If the user asks for "envelope" pizza, he will get a free order
pizza_prices['envelope'] = -10000000.00
for i,pizza in enumerate(vegetarian_pizzas):
	if i >= 3:
		pizza_prices[pizza] = 7.99
	else:
		pizza_prices[pizza] = 7.20

for i,pizza in enumerate(fish_pizzas):
	pizza_prices[pizza] = 7.00

for i,pizza in enumerate(meat_pizzas):
	if i >= 1 and i < 3:
		pizza_prices[pizza] = 9.49
	elif i<1:
		pizza_prices[pizza] = 8.75
	else:
		pizza_prices[pizza] = 8.99

for i,pizza in enumerate(home_specialty):
	pizza_prices[pizza] = 11.99

available_pizzas = vegetarian_pizzas + fish_pizzas + meat_pizzas + home_specialty


''' 
___________________________________________________________________________________________________________________________________
CUSTOM ACTIONS

'''
class UserAsksWhenPayment(Action):
	def name(self):
		return 'action_user_asks_when_payment'
	def run(self, dispatcher, tracker, domain):
		active_loop = tracker.active_loop_name
		if active_loop == 'party_setup_form':
				dispatcher.utter_message("You will pay after the party is over, in our restaurant. We accept cash, crypto and credit card.")
				return[FollowupAction('party_setup_form')]
		dispatcher.utter_message("Don't worry about the payment, you can pay when the delivery arrives. We accept cash, crypto and credit card.")
		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		elif active_loop == 'finish_order_form':
				return[FollowupAction('finish_order_form')]
		else:
			return [FollowupAction('action_listen')]

class utterCakeOptions(Action):
	def name(self):
		return 'action_utter_cake_options'

	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("We have the following cakes available:\n" + ", ".join(available_cakes))
		return[FollowupAction('party_setup_form')]

class utterDrinkOptions(Action):
	def name(self):
		return 'action_utter_drink_options'

	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("We have the following drinks available:\n" + ", ".join(available_drinks))
		return[FollowupAction('party_setup_form')]

class correctPartySetup(Action):
	def name(self):
		return 'action_correct_party_setup'
	def run(self, dispatcher, tracker, domain):
		entities = tracker.latest_message['entities']
		entity_present = False
		for entity in entities:
			if (entity['entity'] == 'pizza_size' or entity['entity'] == 'cake' or entity['entity'] == 'drinks') and entity['confidence_entity'] >= 0.5:
				entity_present = True
		if entity_present:
			dispatcher.utter_message("The party setup has been corrected.")
			return[FollowupAction('action_confirm_party_setup')]
		else:
			dispatcher.utter_message("I have reset the party setup.")
			return[SlotSet('number_of_people',None), SlotSet('cake',None), SlotSet('drinks',None), FollowupAction('party_setup_form')]

class ConfirmPartySetup(Action):
	def name(self):
		return 'action_confirm_party_setup'
	def run(self, dispatcher, tracker, domain):
		cake = tracker.get_slot("cake")
		drinks = tracker.get_slot("drinks")
		human_target = tracker.get_slot("human_target")
		number_of_people = tracker.get_slot("number_of_people")
		dispatcher.utter_message(f"Your party setup includes pizza slices for {number_of_people} {human_target}, {drinks} and {cake}. Is that correct?")
		return[FollowupAction('action_listen')]

class AskBannedIngredients(Action):
	def name(self):
		return 'action_ask_banned_ingredients'
	def run(self, dispatcher, tracker, domain):

		last_intent = tracker.latest_message.get("intent", {}).get("name")
		if last_intent == "negative" or last_intent == "positive":
			dispatcher.utter_message("I see, no problem. Do you want to confirm the party order?")
			return[SlotSet("banned_ingredients", 'no banned ingredient'),FollowupAction('action_listen')]	

		entities = tracker.latest_message['entities']
		ingredients = []
		for i in entities:
			if i['entity'] == 'banned_ingredients' and i['confidence_entity'] >= 0.5:
				ingredients.append(i['value'])
		valid_ingredients = ingredients
		'''
		for ingredient in ingredients:
			if ingredient in available_ingredients:
				valid_ingredients.append(ingredient)
			else:
				dispatcher.utter_message(f"I'm sorry, but the ingredient '{ingredient}' you are requesting is not available. Please choose another one...")
				return [SlotSet("banned_ingredients", None),FollowupAction('action_listen')]
		'''
		if len(valid_ingredients) == 0:
			dispatcher.utter_message("I'm sorry, but I didn't quite understand that. Could you repeat?")
			return [SlotSet("banned_ingredients", None),FollowupAction('nlu_fallback')]
		elif len(valid_ingredients) == 1:
			dispatcher.utter_message(f"Sure, I will make sure that your pizza does not contain {valid_ingredients[0]}. Do you want to confirm the party order?")
			return[SlotSet("banned_ingredients", valid_ingredients),FollowupAction('action_listen')]
		else:
			ing_list = ''
			for i,ing in enumerate(valid_ingredients):
				if i == len(valid_ingredients)-1:
					ing_list += 'and ' + ing
				else:
					if i == len(valid_ingredients)-2:
						ing_list += ing + ' '
					else:
						ing_list += ing + ', '
			dispatcher.utter_message(f"Sure, I will make sure that your pizza does not contain {ing_list}. Do you want to confirm the party order?")
			return[SlotSet("banned_ingredients", valid_ingredients),FollowupAction('action_listen')]

class countFailures(Action):
	def name(self):
		return 'action_count_failures'
	def run(self, dispatcher, tracker, domain):
		fails = tracker.get_slot("failures")
		if fails is None:
			dispatcher.utter_message("I'm sorry, I didn't quite understand that. Could you repeat?")
			return [SlotSet("failures", 1)]
		else:
			if fails >= 3:
				dispatcher.utter_message("Sorry but I am not able to help, you are being redirected to a human operator. Please wait...")
				return[FollowupAction('wait_for_human_form')]
			else:
				dispatcher.utter_message("I'm sorry, I didn't quite understand that. Could you repeat?")
				return [SlotSet("failures", fails+1)]


class resetEverything(Action):
	def name(self):
		return 'action_reset_everything'
	def run(self, dispatcher, tracker, domain):
		return[	SlotSet("pizza_type", None),
				 		SlotSet("pizza_size", None),
						SlotSet("pizza_amount", None),
						SlotSet("order_pizza_list", None),
						SlotSet("user_name", None),
						SlotSet("user_address", None),
						SlotSet("user_time", None),
						SlotSet("response", None),
						SlotSet("failures", None),
						SlotSet("human", None),
						SlotSet("human_target", None),
						SlotSet("banned_ingredients", None),
						SlotSet("number_of_people", None),
						SlotSet("cake", None),
						SlotSet("drinks", None),
					]

class askPizzaPrice(Action):
	def name(self):
		return 'action_ask_pizza_price'
	def run(self, dispatcher, tracker, domain):
		pizza = None
		amount = 1
		entity_pizza_in_the_message = False
		entity_amount_in_the_message = False
		entities = tracker.latest_message['entities']
		active_loop = tracker.active_loop_name
		print(active_loop)
		if active_loop == 'party_setup_form':
			dispatcher.utter_message("The price for a party is 15€ per person all included. If you don't want to include drinks and/or cake, the price will be -2€ per missing item, so if you just want pizza slices the price is 11€ per person.")
			return[FollowupAction('party_setup_form')]
		for entity in entities:
			if entity['entity'] == 'pizza_type' and entity['confidence_entity'] >= 0.5:
				pizza = entity['value']
				entity_pizza_in_the_message = True
			if entity['entity'] == 'pizza_amount' and entity['confidence_entity'] >= 0.5:
				try:
					amount = int(entity['value'])
					entity_amount_in_the_message = True
				except:
					amount = 1

		pizza = validate_pizza_type_outside(self, pizza, dispatcher, tracker, domain)

		if pizza is None:
			entity_in_the_message = False
			pizza = tracker.get_slot("pizza_type")

		if pizza is None:
			dispatcher.utter_message("You have to specify which pizza you want the price of!")
			if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
			else:
				return [FollowupAction('action_listen')]
		
		price = pizza_prices[pizza]
		price = "{:.2f}".format(price)
		dispatcher.utter_message("The price of " + str(amount) + " " + pizza + " is "+ str(price) + " €. For a maxi pizza add 5 €.")
		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		else:
			return [FollowupAction('action_listen')]
		
		


class editAnything(Action):
	def name(self):
		return 'action_edit_anything'
	
	def run(self, dispatcher, tracker, domain):
		try:
			intent = tracker.latest_message['entities']

			# Collect all the intents
			valid_int = []
			target_name = None
			target_address = None
			target_time = None
			add_number = None

			output = []
			for i in intent:
				if i['entity'] == 'focus' and i['confidence_entity'] >= 0.5:
					valid_int.append(i['value'])
				if i['entity'] == 'user_name' and i['confidence_entity'] >= 0.5:
					target_name = i['value']
				if i['entity'] == 'user_address' and i['confidence_entity'] >= 0.5:
					target_address = i['value']
				if i['entity'] == 'user_time' and i['confidence_entity'] >= 0.5:
					target_time = i['value']
				if i['entity'] == 'pizza_amount' and i['confidence_entity'] >= 0.5:
					add_number = i['value']
			
			print(valid_int)
			for vi in valid_int:
				if vi == 'name':
					return [SlotSet('user_name', target_name),FollowupAction('action_order_preview')]
				elif vi == 'address' or vi == 'location':
					if add_number is not None:
						target_address = target_address + ' ' + add_number
						return [SlotSet('user_address', target_address),FollowupAction('action_order_preview')]
					else:
						return [SlotSet('user_address', target_address),FollowupAction('action_order_preview')]
				elif vi == 'time':
					return [SlotSet('user_time', target_time),FollowupAction('action_order_preview')]
				
			print(output)
			return [SlotSet('user_name', None),SlotSet('user_address', None),SlotSet('user_name', None),FollowupAction('action_order_preview')]


		except:
			intent = None
			return [FollowupAction('nlu_fallback')]
		

class sendOrder(Action):
	def name(self):
		return 'action_order_preview'
	
	def run(self, dispatcher, tracker, domain):
		order = tracker.get_slot("order_pizza_list")
		name = tracker.get_slot("user_name")
		address = tracker.get_slot("user_address")
		time = tracker.get_slot("user_time")
		add_number = tracker.get_slot("pizza_amount")

		total, items_cost = self.compute_grand_total(order)
		
		order_with_cost = []
		for i,item in enumerate(order):
			item_string = item + " " + items_cost[i] + " €"
			order_with_cost.append(item_string)
		readable_order = (',\n').join(order_with_cost) 
		try:
			delivery = 'The order has to be deliver to ' + name + ' at '+ time + 'time, with location ' + address + ' ' + str(add_number)+ "."
			dispatcher.utter_message("Your order contains:\n" + readable_order + ".	\n" + delivery + "\nfor a grand total of " + total + " €.\nDo you want to proceed?")
			
		except:
			delivery = 'The order has to be deliver to ' + name + ' at '+ time + 'time, with location ' + address + "."
			dispatcher.utter_message("Your order contains:\n" + readable_order + ".	\n" + delivery + "\nfor a grand total of " + total + " €.\nDo you want to proceed?")
		return[FollowupAction('action_listen')]
		
	def compute_grand_total(self, order):
		total = 0
		items_cost = []
		for pizza in order:
			pizza = pizza.split(' ')
			amount = int(pizza[0])
			size = pizza[1]
			pizza = pizza[2]
			price = pizza_prices[pizza]
			if size == 'maxi':
				price += 5
			total += price * amount
			items_cost.append(str(price * amount))
		if total < 0:
			total = 0 
		return str(total), items_cost

class FinishOrder(Action):
	def name(self):
		return 'action_finish_order'

	def run(self, dispatcher, tracker, domain):
		order = tracker.get_slot("order_pizza_list")
		if order is not None:
			dispatcher.utter_message("Perfect!")
			return[FollowupAction('finish_order_form')]
		else:
			dispatcher.utter_message("You need to have at least one item in the order list before proceeding! Please add something to your order.")
			return[FollowupAction('action_listen')]


class utterHomeSpecialty(Action):
	def name(self):
		return 'action_utter_menu_home_specialty'

	def run(self, dispatcher, tracker, domain):
		active_loop = tracker.active_loop_name
		dispatcher.utter_message("Our home specialty is the RAdicchioSA")
		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		else:
			return [FollowupAction('action_listen')]

class utterVegetarianPizzas(Action):
	def name(self):
		return 'action_utter_vegetarian_pizzas'

	def run(self, dispatcher, tracker, domain):
		active_loop = tracker.active_loop_name
		dispatcher.utter_message("We have the following vegetarian pizzas available:\n" + ", ".join(vegetarian_pizzas))
		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		else:
			return [FollowupAction('action_listen')]

class utterFishPizzas(Action):
	def name(self):
		return 'action_utter_fish_pizzas'

	def run(self, dispatcher, tracker, domain):
		active_loop = tracker.active_loop_name
		dispatcher.utter_message("We have the following fish pizzas available:\n" + ", ".join(fish_pizzas))
		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		else:
			return [FollowupAction('action_listen')]
		
class utterCalories(Action):
	def name(self):
		return 'action_calories'

	def run(self, dispatcher, tracker, domain):
		active_loop = tracker.active_loop_name
		dispatcher.utter_message("I'm so sorry, but I don't have this kind of knowledge. We will work on implementing the calorie count in the future.")
		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		elif active_loop == 'finish_order_form':
				return[FollowupAction('finish_order_form')]
		elif active_loop == 'party_setup_form':
				return[FollowupAction('party_setup_form')]
		else:
			return [FollowupAction('action_listen')]

class utterMeatPizzas(Action):
	def name(self):
		return 'action_utter_meat_pizzas'

	def run(self, dispatcher, tracker, domain):
		active_loop = tracker.active_loop_name
		dispatcher.utter_message("We have the following meat pizzas available:\n" + ", ".join(meat_pizzas))
		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		else:
			return [FollowupAction('action_listen')]

class utterAvailablePizzas(Action):
	def name(self):
		return 'action_utter_menu_pizza'

	def run(self, dispatcher, tracker, domain):
		active_loop = tracker.active_loop_name
		dispatcher.utter_message("We have the following pizzas available:\n" + ", ".join(available_pizzas))
		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		else:
			return [FollowupAction('action_listen')]

class ContinueOrder(Action):
	def name(self):
		return 'action_continue_order'

	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("Your order has been set. Would you like anything else?")
		return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None),FollowupAction('action_listen')]

class ResetOrder(Action):
	def name(self):
		return 'action_reset_order'

	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("Your order has been reset. Please start again.")
		return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None),FollowupAction('pizza_order_form')]

class UtterConfirmOrder(Action):
	def name(self):
		return 'action_confirm_order'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		#print(pizza_amount)
		#print(type(pizza_amount))
		pizza_amount = str(pizza_amount)
		order_details =  str(pizza_amount + " "+pizza_size + " "+pizza_type )
		dispatcher.utter_message("So you want " + order_details + ". Is that correct?")
		return[]

class ActionPizzaOrderAdd(Action):
	def name(self):
		return 'action_pizza_order_add'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		pizza_amount = str(pizza_amount)
		order_details =  str(pizza_amount + " "+pizza_size + " "+pizza_type )
		old_order = tracker.get_slot("order_pizza_list")
		if old_order is None:
			return[SlotSet("order_pizza_list", [order_details])]
		else:
			 old_order.append(order_details)
			 return[SlotSet("order_pizza_list", old_order)]
	

	
class replyToPrivacyQuestion(Action):
	def name(self):
		return 'action_explain_why_need_info'

	def run(self, dispatcher, tracker, domain):
		try:
			intent = tracker.latest_message['entities'][0].get('value')
		except:
			intent = None
		print(intent)
		active_loop = tracker.active_loop_name
		if intent == "name":
			dispatcher.utter_message("I need your name to know who needs to receive the order. Don't worry, I will not share your data with anyone.")
		elif intent == "number":
			dispatcher.utter_message("I need your number so that if we need we can contact you. Don't worry, I will not share your data with anyone.")
		elif intent == "address":
			dispatcher.utter_message("I need to know your address in order to deliver your order to you. Don't worry, I will not share your data with anyone.")
		else:
			dispatcher.utter_message("I need your information in order to setup your order. Don't worry, I will not share your data with anyone.")

		if active_loop == 'pizza_order_form':
				return[FollowupAction('pizza_order_form')]
		elif active_loop == 'finish_order_form':
				return[FollowupAction('finish_order_form')]
		else:
			return [FollowupAction('action_listen')]
		
	

class handle_form_exit(Action):
	def name(self):
		return 'action_handle_form_exit'
	def run(self, dispatcher, tracker, domain):
		try:
			intent = tracker.latest_message['intents'].get('name')
		except:
			intent = None
		#print(intent)
		if intent == "affermative":
			dispatcher.utter_message("Got it.")
		elif intent == "negative":
			dispatcher.utter_message("Here we go again.")
		else:
			dispatcher.utter_message("Can't understand you, well let's start again.")
		return[]	

''' 
___________________________________________________________________________________________________________________________________
CUSTOM VALIDATIONS

'''
class ValidateFinishOrderForm(FormValidationAction):
	def name(self) -> str:
		return "validate_finish_order_form"
	
	def validate_user_name(self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		slot = tracker.get_slot('user_name')
		if slot is not None:
			return {"user_name" : slot}
		return {'user_name':value}

	def validate_user_address(self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		slot = tracker.get_slot('user_address')
		if slot is not None:
			return {"user_address" : slot}
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		#print(last_intent)
		if last_intent != "provide_personal_info":
			return {"user_address" : None}
		#print(value)

		entities = tracker.latest_message['entities']
		street_number = None
		for entity in entities:
			if entity['entity'] == 'pizza_amount' and entity['confidence_entity'] >= 0.5:
				street_number = entity['value']
		if isinstance(value, str):
			word = value.lower()
			words = word.split(' ')
			if words[0] not in ['via', 'viale', 'piazza', 'largo','corso','piazzale','piazzetta','vicolo','strada','contrada','ponte','borgo','frazione','località']:
				dispatcher.utter_message("Not a valid address.")
			else:
				success = 5
				last_w = words[-1]
				print('lastw',last_w)
				try:
					add_num = int(last_w)
					print(add_num)
					
				except:
					success -= 1

				last_w = words[-1]
				last_w = last_w.split(',')[-1]
				try:
					add_num = int(last_w)
					print(add_num)
					
				except:
					success -= 1
				
				last_w = words[-1]
				last_w = last_w.split('.')[-1]
				try:
					add_num = int(last_w)
					print(add_num)
					
				except:
					success -= 1

				last_w = words[-1]
				last_w = last_w.split('nr')[-1]
				try:
					add_num = int(last_w)
					print(add_num)
				
				except:
					success -= 1

				last_w = words[-1]
				last_w = last_w.split('n')[-1]
				try:
					add_num = int(last_w)
					print(add_num)
					
				except:
					success -= 1
				
				if success > 0:
					return {'user_address' : word}
				else:
					if street_number is not None:
						print('nafp')
						return {'user_address' : word + ' ' + str(street_number)}
					print('no number found', success)
					dispatcher.utter_message("I also need the address number!")
					return {'user_address' : None}
		else:
			return {"user_address" : None}
	
	def validate_user_time(self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		slot = tracker.get_slot('user_time')
		if slot is not None:
			return {"user_time" : slot}
		#print(last_intent)
		if last_intent != "provide_personal_info":
			return {}
		#print(value)
		if isinstance(value, str):
			word = value.lower()
			if word not in ['lunch', 'dinner']:
				if word == '13:30':
					return[{"user_time" : 'lunch'}]
				elif word == 'lunchtime' or word == 'lunch time':
					return[{"user_time" : 'lunch'}]
				elif word == 'dinertime' or word == 'dinner time':
					return[{"user_time" : 'dinner'}]
				elif word == '20:30':
					return[{"user_time" : 'dinner'}]
				else:
					dispatcher.utter_message("I'm not sure I understand. Please choose between lunch or dinner.")
					return {"user_time" : None}
			else:
				return {"user_time" : word}
	
class ValidateConfirmationForm(FormValidationAction):
	def name(self) -> str:
		return "validate_confirmation_form"
	
	
	def validate_response(self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		if last_intent=="affermative":
			dispatcher.utter_message("Got it.")
			return {"response": "true"}
		elif last_intent == "negative":
			dispatcher.utter_message("Here we go again.")
			return {"response": "false"}
		else:
			dispatcher.utter_message("Can't understand you.")
		return[]	

def validate_pizza_type_outside(self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		#print(last_intent)
		if last_intent=="exit":
			return {}
		#print(value)
		if isinstance(value, str):
			word = value.lower()
			if word not in available_pizzas:
				word = word[:-1]
			#print(word)
			if word not in available_pizzas:
				print('invalid pizza', word)
				if word == 'envelope':
						return {"pizza_type": 'envelope'}
				else:
					dispatcher.utter_message(f"I'm sorry, but the pizza '{value.lower()}' you are requesting is not available. Please choose another one...")
				return None
			else:
				print('valid pizza, returning', word)
				return word
			
class Validate_pizza_order_form(FormValidationAction):
	def name(self) -> str:
		return "validate_pizza_order_form"
		
	def validate_pizza_type(self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		entities = tracker.latest_message['entities']
		# Make sure the user is only adding one pizza at a time
		pizza_entity = 0
		for entity in entities:
			if entity['entity'] == 'pizza_type' and entity['confidence_entity'] >= 0.5:
				pizza_entity += 1
		print('validating pizza')
		if pizza_entity > 1:
			dispatcher.utter_message("I'm sorry, but you can only add one pizza at a time. Please specify only one pizza, the next one you can add it later.")
			return {"pizza_type": None}
		#print(last_intent)
		if last_intent!="provide_detailed_pizza_order":
			return {}
		#print(value)
		else:
			if isinstance(value, str):
				word = value.lower()
				if word not in available_pizzas:
					word = word[:-1]
				#print(word)
				if word not in available_pizzas:
					if word == 'envelope':
						return {"pizza_type": 'envelope'}
					elif word == 'envelop':
						return {"pizza_type": 'envelope'}
					elif word == 'radicchi':
						return {"pizza_type": 'radicchiosa'}
					else:
						dispatcher.utter_message(f"I'm sorry, but the pizza '{value.lower()}' you are requesting is not available. Please choose another one...")
					return {"pizza_type": None}
				else:
					print('returning', word)
					return {"pizza_type": word}
			
	
	def validate_pizza_amount(
		self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		if last_intent=="exit":
			return {}
		try:
			value = int(value)
			if value > 20:
				dispatcher.utter_message("I'm sorry, we can't sell you that many pizzas.")
				return {"pizza_amount": None}
			elif value < 0:
				dispatcher.utter_message("Seriously? You want negative pizzas?")
				return {"pizza_amount": None}
			else:
				return {"pizza_amount": str(value)}
		except:
			digits = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
			 			'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen',
						'eighteen', 'nineteen', 'twenty']
			
			if value.lower() not in digits:
				dispatcher.utter_message("I'm sorry, but I can't understand you. Please choose a number between one and twenty.")
				return {"pizza_amount": None}
			else:
				for i, digit in enumerate(digits):
					if value.lower() == digit:
						return {"pizza_amount": str(i+1)}
				
		
	
	def validate_pizza_size(
		self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		if last_intent=="exit":
			return {}
		entities = tracker.latest_message['entities']
		# Make sure the user is only adding one pizza size at a time
		size_entity = 0
		for entity in entities:
			if entity['entity'] == 'pizza_size' and entity['confidence_entity'] >= 0.5:
				size_entity += 1
		if size_entity > 1:
			dispatcher.utter_message("I'm sorry, but you can only specify one size at a time. Please specify only one size, the next one you can add it later.")
			return {"pizza_size": None}
		if value.lower() not in ["normal","standard", "large", "extra large", "big", "maxi", "huge",'classic','average','medium','regular']:
			dispatcher.utter_message("I'm sorry, we only have normal and maxi sized pizzas.")
			return {"pizza_size": None}
		if value.lower() in ['standard','normal','classic','average','medium','regular']:
			return {"pizza_size": value.lower()}
		else:
			return {"pizza_size": 'maxi'}
		
class ValidatePartyForm(FormValidationAction):
	def name(self) -> str:
		return "validate_party_setup_form"
	
	def validate_cake(self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		print(last_intent)
		entities = tracker.latest_message['entities']
		# Make sure the user is only adding one cake
		cake_entity = 0
		for entity in entities:
			if entity['entity'] == 'cake' and entity['confidence_entity'] >= 0.5:
				cake_entity += 1
		print('validating cake')
		if cake_entity > 1:
			dispatcher.utter_message("I'm sorry, but you can only add one cake. Please specify the one you want for your party.")
			return {"cake": None}
		#print(last_intent)
		if last_intent == "negative":
			return {"cake": 'no cake'}
		if last_intent!="provide_party_info":
			print('wrong intent, returning')
			return {}
		#print(value)
		else:
			if isinstance(value, str):
				word = value.lower()
				if word == 'cake':
					dispatcher.utter_message(f"'Cake' is too generic, you need to choose a cake.")
				if word in tiramisu_syn:
					word = 'tiramisù'
				if word not in available_cakes:
					dispatcher.utter_message(f"I'm sorry, but the cake '{value.lower()}' you are requesting is not available. Please choose another one...")
					return {"cake": None}
				else:
					print('returning', word)
					return {"cake": word}
				
	def validate_drinks(self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		entities = tracker.latest_message['entities']
		# Make sure the user is only adding one drink
		drink_entity = 0
		for entity in entities:
			if entity['entity'] == 'drinks' and entity['confidence_entity'] >= 0.5:
				drink_entity += 1
		print('validating drinks')
		if drink_entity > 1:
			dispatcher.utter_message("I'm sorry, but you can only add one drink. Please specify the one you want for your party.")
			return {"drinks": None}
		#print(last_intent)
		if last_intent == "negative":
			return {"drinks": 'no drink'}
		if last_intent!="provide_party_info":
			print('wrong intent, returning')
			return {}
		#print(value)
		else:
			if isinstance(value, str):
				word = value.lower()
				if word == 'drink':
					dispatcher.utter_message(f"'Drink' is too generic, you neeD to choose a cake.")
				if word in coca_cola_syn:
					word = 'coca cola'
				if word not in available_drinks:
					dispatcher.utter_message(f"I'm sorry, but the drink '{value.lower()}' you are requesting is not available. Please choose another one...")
					return {"drinks": None}
				else:
					print('returning', word)
					return {"drinks": word}
			
	
	def validate_number_of_people(
		self,
		value: Text,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		last_intent = tracker.latest_message.get("intent", {}).get("name")
		if last_intent=="exit":
			return {}
		try:
			value = int(value)
			if value > 50:
				dispatcher.utter_message("I'm sorry, we can't handle that many people.")
				return {"number_of_people": None}
			elif value < 0:
				dispatcher.utter_message("Seriously? You have negative people?")
				return {"number_of_people": None}
			else:
				return {"pizza_amount": str(value)}
		except:
			digits = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
			 			'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen',
						'eighteen', 'nineteen', 'twenty']
			
			if value.lower() not in digits:
				dispatcher.utter_message("I'm sorry, but I can't understand you. Please choose a number between one and twenty.")
				return {"number_of_people": None}
			else:
				for i, digit in enumerate(digits):
					if value.lower() == digit:
						return {"number_of_people": str(i+1)}
				




