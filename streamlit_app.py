import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

key_dict = json.loads(st.secrets["textkey"])
# creds = service_account.Credentials.from_service_account_info(key_dict)
creds = credentials.Certificate (key_dict)
if not firebase_admin._apps:
    firebase_admin.initialize_app(creds)

# db = firestore.Client(credentials=creds, project="names-project-demo")
# Initialize Firestore
db = firestore.client()
dbProducts = db.collection(u"products")

# ...
def loadByProduct (nombre):
  products_ref = dbProducts.where(u'nombre', u'==', nombre)
  currentProduct = None
  for myProduct in products_ref.stream():
    currentProduct = myProduct
  return currentProduct


st.sidebar.subheader("Buscar Producto")
nameSearch = st.sidebar.text_input("nombre")
btnFiltrar = st.sidebar.button("Buscar")

if btnFiltrar:
    doc = loadByProduct(nameSearch)
    if doc is None:
        st.sidebar.write("Nombre no existe")
    else:
        st.sidebar.write(doc.to_dict())

# Codificar la eliminación de un documento, este proceso deberá probarse
# después de la búsqueda del documento...

st.sidebar.markdown("""---""")
btnEliminar = st.sidebar.button("Eliminar")

if btnEliminar:
  deleteProduct = loadByProduct(nameSearch)
  if deleteProduct is None:
    st.sidebar.write(f"{nameSearch} no existe")
  else:
    dbProducts.document(deleteProduct.id).delete()
    st.sidebar.write(f"{nameSearch} eliminado")

# Codificar proceso para actualizar un documento
st.sidebar.markdown("""---""")
newproduct = st.sidebar.text_input("Actualizar producto")
btnActualizar = st.sidebar.button("Actualizar")

if btnActualizar:
  updateproduct = loadByProduct(nameSearch)
  if updateproduct is None:
    st.sidebar.write(f"{nameSearch} no existe")
  else:
    myupddateproduct = dbProducts.document(updateproduct.id)
    myupddateproduct.update ({
        "nombre": newproduct
         }
    )

st.header("Nuevo registro")

codigo = st.text_input("Codigo")
nombre = st.text_input("Nombre")
precio = st.number_input("Precio", value=0.00)
existencias = st.number_input("Existencias", value=0)
stock_min = st.number_input ("Stock Minimo", value=0)
stock_max = st.number_input("Stock Máximo", value=0)

submit = st.button("Crear nuevo producto")

# Once the name has submitted, upload it to the database
if codigo and nombre and precio and existencias and stock_min and stock_max and submit:
  doc_ref = db.collection("products").document()
  doc_ref.set ({
      "codigo": codigo,
      "nombre": nombre,
      "precio": precio,
      "existencias": existencias,
      "stock_min": stock_min,
      "stock_max": stock_max
  })
  st.sidebar.write("Producto insertado correctamente")

products_ref = list(db.collection(u'products').stream())
products_dict = list(map(lambda x: x.to_dict(), products_ref))
column_order = ["codigo","nombre", "precio", "existencias", "stock_min", "stock_max"]
products_dataframe = pd.DataFrame(products_dict, columns=column_order)

st.dataframe(products_dataframe)
