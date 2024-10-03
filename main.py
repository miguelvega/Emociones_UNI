import tempfile
import os
from flask import Flask, request, redirect, send_file
from skimage import io
import base64
import glob
import numpy as np

app = Flask(__name__)


imagenes = []
etiquetas = []

main_html = """
<html>
<head></head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;

  function InitThis() {
      ctx = document.getElementById('myCanvas').getContext("2d");

      emociones = ["🙂", "🙁", "😠"];
      dibujantes = ["Vega", "Canales", "Acuña"];
      
      
      random_emocion = Math.floor(Math.random() * emociones.length);
      aleatorio_emocion = emociones[random_emocion];
      
      
      random_dibujante = Math.floor(Math.random() * dibujantes.length);
      aleatorio_dibujante = dibujantes[random_dibujante];

      
      document.getElementById('mensaje').innerHTML = aleatorio_dibujante + ' dibuje una cara ' + aleatorio_emocion;
      
      
      document.getElementById('numero').value = aleatorio_emocion;  
      document.getElementById('dibujante').value = aleatorio_dibujante;  

      $('#myCanvas').mousedown(function (e) {
          mousePressed = true;
          Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, false);
      });

      $('#myCanvas').mousemove(function (e) {
          if (mousePressed) {
              Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, true);
          }
      });

      $('#myCanvas').mouseup(function (e) {
          mousePressed = false;
      });
  	    $('#myCanvas').mouseleave(function (e) {
          mousePressed = false;
      });
  }

  function Draw(x, y, isDown) {
      if (isDown) {
          ctx.beginPath();
          ctx.strokeStyle = 'black';
          ctx.lineWidth = 11;
          ctx.lineJoin = "round";
          ctx.moveTo(lastX, lastY);
          ctx.lineTo(x, y);
          ctx.closePath();
          ctx.stroke();
      }
      lastX = x; lastY = y;
  }

  function clearArea() {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  //https://www.askingbox.com/tutorial/send-html5-canvas-as-image-to-server
  function prepareImg() {
     var canvas = document.getElementById('myCanvas');
     document.getElementById('myImage').value = canvas.toDataURL();  // Convertir canvas a base64
  }
</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript" ></script>
    <div align="left">
      <img src="https://upload.wikimedia.org/wikipedia/commons/f/f7/Uni-logo_transparente_granate.png" width="300"/>
    </div>
    <div align="center">
        <h1 id="mensaje">Dibujando...</h1>
        <canvas id="myCanvas" width="200" height="200" style="border:2px solid black"></canvas>
        <br/>
        <br/>
        <button onclick="javascript:clearArea();return false;">Borrar</button>
    </div>
    <div align="center">
      <form method="post" action="upload" onsubmit="javascript:prepareImg();"  enctype="multipart/form-data">
      <input id="numero" name="numero" type="hidden" value="">
      <input id="dibujante" name="dibujante" type="hidden" value="">  <!-- Dibujante oculto -->
      <input id="myImage" name="myImage" type="hidden" value="">
      <input id="bt_upload" type="submit" value="Enviar">
      </form>
    </div>
</body>
</html>
"""

@app.route("/")
def main():
    return(main_html)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        
        img_data = request.form.get('myImage').replace("data:image/png;base64,", "")
        emocion = request.form.get('numero')  
        dibujante = request.form.get('dibujante')  

        print(f"Emoción: {emocion}, Dibujante: {dibujante}")

        emociones = ["🙂", "🙁", "😠"]  
        emociones_palabras = ["Feliz", "Triste", "Enojado"]  

        
        emocion_index = emociones.index(emocion)
        emocion_palabra = emociones_palabras[emocion_index]

        
        with tempfile.NamedTemporaryFile(delete=False, mode="w+b", suffix='.png', dir=str(emocion_palabra)) as fh:
            fh.write(base64.b64decode(img_data))

        
        imagenes.append(fh.name)  
        etiquetas.append((dibujante, emocion_palabra))  

        print("Imagen cargada correctamente")
    except Exception as err:
        print("Error ocurrido al cargar la imagen")
        print(err)

    return redirect("/", code=302)


@app.route('/prepare', methods=['GET'])
def prepare_dataset():
    
    loaded_images = []
    loaded_labels = []

    for img_path, etiqueta in zip(imagenes, etiquetas):
        
        img = io.imread(img_path)
        loaded_images.append(img)

        
        loaded_labels.append(etiqueta)

    
    images_np = np.array(loaded_images)
    labels_np = np.array(loaded_labels)

    
    np.save('X.npy', images_np)
    np.save('y.npy', labels_np)

    print(f"{len(loaded_images)} imágenes procesadas y guardadas correctamente.")
    
    return "Ok!"

@app.route('/X.npy', methods=['GET'])
def download_X():
    return send_file('./X.npy')

@app.route('/y.npy', methods=['GET'])
def download_y():
    return send_file('./y.npy')

if __name__ == "__main__":
    emociones_palabras = ['Feliz', 'Triste', 'Enojado']
    for e in emociones_palabras:
        if not os.path.exists(str(e)):
            os.mkdir(str(e))
    app.run()
