from django.shortcuts import render, redirect

from main.models import Client


def index(request):
    client_all = Client.objects.all()
    fl_inn = 1
    cur_user = 0
    list_mb_user = []
    chech_list_mb_user = 0

    if request.method == 'POST':

        if request.POST.get('hid_inp') == 'registration':
            fl_inn = 1
            for c in client_all:
                if int(c.inn) == int(request.POST['inn']):
                    fl_inn = 0
                    break
            if fl_inn:
                Client.objects.create(last_name=request.POST['last_name'],
                                      second_name=request.POST['second_name'],
                                      first_name=request.POST['first_name'],
                                      inn=int(request.POST['inn']))
                return redirect('home')
    else:

        if request.GET.get('inn'):
            for c in client_all:
                print('c.inn',str(c.inn),'request.GET.get()', str(request.GET.get('inn')))

                if str(c.inn) == str(request.GET.get('inn')):
                    cur_user = c
                    print('cur_user', cur_user.first_name)

                elif str(request.GET.get('inn')) in str(c.inn):
                    chech_list_mb_user = 1
                    list_mb_user.append(c)


        print('list_mb_user', list_mb_user)

    return render(request, 'main/index.html', {'chech_list_mb_user':chech_list_mb_user,'list_mb_user':list_mb_user,'cur_user':cur_user,'client_all':client_all,'fl_inn': fl_inn})


