from django import forms
from .models import Task,CustomUser,Project
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username','email','password','department','is_superuser','is_staff','head','phone_number']

        widgets ={
            'username':forms.TextInput(attrs={
                'class':'username_1 common_class'
            }),
            'phone_number':forms.TextInput(attrs={
                'required': 'required',
                'class':'phone_number_1 common_class'
            }),
            'email':forms.EmailInput(attrs={
                'required': 'required',
                'class':'email_1 common_class'
            }),
            'password':forms.PasswordInput(attrs={
                'class':'password_1 common_class'
            }),
            'is_superuser':forms.CheckboxInput(attrs={
                'class':'is_superuser_1 common_class'
            }),
            'is_staff':forms.CheckboxInput(attrs={
                'class':'is_staff_1 common_class'
            }),
            'department':forms.Select(attrs={
                'class':'department_1 common_class'
            }),
            'head':forms.CheckboxInput(attrs={
                'class':'head_1 common_class'
            })
        }


    def clean_password(self):
        password = self.cleaned_data.get('password')
        print(f'Password entered: {password}')
        if password and len(password)<7:
            raise ValidationError("Password must be more than 7 characters")
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and len(username) <7:
            raise ValidationError("Username must be more than 7 characters ")
        return username

    def save(self,commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        user.set_password(password)
        if commit:
            user.save()
        return user

class loginForm(AuthenticationForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].widget.attrs.update({
            'class':'form_username'
        })
        self.fields['password'].widget.attrs.update({
            'class':'form_password'
        })

class projectfilterform(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project']

        widgets ={
            'project':forms.Select(attrs={
                'class':'form_filterfield',
                'required':'required'
            })
        }

class taskform(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description','assigned_to', 'due_date', 'status', 'created_by','message','project']

        widgets ={
            'title':forms.TextInput(attrs={
                'class':"form_title",
                'readonly': 'readonly'
            }),
            'description':forms.Textarea(attrs={
                'class':'form_description',
                'readonly': 'readonly'
            }),
            'assigned_to':forms.TextInput(attrs={
                'class':'form_assigned_to',
                'readonly': 'readonly'
            }),
            'due_date':forms.DateInput(attrs={
                'class':'form_due_date',
                'readonly': 'readonly'
            }),
            'status':forms.Select(attrs={
                'class':'form_status status_selection'
            }),
            'created_by':forms.TextInput(attrs={
                'class':'form_created_by',
                'readonly': 'readonly'
            }),
            'message':forms.Textarea(attrs={
                'class':'form_message'
            })
        }
class Taskcreation_form(forms.ModelForm):
    class Meta:
        model = Task
        fields = fields = ['title', 'description', 'due_date', 'status','project','including_sunday']

        widgets ={
            'title':forms.TextInput(attrs={
                'class':"task_form_title common1",
                'id':'task_form_title_id'
            }),
            'description':forms.Textarea(attrs={
                'class':'task_form_description common1'
            }),
            'assigned_to':forms.TextInput(attrs={
                'class':'task_form_assigned_to common1',
                'required':True
            }),
            'due_date':forms.DateInput(attrs={
                'class':'task_form_due_date common1',
                'placeholder': 'YYYY-MM-DD',
            }),
            'status':forms.Select(attrs={
                'class':'task_form_status common1'
            }),
            'created_by':forms.TextInput(attrs={
                'class':'task_form_created_by common1',
            }),
            'message':forms.Textarea(attrs={
                'class':'task_form_message common1'
            }),
            "project":forms.Select(attrs={
                'class':'task_form_project common1',
                'required':True
            }),
            "including_sunday":forms.CheckboxInput(attrs={
                'class':'task_form_incl_sunday'
            })
        }

class project_form(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name','description','Is_daily','Is_weekly','Is_monthly']

        widgets={
            'project_name':forms.TextInput(attrs={
                'class':'project_name_1 project_c',
                'id':'fetch_project_name'
            }),
            'description':forms.Textarea(attrs={
                'class':'description_1 project_c'
            }),
            'Is_daily':forms.CheckboxInput(attrs={
                'class':'Is_daily_1 project_c'
            })
        }
    
