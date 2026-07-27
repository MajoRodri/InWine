"""
add_wine.py
===========
Script interactivo para añadir un vino nuevo al catálogo de la app.
Pregunta los datos campo por campo, calcula cluster_id, PC1 y PC2,
y lo añade a wines_SPA_enriched.csv.

Uso / Usage:
    python -m src.add_wine
"""

import sys
from pathlib import Path

import pandas as pd  # Para construir el DataFrame de una sola fila con el vino nuevo / To build the single-row DataFrame with the new wine

# Ruta raíz del proyecto / Project root path
ROOT = Path(__file__).resolve().parents[1]

# Añade preprocessing/ al path porque predict_pipeline lo necesita internamente
# Adds preprocessing/ to the path because predict_pipeline needs it internally
sys.path.insert(0, str(ROOT / "preprocessing"))

# Importa las funciones necesarias de predict_pipeline
# Imports the necessary functions from predict_pipeline
# DEFAULT_MODEL_PATH   → ruta al artefacto .joblib / path to the .joblib artifact
# append_to_catalog    → añade el vino procesado al CSV del catálogo / adds the processed wine to the catalog CSV
# predict_from_artifacts → aplica el pipeline a un DataFrame sin reentrenar / applies the pipeline to a DataFrame without retraining
from src.predict_pipeline import DEFAULT_MODEL_PATH, append_to_catalog, predict_from_artifacts  # noqa: E402

import joblib  # Para cargar el artefacto desde disco / To load the artifact from disk  # noqa: E402

# ──────────────────────────────────────────────────────────────────────────────
# Listas de valores válidos para los campos de elección múltiple
# Lists of valid values for multiple-choice fields
# ──────────────────────────────────────────────────────────────────────────────

# Tipos de vino permitidos en el catálogo / Wine types allowed in the catalog
VINE_TYPES = ["Tinto", "Blanco", "Rosado", "Espumoso", "Generoso"]

# Rangos de temperatura de servicio reconocidos por el pipeline
# Service temperature ranges recognized by the pipeline
TEMPERATURES = ["6-8°C", "8-10°C", "10-12°C", "10-14°C", "12-14°C", "16-18°C"]

# Acepta tanto números como palabras para indicar si el vino tiene crianza
# Accepts both numbers and words to indicate if the wine has ageing
# Las claves son lo que puede escribir el usuario; el valor es 0 (joven) o 1 (crianza)
# Keys are what the user can type; the value is 0 (young) or 1 (aged)
AGEING_OPTIONS = {"0": 0, "joven": 0, "no": 0, "1": 1, "crianza": 1, "si": 1, "sí": 1}


# ──────────────────────────────────────────────────────────────────────────────
# Funciones auxiliares de entrada por teclado
# Keyboard input helper functions
# ──────────────────────────────────────────────────────────────────────────────

def _ask(prompt: str, default: str = "") -> str:
    """
    Muestra un prompt y devuelve lo que escribe el usuario.
    Si el usuario pulsa Enter sin escribir nada, devuelve el valor por defecto.

    Shows a prompt and returns what the user types.
    If the user presses Enter without typing, returns the default value.
    """
    # Muestra el valor por defecto entre corchetes si existe / Shows the default value in brackets if it exists
    suffix = f" [{default}]" if default else ""
    value = input(f"  {prompt}{suffix}: ").strip()  # .strip() elimina espacios sobrantes / removes extra spaces
    return value if value else default  # Si vacío, devuelve el default / If empty, returns the default


def _ask_float(prompt: str, min_val: float = None, max_val: float = None) -> float:
    """
    Pide un número decimal al usuario, validando que esté dentro del rango indicado.
    Sigue preguntando hasta recibir un valor válido.

    Asks the user for a decimal number, validating it's within the indicated range.
    Keeps asking until a valid value is received.
    """
    while True:  # Bucle infinito hasta que el usuario introduzca un valor válido / Infinite loop until user enters a valid value
        try:
            value = float(_ask(prompt))  # Intenta convertir la entrada a número decimal / Tries to convert input to decimal number
            if min_val is not None and value < min_val:  # Comprueba límite inferior / Checks lower bound
                print(f"    ✗ Debe ser >= {min_val}")
                continue  # Vuelve al inicio del bucle / Goes back to start of loop
            if max_val is not None and value > max_val:  # Comprueba límite superior / Checks upper bound
                print(f"    ✗ Debe ser <= {max_val}")
                continue
            return value  # Valor válido, sale del bucle / Valid value, exits the loop
        except ValueError:  # float() lanza ValueError si el texto no es un número / float() raises ValueError if text isn't a number
            print("    ✗ Introduce un número válido.")


def _ask_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """
    Pide un número entero al usuario, validando que esté dentro del rango indicado.
    Asks the user for an integer, validating it's within the indicated range.
    """
    while True:
        try:
            value = int(_ask(prompt))  # Intenta convertir a entero / Tries to convert to integer
            if min_val is not None and value < min_val:
                print(f"    ✗ Debe ser >= {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"    ✗ Debe ser <= {max_val}")
                continue
            return value
        except ValueError:
            print("    ✗ Introduce un número entero válido.")


def _ask_choice(prompt: str, options: list[str]) -> str:
    """
    Muestra una lista numerada de opciones y devuelve la que el usuario elige.
    Acepta tanto el número como el texto exacto de la opción.

    Shows a numbered list of options and returns the one the user chooses.
    Accepts both the number and the exact text of the option.
    """
    # Muestra todas las opciones numeradas / Shows all options numbered
    for i, opt in enumerate(options, 1):  # enumerate empieza en 1 para que sea más intuitivo / enumerate starts at 1 to be more intuitive
        print(f"    {i}. {opt}")
    while True:
        raw = _ask(prompt)
        # Si escribe un número válido, devuelve la opción correspondiente
        # If they type a valid number, returns the corresponding option
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]  # -1 porque las listas empiezan en 0 / -1 because lists start at 0
        # Si escribe el texto, busca la coincidencia sin distinguir mayúsculas
        # If they type the text, searches for the match case-insensitively
        match = next((o for o in options if o.lower() == raw.lower()), None)
        if match:
            return match
        print(f"    ✗ Elige un número del 1 al {len(options)} o escribe la opción exacta.")


# ──────────────────────────────────────────────────────────────────────────────
# Script principal / Main script
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Función principal: recoge datos, procesa el vino y lo añade al catálogo.
    Main function: collects data, processes the wine and adds it to the catalog.
    """
    print("\n═══════════════════════════════════════")
    print("   InWine · Añadir vino nuevo")
    print("═══════════════════════════════════════\n")

    # Comprueba que el artefacto existe antes de continuar
    # Si no existe, significa que train_pipeline.py no se ha ejecutado todavía
    # Checks that the artifact exists before continuing
    # If it doesn't exist, it means train_pipeline.py hasn't been run yet
    if not DEFAULT_MODEL_PATH.exists():
        print(f"✗ No se encontró el artefacto en {DEFAULT_MODEL_PATH}")
        print("  Ejecuta primero: python -m src.train_pipeline")
        sys.exit(1)  # Sale con código de error 1 / Exits with error code 1

    print("Rellena los datos del vino (Ctrl+C para cancelar):\n")

    # try/except KeyboardInterrupt captura Ctrl+C para salir limpiamente
    # try/except KeyboardInterrupt catches Ctrl+C to exit cleanly
    try:
        # Pide cada campo con validación / Asks for each field with validation
        winery = _ask("Bodega")
        while not winery:  # No permite campo vacío / Doesn't allow empty field
            print("    ✗ La bodega no puede estar vacía.")
            winery = _ask("Bodega")

        wine_name = _ask("Nombre del vino")
        while not wine_name:
            print("    ✗ El nombre no puede estar vacío.")
            wine_name = _ask("Nombre del vino")

        # min_val y max_val limitan el rango aceptado / min_val and max_val limit the accepted range
        year = _ask_int("Añada", min_val=1900, max_val=2100)
        rating = _ask_float("Rating (1.0 – 5.0)", min_val=1.0, max_val=5.0)

        region = _ask("Región (D.O.)")
        while not region:
            print("    ✗ La región no puede estar vacía.")
            region = _ask("Región (D.O.)")

        price = _ask_float("Precio (€)", min_val=0.01)  # No permite precio 0 o negativo / Doesn't allow 0 or negative price

        print("  Tipo de vino:")
        vine_type = _ask_choice("  Elige (número o nombre)", VINE_TYPES)  # Solo acepta las 5 opciones válidas / Only accepts the 5 valid options

        # default="Blend/Other" si el usuario no escribe nada / default="Blend/Other" if user doesn't type anything
        grape_variety = _ask("Variedad de uva", default="Blend/Other")

        print("  ¿Tiene crianza?  (0 = Joven, 1 = Crianza)")
        while True:
            raw_ageing = _ask("Crianza [0/1]", default="0").lower()  # .lower() para aceptar "SI", "Si", "si"
            if raw_ageing in AGEING_OPTIONS:  # Comprueba si está en el diccionario de opciones válidas / Checks if it's in the valid options dictionary
                wine_ageing = AGEING_OPTIONS[raw_ageing]  # Convierte el texto al valor numérico (0 o 1) / Converts text to numeric value (0 or 1)
                break  # Valor válido, sale del bucle / Valid value, exits the loop
            print("    ✗ Escribe 0 (Joven) o 1 (Crianza).")

        print("  Temperatura de servicio:")
        service_temperature = _ask_choice("  Elige (número o valor)", TEMPERATURES)

    except KeyboardInterrupt:  # El usuario pulsó Ctrl+C / User pressed Ctrl+C
        print("\n\nCancelado.")
        sys.exit(0)  # Sale con código 0 (sin error) / Exits with code 0 (no error)

    # Calcula automáticamente los campos derivados del precio y el rating
    # Calculates automatically the fields derived from price and rating
    quality_price_ratio = round(rating / price, 4)  # Cuánta calidad se obtiene por euro / How much quality per euro
    luxury_category = 1 if price > 50 else 0         # Mismo umbral que el scraper: > 50€ = premium / Same threshold as scraper: > 50€ = premium

    # Construye un DataFrame de una sola fila con todos los campos del vino
    # Builds a single-row DataFrame with all the wine fields
    df_new = pd.DataFrame([{
        "winery": winery,
        "wine_name": wine_name,
        "year": year,
        "rating": rating,
        "region": region,
        "price_euros": price,
        "vine_type": vine_type,
        "grape_variety": grape_variety,
        "wine_ageing": wine_ageing,
        "service_temperature": service_temperature,
        "quality_price_ratio": quality_price_ratio,
        "luxury_category": luxury_category,
    }])

    # Muestra un resumen de los datos antes de confirmar
    # Shows a summary of the data before confirming
    print("\n─── Resumen ───────────────────────────")
    print(f"  Bodega:       {winery}")
    print(f"  Vino:         {wine_name} ({year})")
    print(f"  Región:       {region}")
    print(f"  Tipo:         {vine_type}  ·  Uva: {grape_variety}")
    print(f"  Precio:       {price}€  ·  Rating: {rating}")
    print(f"  Crianza:      {'Sí' if wine_ageing else 'No'}")
    print(f"  Temperatura:  {service_temperature}")
    print(f"  Calidad/€:    {quality_price_ratio}  ·  Lujo: {'Sí' if luxury_category else 'No'}")
    print("───────────────────────────────────────\n")

    try:
        # Pide confirmación final antes de modificar el catálogo
        # Asks for final confirmation before modifying the catalog
        confirm = _ask("¿Añadir al catálogo? [s/n]", default="s").lower()
    except KeyboardInterrupt:
        print("\n\nCancelado.")
        sys.exit(0)

    # Si el usuario no confirma, cancela sin hacer nada
    # If the user doesn't confirm, cancels without doing anything
    if confirm not in ("s", "si", "sí", "y", "yes"):
        print("Cancelado. El vino no se ha añadido.")
        sys.exit(0)

    print("\nProcesando...")

    # Carga el artefacto completo desde el archivo .joblib
    # Loads the complete artifact from the .joblib file
    artifacts = joblib.load(DEFAULT_MODEL_PATH)

    # Aplica todo el pipeline al vino nuevo: preprocesa, escala, predice cluster y PCA
    # Applies the full pipeline to the new wine: preprocesses, scales, predicts cluster and PCA
    df_result = predict_from_artifacts(df_new, artifacts)

    # Extrae los resultados del pipeline para mostrarlos en pantalla
    # Extracts the pipeline results to display them on screen
    cluster_id = int(df_result["cluster_id"].iloc[0])       # .iloc[0] accede a la primera (y única) fila / .iloc[0] accesses the first (and only) row
    pc1 = round(float(df_result["PC1"].iloc[0]), 4)
    pc2 = round(float(df_result["PC2"].iloc[0]), 4)

    print(f"  → Cluster asignado: {cluster_id}  ·  PC1: {pc1}  ·  PC2: {pc2}")

    # Añade el vino al CSV del catálogo que usa la app
    # Adds the wine to the catalog CSV that the app uses
    append_to_catalog(df_result)
    print(f"\n✓ '{wine_name}' añadido al catálogo.")
    print("  Reinicia la app para verlo reflejado.\n")


# Solo ejecuta main() si este archivo se llama directamente
# Only runs main() if this file is called directly
if __name__ == "__main__":
    main()
