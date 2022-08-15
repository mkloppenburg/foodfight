The database has been reset by removing it and running:
python manage.py migrate
python manage.py migrate --run-syncdb

The app has been started with:
python manage.py createsuperuser
username: admin
email: admin@test.local
password: admin12345
player: Admin

An additional user has been created:
username: test@test.local
password: test12345
player: Test

The following items and ranks have been created (needs to be done before player creation, because the player needs a rank):
Ranks:
Rank 	Description 	Games needed
1 	    Total beginner 	0
2 	    Novice 	        25
3 	    Student 	    150
4 	    Graduate 	    250
5 	    Expert 	        1000 

Items:
Item            Effect
Broccoli 	    10
Hamburger   	-3
Fruit Salad 	10
Döner Kebab 	-10
Bread           4

To test the app on cs50.io run: 
python manage.py runserver $IP:$PORT

The following line has been added to settings.py, which can be considered unsafe:
# Allow all hosts for testing on Cloud9
ALLOWED_HOSTS = ['*']

This was changed as well in settings.py
# set from mandatory to optional, to have it working for testing at Cloud9
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# set the storage of messages to session, which is needed for Cloud9
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'