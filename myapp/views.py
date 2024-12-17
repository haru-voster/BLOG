from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from .models import Comment,Post
# Create your views here.
def index(request):
    return render(request,"index.html",{
        'posts':Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts':Post.objects.all().order_by("-likes"),
        'recent_posts':Post.objects.all().order_by("-id"),
        'user':request.user,
        'media_url':settings.MEDIA_URL
    })


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,"Username already Exists")
                return redirect('signup')
            if User.objects.filter(email=email).exists():
                messages.info(request,"Email already Exists")
                return redirect('signup')
            else:
                User.objects.create_user(username=username,email=email,password=password, is_active=False).save()
                return redirect('signin')
        else:
            messages.info(request, 'Registration successful. Please wait for admin approval.')
            return redirect('signin')
            
    return render(request,"signup.html")

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")
            else:
                messages.info(request, 'Username or Password Incorrect.')
                return redirect("signin")
        else:
            messages.info(request, 'Thank you for Registering. Please contact/whatsapp admin for approval')
            return redirect("signin")

    return render(request, "signin.html")

def logout(request):
     if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/')
        return HttpResponse("Only POST method is allowed for logout.", status=405)

def blog(request):
    return render(request,"blog.html",{
            'posts':Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
            'top_posts':Post.objects.all().order_by("-likes"),
            'recent_posts':Post.objects.all().order_by("-id"),
            'user':request.user,
            'media_url':settings.MEDIA_URL
        })
    
def create(request):
    if request.method == 'POST':
        try:
            postname = request.POST['postname']
            content = request.POST['content']
            category = request.POST['category']
            image = request.FILES['image']
            Post(postname=postname,content=content,category=category,image=image,user=request.user).save()
        except:
            print("Error")
        return redirect('index')
    else:
        return render(request,"create.html")
  
@login_required  
def profile(request,id):
    
    return render(request,'profile.html',{
        'user':User.objects.get(id=id),
        'posts':Post.objects.all(),
        'media_url':settings.MEDIA_URL,
    })
    
    
def profileedit(request,id):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
    
        user = User.objects.get(id=id)
        user.first_name = firstname
        user.email = email
        user.last_name = lastname
        user.save()
        return profile(request,id)
    return render(request,"profileedit.html",{
        'user':User.objects.get(id=id),
    })
    
def increaselikes(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            # Store anonymous likes in session to prevent multiple likes
            liked_posts = request.session.get('liked_posts', [])
            if id not in liked_posts:
                post.likes += 1
                post.save()
                liked_posts.append(id)
                request.session['liked_posts'] = liked_posts
                messages.success(request, "You liked this post.")
            else:
                messages.warning(request, "You have already liked this post.")
        else:
            post.likes += 1
            post.save()

    return redirect('post', id=id)



def post(request,id):
    post = Post.objects.get(id=id)
    
    return render(request,"post-details.html",{
        "user":request.user,
        'post':Post.objects.get(id=id),
        'recent_posts':Post.objects.all().order_by("-id"),
        'media_url':settings.MEDIA_URL,
        'comments':Comment.objects.filter(post_id = post.id),
        'total_comments': len(Comment.objects.filter(post_id = post.id))
    })
    
def savecomment(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('message')

        if not request.user.is_authenticated:
            # For anonymous users
            if not name or not email:
                messages.error(request, "Name and email are required for commenting.")
                return redirect('post', id=id)
            Comment(post_id=post.id, name=name, email=email, content=content).save()
        else:
            # For authenticated users
            Comment(post_id=post.id, user_id=request.user.id, content=content).save()

        messages.success(request, "Your comment has been posted.")
        return redirect('post', id=id)

@login_required
def deletecomment(request, id):
    comment = get_object_or_404(Comment, id=id)
    post_id = comment.post.id  # Get the post ID before deletion
    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect('post', id=post_id)

@login_required
def editpost(request,id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        try:
            postname = request.POST['postname']
            content = request.POST['content']
            category = request.POST['category']
            
            post.postname = postname
            post.content = content
            post.category = category
            post.save()
        except:
            print("Error")
        return profile(request,request.user.id)
    
    return render(request,"postedit.html",{
        'post':post
    })
@login_required  
def deletepost(request,id):
    Post.objects.get(id=id).delete()
    return profile(request,request.user.id)


def contact_us(request):
    context={}
    if request.method == 'POST':
        name=request.POST.get('name')    
        email=request.POST.get('email')  
        subject=request.POST.get('subject')  
        message=request.POST.get('message')  

        obj = Contact(name=name,email=email,subject=subject,message=message)
        obj.save()
        context['message']=f"Dear {name}, Thanks for your time!"

    return render(request,"contact.html")
