import time
import mxnet as mx
import cv2
import math

def pt():
    t1 = []
    for i in range(1,1000):
        t1.append(test1())
    r = math.fsum(t1)/len(t1)
    print(" mx:" + str(f'{r:.25f}'))
    t2 = []
    for i in range(1,1000):
        t2.append(test2())
    r = math.fsum(t2)/len(t2)
    print("cv2:" + str(f'{r:.25f}'))

def test1():
    start = time.time()
    with open("tests/tree.jpg", 'rb') as fp:
        str_image = fp.read()
    image = mx.img.imdecode(str_image)
    end = time.time()
    # print(image)
    # print(" mx:" + str(f'{r:.20f}'))
    return end-start

def test2():
    start = time.time()
    image = cv2.imread("tests/tree.jpg")
    image = mx.nd.array(image)
    end = time.time()
    r=round(end-start,6)
    # print("cv2:" + str(f'{r:.20f}'))
    # cv2.imshow("image", image)
    # cv2.waitKey(0)
    return end-start

pt()