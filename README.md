# LITReview - Books and articles review web app
***
The LITReview web application allows logged in users to ask, read and write reviews about books and articles.
## How to install the project
1. Open the Terminal
2. Clone the repository:
```
$ git clone https://github.com/CeliaTois/CeliaTOIS_9_02052022.git
```
3. Go to the project folder:
```
$ cd ../path/to/the/file
```
4. Create the **virtual environment**:
```
python3 -m venv env
```
5. Activate the **virtual environment**:
   - on macOS and Linux:
     ```
     source env/bin/activate
     ```
   - on windows:
     ```
     env/Scripts/activate
     ```
6. Install the packages:
```
$ pip install -r requirements.txt
```

## How to run the web app
1. Open the Terminal
2. Go to the project folder:
```
$ cd ../path/to/the/file
```
3. Activate the virtual environment
4. Run the command:
```
$ python manage.py runserver
```
5. Open the link written in your terminal or copy/paste it in your browser: http://127.0.0.1:8000/
6. Enter the following login details:

    **username:** celiatois

    **password:** litreview


## How to use the web app
Log in the app:  
* If it's your first time using the app, you should create an account by clicking on **"S'inscrire"**.
* If you already have an account, enter your username and password and click on **"Se connecter"**.

**FLUX -** The flux page is the home page. Here you can see all the reviews and requests for review that you and the users you follow have posted. You can also respond to a request for review, create a review and create a request for review.

**POSTS -** Enables you to see all the reviews and requests for review that you have posted. You can also modify and delete your posts.

**ABONNEMENTS -** Enables you to follow and unfollow an user, see the users following you and the users you are following.

**SE DÉCONNECTER -** Logs you out of the web app.
