from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpRequest
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .forms import LoginForm
from django.contrib.auth import authenticate
from django.contrib.auth import logout as logoutAuth
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
def commandpage(request,number):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("login")
    class product():
        def __init__(self, listen):
            self.name = listen[0]
            self.quantity = listen[1]
            self.price = listen[2]
    try:
        clientname, idclient = sendstr("CLIENTNAME,=" + str(number)).split(",=")
    except:
        clientname, idclient = "VAZIO", ""
    products = sendstr("PRODUCTSON,=" + str(number)).split(",=")
    if products != [""]:
        for k, i in enumerate(products):
            products[k] = product(i.split("|"))
        productson = True 
    else:
        productson = False
    return render(request, "aplicacao/command.html", {"navname": f"comanda {number}({clientname})", "clientname": clientname, "id": idclient, "products": products, "productson": productson, "number":number, "backname": "commands"})
def commands(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("login")
    class occupiedclass():
        def __init__(self, number, text, occupied = False):
            self.number = number
            self.occupied = occupied
            self.text = text
    limit = int(sendstr("LIMITCOMMANDS")) + 1
    occupied = sendstr("OPENCOMMANDS").split(",=")
    listen = []
    numbers = len(str(limit - 1))
    for i in range(1, limit):
        temp = str(i)
        if str(temp) in occupied:
            text = ((len(str(temp)) - numbers) * -1) * "0" + f"{temp}"
            listen.append(occupiedclass(i, text, True ))
        else:
            text = ((len(str(temp)) - numbers) * -1) * "0" + f"{temp}"
            listen.append(occupiedclass(temp, text))
    return render(request, "aplicacao/commands.html", {"navname": "commands", "backname": '', "commands": listen})

def neworder(request, number):
    class category():
        def __init__(self, cod, name):
            self.cod = cod
            self.name = name
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    
    pdt = sendstr("CATEGORIES").split(",=")
    categories = []
    empty = False
    if pdt == ['']:
        empty = True
    for i in pdt:
        n = i.split(".=")
        categories.append(category(n[0], n[1]))
    return render(request, 'aplicacao/neworder.html', {"categories": categories, "empty": empty, "number": number, "navname":f"comanda({number})"})
def category(request, number, cod):
    class products():
        def __init__(self, name, tipe, price, printer):
            self.name = name   
            self.tipe = tipe
            price = price.replace(".", ",")
            if not "," in price:
                price = price + ",00"
            self.price = "R$ " + price
            self.printer = printer
    productscategory = sendstr(f"PRODUCTSCATEGORYID,={cod}").split(",=")
    empty = False
    if productscategory == [""]:
        empty = True
    productslist = []
    for i in productscategory:
        product = i.split("|")
        productslist.append(products(product[0], product[1], product[2], product[3]))
    return render(request, 'aplicacao/category.html', {"products": productslist, "empty": empty, "number": number, "navname":f"comanda({number})", "cod": cod})
def categorysizes(request, number, cod, product, printer):
    class products():
        def __init__(self, name, tipe, price, size):
            self.name = name   
            self.tipe = tipe
            price = price.replace(".", ",")
            if not "," in price:
                price = price + ",00"
            self.price = "R$ " + price
            self.size = size
    sizes = sendstr(f"SIZESCATEGORYID,={product},={cod}").split(",=")
    productslist = []
    empty = False
    if sizes == [""]:
        empty = True
    for i in sizes:
        product = i.split("|")
        productslist.append(products(product, "SIZE", product[1], product[0]))
    print(productslist)
    return render(request, 'aplicacao/categorysize.html', {"products": productslist, "empty": empty, "number": number, "navname":f"comanda({number})", "printer": printer})
def login(request):
    if not request.user.is_authenticated:
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
    return HttpResponse(request, 'commands')

def logout(request):
    if request.user.is_authenticated:
        logoutAuth(request)
    return HttpResponseRedirect(reverse('index'))    


def orderrevision():
    pass