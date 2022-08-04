from audioop import reverse
from code import interact
from datetime import datetime
from itertools import count
from random import choices
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from requests import post
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .filters import opportunityFilter
from .forms import *
from .models import *


def index(request):
    web = opportunity.objects.filter(interest__icontains = 'Web').count()
    mobile = opportunity.objects.filter(interest__icontains = 'Mobile').count()
    game = opportunity.objects.filter(interest__icontains = 'Gaming').count()
    ml_ai = opportunity.objects.filter(interest__icontains = 'Machine Learning/AI').count()
    cloud = opportunity.objects.filter(interest__icontains = 'Cloud').count()
    devops = opportunity.objects.filter(interest__icontains = 'Devops').count()
    cyber = opportunity.objects.filter(interest__icontains = 'Cybersecurity').count()
    ar_vr = opportunity.objects.filter(interest__icontains = 'AR/VR').count()
    block = opportunity.objects.filter(interest__icontains = 'Blockchain').count()
    dict1 = {('Web',web),('Mobile',mobile),('blockchain',block),('Gaming',game),('Machine Learning/AI',ml_ai),('Cloud',cloud),('Devops',devops),('Cybersecurtiy',cyber),('AR/VR',ar_vr)}
    dict = sorted(dict1, reverse=True,key=lambda x:x[1])
    return render(request, "Allops/index.html",{
        "dict": dict
    })


def signin(request):
    if request.method == 'POST':
        form = signin_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                return render(request, "Allops/signin.html", {
                    "form": form,
                    "message": "Invalid username or password!"
                })
    else:
        form = signin_form()
        return render(request, "Allops/signin.html", {
            "form": form
        })


def signup(request):
    if request.method == 'POST':
        form = signup_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_pass = form.cleaned_data['confirm_pass']
            if password != confirm_pass:
                return render(request, "Allops/signup.html", {
                    "form": form,
                    "message": "Passwords didn't match!"
                })
            try:
                user = User.objects.create_user(username, email, password)
                user.save
            except IntegrityError:
                return render(request, "Allops/signup.html", {
                    "form": form,
                    "message": "Username already taken!"
                })
            login(request, user)
            return redirect('index')
    else:
        form = signup_form()
        return render(request, "Allops/signup.html", {
            "form": form
        })


def signout(request):
    logout(request)
    return redirect('index')


def compete(request):
    items = opportunity.objects.filter(type='Competitive').order_by('-time')
    filter = opportunityFilter(request.GET, queryset=items)
    items = filter.qs
    user = request.user
    if user.is_authenticated:
        saves = save.objects.filter(user=request.user)
        return render(request, "Allops/Compete.html", {
            "items": items,
            "saves": saves,
            "filter": filter
        })
    else:
        return render(request, "Allops/compete.html", {
            "items": items,
            "filter": filter
        })


def event(request):
    items = opportunity.objects.filter(type='Event')
    user = request.user
    if user.is_authenticated:
        saves = save.objects.filter(user=request.user)
        return render(request, "Allops/event.html", {
            "items": items,
            "saves": saves
        })
    else:
        return render(request, "Allops/event.html", {
            "items": items
        })


def program(request):
    items = opportunity.objects.filter(type='Program')
    user = request.user
    if user.is_authenticated:
        saves = save.objects.filter(user=request.user)
        return render(request, "Allops/program.html", {
            "items": items,
            "saves": saves
        })
    else:
        return render(request, "Allops/program.html", {
            "items": items
        })


def course(request):
    items = opportunity.objects.filter(type = 'Course')
    user = request.user
    if user.is_authenticated:
        saves = save.objects.filter(user = request.user)
        return render(request, "Allops/course.html", {
            "items": items,
            "saves": saves
        })
    
    else:
        return render(request, "Allops/course.html", {
            "items": items
        })


def activity(request, item_id):
    item = opportunity.objects.get(id = item_id)
    user = request.user
    if user.is_authenticated:
        saved = save.objects.filter(user = user, activity = item).first()
        return render(request, "Allops/opportunity.html",{
            "item": item,
            "saved": saved
        })
    else:
        return render(request, "Allops/opportunity.html",{
            "item": item
        })

@login_required
@csrf_exempt
def save_it(request, item_id):
    try:
        user = request.user
        post = opportunity.objects.get(id = item_id)

        saved = save.objects.filter(user = user, activity = post).first()

        if saved is None:
            saveit = save.objects.create(user = user, activity = post)
            saveit.save()
            css="fas fa-bookmark"
        else:
            saved.delete()
            css="far fa-bookmark fa-inverse"
    except:
        return HttpResponseBadRequest("somethins went wrong!")
    return JsonResponse({
        "css": css
    })

@login_required
def saved(request):
    user = request.user

    saves = save.objects.filter(user = user)
    items = opportunity.objects.all()
    if saves is not None:
        return render(request, "Allops/saved.html",{
            "saves": saves,
            "itmes": items
        })
    else:
        return render(request, "Allops/saved.html",{
            "msg": "Such empty! 0_0..."
        })

@login_required
def share(request):
    if request.method == 'POST':
        form = share_form(request.POST)
        if form.is_valid():
            head = form.cleaned_data['head']
            desc = form.cleaned_data['desc']
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            location = form.cleaned_data['location']
            details = form.cleaned_data['details']
            image = form.cleaned_data['image']
            link = form.cleaned_data['link']
            type = form.cleaned_data['type']
            interest = form.cleaned_data['interest']
            time = datetime.now
            user = request.user
            try:
                opportunity.objects.create(
                    head = head, desc = desc, start = start, end = end, location = location, details = details,
                    image = image, link = link, type = type, interest = interest, time = time, user = user
                )
            except:
                return render(request, "Allops/share.html",{
                    "msg": "Something went wrong, we migth alredy have this listed!"
                })
            users = mails()
            recep_list = []
            for tag in interest:
                users = mails.objects.filter(fields__icontains = tag)
            for user in users:
                recep_list.append(user.mail_id)
            #send mails to user
            template = render_to_string('Allops/mail_template.html',{
                "user": request.user,
                "head": head
            })
            email = EmailMessage(
                'Opportunity for you on Allops',
                template,
                settings.EMAIL_HOST_USER,
                recep_list
            )
            email.fail_silently = False
            email.send()
                
            return render(request, "Allops/share.html",{
                "msg": "Successfully posted!, thank you for your time and effort.",
                "recep_list": recep_list
            })
    else:
        form = share_form()
        return render(request, "Allops/share.html",{
            "form": form
        })

@login_required
def profile(request):

    user = request.user
    items = opportunity.objects.filter(user = user).order_by('-time')
    filter = opportunityFilter(request.GET, queryset=items)
    items = filter.qs
    saves = save.objects.filter(user = user)

    return render(request, "Allops/profile.html",{
        "items": items,
        "saves": saves,
        "filter": filter
    })

@login_required
def activate_mails(request):
    if request.method == 'POST':
        form = mails_form(request.POST)
        if form.is_valid():
            fields = form.cleaned_data['fields']
            mail_id = form.cleaned_data['mail_id']
            user = request.user
            mail_user = mails.objects.create(user = user, mail_id = mail_id, fields = fields)
            mail_user.save()
            return render(request, "Allops/mails.html",{
                "message": "Successfully subscribed to mails"
            })
    else:
        form = mails_form()
        user = request.user
        return render(request, "Allops/mails.html",{
            "form": form,
            "user": user
        })
