from django.core.management.base import BaseCommand
from templates.models import *
from datetime import *
from random import *
from django.core.exceptions import ObjectDoesNotExist

BASE_EXERCISES = {'Walking (default)' : 3.3, 
                  'Jogging (default)' : 8.0,
                  'Running (default)' : 12.5, 
                  'Cycling (default)' : 8, 
                  'Weight Lifting (default)' : 6, 
                  'Soccer (default)' : 10, 
                  'Swimming (default)' : 7}

class Command(BaseCommand):
    help = 'Creates default exercises'

    def add_arguments(self, parser):

        #Optional arguments
        parser.add_argument(
            '--wipe',
            type=bool,
            default=False,
            help='Wipes default exercises before creating them (Default: False)'
        )

    def handle(self, *args, **options):
        users = User.objects.all()
        for name, MeT in BASE_EXERCISES.items():
            if options['wipe']:
                try:
                    Exercise.objects.get(name=name).delete()
                except Exercise.DoesNotExist:
                    pass
                
            if not Exercise.objects.filter(name=name):
                exercise = Exercise(
                    name = name,
                    met = MeT,
                    duration = 60
                )

                #exercise.calories_burned = (exercise.met * 3.5 * user.height * exercise.duration) / 200

                if exercise.met < 3:
                    exercise.type = 'light'
                elif exercise.met <= 6:
                    exercise.type = 'moderate'
                else:
                    exercise.type = 'vigorous'

                exercise.save()

        self.stdout.write(f'Default exercises created.')