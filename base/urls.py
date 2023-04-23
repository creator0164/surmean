from django.urls import path
# import home and base from views.py put in curly braces
from .views import home, dashboard, user_logout, test_view,scrape, name_scrape, new_scrape, register_view
urlpatterns = [
    path('', home, name='home'),
    path('dashboard', dashboard, name='dashboard'),
    path('logout', user_logout, name='logout'),
    path('register', register_view, name='register'),
    # path('test', test_view, name='test'),
    # path('scrape', scrape, name='scrape'),
    path('surname/<str:name>', scrape, name='surname'),
    path('meaning/<str:name>', name_scrape, name='name_scrape'),
    path('new_scrape/<str:name>', new_scrape, name='new_scrape')
]