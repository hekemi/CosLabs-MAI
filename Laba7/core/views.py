from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from .forms import AssetForm, CounterpartyForm
from .models import Asset, Counterparty, Department
from .services import assign_internal_codes_bulk, find_inn_matches, mark_duplicate_inn


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


class AssetListView(View):
    def get(self, request):
        return render(request, 'assets/list.html', {'assets': Asset.objects.select_related('storage_department')})

    def post(self, request):
        changed = assign_internal_codes_bulk()
        messages.success(request, f'Готово. Обновлено внутренних кодов: {changed}')
        return redirect('assets_list')


class AssetCreateView(View):
    def get(self, request):
        form = AssetForm()
        return render(request, 'assets/form.html', {'form': form})

    def post(self, request):
        form = AssetForm(request.POST)
        if 'assign_code' in request.POST:
            if form.is_valid():
                obj = form.save(commit=False)
                obj.assign_internal_code()
                form = AssetForm(instance=obj)
                messages.info(request, f'Назначен внутренний код: {obj.internal_code}')
            return render(request, 'assets/form.html', {'form': form})

        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.internal_code:
                obj.assign_internal_code()
            obj.save()
            messages.success(request, 'Основное средство сохранено.')
            return redirect('assets_list')
        return render(request, 'assets/form.html', {'form': form})


class CounterpartyListView(View):
    def get(self, request):
        data = Counterparty.objects.all().order_by('id')
        return render(request, 'counterparties/list.html', {'counterparties': data})

    def post(self, request):
        marked = mark_duplicate_inn()
        if not marked:
            messages.info(request, 'Дубликатов ИНН не найдено.')
        else:
            text = '; '.join([f'{m.name} [{m.code}]' for m in marked])
            messages.warning(request, f'Помечены на удаление: {text}')
        return redirect('counterparties_list')


class CounterpartyCreateView(View):
    def get(self, request):
        return render(request, 'counterparties/form.html', {'form': CounterpartyForm()})

    def post(self, request):
        form = CounterpartyForm(request.POST)

        if 'check_inn' in request.POST:
            if form.is_valid():
                inn = form.cleaned_data['inn']
                matches = find_inn_matches(inn)
                if matches:
                    txt = '; '.join([f'{x.name} [{x.code}] ИНН={x.inn}' for x in matches])
                    messages.warning(request, f'Найдены совпадения ИНН/подстроки: {txt}')
                else:
                    messages.success(request, 'Совпадений не найдено.')
            return render(request, 'counterparties/form.html', {'form': form})

        if form.is_valid():
            form.save()
            messages.success(request, 'Контрагент сохранен.')
            return redirect('counterparties_list')
        return render(request, 'counterparties/form.html', {'form': form})