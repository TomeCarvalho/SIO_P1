

### Authors

| NMEC   | Name            |
| ------ | --------------- |
| 96123  | Lucius Vinicius |
| 97939  | Tomé Carvalho   |
| 98452  | Dinis Lei       |
| 100055 | Afonso Campos   |



### How to run

First, make sure django is installed. If not, run:
`python3 -m pip install django`

A virtual environment can also be used.

On the respective app folder (secure or insecure) run:
`python3 manage.py runserver [port]`

Omitting the port will attempt to run the app on Django's default port 8000.



### Project Description

The project is a wiki about memes related to the LEI course. It includes the following features:

- User registration, login and logout
- Page creation, searching and browsing
- Comments on pages



The following vulnerabilities are present in the insecure version of the project:

- **CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')**
  
  - **Type 1: Reflected XSS (or Non-Persistent)**: The search function echoes the prompt back to the user. A victim can be tricked into opening, for example, http://localhost:8000/wiki/?search_prompt=%3Cscript%3Ealert%28%22hi%22%29%3C%2Fscript%3E. This will cause the script to be ran in the victim's browser.
  - **Type 2: Stored XSS (or Persistent)**: Leaving a comment that contains a script will allow the script to run when someone visits the comment's respective page.
  - **Solution**: Django has an autoescape feature that automatically escapes the characters `<`, `>`, `&`, `"` and `'`, swapping them for their HTML equivalents `&lt`, `&gt`, `&amp`, `&quot` and `&#39`, respectively. This substitution negates the insertion of XSS content on pages, since these symbols aren't interpreted as **HTML tags**. The solution works for both Reflected XSS and Stored XSS.
  
- **CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')**
  
  - To obtain information about the tables in the DB, «`' UNION SELECT null, * FROM sqlite_master WHERE type = "table"-- //` » can be entered in the search bar.
  - It is possible to bypass the login by entering «`' OR 1=1 -- //` » in the username field, causing the query to be «`SELECT username FROM app_insec_user WHERE username='' OR 1=1 `», resulting in a log in as the first user in the table.
  - The users' login information can be shown by entering «`' UNION SELECT null, *, null, null FROM app_insec_user -- //`», giving the attacker the necessary information to log in as any user they desire.
  - In the wiki page creation page, it is possible to create a page using another user's name by exploiting the title field. For example, entering «`My Confession', 'innocent_user', 'https://imgflip.com/s/meme/Confession-Bear.jpg', 'I am an evil, EVIL person!<script>alert("hackermanned!");</script>', '2021-11-12 23:59:59') -- //  `» will create a post using *innocent_user*'s username, with an XSS attack to boot, allowing the attacker to frame them. The date may also be manipulated.
  - **Solution**: One of the most commons methods to prevent SQL Injections is the use of *Stored Procedures*: SQL "functions" with parameters, whose use stops SQL Injections. In Django, these SPs are called when used the `raw` method with `params` as an argument.
  For example, `User.objects.raw('SELECT * FROM app_user WHERE name = " + username)` is a vulnerable query, while `User.objects.raw('SELECT * FROM app_user WHERE name = %s', [username])` is a secure one, because it uses an SP.

- **CWE-209: Generation of Error Message Containing Sensitive Information**

  - If an error occurs, the application doesn't handle it gracefully, showing a detailed error message. A malicious attacker can get information that they aren't supposed to and use that for an attack. For example, in the SQL Injection where you get all tables «`' UNION SELECT null, * FROM sqlite_master WHERE type = "table"-- //`», the amount of `null`s required in the query can be inferred from the error message, which warns the attacker about the different number of columns in the `UNION` operation.
  - **Solution**: Django has a boolean setting DEBUG that, if false, doesn't show important error messages.

- **CWE-250: Execution with Unnecessary Privileges**
  - The **admin** has an excessive amount of privileges, including **deleting pages and comments from the database**. This means that if, for some reason, another person is using the admin account (a hacker that obtained its credentials, or another person using the admin's computer), they can delete content **permanently**.
  - **Solution**: The admin's purpose still needs to be the same: filter pages and comments from the website. However, instead of deleting content from database, they can just hide it. This way, if another person "deletes" content, it's possible to restore it.

- **CWE-256: Plaintext Storage of a Password**
  
  - The passwords for the users' accounts are not hashed, but stored in plaintext in the DB. As explained previously, it is possible to retrieve the passwords through SQL Injection.
  - **Solution**: The solution was to use a **hash function** to encrypt/descrypt passwords in the Database.
  
- **CWE-285: Improper Authorization**

  - Users that aren't logged in shouldn't be supposed to be able to access the wiki page creation page. While the option isn't provided in the navbar, they can, however, enter the "/wiki/create" URL in order to access it, due to lack of authorization checks. 
  - **Solution**: Perform authorization checks when rendering pages that require authorization granted through being logged in. If the user isn't authorized (not logged in), they aren't granted access to the page.
  
- **CWE-352: Cross-Site Request Forgery (CSRF)**
  
  - A page with an Image URL like http://vulnerable-bank.com/transfer.jsp?amount=1000&to_nib=12345300033233 can be created. This would, hypothetically, cause the victim to transfer money to an attacker through *vulnerable-bank* once they visit the page or even just the dashboard, since it also contains the "image".
  - **Solution**: Through model and form validation, only URLs from trusted sources are allowed when creating a wiki page.

- **CWE-522: Insufficiently Protected Credentials (4.6)**

  - The program allows a user to change their password, however it does not verify if the user who requests the change is the same as the one whose password will be changed.
  - **Solution**: Verify if the user requesting the change is the same as the one whose password will be changed.

- **CWE-798: Use of Hard-coded Credentials**

  - To check if a determined user is an admin, the insecure program makes a hardcoded check `if request.session.get('user_id') == "admin"` which consists in checking if the user_id (username) is equal to "admin". This way, it's easy for some malicious attacker to create an account that simulates the admin privilegies (in this example, using "admin" as its username).
  - **Solution**: Instead of checking username or id with a hardcoded value, the boolean column **admin** was added to the SQL Table Users, changing the check to **if a user is admin**. That way, a person can't manipulate their username to match a hardcoded value and it also enables creation of more than one admin.

  

