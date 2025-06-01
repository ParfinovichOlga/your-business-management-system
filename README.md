# your-business-management-system
App for management business system.
### You can
- Create and manage your team: set manager and subordinates  (only admin user can do it).
- Create, take, update, delete tasks change its status, take to your to-do list. Only manager user can create task.
- Leave a comment to a task.
- Create and cancel meetings. Check if meetings overlap. After meeting is saved or canceled all participants will get emails.
- Login, register, logout, update, delete user.
- Evaluation task and walk through evaluations.
- Get list of today's and month's tasks.

## Project structure:
- core:
    - templates
    - view for rendering templates
    - services for getting template context
    - tasks.py for asynchronous celery tasks
    - permissions for API
    - forms
    - urls for frontend
    - admin.py for configuring Admin panel
    - tests for services.py
- Next modules contains models, views, urls, serializers, tests for API
    - evaluation
    - meetings
    - task
    - team
    - user


## Installation
- git clone git@github.com:ParfinovichOlga/your-business-management-system.git
- create superuser for admin role
docker compose run --rm app sh -c "python manage.py createsuperuser"
- docker-compose up


## Usage
See the api swagger documentation on localhost:8000/api/docs when docker container is run
