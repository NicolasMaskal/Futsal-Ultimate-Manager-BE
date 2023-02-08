# Futsal Ultimate Manager (Backend - Django)

# Social
[![Nico linkedin](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nicolasmaskal/)
[![Nico github](https://img.shields.io/badge/GitHub-Nicolas264859-181717.svg?style=flat&logo=github)](https://github.com/Nicolas264859)

# Basic info about the project
[![Lint & test](https://github.com/Nicolas264859/Futsal-Sim-BE/actions/workflows/django.yml/badge.svg)](https://github.com/Nicolas264859/Futsal-Sim-BE/actions/workflows/django.yml)
[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

**Link to site**: https://www.futsal-manager.tech

The **Futsal Ultimate Manager** is a project consisting of a frontend built with React Typescript and a backend built with Django. The frontend code can be found on [Github](https://github.com/Nicolas264859/Futsal-sim-FE), 
while the backend code can be found here in this repo. 
The backend follows the best practices specified in the 
[Hacksoftware Style Guide](https://github.com/HackSoftware/Django-Styleguide). 
Codebase was built on top of the [Hacksoftware Cookiecutter Example](https://github.com/HackSoftware/Django-Styleguide-Example).

# Code Overview
- The project uses Python 3.10 and the Django Rest Framework.
- The code is formatted using [Black](https://github.com/psf/black). and imports are organized using [Isort](https://pycqa.github.io/isort/).
- Type checking is done using [mypy](http://mypy-lang.org/).
- Project uses [Github actions](https://github.com/Nicolas264859/Futsal-Sim-BE/actions/workflows/django.yml) to run code checkers and tests.

# Deployment
The project is hosted on DigitalOcean's App Platform, and a commit to the deploy branch triggers a deployment. 
The deployed version contains built React files, which are served statically using gunicorn and whitenoise.

# Other Information
API documentation can be found at:
- [Swagger-ui (Contains only BE endpoints)](https://futsal-manager.tech/api/schema/swagger-ui/).
- [Redoc (Contains only BE endpoints)](https://futsal-manager.tech/api/schema/redoc/).

For **authorization**, the backend supports both **HTTP-only cookies** and **JWT tokens**.


I used **Docker** during local development, so I could have a postgresql database locally. 


Email sending is done by using a simple **Gmail backend**.

Constants used for match/team/player/pack generation can be found [here](https://github.com/Nicolas264859/Futsal-Sim-BE/blob/master/src/futsal_sim/constants.py)


# Future improvements 
* Add tests.
* Document the Swagger API docs.
* Shift intensive tasks such as email sending to Celery.
* Consider using SendGrid instead of Gmail backend.

More improvements are listed as issues in this repository.
