# Belvo Transactions API

This project is a REST API that allows the registration of Belvo user's transactions, and provides an overview of how the users are using their money. The API is built with Django Rest Framework. 


## Running the application

This project utilizes Docker to set up the applications and its database.

To run the application locally, execute the following command inside the project directory:

```bash
docker-compose up
```
The application will run on http://127.0.0.1:8000/

## Running the tests

To run the tests, execute the following command:

```bash
docker-compose run --rm app sh -c "python manage.py test"
```