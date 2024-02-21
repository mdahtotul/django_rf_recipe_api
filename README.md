## Main-Dir: ⚡\Udemy-Build a Backend REST API with Python & Django - Advanced

### Sub-Dir: 10 - Setup Django Admin

#### Done: 005 Support creating users [Follow Along]

#### Start:

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
