from django.db import models

EMAIL_LENGTH = 50
PASSWORD_LENGTH = 50
NAME_LENGTH = 40

# Create your models here.
class User(models.Model):
    email = models.CharField(max_length=EMAIL_LENGTH) #User see's
    password = models.CharField(max_length=PASSWORD_LENGTH)
    username = models.CharField(max_length=NAME_LENGTH, primary_key=True) #User see's
    age = models.IntegerField() #User see's
    weight = models.FloatField() #User see's
    height = models.FloatField() #User see's
    gender = models.CharField(max_length=NAME_LENGTH) #User see's
    journal = models.JSONField(default=dict(), blank=True, null=True)  #{A date : { name of food : serving size in g }} e.g. {"11/11/2025" : {"egg" : "70", "total" : 70}}
    exercises = models.JSONField(default=dict(), blank=True, null=True) #{A date : { name of exercise : time in min spent exercising } e.g. {"03/06/25": {"Cycling": 30, "total" : 756 }}
    average_calorie_intake = models.IntegerField(default=3000)
    target_calories = models.IntegerField(default=2400) #User see's
    min_calories = models.IntegerField(default=1800) #User see's
    last_exercises = models.JSONField(default=dict(), blank=True, null=True) #{name of ealiest exercise : 0, 2nd earliest : 1, 3rd earliest : 2, and so on}
    last_food = models.JSONField(default=dict(), blank=True, null=True) #{name of ealiest food : 0, 2nd earliest : 1, 3rd earliest : 2, and so on}
    cals_lost_today = models.IntegerField(default=0, blank=True)
    cals_gained_today = models.IntegerField(default=0, blank=True)

class Food(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, primary_key=True) #User see's
    calories = models.FloatField() #per 100g #User might see (not currently)
    protein = models.FloatField() #per 100g #Used in form
    carbs = models.FloatField() #per 100g #Used in form
    fats = models.FloatField() #per 100g #Used in form
    servings = models.FloatField(blank=True, null=True) #default serving size #User see's
    total_calories = models.FloatField(blank=True, null=True) 

class Exercise(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, primary_key=True) #User see's
    type = models.CharField(max_length=NAME_LENGTH) #light, moderate, vigorous
    calories_burned = models.FloatField(blank=True, null=True) #Calories burned per hour, not user specific, might delete later #Used in form
    met = models.FloatField() #Used in form
    duration = models.IntegerField(blank=True, null=True) #Default time doing exercise #Used in form
    #Exercise calories = (MET level of activity x 3.5 x Weight (kg) x minutes of activity) / 200

