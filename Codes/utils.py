import os
import cv2
import numpy as np

# General
def convert_to_grayscale(img):
    imGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return imGray

def read_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    return img

def save_image(save_path, img):
    cv2.imwrite(save_path, img)
    
def find_all_files(path):
    all_files = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            all_files.append(file)
    
    return all_files

def find_all_paths(path):
    all_paths = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            all_paths.append(root + file)
    
    return all_paths

def read_images_from_path(img_paths):
    img_list = []
    
    for path in img_paths:
        img = read_image(path)
        img_list.append(img)

    return img_list

def normalize(x):
    max_, min_ = np.max(x), np.min(x)
    normalized = (x - min_) /(max_ - min_)
    return normalized