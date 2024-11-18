import cv2
from simple_facerec import SimpleFacerec
import time
import os
import requests
import numpy as np
import pandas as pd  # type: ignore
from datetime import datetime
from openpyxl import load_workbook


PATH_IMAGES = 'images/'
PATH_CSV = 'csv_files/chamada.csv'


def capture_video(timeOn):
    url = f'http://127.0.0.1:8000/{timeOn}'
    print(url)  # Para verificar o formato da URL gerada

    # Abre uma sessão para a captura do stream
    session = requests.Session()

    # Envia uma requisição GET para o servidor
    response = session.get(url, stream=True)

    if response.status_code != 200:
        print("Erro ao acessar a live")
    else:
        bytes_data = b''
        for chunk in response.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')  # JPEG início
            b = bytes_data.find(b'\xff\xd9')  # JPEG fim  
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]

                # Converte bytes em uma imagem numpy
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                # Salva o frame atual como uma imagem (opcional)
                cv2.imwrite('frame_capturado.jpg', frame)

                face_locations, face_names = sfr.detect_known_faces(frame)
                for face_loc, name in zip(face_locations, face_names):
                    y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
                    if(name.strip().lower() not in recognized_faces and name.strip().lower() != 'unknown'):
                        recognized_faces.append(name.strip().lower())
                    cv2.putText(frame, name, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1)
                if key == 27 or time.time() - start_time > run_time:
                    break

    cv2.destroyAllWindows()
    response.close()


conteudo_pasta = os.listdir(PATH_IMAGES)


# Cria uma lista com os números de matrículas dos alunos dessa turma
alunos = {
    'matriculas': []
}
for i in range(0, len(conteudo_pasta)):
    alunos['matriculas'].append(conteudo_pasta[i].split('.')[0])


dataframe_matriculas = pd.DataFrame(alunos)

# Fazer o "encode" das imagens para reconhecer
sfr = SimpleFacerec()
sfr.load_encoding_images(PATH_IMAGES)

recognized_faces = []  # Lista para armazenar os nomes das imagens reconhecidas
start_time = time.time()
run_time = 40  # Tempo de execução em segundos

while True:
    hora = datetime.now().strftime('%H:%M')
    if True:
        capture_video(10)
        break


cv2.destroyAllWindows()

# Normalizar nomes das faces reconhecidas
recognized_faces = [name.strip().lower() for name in recognized_faces]

lista_de_presenca = []
# print(dataframe_matriculas[data_atual])
for aluno in dataframe_matriculas['matriculas']:
    if aluno.strip().lower() in recognized_faces:
        lista_de_presenca.append('P')
        print(f'Aluno {aluno} presente')
    else:
        lista_de_presenca.append('F')
        print(f'Aluno {aluno} ausente')

data_atual = datetime.today().strftime("%m/%d/%Y")

dataframe_matriculas[data_atual] = lista_de_presenca

dataframe_matriculas.to_csv(PATH_CSV, sep=',', index=False, encoding='utf-8')

# Atualizar o arquivo csv no Google Drive (substituir o existente)
