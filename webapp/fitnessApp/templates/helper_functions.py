from .models import *
from datetime import *
from random import choice, randint
from django.core.exceptions import ObjectDoesNotExist

PAL_DICT = {'sedentary' : 1.2, 'slightly_active' : 1.375, 'moderately_active' : 1.55, 'very_active' : 1.725, 'super_active' : 1.9}

DEFAULT_EMAIL = "pulsefitintra@gmail.com"
FOOD_NAMES = list(Food.objects.values_list('name', flat=True))
EXERCISE_NAMES = list(Exercise.objects.values_list('name', flat=True))
OPTIONS = 3 #used to determine how many different exercises/food items the user will be recommended


def calcBMR(user: User):
    if (user.gender == "male"):
        return (66.5 + (13.75 * user.weight) + (5.003 * user.height) - (6.75 * user.age))
    else:
        return (655.1 + (9.563 * user.weight) + (1.850 * user.height) - (4.676 * user.age))
    
def calTDEE(user: User, pal: float):
    bmr = calcBMR(user)
    return (pal * bmr)
    #Calories needed to maintain weight
    #Remove 500-700 cals to reduce weight
    #Add 300-500 to gain

def Calories_Eaten_Today(user: User, today=datetime.today().strftime("%d/%m/%y")):
    '''Calcs food the user has waten today'''
    eaten_calories = 0
    #today = datetime.today().strftime("%d/%m/%y")
    if today in user.journal:
        for name, servings in user.journal[today].items():
            if name != "total":
                food = Food.objects.get(name=name)
                eaten_calories += (food.calories / 100) * servings

    return int(eaten_calories)

def Calories_Lost_Today(user: User, today=datetime.today().strftime("%d/%m/%y")):
    '''Calcs calories the user lost today'''
    #Exercise calories = (MET level of activity x 3.5 x Weight (kg) x minutes of activity) / 200
    lost_calories = 0
    #today = datetime.today().strftime("%d/%m/%y")
    if today in user.exercises:
        for name, duration in user.exercises[today].items():
            if name != 'total':
                exercise = Exercise.objects.get(name=name)
                lost_calories += (exercise.met * 3.5 * user.height * duration) / 200

    return int(lost_calories)

def Calories_Today(user: User, today=datetime.today().strftime("%d/%m/%y")):
    '''Calcs total calories gained/lost today. Calories_Eaten_Today - Calories_Lost_Today'''
    todays_calories = 0
    #today = datetime.today().strftime("%d/%m/%y")
    if today in user.journal:
        for name, servings in user.journal[today].items():
            if name != "total":
                food = Food.objects.get(name=name)
                todays_calories += (food.calories / 100) * int(servings)

    today = datetime.today().strftime("%d/%m/%y")
    if today in user.exercises:
        for name, duration in user.exercises[today].items():
            if name != 'total':
                exercise = Exercise.objects.get(name=name)
                todays_calories -= (exercise.met * 3.5 * user.height * duration) / 200

    return int(todays_calories)

def Favourite_Exercise(user : User, cut=[]):
    exercise_dict = {}
    for date, pair in user.exercises.items():
        for name, duration in pair.items():
            if name not in cut and name != 'total':
                if name in exercise_dict.keys():
                    exercise_dict[name] += int(duration)
                else:
                    exercise_dict[name] = int(duration)

    while exercise_dict:
        try:
            fav = max(exercise_dict, key=exercise_dict.get)
            return Exercise.objects.get(name=fav)
        except Exercise.DoesNotExist:
            exercise_dict.pop(fav)
    
    random_exercise_name = choice(EXERCISE_NAMES)
    return Exercise.objects.get(name=random_exercise_name)

def Favourite_Food(user : User, cut=[]):
    food_dict = {}
    for date, pair in user.journal.items():
        for name, grams in pair.items():
            if name not in cut and name != 'total':
                if name in food_dict.keys():
                    food_dict[name] += int(grams)
                else:
                    food_dict[name] = int(grams)

    while food_dict:
        try:
            fav = max(food_dict, key=food_dict.get)
            return Food.objects.get(name=fav)
        except Food.DoesNotExist:
            food_dict.pop(fav)

    if FOOD_NAMES:
        random_food_name = choice(FOOD_NAMES)
        return Food.objects.get(name=random_food_name)
    else:
        return None

class UserNotFound(Exception):
    '''Error for when a user hasn't signed in'''
    pass

def get_user(request):
    '''used to get the user's account details from cookies'''
    #email = request.session['user']
    #user = User.objects.get(email=email)
    email = request.COOKIES.get('user', '')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise UserNotFound("User does not exist")
    
    return user


def Log_Message(picked=randint(0, 2)):
    '''Returns a message for when the user hasn't logged their activity today.
    3 messages: 
        0 = Standard
        1 = Nice, idk
        2 = Short, matter of fact
    Randomly selected if picked is left empty'''
    message1 = {"subject" : "Make sure you log your activity",
                "message" : f"""Make sure you log the food you've eaten and the exercise you've done today."""}
    message2 = {"subject" : "No Activity Logged",
                "message" : "Hello, you forgot to log the food you've eaten today or the exercise you've done.\nHope I'm not interrupting, please make sure you log your activity later.\nGood luck on your fitness journey."}
    message3 = {"subject" : "Log Avtivity",
                "message" : "No activity logged today"}
    
    messages = [message1, message2, message3]
    return messages[picked]


def Excess_Message(excess_calories, duration, fav_exercise, picked=randint(0, 2)):
    '''Returns a message for when the user has exceeded their calories today.
    3 messages: 
        0 = Standard
        1 = Nice, idk
        2 = Short, matter of fact
    Randomly selected if picked is left empty'''
    message1 = {"subject" : "Exceeded Target Calories",
                "message" : f"""You are currently {excess_calories} calories over your target calories.\nI recommend that you exercise to stay within your target calories.\nFor example, {fav_exercise} for at least {duration:.0f} minutes."""
                }
    message2 = {"subject" : "Overeating",
                "message" : f"""Hello. You've been over aeting a bit.\nI recommend that you do about {duration:.0f} minutes of {fav_exercise} or something as hard as that before ending the day.\nGood luck."""}
    message3 = {"subject" : "Exceeded Target Calories",
                "message" : f"""{duration:.0f} minutes of {fav_exercise}.\n{excess_calories} calories over target calories."""}
    
    messages = [message1, message2, message3]
    return messages[picked]


def Min_Message(missing_calories=None, fav_food=None, grams=None, picked=randint(0, 2)):
    '''Returns a message for when the user is below their daily minimun calories today.
    3 messages: 
        0 = Standard
        1 = Nice, idk
        2 = Short, matter of fact
    Randomly selected if picked is left empty'''
    if not fav_food:
        message1 = {"subject" : "Below Minimum Calories",
                    "message" : f"""You are currently {missing_calories} calories below your minimum calories.\nI recommend that you eat something to make up for that to stay above you're minimum daily calories.""",}
        message2 = {"subject" : "Under Eating",
                    "message" : f"""Under eating isn't healthy. Fitness doesn't mean starving yourself.\nTry to eat something today.\nI recommend that you anything that will give provide at least {missing_calories} calories.\nGodd luck, you're doing well."""}
        message3 = {"subject" : "Not Eating Enough",
                    "message" : f"""You are {missing_calories} below yor target calories."""}
        
        messages = [message1, message2, message3]
        return messages[picked]
    
    message1 = {"subject" : "Below Minimum Calories",
                "message" : f"""You are currently {missing_calories} calories below your minimum calories.\nI recommend that you eat something to make up for that to stay above you're minimum daily calories.\n For example about {grams} grams of {fav_food}.""",}
    message2 = {"subject" : "Under Eating",
                "message" : f"""Under eating isn't healthy. Fitness doesn't mean starving yourself.\nTry to eat something today.\nI recommend about {grams} grams of {fav_food} or anything that will give provide at least {missing_calories} calories.\nGodd luck, you're doing well."""}
    message3 = {"subject" : "Not Eating Enough",
                "message" :  f"""Recommendation: Eat {grams} grams of {fav_food}.\nYou are {missing_calories} below your target calories."""}
    
    messages = [message1, message2, message3]
    return messages[picked]

#preference = user.preference  #type of message user prefers?

def Status(user: User):
    '''Used to check on the user's progress today and returns a message (in a dict) describing it.'''
    today = datetime.today().strftime("%d/%m/%y")
    message = {}
    todays_calories = Calories_Today(user)

    if len(user.last_exercises) >= OPTIONS:
        user.last_exercises = {}
    
    if len(user.last_food) >= OPTIONS:
        user.last_food = {}

    if today not in user.journal:
        message = Log_Message(picked=randint(0, 2))

    elif todays_calories > user.target_calories:
        excess_calories = todays_calories - user.target_calories
        try:
            fav_exercise = Favourite_Exercise(user, list(user.last_exercises.keys()))
            user.last_exercises[fav_exercise.name] = len(user.last_exercises)

        except Exercise.DoesNotExist:
            fav_exercise = Exercise.objects.get(name=choice(EXERCISE_NAMES))
            user.last_exercises[fav_exercise.name] = len(user.last_exercises)

        duration =int( (excess_calories * 200) / (3.5 * user.height * fav_exercise.met) )
        message = Excess_Message(excess_calories=excess_calories, duration=duration, fav_exercise=fav_exercise.name, picked=randint(0, 2))


    elif todays_calories < user.min_calories:
        missing_calories = user.min_calories - todays_calories
        try:
            fav_food = Favourite_Food(user, list(user.last_food.keys()))
            
        except Food.DoesNotExist:
            fav_food = Food.objects.get(name=choice(FOOD_NAMES))
            
        if fav_food:
            grams =int( (100 / fav_food.calories) * missing_calories )
            user.last_food[fav_food.name] = len(user.last_food)
            message = Min_Message(missing_calories=missing_calories, fav_food=fav_food.name, grams=grams, picked=randint(0, 2))

        else:
            message = Min_Message(missing_calories=missing_calories)

    user.save()
    return message

