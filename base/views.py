from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
import json
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from rest_framework.response import Response

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .models import SurnameMeaning
from django.contrib.auth.models import User


@api_view(['GET'])
def new_scrape(request, name):
    try:
        # Create ChromeOptions object
        chrome_options = Options()
        # Add --headless option to ChromeOptions
        chrome_options.add_argument("--headless")
        # Initialize web driver with ChromeOptions and Service
        with webdriver.Chrome(options=chrome_options) as driver:
            # Navigate to the URL
            driver.get(f'https://forebears.io/surnames/{name}')
            # Find element by class name
            myDiv = driver.find_element(By.CLASS_NAME, 'break-word')
            # Get text content of the element
            element_text = myDiv.text
            driver.quit()
            print("Element text:", element_text)
        return JsonResponse({'text': element_text})
    except Exception as e:
        return JsonResponse(e)



@api_view(['GET'])
def name_scrape(request, name):
    try:
        if request.method == 'GET':
            data = {}
            url = f'https://www.behindthename.com/name/{name}'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            namedef_elements = soup.find(class_='namedef')
            if not namedef_elements:
                return JsonResponse({'status':'fail','error': 'No name found'})
            data['meaning'] = namedef_elements.get_text()
            data['name'] = name

            # Serialize the data as JSON
            serialized_data = {
                'status': 'success',
                'name': data['name'],
                'meaning': data['meaning'],
                
            }
            return JsonResponse(serialized_data)
    except Exception as e:
        return JsonResponse(e)
    
def scrape(request, name):
    try:
        if request.method == 'POST':
            SurnameMeaning.objects.create(user=request.user, name=name, meaning=request.POST.get('meaning'))
            return render(request, 'base/surname.html',{'status':'success','name': name, 'meaning': request.POST.get('meaning')})
      
        check_name = SurnameMeaning.objects.filter(name=name)
        if check_name.exists():
            return render(request, 'base/surname.html',{'status':'success','name': check_name[0].name, 'meaning': check_name[0].meaning})
        
        data = {}
        url = f'https://www.behindthename.com/name/{name}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        namedef_elements = soup.find(class_='namedef')
        if not namedef_elements:
            return render(request, 'base/surname.html',{'status':'fail','name':name,'message': 'No name found'})
        data['meaning'] = namedef_elements.get_text()
        data['name'] = name

        # Serialize the data as JSON
        serialized_data = {
            'status': 'success',
            'name': data['name'],
            'meaning': data['meaning'],
            'message': 'Successfully fetched data'
        }
        return render(request, 'base/surname.html', serialized_data)
    except Exception as e:
        return render(request, 'base/surname.html', {'status':'fail','name':name,'message': e})
    


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'index.html')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        surname  = request.POST.get('surname')

        return redirect('surname', surname)
    return render(request, 'base/dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def fetch_data(url):

    response = requests.get(url)
    return response.json()

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:  
            print(password1, password2)
            user = User.objects.create_user(username=username, password=password1)
            user.save()
            return redirect('home')
    return render(request, 'base/register.html')

def test_view(request):
    data = request
    fn = data.GET.get('fn')
    sn = data.GET.get('sn')
    ssn = data.GET.get('ssn')
    url = f'https://ono.4b.rs/v1/nat?key=9e20aa56442446a5b00c89bb5868f3f8&fn={fn}&sn={sn}&ssn={ssn}'
    fetchData = fetch_data(url)
    return JsonResponse(json.dumps(fetchData), safe=False)

