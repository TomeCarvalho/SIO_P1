import django
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from .forms import WikiForm, LoginForm, CreateAccountForm, CommentForm, ChangePasswordForm
from app_insec.models import User, Page, Comment
from itertools import zip_longest
from django.db import connection
from django.shortcuts import redirect
from django.utils import timezone

import datetime
from datetime import datetime


def dashboard(request):
    """Show the pages that match the search prompt (all if it's empty)"""
    search_prompt = request.GET.get('search_prompt', '')
    page_list = Page.objects.raw(f"SELECT * FROM app_insec_page WHERE title LIKE '%{search_prompt}%'")
    pgs = zip_longest(*(iter(page_list),) * 3)  # Divide the page cards into groups of 3
    tparams = {
        'three_page_group': pgs,
        'search_prompt': search_prompt,
        'logged': request.session.get('user_id'),
        'dashboardPage': True
    }
    return render(request, 'dashboard.html', tparams)


@csrf_exempt
def create_wiki(request):
    if request.method == 'POST':
        form = WikiForm(request.POST)
        post = request.POST
        if form.is_valid():
            with connection.cursor() as cursor:
                title = post['title']
                img = post['img_url']
                content = post['content']
                date = datetime.now()
                user = request.session.get('user_id')
                st = f"('{title}', '{user}', '{img}', '{content}', '{date}');"
                cursor.execute('INSERT INTO app_insec_page (title, user_id, img_url, content, date) VALUES' + st)
                return redirect(dashboard)
    else:
        form = WikiForm()

    return render(request, 'createWiki.html', {
        'form': form,
        'createPage': True,
        'logged': request.session.get('user_id')
    })


def wiki_page(request, i):
    if request.session.get('user_id'):
        print('DEBUG Username:', request.session.get('user_id'))

    page = Page.objects.raw(f"SELECT * FROM app_insec_page WHERE id='{i}'")
    comments = Comment.objects.raw(f"SELECT * FROM app_insec_comment WHERE page_id = {i} ORDER BY date DESC")
    print(page)
    for p in page:
        print(p.title)
        params = {
            'page': {
                'title': p.title,
                'content': p.content,
                'date': p.date,
                'date_pretty': None if p.date is None else p.date.strftime('%c'),
                'img_url': p.img_url,
                'user': p.user_id,
                'comments': comments,
                'id': p.id
            },
            'logged': request.session.get('user_id')
        }
        return render(request, 'wikiPage.html', params)
    return HttpResponse('404 - Page not found.')


@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            print('DEBUG: login_page - form is valid')
            user = User.objects.raw(
                f"SELECT * FROM app_insec_user "
                f"WHERE username='{request.POST['username']}' "
                f"AND password='{request.POST['password']}'"
            )
            if user:
                u = list(user)[0]
                request.session['user_id'] = u.username
                return redirect(dashboard)
            else:
                form.add_error(field='username', error='User/password combination doesn\'t exist.')
    else:
        form = LoginForm()
    return render(request, 'loginPage.html', {
        'form': form, 'loginPage': True,
        'logged': request.session.get('user_id')
    })


@csrf_exempt
def create_account(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        print(request.POST)
        if form.is_valid():
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            repeat_password = request.POST['repeat_password']

            if password != repeat_password:
                form.add_error(field='password', error='Passwords don\'t match')
            elif list(User.objects.raw(f"SELECT username FROM app_insec_user WHERE username='{username}'")):
                form.add_error(field='username', error='Username already exists')
            else:
                print("Inserting")
                with connection.cursor() as cursor:
                    cursor.execute(f"INSERT INTO app_insec_user (username, password, email)"
                                   f" VALUES ('{username}','{password}','{email}') ")
                return redirect(login_page)
    else:
        form = CreateAccountForm()
    return render(request, 'createAccount.html', {
        'form': form,
        'logged': request.session.get('user_id')
    })


def logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return redirect(dashboard)


@csrf_exempt
def create_comment(request, _id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        post = request.POST
        if form.is_valid():
            with connection.cursor() as cursor:
                content = post['content']
                date = datetime.now()
                user = request.session.get('user_id')
                st = f"('{_id}', '{user}', '{content}', '{date}');"
                cursor.execute('INSERT INTO app_insec_comment (page_id, user_id, content, date) VALUES' + st)
                return redirect(wiki_page, i=_id)
    else:
        form = CommentForm()

    return render(request, 'createWiki.html', {
        'form': form,
        'logged': request.session.get('user_id')
    })


@csrf_exempt
def delete_page(request):
    if request.session.get('user_id') != 'admin':
        return HttpResponse('You lack permissions >:(')

    if 'delete-page' in request.POST:
        page_id = request.POST['delete-page']
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM app_insec_page WHERE id={page_id}")
        return redirect(dashboard)

    return HttpResponse('An error occurred :(')


@csrf_exempt
def delete_comment(request):
    if request.session.get('user_id') != 'admin':
        return HttpResponse('You lack permissions >:(')

    print(request.POST)
    if 'delete-comment' in request.POST:
        st = request.POST['delete-comment']
        comment_id = st.split(',')[0]
        page_id = st.split(',')[1]
        with connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM app_insec_comment WHERE id={comment_id}')
        return redirect(wiki_page, i=page_id)

    return HttpResponse('An error occurred :(')


def profile(request):
    if request.session.get('user_id'):

        data = User.objects.raw(f"SELECT * FROM app_insec_user WHERE username='{request.session.get('user_id')}'")
        for d in data:
            params = {
                'info': {
                    'username': d.username,
                    'email': d.email,
                },
                'logged': request.session.get('user_id')
            }
        return render(request, 'profile.html', params)
    return HttpResponse('404 - Page not found :(')


@csrf_exempt
def change_password(request):
    if request.session.get('user_id'):
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                repeat_password = request.POST['repeat_password']

                if password != repeat_password:
                    form.add_error(field='password', error='Passwords don\'t match')
                else:
                    with connection.cursor() as cursor:
                        cursor.execute(f"UPDATE app_insec_user "
                                       f"SET password='{password}'"
                                       f"WHERE username='{username}'")
        else:
            form = ChangePasswordForm()
        return render(request, 'createAccount.html', {
            'form': form,
            'logged': request.session.get('user_id')
        })
    return HttpResponse('404 - Page not found :(')


def go_to_dashboard(request):
    return redirect(dashboard)
