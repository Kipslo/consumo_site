from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.template import loader
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .forms import LoginForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as loginAuth
from django.contrib.auth.models import User as Userdata
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    template = loader.get_template("aplicacao/index.html")
    return render(request, "aplicacao/index.html")

def command(request, number):
    return

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "aplicacao/detail.html", {"question": question})


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def login(request):
    if request.method != 'POST':
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            Userdata.objects.aget_or_create
            username = request.POST.get('usuário')
            password = request.POST.get('senha')
            user = authenticate(username= username, password= password)

            if user:
                loginAuth(request, user)
                return HttpResponseRedirect(reverse('index'))
    context = {'form': form}
    return render(request, 'aplicacao/login.html', context)

