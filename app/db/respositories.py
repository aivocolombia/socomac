# app/db/postgres.py

import psycopg2
import os
from typing import Union, List, Tuple


class PostgresDB:
    def __init__(self):
        self.conn = None
        self.historial = []

        self.queries = {
            "proyectos_por_distrito": "select name, description, district, address, reference  FROM projects WHERE district ILIKE %s",
            "mas_informacion_proyecto": "select name, details, video_url, brochure_url  FROM projects WHERE name ILIKE %s",
            "imagenes_proyecto_planos": "SELECT  pi2.title AS type, pi2.url AS url FROM project_images pi2 JOIN projects p ON p.id = pi2.project_id WHERE pi2.title = 'Mapa_proyecto' AND p.name ILIKE %s",
            "imagenes_proyecto_zonas_comunes": "SELECT  pi2.title AS type, pi2.url AS url FROM project_images pi2 JOIN projects p ON p.id = pi2.project_id WHERE pi2.title IN ('Acceso_a_edificio', 'Lobby', 'Pet_wash', 'Play_room') AND p.name ILIKE %s",
            "imagenes_proyecto_departamento_modelo": "SELECT  pi2.title AS type, pi2.url AS url FROM project_images pi2 JOIN projects p ON p.id = pi2.project_id WHERE pi2.title IN ('Cocina', 'Dormitorio', 'Sala') AND p.name ILIKE %s",
            "imagenes_propiedades_disponibles": "SELECT  pi2.title AS type, pi2.url AS url FROM images pi2 JOIN properties p ON p.id = pi2.property_id join  projects as pj on pj.id = p.project_id where pj.name ILIKE %s",
            "precios_promociones_propiedad": "SELECT pj.name AS name_project, pr.title, pr.area_m2, pr.description AS descripcion_propiedad, prc.price_description, prc.promotion FROM  projects AS pj JOIN properties AS pr ON pj.id = pr.project_id  LEFT JOIN pricing AS prc ON pr.id = prc.property_id  WHERE pj.name ILIKE %s",
            "propiedades_disponibles_proyecto":"select pj.name, pr.title, pr.bedrooms, pr.bathrooms, pr.area_m2, pr.description  FROM projects as pj join properties as pr on pr.project_id = pj.id where pr.status = 'available' and  pj.name ILIKE %s",
            "obtener_proyectos":"select distinct name, district from projects",
        }

    def conectar(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

    def ejecutar(self, query: str, params: Union[tuple, None] = None) -> Union[List[dict], str]:
        try:
            self.conectar()
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()

            if cursor.description:
                columnas = [desc[0] for desc in cursor.description]
                filas = cursor.fetchall()
                datos = [dict(zip(columnas, fila)) for fila in filas]
            else:
                datos = []

            self.historial.append((query, params))
            return datos

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return f"❌ Error al ejecutar la consulta: {e}"

        finally:
            if self.conn:
                self.conn.close()

    def execute_single_param(self, value: str, query_name: str) -> Union[List[Tuple], str]:
        query = self.queries[query_name]
        return self.ejecutar(query, (f"%{value}%",))



    def execute_without_param(self, query_name: str) -> Union[List[Tuple], str]:
        return self.ejecutar(self.queries[query_name])
