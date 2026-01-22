from decimal import Decimal


# функция для вычисления общего веса и количества посылок
def weight_list(data):
    weights = data.get("weightsHidden", "")  # "1.23 5.34 1.23"
    
    weight_list = [w for w in weights.split() if w.strip()]
    
    parcels_count = len(weight_list)
    total_weight = sum(Decimal(w) for w in weight_list)

    return total_weight, parcels_count