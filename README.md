# content-manager
A prototype project includes features for user authentication, content creation, moderation with profanity filtering, and analytics on user interactions.
## Features
* JWT authentication
* Integration with the PurgoMalum profanity checking service 
* Moderation with profanity filtering
* Analytics on user interactions
* Automatic API documentation generation for http://127.0.0.1:8000/docs

##  Installation:
Python3 must be already installed

### 1.Clone the Repository:
```shell
git clone https://github.com/svitlana-savikhina/content-manager.git
cd content-manager
```
### 2.Environment Configuration: 
Create a .env file in the root directory with the following content, define environment variable in it (example you can find in .env_sample)
```shell
SECRET_KEY=SECRET_KEY
```
### 3.Activate venv:
```shell
python -m venv venv
source venv/bin/activate (Linux/Mac)
venv\Scripts\activate (Windows)
```
### 4.Install Dependencies:
```shell
pip install -r requirements.txt
```
### 5.Generate a new migration revision
```shell
alembic revision --autogenerate
```
### 6. Run Alembic Migrations:
```shell
 alembic upgrade head
```
### 7.Run:
```shell
uvicorn main:app --reload
```
