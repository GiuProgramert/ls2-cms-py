from django.shortcuts import render

def kanban_view(request):
    return render(request, 'kanban/kanban.html')