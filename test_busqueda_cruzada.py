from services.busqueda_cruzada import buscar_email

# 🔁 Puedes cambiar el username y el nombre real para probar distintos perfiles
username = ""
nombre_real = "Joan Pradells"

resultado = buscar_email(username, nombre_real)

print("\n📦 RESULTADO DE LA BÚSQUEDA CRUZADA:\n")
for clave, valor in resultado.items():
    print(f"{clave}: {valor}")
