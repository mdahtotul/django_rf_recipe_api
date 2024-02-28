## Main-Dir: ⚡\Udemy-Build a Backend REST API with Python & Django - Advanced

### Sub-Dir: 12 - Build tags API

#### Done:

#### Start: 001 Tags API design

##### To run server using docker:

`docker-compose up`

##### To build server using docker:

`docker-compose up -d --build`

##### To remove all docker container

`docker-compose down`

##### To check linting using docker & flake8:

`docker-compose run --rm app sh -c "flake8"`

##### To check database is online using docker:

`docker-compose run --rm app sh -c "python manage.py wait_for_db"`

##### To run tests using docker:

`docker-compose run --rm app sh -c "python manage.py test"`

##### To run migrations using docker:

`docker-compose run --rm app sh -c "python manage.py makemigrations"`
`docker-compose run --rm app sh -c "python manage.py migrate"`

##### To remove previous migrations using docker:

`docker volume ls`
`docker volume rm <volume-name>`

##### To add new package using docker:

add the package to requirements.txt and run `docker-compose build`
