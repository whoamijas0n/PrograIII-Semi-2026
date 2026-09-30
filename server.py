from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse
from urllib.parse import urlparse, parse_qs
import json

import conexion
import crud_clientes
import crud_tarifas
import crud_periodos
import crud_cobros

port = 3000
db = conexion.Conexion()
crudClientes = crud_clientes.crud_clientes()
crudTarifas = crud_tarifas.crud_tarifas()
crudPeriodos = crud_periodos.crud_periodos()
crudCobros = crud_cobros.crud_cobros()


class miServidor(SimpleHTTPRequestHandler):
    def responder_json(self, datos, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(datos, ensure_ascii=False).encode("utf-8"))

    def do_POST(self):
        urlParse = urlparse(self.path)
        longitud = int(self.headers.get('Content-Length', 0))
        cuerpo = self.rfile.read(longitud).decode("utf-8")
        if cuerpo:
            try:
                # Soporte para cuerpo JSON o urlencoded
                if cuerpo.startswith("{"):
                    datos = json.loads(cuerpo)
                else:
                    datos = json.loads(parse.unquote(cuerpo))
            except Exception as e:
                self.responder_json({"status": "error", "msg": f"JSON inválido: {e}"}, 400)
                return
        else:
            datos = {}

        ruta = urlParse.path

        if ruta in ("/cliente", "/clientes"):
            resultado = crudClientes.administrar(datos)
            self.responder_json({"msg": resultado})

        elif ruta == "/calcular_impuesto":
            resultado = crudPeriodos.calcular_vista_previa(datos)
            self.responder_json(resultado)

        elif ruta in ("/periodo", "/periodos"):
            resultado = crudPeriodos.administrar(datos)
            self.responder_json(resultado)

        elif ruta == "/periodo/corregir":
            datos["accion"] = "corregir_autorizado"
            resultado = crudPeriodos.administrar(datos)
            self.responder_json(resultado)

        elif ruta == "/cobro/facturar":
            idCliente = datos.get("idCliente")
            fecha_cobro = datos.get("fecha_cobro")
            meses = int(datos.get("meses", 1))
            resultado = crudCobros.facturar(idCliente, fecha_cobro, meses)
            self.responder_json(resultado)

        elif ruta == "/tarifas":
            resultado = crudTarifas.administrar(datos)
            self.responder_json({"msg": resultado})

        else:
            # Compatibilidad hacia atrás: si no especifica ruta conocida, redirigir a clientes
            resultado = crudClientes.administrar(datos)
            self.responder_json({"msg": resultado})

    def do_GET(self):
        urlParse = urlparse(self.path)
        qs = parse_qs(urlParse.query)
        ruta = urlParse.path

        if ruta == "/clientes":
            buscar = qs.get('buscar', [''])[0]
            datos = crudClientes.consultar(buscar)
            self.responder_json(datos)

        elif ruta == "/productos":
            datos = db.consultar("SELECT * FROM productos ORDER BY codigo ASC") or []
            self.responder_json(datos)

        elif ruta == "/tarifas":
            idProducto = qs.get('idProducto', [None])[0]
            datos = crudTarifas.consultar(idProducto) or []
            self.responder_json(datos)

        elif ruta == "/periodos":
            idCliente = qs.get('idCliente', [None])[0]
            idProducto = qs.get('idProducto', [None])[0]
            if not idCliente:
                self.responder_json({"status": "error", "msg": "idCliente es requerido"}, 400)
                return
            datos = crudPeriodos.consultar_por_cliente(idCliente, idProducto)
            self.responder_json(datos)

        elif ruta == "/auditoria":
            idPeriodo = qs.get('idPeriodo', [None])[0]
            if not idPeriodo:
                self.responder_json([])
                return
            datos = crudPeriodos.consultar_auditoria(idPeriodo)
            self.responder_json(datos)

        elif ruta == "/cobros/simular":
            idCliente = qs.get('idCliente', [None])[0]
            fecha = qs.get('fecha', [None])[0]
            meses = int(qs.get('meses', [1])[0])
            if not idCliente or not fecha:
                self.responder_json({"status": "error", "msg": "idCliente y fecha son requeridos"}, 400)
                return
            datos = crudCobros.simular_cobro(idCliente, fecha, meses)
            self.responder_json(datos)

        elif ruta == "/recibos":
            idCliente = qs.get('idCliente', [None])[0]
            datos = crudCobros.consultar_recibos(idCliente)
            self.responder_json(datos)

        elif ruta == "/":
            self.path = "/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        else:
            return SimpleHTTPRequestHandler.do_GET(self)


if __name__ == "__main__":
    print(f"Servidor corriendo en el puerto {port}")
    server = HTTPServer(("localhost", port), miServidor)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")