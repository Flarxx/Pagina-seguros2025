def calcular_prima(producto, edad=None, cobertura_extra=None):
    base = float(producto.prima_base)
    if edad:
        base *= 1.2 if edad > 45 else 1.0  # recargo por edad
    if cobertura_extra:
        base += sum(cobertura_extra.values())  # suma costos adicionales
    return round(base, 2)