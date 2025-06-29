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
    return render(request, "aplicacao/commands.html", {"navname": "Comandas", "backname": '', "commands": listen})

def neworder(request, number):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    class category():
        def __init__(self, cod, name):
            self.cod = cod
            self.name = name
    
    
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    class products():
        def __init__(self, name, cod, tipe, price, printer):
            self.name = name   
            self.tipe = tipe
            self.category = cod
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
        productslist.append(products(product[0], cod, product[1], product[2], product[3]))
    return render(request, 'aplicacao/category.html', {"products": productslist, "empty": empty, "number": number, "navname":f"comanda({number})", "cod": cod})
def categorysizes(request, number, cod, product, printer):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    class products():
        def __init__(self, name, cod, price, size):
            self.name = name   
            price = price.replace(".", ",")
            self.category = cod
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
        productnow = i.split("|")
        productslist.append(products(product, cod, productnow[1], productnow[0]))
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


def orderrevision(request, number):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    class product():
        def __init__(self, index, name, category, tipe, price, printer, qtd, htmlcod):
            self.cod = index
            self.name = name
            self.category = category
            self.tipe = tipe
            self.price = price
            self.printer = printer
            self.qtd = qtd
            self.htmlcod = htmlcod
    products = []
    try:
        products2 = request.COOKIES['products'].split("|")[0:-1]
    except:
        return HttpResponseRedirect(reverse("index"))
    htmlcod = 0
    for j, i in enumerate(products2):
        productcookie = i.split(",-")
        if productcookie[0] != "none":
            products.append(product(j, productcookie[0], productcookie[1], productcookie[2], productcookie[3], productcookie[4], productcookie[5], htmlcod))
            htmlcod += 1
    if products == []:
        return HttpResponseRedirect(reverse('index'))
    return render(request, "aplicacao/revision.html", {"navname": f"Comanda ({number})", "products": products, "number":number})

def edittext(request, number, index):
    class text():
        def __init__(self, value, active = False, index = -1):
            self.text = value
            self.active = active
            self.cod = index
        def test(self, newtext):
            if self.text == newtext:
                print("foi")
                self.active = True
                return True
            return False
    product = request.COOKIES['products'].split("|")[index].split(",-")
    predefnotes = sendstr(f"GETNOTESID,={product[1]}").split(".=")
    product[6] = product[6].split(".-")
    print(product)
    texts = []
    predeftexts = []
    if predefnotes != [""]:
        for m, n in enumerate(predefnotes):
            predeftexts.append(text(n, index = m))
    for j in product[6]:
        num = True
        for n in predeftexts:

            if n.test(j):
                num = False
        if j == "":
            num = False
        if num:
            texts.append(text(j))
    
    return render(request, "aplicacao/edittext.html", {"navname": f"Comanda ({number})", "texts": texts, "predeftexts": predeftexts, "number":number, "indexofproduct": index})



            
def sendorder(request, number):
    products = request.COOKIES['products'].split("|")[index]
    for i, j in enumerate(products):
        products[i] = products[i].split(',-')
        products[i][6] = products[i][6].split(",-")
    print(products)