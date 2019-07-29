from django.shortcuts import render,get_object_or_404
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
def index(request):
    return render(request, "index.html")


def login_action(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)  # 登录
            request.session['user'] = username  # 将信息记录到浏览器
            response = HttpResponseRedirect("/event_manage/")
            return response

        else:
            return render(request, "index.html",
                          {"error": "username or password"
                                    "error"})


@login_required
def event_manage(request):
    event_list = Event.objects.all()
    username = request.session.get("user")
    return render(request, "event_manage.html", {"user": username,
                                                 'events': event_list})


# 发布会名称搜索
@login_required
def search_name(request):
    username = request.session.get("user")
    search_name = request.GET.get('name')
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request, "event_manage.html", {"user": username,
                                                 'events': event_list})


@login_required
def guest_manage(request):
    username = request.session.get("user")
    guest_list = Guest.objects.all()
    paginator = Paginator(guest_list, 2)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页面数据
        contacts=paginator.page(1)
    except EmptyPage:
        # 如果page不在范围，取最后一个页面
        contacts = paginator.page(paginator.num_pages)
    return render(request, "guest_manage.html", {"user": username,
                                                 'guests': contacts})


#签到页面
@login_required
def sign_index(request,eid):
    event = get_object_or_404(Event, id=eid)
    guest_count = len(Guest.objects.filter(event_id=eid))#指定发布会的嘉宾人数
    sign_count=len(Guest.objects.filter(sign='1',event_id=eid))#指定发布会的嘉宾已签到人数
    return render(request, 'sign_index.html', {'event': event,
                                               'guest_count':guest_count,
                                               'sign_count':sign_count})


#签到动作
@login_required
def sign_index_action(request,eid):
    sign_count=0#定义指定发布会的嘉宾已签到人数的变量
    event = get_object_or_404(Event, id=eid)

    guest_list=Guest.objects.filter(event_id=eid)
    guest_count=str(len(guest_list))
    for guest in guest_list:
        if guest.sign==True:
            sign_count+=1

    phone=request.POST.get('phone')
    print(phone)
    result=Guest.objects.filter(phone=phone)
    if not result:
        return render(request,"sign_index.html",{'event':event,
                                                 'guest_count': guest_count,
                                                 'hint':'phone error'})
    result=Guest.objects.filter(phone=phone,event_id=eid)
    if not result:
        return render(request,"sign_index.html",{'event':event,
                                                 'guest_count': guest_count,
                                                 'hint':'event_id or phone error'})
    result=Guest.objects.get(phone=phone,event_id=eid)
    if result.sign:
        return render(request,'sign_index.html', {'event': event,
                                               'hint':'user has sign in',
                                                  'guest_count': guest_count,})
    else:
        Guest.objects.filter(phone=phone,event_id=eid).update(sign="1")
    return render(request, 'sign_index.html', {'event': event,
                                               'hint':'sign in success',
                                               'guest_count': guest_count,
                                               'guest':result,
                                               'sign_count':str(int(sign_count)+1)})


@login_required
def logout(request):
    auth.logout(request)#退出登录
    return HttpResponseRedirect('/index/')