import sympy
from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
from matplotlib import pyplot as plt

app = FastAPI()


def print_hi(name):
    print(f'Hi, {name}')

# done
@app.get("/prime/{number}", status_code=200)
async def read_foods(number: int):
    return sympy.isprime(number)


@app.post("/picture/invert/", status_code=201)
def upload(file: UploadFile):
    try:
        image = file.file.read()
        npAr = np.frombuffer(image, np.uint8)
        imagev2 = cv2.imread(npAr, cv2.IMREAD_COLOR)
        invertedImg = cv2.bitwise_not(imagev2)
        return invertedImg;
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}


if __name__ == '__main__':
    print_hi('PyCharm')
