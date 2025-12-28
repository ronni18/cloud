from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import cgi
import pandas as pd
from io import BytesIO
import mysql.connector
import os
from decimal import Decimal
from urllib.parse import urlparse, parse_qs


# ===============================
# CONEXIÓN A BASE DE DATOS
# ===============================
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "mysql"),
        user=os.getenv("DB_USER", "farmacia_user"),
        password=os.getenv("DB_PASSWORD", "farmacia_pass"),
        database=os.getenv("DB_NAME", "farmacia")
    )


# ===============================
# FUNCIONES AUXILIARES
# ===============================
def convert_decimals(obj):
    """Convierte todos los Decimals en dict/list a float para JSON"""
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


# ===============================
# HANDLER API
# ===============================
class APIHandler(BaseHTTPRequestHandler):

    # ---------- CORS ----------
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, DELETE, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    # ---------- ROUTING ----------
    def do_GET(self):
        if self.path == "/api/format":
            self.download_format()
        elif self.path == "/api/medicamentos":
            self.list_medicamentos()
        else:
            self.send_response(404)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint no encontrado"}).encode())

    def do_POST(self):
        if self.path == "/api/upload":
            self.upload_excel()
        else:
            self.send_response(404)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint no encontrado"}).encode())
    
    def do_DELETE(self):
        if self.path.startswith("/api/medicamentos"):
            self.delete_medicamento()
        else:
            self.send_response(404)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint no encontrado"}).encode())


    # ---------- DESCARGAR FORMATO ----------
    def download_format(self):
        df = pd.DataFrame(columns=["codigo", "nombre", "cantidad", "precio"])
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        self.send_response(200)
        self._set_cors_headers()
        self.send_header("Content-Disposition", "attachment; filename=formato_medicamentos.xlsx")
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.end_headers()
        self.wfile.write(output.read())

    # ---------- SUBIR EXCEL ----------
    def upload_excel(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": self.headers.get("Content-Type"),
                }
            )

            if "excel" not in form:
                raise Exception("No se envió el archivo")

            file_item = form["excel"]
            file_data = file_item.file.read()
            df = pd.read_excel(BytesIO(file_data))

            conn = get_connection()
            cursor = conn.cursor()

            insert_sql = """
                INSERT INTO medicamentos (codigo, nombre, cantidad, precio)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nombre = VALUES(nombre),
                    cantidad = VALUES(cantidad),
                    precio = VALUES(precio)
            """


            rows_inserted = 0
            for _, row in df.iterrows():
                cursor.execute(insert_sql, (
                    str(row["codigo"]),
                    str(row["nombre"]),
                    int(row["cantidad"]),
                    float(row["precio"])
                ))
                rows_inserted += 1

            conn.commit()
            cursor.close()
            conn.close()

            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Archivo procesado correctamente",
                "rows": rows_inserted
            }).encode())

        except Exception as e:
            self.send_response(500)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    # ---------- LISTAR MEDICAMENTOS ----------
    def list_medicamentos(self):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT codigo, nombre, cantidad, precio
                FROM medicamentos
                ORDER BY id DESC
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            rows = convert_decimals(rows)  # <-- convertimos Decimal a float

            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode())

        except Exception as e:
            self.send_response(500)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def delete_medicamento(self):
        try:
            # Obtener query params (?codigo=XXX)
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            if "codigo" not in params:
                self.send_response(400)
                self._set_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "El parámetro 'codigo' es obligatorio"}).encode()
                )
                return

            codigo = params["codigo"][0]

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM medicamentos WHERE codigo = %s",
                (codigo,)
            )

            conn.commit()
            deleted_rows = cursor.rowcount

            cursor.close()
            conn.close()

            if deleted_rows == 0:
                self.send_response(404)
                response = {"error": "Medicamento no encontrado"}
            else:
                self.send_response(200)
                response = {
                    "message": "Medicamento eliminado correctamente",
                    "codigo": codigo
                }

            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


# ===============================
# SERVER
# ===============================
if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), APIHandler)
    print("✅ API corriendo en http://localhost:8000")
    server.serve_forever()
