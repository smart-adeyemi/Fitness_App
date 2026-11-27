from django.core.management.base import BaseCommand
from templates.models import *
from datetime import *
from random import *
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    help = 'Creates a history for a user by adding random foods and exercises'

    def add_arguments(self, parser):

        #Optional arguments
        parser.add_argument(
            '--email',
            type=str,
            default='test@example.com',
            help='Email of user to create history for (default: test@example.com)'
        )

        parser.add_argument(
            '--days',
            type=int,
            default=60,
            help='How far back the history should be made (default: 60)'
        )

        parser.add_argument(
            '--overwrite',
            type=bool,
            default=False,
            help='''If user's history should be wiped for the days specified (default: False)'''
        )
        
        parser.add_argument(
            '--wipe',
            type=bool,
            default=False,
            help='''If user's history should be wiped before adding history (default: False)'''
        )

        parser.add_argument(
            '--today',
            type=bool,
            default=False,
            help='''If History should be created for today (Default: False)'''
        )
        
    def handle(self, *args, **options):
        FOOD_NAMES = list(Food.objects.values_list('name', flat=True))
        EXERCISE_NAMES = list(Exercise.objects.values_list('name', flat=True))
        today = datetime.today()

        try:
            days = options['days']
            user = User.objects.get(email=options['email'])
            boundries = [user.min_calories, user.target_calories, user.average_calorie_intake] #user will randomly over or under eat
            
            if options['wipe']:
                user.journal = {}
                user.exercises = {}

            for x in range(days):
                if options['today']:
                    x += 1
                day = (today - timedelta(days - x)).strftime("%d/%m/%y")
                if day not in user.journal or options['overwrite']:
                    food_name = choice(FOOD_NAMES)
                    food = Food.objects.get(name=food_name)
                    grams_per_calorie = 100 / food.calories #e.g. 1.25
                    #calories_per_gram = food.calories / 100 #e.g. 0.80
                    total_grams = int( choice(boundries) * grams_per_calorie ) + randint(-100, 100)
                    total_eaten = int((food.calories / 100) * total_grams)
                    user.journal[day] = {food_name : total_grams, "total" : total_eaten}

                if day not in user.exercises or options['overwrite']:
                    exercise_name = choice(EXERCISE_NAMES)
                    exercise = Exercise.objects.get(name=exercise_name)
                    max_calorie_loss = (user.journal[day]["total"] / 2) + randint(-100, 100) #Make sure user doesn't lose more calories than they gain
                    max_duration = int( (max_calorie_loss * 200) / (3.5 * user.height * exercise.met) )
                    duration = randint(0, max_duration)
                    if duration > 0:
                        total_lost = int( (exercise.met * 3.5 * user.height * duration) / 200 )
                        user.exercises[day] = {exercise_name : duration, "total" : total_lost}

    
            user.save()
            self.stdout.write(f'History for user "{user.username}" created.')

        except ObjectDoesNotExist:
            self.stderr.write(self.style.ERROR(f"There is no user with this email: {options['email']}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))

