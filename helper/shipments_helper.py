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