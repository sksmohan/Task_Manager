from django import forms
from .models import Task
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


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
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status', 'created_by','message','project']

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
                'class':'form_status'
            }),
            'created_by':forms.TextInput(attrs={
                'class':'form_created_by',
                'readonly': 'readonly'
            }),
            'message':forms.Textarea(attrs={
                'class':'form_message'
            })

        }