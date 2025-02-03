from fastapi import FastAPI,Form
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel,Field
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
from fastapi.responses import RedirectResponse

#instancioamos la API
app = FastAPI()

#Definimos la base de datos y la colección
cliente = MongoClient('localhost', 27017)
db = cliente["crud-productos"]
coleccion = db["productos"]

#Definimos las plantillas html
templates = Jinja2Templates(directory="templates")

#Definimos la clase Producto
class Producto(BaseModel):
    nombre: str = Field(title="Nombre del producto")
    precio: float = Field(title="Precio del producto")
    descripcion: Optional[str] = None
    cantidad: int = Field(title="Cantidad del producto")


#Definimos la ruta principal
@app.get("/",tags=["Producto"])
def mostrar_productos(request: Request):
    productos = list(coleccion.find())
    return templates.TemplateResponse("crud.html", {"request": request, "productos": productos})

#mostranis el formulario para crear productos
@app.get("/crear",tags=["Producto"])
def formulario_producto(request:Request):
    return templates.TemplateResponse("crear.html",{"request":request})

#creamos la funcion para agregar productos usando Form de fastapi
@app.post("/crear",tags=["Producto"])
def crear_producto(request: Request,             #le pasamos los parametros separados por que 
                    nombre: str = Form(...),     # se va a interactuar con un formulario
                    precio: float = Form(...), 
                    descripcion: str = Form(...), 
                    cantidad: int = Form(...)):
    # Crear un diccionario con los datos recibidos del formulario
    producto_dict = {
        "nombre": nombre,
        "precio": precio,
        "descripcion": descripcion,
        "cantidad": cantidad
    }
    # Insertar el producto en la base de datos
    coleccion.insert_one(producto_dict)
    
    # Redirigir al usuario a la página principal
    return RedirectResponse(url="/", status_code=303)

#Funcion para eliminar productos
@app.get("/eliminar/{producto_id}", tags=["Producto"])
def eliminar_producto(producto_id: str):
    # Convertimos el producto_id de tipo string a ObjectId
    producto_id = ObjectId(producto_id)
    coleccion.delete_one({"_id": producto_id})
    # Redirigimos al usuario a la página principal después de eliminar
    return RedirectResponse(url="/", status_code=303)


#renderizamos el formulario de actualizacion
@app.get("/actualizar/{producto_id}", tags=["Producto"])
def formulario_actualizar(request: Request, producto_id: str):
    producto = coleccion.find_one({"_id": ObjectId(producto_id)})
    return templates.TemplateResponse("actualizar.html", {"request": request, "producto": producto})

#creamos la funcion para actualizar utilizando el de nuevo el form.
@app.post("/actualizar/{producto_id}", tags=["Producto"])
def actualizar_producto(request: Request, producto_id: str, 
                        nombre: str = Form(...), precio: float = Form(...),
                        descripcion: str = Form(...), cantidad: int = Form(...)):
    # Convertimos el producto_id de tipo string a ObjectId
    producto_id = ObjectId(producto_id)
    
    # Crear un diccionario con los nuevos datos
    producto_actualizado = {
        "nombre": nombre,
        "precio": precio,
        "descripcion": descripcion,
        "cantidad": cantidad
    }
    
    # Actualizar el producto en la base de datos
    coleccion.update_one({"_id": producto_id}, {"$set": producto_actualizado})
    
    # Redirigir al usuario a la página principal después de actualizar
    return RedirectResponse(url="/", status_code=303)
