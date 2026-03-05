from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Goal, PartnerRequest
from django.contrib.auth.models import User
import datetime

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def dashboard(request):
    today = datetime.date.today()
    goals = Goal.objects.filter(user=request.user, date=today)
    goals_completed = goals.filter(completed=True).count()
    
    partner_progress = 0
    if request.user.profile.partner:
        partner_goals = Goal.objects.filter(user=request.user.profile.partner.user, date=today)
        if partner_goals.exists():
            partner_progress = int((partner_goals.filter(completed=True).count() / partner_goals.count()) * 100)

    return render(request, 'core/dashboard.html', {
        'goals': goals,
        'goals_completed': goals_completed,
        'partner_progress': partner_progress
    })

@login_required
def add_goal(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Goal.objects.create(user=request.user, title=title)
    return redirect('dashboard')

@login_required
def toggle_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.completed = not goal.completed
    goal.save()
    return redirect('dashboard')

@login_required
def accept_request(request, request_id):
    partner_req = get_object_or_404(PartnerRequest, id=request_id, receiver=request.user, status='pending')
    partner_req.status = 'accepted'
    partner_req.save()
    
    # Create symmetrical partnership
    sender_profile = partner_req.sender.profile
    receiver_profile = request.user.profile
    sender_profile.partner = receiver_profile
    receiver_profile.partner = sender_profile
    sender_profile.save()
    receiver_profile.save()
    
    messages.success(request, f"You are now partnered with {partner_req.sender.username}!")
    return redirect('profile')

@login_required
def profile_view(request):
    profile = request.user.profile
    sent_requests = PartnerRequest.objects.filter(sender=request.user)
    received_requests = PartnerRequest.objects.filter(receiver=request.user, status='pending')
    
    if request.method == 'POST':
        search_username = request.POST.get('search_user')
        if search_username:
            try:
                receiver = User.objects.get(username=search_username)
                if receiver != request.user:
                    PartnerRequest.objects.get_or_create(sender=request.user, receiver=receiver)
                    messages.success(request, f"Request sent to {search_username}")
                else:
                    messages.error(request, "You cannot partner with yourself!")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

    return render(request, 'core/profile.html', {
        'profile': profile,
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })
