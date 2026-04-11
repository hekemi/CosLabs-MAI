from collections import defaultdict
from .models import Asset, Counterparty


def assign_internal_codes_bulk():
    counters = defaultdict(int)
    assets = Asset.objects.select_related('storage_department').order_by('storage_department_id', 'id')
    changed = 0

    for asset in assets:
        dept = asset.storage_department
        dept_pk = dept.pk
        if dept_pk is None:
            continue

        counters[dept_pk] += 1
        new_code = f'{dept.code}{counters[dept_pk]:04d}'

        if asset.internal_code != new_code:
            asset.internal_code = new_code
            asset.save(update_fields=['internal_code'])
            changed += 1

    return changed


def find_inn_matches(inn: str):
    inn = (inn or '').strip()
    if not inn:
        return []

    all_items = Counterparty.objects.all()
    result = []
    for cp in all_items:
        cp_inn = (cp.inn or '').strip()
        if cp_inn == inn or inn in cp_inn or cp_inn in inn:
            result.append(cp)
    return result


def mark_duplicate_inn():
    groups = defaultdict(list)
    for cp in Counterparty.objects.all().order_by('id'):
        groups[cp.inn.strip()].append(cp)

    marked = []
    for inn_key, items in groups.items():
        if inn_key and len(items) > 1:
            for duplicate in items[1:]:
                duplicate.marked_for_deletion = True
                duplicate.save(update_fields=['marked_for_deletion'])
                marked.append(duplicate)
    return marked