# eCourseApp
Create virtual environment

	python -m venv venv
Active virtual environment

	venv\Scripts\activate
Install necessary package (setuptools: for No module named pkg_resources Error)

	pip install django, pymysql, cloudinary, pillow, django-ckeditor, djangorestframework, drf-yasg 
<p>Create database in mySQL<br/>
Run migrate

	python manage.py migrate
Create superuser
	
	python manage.py createsuperuser


