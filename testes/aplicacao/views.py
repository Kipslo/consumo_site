from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .forms import LoginForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as loginAuth
from django.contrib.auth.models import User as Userdata
import socket


PORT = 55261
def sendstr(data):       
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostbyname(socket.gethostname()), PORT))
    s.sendall(str.encode(data))
    data = s.recv(2024)
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    return data.decode()

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("login")
    return HttpResponseRedirect("commands")
def command(request,number):
    return
def commands(request):
    limit = int(sendstr("LIMITCOMMANDS")) + 1
    return render(request, "aplicacao/commands.html", {"navname": "commands", "back": False, "backname": '', "limit": range(1,limit), })

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "aplicacao/detail.html", {"question": question})


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def login(request):
    messageerror = ""
    if request.method != 'POST':
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = False
            username = request.POST.get('usuário')
            password = request.POST.get('senha')
            data = ""
            try:
                data = sendstr("LOGIN,=" + username + ",=" + password)
                if data == "YES":
                    try:
                        user = authenticate(username= username, password=password)
                        if not user:
                            user = Userdata.objects.get(username= username)
                            user.delete()
                            raise
                    except:
                        Userdata.objects.create_user(username=username, email="9999999@gmail.com", password=password)
                        user = authenticate(username= username, password=password)
                elif data == "NOT":
                    messageerror = "USUÁRIO OU SENHA INVÁLIDO"
            except Exception as error:
                print(error)
                messageerror = "FALHA NA CONEXÃO"
            if user:
                loginAuth(request, user)
                return HttpResponseRedirect(reverse('index'))
    context = {'form': form, 'error': messageerror}
    return render(request, 'aplicacao/login.html', context)

