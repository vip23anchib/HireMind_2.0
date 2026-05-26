
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from .models import Member
from django.contrib.auth.decorators import login_required
from .forms import MemberForm


print("VIEWS FILE LOADED")


@login_required(login_url='login_view')
def members(request):
    mymembers = Member.objects.all()
    return render(request, 'all_members.html', {
        'mymembers': mymembers,
        'active_page': 'members'
    })


@login_required(login_url='login_view')
def details(request, id):
    mymember = Member.objects.get(id=id)
    return render(request, 'details.html', {
        'mymember': mymember,
        'active_page': 'members'
    })


@login_required(login_url='login_view')
def main(request):
    return render(request, 'main.html', {
        'active_page': 'home'
    })

def testing(request):
    mydata = Member.objects.filter(firstname='Emil').values()
    return render(request, 'testTemplate.html', {'mymembers': mydata})



def add_member(request):
    if request.method == "POST":
        form = MemberForm(request.POST)

        print("POST DATA:", request.POST)   
        print("VALID?", form.is_valid())    

        if form.is_valid():
            form.save()
            return redirect('members')
    else:
        form = MemberForm()

    return render(request, 'add_member.html', {'form': form})


   
