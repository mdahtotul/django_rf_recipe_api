## Main-Dir: ⚡\Udemy-Build a Backend REST API with Python & Django - Advanced

### Sub-Dir: 12 - Build user API

#### Done: 007 Implement token API [Follow Along]

#### Start: 008 Write tests for manage user API [Follow Along]

##### To run server using docker:

`docker-compose up`

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
