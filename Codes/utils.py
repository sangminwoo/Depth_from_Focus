import os
import cv2
import numpy as np

# General
WEIGHTS = np.array(
        [[0, 0, 1, 2, 1, 0, 0],
        [0, 1, 2, 3, 2, 1, 0],
        [1, 2, 3, 4, 3, 2, 1],
        [2, 3, 4, 5, 4, 3, 2],
        [1, 2, 3, 4, 3, 2, 1],
        [0, 1, 2, 3, 2, 1, 0],
        [0, 0, 1, 2, 1, 0, 0]])

def convert_to_grayscale(img):
    imGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return imGray

def read_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    return img

def save_image(save_path, save_as, img):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    cv2.imwrite(save_path+save_as, img)
    
def find_all_files(path):
    all_files = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            all_files.append(file)
    
    return all_files

def read_images_from_path(img_path):
    img_list = []
    
    for root, dirs, files in os.walk(img_path):
        for file in files:
            img_list.append(read_image(root + file))

    return img_list

def normalize(x):
    max_, min_ = np.max(x), np.min(x)
    normalized = (x - min_) /(max_ - min_)
    return normalized