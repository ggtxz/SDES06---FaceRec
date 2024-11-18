from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2 as cv
import time


def findCamIndex():
    for i in range(10):

        cap = cv.VideoCapture(i)

        if cap.isOpened():
            cap.release()
            return i
        cap.release()

    return None


def gen_frames(index, timeOn):
    camera = cv.VideoCapture(index)

    inicio = time.time()
    tempo = time.time() - inicio

    while tempo <= timeOn:
        tempo = time.time() - inicio
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv.imencode('.jpeg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()

    return


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Try addres/{time you wants the camera on}"}


@app.get("/{timeOn}")
async def getCam(timeOn: int):
    index = findCamIndex()
    if index is None:
        return {"Message": "Nenhuma câmera foi encontrada"}
    media_type = 'multipart/x-mixed-replace; boundary=frame'
    return StreamingResponse(gen_frames(index, timeOn), media_type=media_type)
