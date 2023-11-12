
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

from tasks.forms import CreateTaskForm
from tasks.models import Task


# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except Exception as e:  # se puede usar un error en especifico como IntegrityError
                print(e)
                return render(request, 'signup.html', {'form': UserCreationForm, 'error': 'Username already existss'})
        else:
            return render(request, 'signup.html', {'form': UserCreationForm, 'error': 'Passwords do not match'})

    return render(request, 'signup.html', {'form': UserCreationForm})


def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True).order_by('important').reverse()
    return render(request, 'task.html', {'tasks': tasks})


def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'POST':
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Username or password is incorrect'})

    return render(request, 'signin.html', {
        'form': AuthenticationForm
    })


# tasks
def create_task(request):

    if request.method == 'POST':
        form = CreateTaskForm(request.POST)

        if form.is_valid():
            try:
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                return redirect('tasks')
            except ValueError as e:
                return render(request, 'create_task.html', {
                    'form': form,
                    'error': f'Error saving task {e}'
                })

        else:
            return render(request, 'create_task.html', {
                'form': form
            })

    form = CreateTaskForm
    return render(request, 'create_task.html', {
        'form': form
    })


def task_detail(request, task_id):
    
    task = get_object_or_404(Task, id = task_id, user_id=request.user)
    if task.user != request.user:
        return redirect('tasks')
    form = CreateTaskForm(instance=task)
    if request.method == 'POST':
        form = CreateTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')
    return render(request, 'task_detail.html', {'task': task, 'form': form})


def task_delete(request, task_id):
    
    task = get_object_or_404(Task, id = task_id, user_id=request.user)
    if task.user != request.user:
        return redirect('tasks')
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
    return redirect('tasks')

def task_done(request, task_id):
    
    task = get_object_or_404(Task, id = task_id, user_id=request.user)
    if task.user != request.user:
        return redirect('tasks')
    if request.method == 'POST':
        task.datecompleted = datetime.now()
        task.save()
        return redirect('tasks')
    
    return redirect('tasks')

def completed_task(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'completed-tasks.html', {'tasks': tasks})