from decimal import Decimal


# функция для вычисления общего веса и количества посылок
def weight_list(data):
    weights = data.get("weightsHidden", "")  # "1.23 5.34 1.23"
    
    weight_list = [w for w in weights.split() if w.strip()]
    
    parcels_count = len(weight_list)
    total_weight = sum(Decimal(w) for w in weight_list)

    return total_weight, parcels_count


def extract_inventory_names(clean_inventory):
    names = []
    print(clean_inventory)
    for item in clean_inventory:
        name = item.split(":")[0].strip()
        if name:
            names.append(name)

    return names


def split_fio(fio: str):
    if not fio:
        return "", ""
    parts = fio.strip().split()
    surname = parts[0] if len(parts) > 0 else ""
    name = parts[1] if len(parts) > 1 else ""
    return name, surname



def data_collection(base):
    total_count = 0
    total_weight = 0

    paid_rub = 0
    unpaid_rub = 0
    card_rub = 0

    paid_gel = 0
    unpaid_gel = 0
    card_gel = 0

    unicue_users = 0

    for s in base:
        total_count += s.parcels_count
        total_weight += s.total_weight
        if s.currency == 'RUB':
            if s.payment_status == 'paid':
                paid_rub += s.payment_amount
            elif s.payment_status == 'card':
                card_rub += s.payment_amount
            else:
                unpaid_rub += s.payment_amount

        if s.currency == 'GEL':
            if s.payment_status == 'paid':
                paid_gel += s.payment_amount
            elif s.payment_status == 'card':
                card_gel += s.payment_amount
            else:
                unpaid_gel += s.payment_amount
        if s.sequence == 0:
            unicue_users += 1

    return {
        "total_count": total_count,
        "total_weight": total_weight,
        "paid_rub": paid_rub,
        "unpaid_rub": unpaid_rub,
        "card_rub": card_rub,
        "paid_gel": paid_gel,
        "unpaid_gel": unpaid_gel,
        "card_gel": card_gel,
        "unicue_users": unicue_users,
        "chart_labels": ["Оплачено в рублях", "Оплачено в лари"],
        "chart_values": [paid_rub + card_rub, paid_gel + card_gel],
    }






           
