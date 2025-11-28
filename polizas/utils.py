# polizas/utils.py

# Diccionario de ejemplo para los factores de recargo por edad
# (Esto debería estar en una tabla de tu base de datos o settings)
FACTOR_EDAD = {
    '0-18': 0.8,
    '19-35': 1.0,
    '36-45': 1.2,
    '46-55': 1.5,
    '56-65': 1.8,
}

# Diccionario de ejemplo para el impacto del deducible
# A mayor deducible, menor es el factor de recargo (descuento indirecto)
FACTOR_DEDUCIBLE = {
    1000: 1.15, # Deducible bajo = Prima más alta
    2500: 1.0,  # Deducible medio = Prima base
    5000: 0.9,  # Deducible alto = Prima más baja
    10000: 0.8,
}

def obtener_factor_edad(edad):
    """Obtiene el factor de riesgo basado en la edad."""
    if edad <= 18:
        return FACTOR_EDAD['0-18']
    elif edad <= 35:
        return FACTOR_EDAD['19-35']
    elif edad <= 45:
        return FACTOR_EDAD['36-45']
    elif edad <= 55:
        return FACTOR_EDAD['46-55']
    else:
        # Por encima de 65, se aplicaría un factor mucho mayor
        return FACTOR_EDAD.get('56-65', 2.0)


def calcular_prima(producto, edades_grupo: dict, deducible_elegido: int):
    """
    Calcula la prima total para un grupo familiar, ajustada por edad,
    deducible y coberturas extra.

    :param producto: Instancia del modelo ProductoPoliza.
    :param edades_grupo: Dict {'titular': 35, 'esposa': 33, 'hijo1': 7, ...}
    :param deducible_elegido: El monto del deducible (ej: 2500)
    :return: Prima mensual total estimada.
    """
    
    prima_base_producto = float(producto.prima_base) # Prima base del plan
    prima_total = 0.0

    # 1. Ajuste por Deducible
    # Buscamos el factor de deducible más cercano al elegido
    # Esto reduce la prima total según qué tan alto sea el deducible.
    deducible_factor = FACTOR_DEDUCIBLE.get(deducible_elegido, 1.0)
    
    # 2. Cálculo por Miembro del Grupo Familiar
    for rol, edad in edades_grupo.items():
        edad_int = int(edad)
        factor_edad = obtener_factor_edad(edad_int)
        
        # Calcular la prima individual usando la base del producto, ajustada por edad y deducible
        prima_individual = (prima_base_producto * factor_edad) * deducible_factor
        
        # Opcional: Descuentos/Recargos por rol (ej: hijos más baratos que adultos)
        if 'hijo' in rol.lower():
            prima_individual *= 0.7 # Ejemplo: los hijos cuestan un 30% menos
        
        prima_total += prima_individual
    
    
    # 3. Ajuste por Coberturas Extra (si aplica)
    # Si tu modelo ProductoPoliza tiene un campo para coberturas extra (ej: meta/json), lo sumas aquí.
    cobertura_extra_costo = float(producto.detalles_extras.get('costo_adicional', 0))
    prima_total += cobertura_extra_costo
    
    return round(prima_total, 2)