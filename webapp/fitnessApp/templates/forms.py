from django import forms
from .models import *
from datetime import *
from django.utils import timezone
from string import punctuation

SPECIAL_CHARS = set(punctuation)
MAX_NUM_ATTENDIES = 128

today = datetime.today()

current_datetime = datetime.now()

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']

    def clean(self):
        try:
            data = self.cleaned_data
            email = data['email']
            password = data['password']

        except KeyError:
            raise forms.ValidationError("You must enter an email and password.")
        
        if (User.objects.filter(email=email, password=password)):
            pass
        else:
            raise forms.ValidationError("Email or password is incorrect")
        
        return self.cleaned_data

       
class Create_Profile_Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'age', 'gender', 'weight', 'height']

    def clean(self):
        try:
            data = self.cleaned_data
            email = data['email']
            password = data['password']
            username = data['username']
            age = data['age']
            gender = data['gender']
            weight = data['weight']
            height = data['height']

        except KeyError:
            raise forms.ValidationError("You must enter an email and password.")
        
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")
        
        elif len(password) > PASSWORD_LENGTH:
            raise forms.ValidationError("Password must be at most " + PASSWORD_LENGTH + " characters long")
        
        if len(username) > NAME_LENGTH:
            raise forms.ValidationError(f"Username can't be longer than {NAME_LENGTH} Characters")
        
        if User.objects.filter(username=username):
            raise forms.ValidationError("Username has been taken")
        
        if User.objects.filter(email=email):
            raise forms.ValidationError("Email already has an account")
        
        special = False
        for x in SPECIAL_CHARS:
            if x in password:
                special = True
                pass

        if not special:
            raise forms.ValidationError("Password must contain special characters, e.g. '/', '!'")
        
        return self.cleaned_data

def Update_Profile_Form(form, old: User):
    try:
        email = form.get('email')
        password = form.get('password')
        username = form.get('username')
        age = form.get('age')
        gender = form.get('gender')
        weight = form.get('weight')
        height = form.get('height')

    except KeyError:
        return "You must enter an email and password."

    if User.objects.filter(username=username) and username != old.username:
        return "Username has been taken"
    
    if len(username) > NAME_LENGTH:
            raise forms.ValidationError(f"Username can't be longer than {NAME_LENGTH} Characters")
    
    if User.objects.filter(email=email) and email != old.email:
        return "Email already has an account"
    
    return "Valid"
    

def ChangePasswordForm(form, user):

    old = form.get('old')
    password = form.get('password')

    if old != user.password:
        return "Wrong Password"
    
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    elif len(password) > PASSWORD_LENGTH:
        return "Password must be at most " + PASSWORD_LENGTH + " characters long"
    
    special = False
    for x in SPECIAL_CHARS:
        if x in password:
            special = True
            pass

    if not special:
        return "Password must contain special characters, e.g. '/', '!'"
    
    return "Valid"

    

class Food_Form(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'calories', 'fats', 'carbs', 'protein', 'servings']

    def clean(self):
        try:
            data = self.cleaned_data
            #print(f'Data  {self.cleaned_data}')
            name = data['name']
            calories = data['calories']
            protein = data['protein']
            carbs = data['carbs']
            fats = data['fats']
            servings = data['servings']

        except KeyError:
            raise forms.ValidationError(f"You must enter all details.") #{name}, {calories}, {protein}, {carbs}, {fats}, {servings}
        
        if name == 'total':
            raise forms.ValidationError("The name 'total' is reserved.")
        
        if Food.objects.filter(name=name):
            raise forms.ValidationError(f"There is already a food item with the name '{name}'.")
        
        '''if protein > 100:
            raise forms.ValidationError("There can't be 100 grams of protein per 100g of food.")
        
        if carbs > 100:
            raise forms.ValidationError("There can't be 100 grams of carbs per 100g of food.")
        
        if fats > 100:
            raise forms.ValidationError("There can't be 100 grams of fats per 100g of food.")'''
        
        return self.cleaned_data

class Exercise_Form(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'met', 'duration']

    def clean(self):
        try:
            data = self.cleaned_data
            name = data['name']
            #calories_burned = data['calories_burned']
            #type = data['type']
            met = data['met']
            duration = data['duration']

        except KeyError:
            raise forms.ValidationError("You must enter all details.")
        
        if name == 'total':
            raise forms.ValidationError("The name 'total' is reserved.")
        
        if Exercise.objects.filter(name=name):
            raise forms.ValidationError(f"There is already an exercises with the name '{name}'.")
        
        return self.cleaned_data
    
'''
class Help_Form(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "Your e-mail"})
    )
    subject = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Subject"}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Your message"})
    )
'''