from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from .forms import *
from .models import *
from django.db.models import Q
from django.db.models import F
from datetime import date
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from datetime import *
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from json import dumps
from .helper_functions import *

def login(request):
    try:
        user = get_user(request)
        return redirect('homepage')
    except UserNotFound:
        pass

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            response = redirect("homepage")
            response.set_cookie('user', user.email)

            #request.session["user"] = user.email
            return response
        else:     
            return render(request, "login.html", {'form': form})
    else:
        form = LoginForm()
        return render(request, "login.html", {'form': form})

def logout(request):
    #request.session.pop("user")
    response = redirect("login")
    response.delete_cookie("user")
    form = LoginForm()
    return response

def Create_Profile(request):
    if request.method == 'POST':
        form = Create_Profile_Form(request.POST)

        if form.is_valid():
            user = form.save()
            pal = request.POST.get('pal')
            user.average_calorie_intake = calTDEE(user, PAL_DICT[pal])
            user.target_calories = calTDEE(user, PAL_DICT[pal]) - 500 #check calcs later
            user.min_calories = calcBMR(user)
            user.save()

            response = HttpResponse("User Cookie Set!")
            response.set_cookie('user', user.email)

            #request.session["user"] = user.email
            return redirect("homepage")
        else:     
            return render(request, "create_profile.html", {'form': form})
    else:
        form = Create_Profile_Form()
        return render(request, "create_profile.html", {'form': form})
    
def Home(request):
    try:
        user = get_user(request)
        
        journal_img = 'templates/images/journal.png'
        recipes_img = 'templates/images/recipes.png'
        exercise_img = 'templates/images/exercise.png'
        nutrition_img = 'templates/images/nutrition.png'

        user.cals_gained_today = Calories_Eaten_Today(user)
        user.cals_lost_today = Calories_Lost_Today(user)
        user.save()

        #target_calories = user.average_calorie_intake - 600 #check calcs later
        #min_calories = user.average_calorie_intake * 0.6 #check calcs later
        
        todays_calories = Calories_Today(user)

        return render(request, "homepage.html", {'user' : user,
                                                    'todays_calories' : todays_calories,
                                                    'journal_img' : journal_img,
                                                    'recipes_img' : recipes_img,
                                                    'exercise_img' : exercise_img,
                                                    'nutrition_img' : nutrition_img})

    except KeyError:
        messages.success(request, 'Please login first.')
        return redirect("login")
    
    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")
  
def View_Profile(request):
    try:
        user = get_user(request)
        return render(request, "profile.html", {'user' : user})

    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")

    #getting account's rentals

def Update_Profile(request):
    try:
        user = get_user(request)
        if request.method == 'POST':
            form = Update_Profile_Form(request.POST, user)

            if form == "Valid":
                user.username = request.POST.get('username')
                user.email = request.POST.get('email')
                user.age = int(request.POST.get('age'))
                user.gender = request.POST.get('gender')
                user.weight = float(request.POST.get('weight'))
                user.height = float(request.POST.get('height'))
                user.save()

                pal = request.POST.get('pal')
                user.average_calorie_intake = calTDEE(user, PAL_DICT[pal])
                user.target_calories = calTDEE(user, PAL_DICT[pal]) - 500 #check calcs later
                user.min_calories = calcBMR(user)
                user.save()

                messages.success(request, 'Profile successfully updated.')

                return redirect("view_profile")
            
            else:
                update_error = form
                return render(request, "update_profile.html", {'user' : user,
                                                               'update_error' : update_error})
        
        '''send_mail(
                "Test",
                f'hi',
                DEFAULT_EMAIL,
                [user.email],
                fail_silently=False,
            )'''
        
        return render(request, "update_profile.html", {'user' : user})
        

    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")

def Change_Password(request):
    try:
        user = get_user(request)

        form = ChangePasswordForm(request.POST, user)

        if form == "Valid":
            new_password = request.POST.get('password')
            user.password = new_password
            user.save()
            messages.success(request, 'Password has changed.')
            return render(request, "profile.html", {'user' : user,
                                                            'changed' : True})
        
        else:
            messages.error(request, f"{form}")
            return render(request, "update_profile.html", {'user' : user,
                                                        'password_form' : form})
        
    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")

def Journal(request):
    '''For the food page. Also used for when a user adds a new food item'''
    try:
        user = get_user(request)
        form = Food_Form()
        if request.method == 'POST': #Adding new food items
            print("Submitted data:", request.POST)
            form = Food_Form(request.POST)
            if form.is_valid():
                food = form.save()
                food.total_calories = (food.calories / 100) * food.servings
                food.save()
                messages.success(request, f'Food item {food.name} added.')
                return redirect("journal")
            
        food_dict = {}
        all_foods = Food.objects.all()
        for food in all_foods:
            food_dict[food.name] = food.calories

        today = datetime.today().strftime("%d/%m/%y")
        food_today = {}
        calories_eaten = 0

        todays_calories = Calories_Today(user)

        if today in user.journal:
            food_today = user.journal[today]

            user.journal[today]["total"] = Calories_Eaten_Today(user)
            calories_eaten = user.journal[today]["total"]
            user.cals_gained_today = user.journal[today]["total"]
            user.save()
        else:
            calories_eaten = 0

        return render(request, "journal.html", {'user': user,
                                                'form' : form,
                                                'food_today' : food_today,
                                                'food_dict' : food_dict,
                                                'todays_calories' : todays_calories,
                                                'calories_eaten' : calories_eaten})

    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")

def Log_Food(request):
    '''Used for logging food eaten today'''
    try:
        user = get_user(request)
        name = request.POST.get('name')
        servings = int(request.POST.get('servings'))
        food = Food.objects.get(name=name)
        if servings == 0:
            servings = food.servings

        today = datetime.today().strftime("%d/%m/%y")
        #eat_time = datetime.today().strftime("%H:%M:%S")

        if today in user.journal:
            if name in user.journal[today]:
                user.journal[today][name] = int(user.journal[today][name]) + servings
            else:
                user.journal[today][name] = servings
        else:
            user.journal[today] = {name : servings}

        user.save()
        user.journal[today]["total"] = Calories_Eaten_Today(user)
        user.cals_gained_today = user.journal[today]["total"]
        user.save()

        if user.journal[today]["total"] > user.target_calories:
            '''excess_calories = user.journal[today]['total'] - user.target_calories
            fav_exercise = Favourite_Exercise(user)
            duration = (excess_calories * 200) / (3.5 * user.height * fav_exercise.met)'''

            message = Status(user)

            send_mail(
                message["subject"],
                message["message"],
                DEFAULT_EMAIL,
                [user.email],
                fail_silently=False,
            )

        messages.success(request, f'{food.name} logged.')

        return redirect("journal")
    
    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")

def Exercise_Page(request):
    '''Used for Exercise page. Also used to add new exercises'''
    try:
        user = get_user(request)
        form = Exercise_Form()
        if request.method == 'POST': #Adding a new exercise
            form = Exercise_Form(request.POST)
            if form.is_valid():
                exercise = form.save()
                messages.success(request, f'New Exercise {exercise.name} added.')
                exercise.calories_burned = (exercise.met * 3.5 * user.height * exercise.duration) / 200

                if exercise.met < 3:
                    exercise.type = 'light'
                elif exercise.met <= 6:
                    exercise.type = 'moderate'
                else:
                    exercise.type = 'vigorous'

                exercise.save()

                return redirect("exercise")

        exercise_dict = {}
        all_exercises = Exercise.objects.all()
        for exercise in all_exercises:
            exercise_dict[exercise.name] = exercise.calories_burned

        total_calories_burned = Calories_Lost_Today(user)
        user.cals_lost_today = Calories_Lost_Today(user)
        user.save()
        today = datetime.today().strftime("%d/%m/%y")
        exercises_today = {}

        todays_calories = Calories_Today(user)

        if today in user.exercises:
            exercises_today = user.exercises[today]

        return render(request, "exercise.html", {'user': user,
                                                'form' : form,
                                                'todays_calories' : todays_calories,
                                                'exercises_today' : exercises_today,
                                                'exercise_dict' : exercise_dict,
                                                'total_calories_burned' : total_calories_burned})
    
    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")

def Log_Exercise(request):
    '''Used to log exercises done today'''
    try:
        user = get_user(request)
        name = request.POST.get('name')
        duration = int(request.POST.get('duration'))
        exercise = Exercise.objects.get(name=name)
        if duration == 0:
            duration = exercise.duration

        today = datetime.today().strftime("%d/%m/%y")

        if today in user.exercises:
            if name in user.exercises[today]:
                user.exercises[today][name] = int(user.exercises[today][name]) + duration
            else:
                user.exercises[today][name] = duration
        else:
            user.exercises[today] = {name : duration}

        user.save()
        user.exercises[today]["total"] = Calories_Lost_Today(user)
        user.cals_lost_today = user.exercises[today]["total"] 
        user.save()

        messages.success(request, f'{exercise.name} logged.')

        return redirect("exercise")
    
    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")

def Stats(request):
    '''Loads page where user can view stats and progress'''
    try:
        user = get_user(request)
        #stats per month
        month = datetime.today().strftime("%m")
        today = datetime.today()
        calories_eaten = []
        calories_lost = []
        calories_total = []
        dates = []
        best_of = {}
        for x in range(7):
            day = (today - timedelta(days=(6 - x))).strftime("%d/%m/%y")
            dates.append(day)
            calories_eaten.append(Calories_Eaten_Today(user, day))
            calories_lost.append(Calories_Lost_Today(user, day))
            calories_total.append(Calories_Today(user, day))

        user.cals_gained_today = Calories_Eaten_Today(user)
        user.cals_lost_today = Calories_Lost_Today(user)
        user.save()

        message = Status(user)

    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")
    
    return render(request, "stats.html", {'user' : user,
                                          'message' : message,
                                          'dates' : dumps(dates),
                                          'calories_eaten' : dumps(calories_eaten),
                                          'calories_lost' : dumps(calories_lost),
                                          'calories_total' : dumps(calories_total)})

def Settings(request):
    '''Used to load settings page'''
    try:
        user = get_user(request)
        return render(request, "settings.html", {'user' : user})
    
    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")
    
'''
def Help(request):
    try:
        user = get_user(request)
        if request.method == 'POST':
            form = Help_Form(request.POST)
            if form.is_valid():
                message = request.POST.get('message')
                subject = request.POST.get('subject')

                send_mail (
                    subject,
                    message,
                    user.email,
                    [DEFAULT_EMAIL],
                    fail_silently=False
                )

                messages.success(request, "Email sent")
                return redirect('help')
            
            else:
                return render(request, "help.html", {'user' : user,
                                                     'form' : form})
            
        return render(request, "help.html", {'user' : user})
    
    except UserNotFound:
        messages.error(request, "Please log in first.")
        return redirect("login")
'''