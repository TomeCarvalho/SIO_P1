from django.shortcuts import render

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect

from .forms import WikiForm, LoginForm, CreateAccountForm, CommentForm, ChangePasswordForm
from app.models import User, Page, Comment
from itertools import zip_longest
from django.db import connection
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password, check_password

import datetime
from datetime import datetime


# Create your views here.

@csrf_protect
def dashboard(request):
    logged = request.session.get('user_id')
    search_prompt = f"%{request.GET.get('search_prompt', '')}%"
    if User.objects.raw("SELECT * FROM app_user WHERE username = %s AND admin = True", params=[logged]):
        page_list = Page.objects.raw("SELECT * FROM app_page WHERE title LIKE %s", params=[search_prompt])
    else:
        page_list = Page.objects.raw("SELECT * FROM app_page WHERE title LIKE %s AND hidden = False", params=[search_prompt])
    pgs = zip_longest(*(iter(page_list),) * 3)  # chunky!
    tparams = {
        "three_page_group": pgs,
        "search_prompt": search_prompt[1:-1],
        # "logged": User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged]),
        "logged": logged,
        "dashboardPage": True,
        "user": User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged])
    }
    # print(User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged])[0])
    return render(request, "dashboard.html", tparams)


def create_wiki(request):
    if not request.session.get('user_id'):
        return HttpResponse("You lack permissions >:(")
    if request.method == "POST":
        form = WikiForm(request.POST)
        print(request.POST)
        post = request.POST
        if form.is_valid():
            with connection.cursor() as cursor:
                title = post["title"]
                img = post["img_url"]
                content = post["content"]
                # date = form.cleaned_data['date']
                date = datetime.now()
                user = request.session.get('user_id')
                cursor.execute('INSERT INTO app_page (title, user_id, img_url, content, date, hidden) '
                               'VALUES (%s, %s, %s, %s, %s, %s)',
                               params=[title, user, img, content, date, 0])
                return redirect(dashboard)
    else:
        form = WikiForm()

    return render(request, "createWiki.html", {
        "form": form,
        "createPage": True,
        "logged": request.session.get('user_id')
    })


def wiki_page(request, i):
    logged = request.session.get('user_id')
    if logged:

        print("DEBUG Username:", logged)

    page = Page.objects.raw("SELECT * FROM app_page WHERE id=%s", params=[i])
    comments = Comment.objects.raw("SELECT * FROM app_comment WHERE page_id = %s ORDER BY date DESC", params=[i])
    print(page)
    for p in page:
        print("1", p.hidden)
        if p.hidden:
            print("2", len(list(User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged]))))
            if len(list(User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged]))) == 0:
                return redirect(dashboard)
            elif not User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged])[0].admin:
                return redirect(dashboard)
        print(p.title)
        params = {
            "page": {
                "title": p.title,
                "content": p.content,
                "date": p.date,
                "date_pretty": None if p.date is None else p.date.strftime('%c'),
                "img_url": p.img_url,
                "user": p.user_id,
                "comments": comments,
                "id": p.id,
                "hidden": p.hidden
            },
            "logged": logged,
            "user": User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged])
        }
        return render(request, "wikiPage.html", params)
    return HttpResponse("404 - Page not found :(")


def login_page(request):
    if request.session.get("user_id"):
        return redirect(profile)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # print(request.POST)
        if form.is_valid():
            print("DEBUG: login_page - form is valid")
            password = request.POST['password']
            user = User.objects.raw(
                "SELECT * FROM app_user "
                "WHERE username=%s ",
                params=[request.POST['username']]
            )
            print(request.POST['password'], make_password(password), password)
            if user:
                u = list(user)[0]
                print(u)
                if check_password(password, u.password):
                    request.session['user_id'] = u.username
                    return redirect(dashboard)
                else:
                    form.add_error(field='password', error="Invalid password.")
            else:
                form.add_error(field='username', error="Username doesn't exist.")
    else:
        form = LoginForm()
    return render(request, "loginPage.html", {
        "form": form, "loginPage": True,
        "logged": request.session.get('user_id')
    })


def create_account(request):
    # teste da session, se estiver login imprime no terminal a mensagem
    if request.session.get('user_id'):
        print("DID IT")

    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        print(request.POST)
        if form.is_valid():
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            repeat_password = request.POST['repeat_password']

            if password != repeat_password:
                form.add_error(field='password', error="Passwords don't match")
            elif list(User.objects.raw("SELECT username FROM app_user WHERE username=%s", params=[username])):
                form.add_error(field="username", error="Username already exists")
            else:
                print("Inserting")
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO app_user (username, password, email, admin)"
                                   " VALUES (%s, %s, %s, %s) ",
                                   params=[username, make_password(password), email, 0])
                return redirect(login_page)
    else:
        form = CreateAccountForm()
    return render(request, "createAccount.html", {
        "form": form,
        "logged": request.session.get('user_id')
    })


def logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return redirect(dashboard)


def create_comment(request, _id):
    logged = request.session.get('user_id')
    for p in Page.objects.raw("SELECT * FROM app_page WHERE id=%s", params=[_id]):
        if p.hidden:
            if len(list(User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged]))) == 0:
                return redirect(dashboard)
            elif not User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged])[0].admin:
                return redirect(dashboard)
    if request.method == "POST":
        form = CommentForm(request.POST)
        print(request.POST)
        post = request.POST
        if form.is_valid():
            with connection.cursor() as cursor:
                content = post["content"]
                # date = form.cleaned_data["date"]
                date = datetime.now()
                print('DEBUG: create_comment - datetime.now():', date)
                user = request.session.get('user_id')
                print('DEBUG: create_comment - user:', user)
                cursor.execute("INSERT INTO app_comment (page_id, user_id, content, date, hidden) "
                               "VALUES (%s, %s, %s, %s, %s);", params=[_id, user, content, date, 0])
                return redirect(wiki_page, i=_id)
    else:
        form = CommentForm()

    return render(request, "createWiki.html", {
        "form": form,
        "logged": request.session.get('user_id')
    })


def hide_page(request):
    logged = request.session.get('user_id')
    if not User.objects.raw("SELECT * FROM app_user WHERE username = %s AND admin = True", params=[logged]):
        return HttpResponse("You lack permissions >:(")

    if "delete-page" in request.POST:
        page_id = request.POST["delete-page"]
        with connection.cursor() as cursor:
            cursor.execute("UPDATE app_page SET hidden = 1 WHERE id=%s", params=[page_id])
        return redirect(dashboard)

    return HttpResponse("An error occurred :(")


def unhide_page(request):
    logged = request.session.get('user_id')
    if not User.objects.raw("SELECT * FROM app_user WHERE username = %s AND admin = True", params=[logged]):
        return HttpResponse("You lack permissions >:(")

    if "delete-page" in request.POST:
        page_id = request.POST["delete-page"]
        with connection.cursor() as cursor:
            cursor.execute("UPDATE app_page SET hidden = 0 WHERE id=%s", params=[page_id])
        return redirect(dashboard)

    return HttpResponse("An error occurred :(")


def hide_comment(request):
    logged = request.session.get('user_id')
    if not User.objects.raw("SELECT * FROM app_user WHERE username = %s AND admin = True", params=[logged]):
        return HttpResponse("You lack permissions >:(")
    print(request.POST)
    if "delete-comment" in request.POST:
        st = request.POST["delete-comment"]
        comment_id = st.split(",")[0]
        page_id = st.split(",")[1]
        with connection.cursor() as cursor:
            cursor.execute("UPDATE app_comment SET hidden = 1 WHERE id=%s", params=[comment_id])
        return redirect(wiki_page, i=page_id)

    return HttpResponse("An error occurred :(")


def unhide_comment(request):
    logged = request.session.get('user_id')
    if not User.objects.raw("SELECT * FROM app_user WHERE username = %s AND admin = True", params=[logged]):
        return HttpResponse("You lack permissions >:(")
    print(request.POST)
    if "delete-comment" in request.POST:
        st = request.POST["delete-comment"]
        comment_id = st.split(",")[0]
        page_id = st.split(",")[1]
        with connection.cursor() as cursor:
            cursor.execute("UPDATE app_comment SET hidden = 0 WHERE id=%s", params=[comment_id])
        return redirect(wiki_page, i=page_id)

    return HttpResponse("An error occurred :(")


def profile(request):
    if request.session.get('user_id'):
        data = User.objects.raw("SELECT * FROM app_user WHERE username=%s", params=[request.session.get('user_id')])
        for d in data:
            params = {
                "info": {
                    "username": d.username,
                    "email": d.email,
                },
                "logged": request.session.get('user_id')
            }
            return render(request, "profile.html", params)
    return HttpResponse("404 - Page not found :(")


def change_password(request):
    if request.session.get('user_id'):
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            print(request.POST)
            if form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                repeat_password = request.POST['repeat_password']

                if username != request.session.get('user_id'):
                    form.add_error(field='username', error="Wrong username")
                if password != repeat_password:
                    form.add_error(field='password', error="Passwords don't match")
                else:
                    print("Inserting")
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE app_user "
                                       "SET password=%s"
                                       "WHERE username=%s",
                                       params=[make_password(password), username])
        else:
            form = ChangePasswordForm()
        return render(request, "createAccount.html", {
            "form": form,
            "logged": request.session.get('user_id')
        })
    return HttpResponse("404 - Page not found :(")


def go_to_dashboard(request):
    return redirect(dashboard)