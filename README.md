1. Setup `virtualenv`:
	```
	virtualenv -p python3 .env
	```

2. Activate the environment:
	```
	. .env/bin/activate
	```

3. Install requirements:
	```
	pip install -r requirements.txt
	```

4. Initialize environment:
	```
	python manage.py migrate
	python manage.py compilemessages
	python manage.py collectstatic
	```

5. Run the program:
	```
	python manage.py runserver
	```

6. Add group 'Law Firm Admin' with the following permissions:
	* Can add jurisdiction
	* Can only change own law firm
	* Can change law firm
	* Can add/change/delete other law* models
