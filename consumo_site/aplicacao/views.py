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


PORT = 54162
def checklogin(request):
    temp = {"Y": True, "N": False}
    responseserver = sendstr(f"CHECKLOGIN,={request.user.username}")
    print(responseserver)
    return temp[responseserver]
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
        return HttpResponseRedirect(reverse("login"))
    return HttpResponseRedirect("commands")
def commandpage(request,number):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
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
    return render(request, "aplicacao/command.html", {"navname": f"Comanda {number}({clientname})", "clientname": clientname, "id": idclient, "products": products, "productson": productson, "number":number, "backname": "commands"})
def commands(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
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
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
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
    return render(request, 'aplicacao/neworder.html', {"categories": categories, "empty": empty, "number": number, "navname":f"Comanda({number})"})
def category(request, number, cod):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
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
    return render(request, 'aplicacao/category.html', {"products": productslist, "empty": empty, "number": number, "navname":f"Comanda({number})", "cod": cod})
def categorysizes(request, number, cod, product, printer):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
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
    return render(request, 'aplicacao/categorysize.html', {"products": productslist, "empty": empty, "number": number, "navname":f"Comanda({number})", "printer": printer})
def divisionpage(request, number):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
    products = request.COOKIES['products'].split("|")
    value = ""
    products[-1] = products[-1].split(",-")[1:]
    temp = False
    for i in products[-1]:
        if temp:
            value = value + ", " + str(i)
        else:
            value = i
            temp = True
    return render(request, 'aplicacao/divisionpage.html', {"navname": f"Dividir a comanda ({number})", "value":value, "number":number})
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
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
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
    except Exception as error:
        return HttpResponseRedirect(reverse("index"))
    htmlcod = 0
    for j, i in enumerate(products2):
        productcookie = i.split(",-")
        if productcookie[0] != "none":
            products.append(product(j, productcookie[0], productcookie[1], productcookie[2], productcookie[3], productcookie[4], productcookie[5], htmlcod))
            htmlcod += 1
    if products == []:
        return HttpResponseRedirect(reverse('index'))
    return render(request, "aplicacao/revision.html", {"navname": f"Comanda ({number})", "products": products, "number":number, "divisionbutton": True})

def edittext(request, number, cod):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
    class text():
        def __init__(self, value, active = False, cod = -1):
            self.text = value
            self.active = active
            self.cod = cod
        def test(self, newtext):
            if self.text == newtext:
                print("foi")
                self.active = True
                return True
            return False
    product = request.COOKIES['products'].split("|")[cod].split(",-")
    predefnotes = sendstr(f"GETNOTESID,={product[1]}").split(".=")
    product[6] = product[6].split(".-")
    texts = []
    predeftexts = []
    if predefnotes != [""]:
        for m, n in enumerate(predefnotes):
            predeftexts.append(text(n, cod = m))
    for j in product[6]:
        num = True
        for n in predeftexts:

            if n.test(j):
                num = False
        if j == "":
            num = False
        if num:
            texts.append(text(j))
    return render(request, "aplicacao/edittext.html", {"navname": f"Comanda ({number})", "texts": texts, "predeftexts": predeftexts, "number":number, "indexofproduct": cod})

def addclient(request, number):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
    class entry():
        def __init__(self, cod, name, htmlcod):
            self.cod = cod
            self.name = name
            self.htmlcod = htmlcod
    entries = sendstr("ENTRIES").split(".=")
    listen = []
    htmlcod = 0
    for i in entries:
        cod, name = i.split(",=") 
        listen.append(entry(cod, name, htmlcod))
        htmlcod += 1
    return render(request, "aplicacao/addclient.html", {"navname": f"Comanda ({number})", "predeftexts": listen, "number":number})
def sendorder(request, number):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
    products = request.COOKIES['products'].split("|")
    print(products)
    for i, j in enumerate(products[:-1]):
        products[i] = j.split(',-') 
        print(products)
        products[i][6] = products[i][6].split(".-")
    products[-1] = products[-1].split(',-')
    username = request.user.username
    commands = f'{products[-1][0]}'
    for i in products[-1][1:]:
        commands = commands + f".={i}"
    if number == int(products[-1][0]):
        end = 0
        for i in products[:-1]:
            product, categoryid, size, unitvalue, prynter, qtd, pretext = i
            unitvalue = unitvalue.replace('R$ ', "")
            if pretext != [''] and pretext != ['undefined'] and pretext != '':
                texts = f'{pretext[0]}'
                for j in range(len(pretext) - 1):
                    texts = texts + f".={pretext[j+1]}"
                strforsend = f"INSERTHOST,={commands},={username},={product}.-{categoryid}.-{unitvalue}.-{qtd}.-{texts}.-{size}.-{prynter}"
            else:
                strforsend = f"INSERTHOST,={commands},={username},={product}.-{categoryid}.-{unitvalue}.-{qtd}.-{size}.-{prynter}"
            result = sendstr(strforsend)
            if result != "Y":
                end = result
        print(end)
        if end == 0:
            return HttpResponseRedirect(reverse('index'))
        
def sendclient(request, number):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
    cod, clientname = request.COOKIES['client'].split(",-")
    entriescookie = request.COOKIES['entries'].split(",-")
    entries = []
    sendtext = f"INSERTCLIENTID,={request.user.username},=passwordfake,={number},={cod},={clientname}"
    num = True
    for i in entriescookie:
        name, qtd = i.split(".-")
        if num:
            sendtext = sendtext + f",={name}.={qtd}"
            num = False
        else:
            sendtext = sendtext + f";={name}.={qtd}"
        entries.append(i.split(".-"))
    print(sendtext)
    print(sendstr(sendtext))
    return HttpResponseRedirect(reverse('index'))
def closecommand(request, number):
    print(request.method)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if not checklogin(request):
        logoutAuth(request)
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        postTipe = request.POST['postTipe']
        print(postTipe)
        temp = request.COOKIES['paymentslist'].split(".-")
        payments = []
        for i in temp[0:-1]:
            payments.append(i.split(",-"))
        print(payments)
        print(temp[-1])
        if int(temp[-1]) == int(number):
            print("aqui")
            textforsend = f"CLOSECOMMAND,={request.user.username},={postTipe},={number}"
            for i in payments:
                textforsend = textforsend + f",={i[0]}.={i[1]}"
            permission = sendstr(textforsend)
            print(permission)
        #if permission == "Y":
        return HttpResponseRedirect(reverse('index'))
        #else:
            #return render(request, "aplicacao/navbar.html", {"navname": permission})
    else:
        class pagment():
            def __init__(self, tipe, quantity):
                self.tipe = tipe
                self.quantity = quantity
        try:
            pagmentstemp = request.COOKIES['paymentslist']
            pagmentstemp = pagmentstemp.split(".-")
            print(pagmentstemp)
            command = pagmentstemp[-1]
        except Exception as Error:
            print(Error)
            command = [0]
        if command == "null":
            command = [0]
        print(command)
        pagments = []
        print(number)
        print(command == number)
        if int(command[-1]) == int(number):
            print(pagmentstemp)
            for i in pagmentstemp[0:-1]:
                tipe, quantity = i.split(",-")
                print(tipe)
                print(quantity)
                pagments.append(pagment(tipe, quantity))
        
        totalPrice = 0
        products = sendstr("PRODUCTSON,=" + str(number)).split(",=")
        pagmentson = False
        
        if products != [""]:
            pagmentson = True
            for i in products:
                priceproduct = i.split("|")[2]
                totalPrice = totalPrice + (float(priceproduct.replace(",", ".")) * 100)
        if "." in str(totalPrice):
            totalPrice = str(totalPrice / 100).split(".")
            totalPrice = totalPrice[0] + "." + totalPrice[1][0:2]
        print(pagments)
        return render(request, "aplicacao/closecommand.html", {"navname": f"Fechar Comanda ({number})", "number": number, "pagments": pagments, "pagmentson":pagmentson, "diferent":command == number, "totalPrice":totalPrice})