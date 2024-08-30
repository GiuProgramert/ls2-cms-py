from django.shortcuts import render, redirect

# Create your views here.
def home(request):
    return render(request, "article/home.html")

def create_article(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "article/create_article.html")