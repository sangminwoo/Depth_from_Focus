from pygco import cut_simple
from utils import *

import argparse
import cv2
import numpy as np

def graph_cut(img_list, gaussian_size, unary_scale, pair_scale, n_iter):
    imGray_list = []
    for img in img_list:
        imGray_list.append(convert_to_grayscale(img))
    
    n = len(imGray_list)
    unary_cost = []
    ii, jj = np.meshgrid(range(n), range(n))
    pairwise_cost = np.abs(ii - jj) * pair_scale
    
    for imGray in imGray_list:
        gray_img = imGray.astype(np.float32) / 255.
        grad = np.exp(-(cv2.Sobel(gray_img, cv2.CV_32F, 1, 1)**2))
        unary_cost.append(cv2.GaussianBlur(grad, (gaussian_size, gaussian_size), 0) * unary_scale)    
    
    unary_cost = normalize(np.stack(unary_cost, axis=-1)) * unary_scale
    graph_img = cut_simple(unary_cost.astype(np.int32), pairwise_cost.astype(np.int32), n_iter)

    return graph_img

def weighted_median_filter(img):
    wmf_img = np.zeros_like(img)
    
    height, width = img.shape
    kernel_size = len(WEIGHTS)
    MARGIN = int(kernel_size/2)
    medIdx = int((np.sum(WEIGHTS) - 1) / 2)
    
    for i in range(MARGIN, height-MARGIN):
        for j in range(MARGIN, width-MARGIN):
            neighbors = []
            for k in range(-MARGIN, MARGIN+1):
                for l in range(-MARGIN, MARGIN+1):
                    a = img.item(i+k, j+l)
                    w = WEIGHTS[k+MARGIN, l+MARGIN]
                    for _ in range(w):
                        neighbors.append(a)
            neighbors.sort()
            median = neighbors[medIdx]
            wmf_img.itemset((i,j), median)
    
    return wmf_img

def main(base_path):
    img_path = base_path + "align/"
    graph_save_path = base_path + "graph_cut/"
    wmf_save_path = base_path + "wmf/"
    save_as = "output.jpg"
    
    img_list = read_images_from_path(img_path)

    print("Obtaining graph-cut depth-map ... It'll take a while ...")
    graph_img = graph_cut(img_list, gaussian_size=9, unary_scale=2*22, pair_scale=2**12, n_iter=5)
    print("Saving graph-cut depth-map : ", graph_save_path)
    save_image(graph_save_path, save_as, graph_img)
    
    print("Obtaining weighted median filtered depth-map ...")
    wmf_img = weighted_median_filter(graph_img)
    print("Saving weighted-median-filtered depth map : ", wmf_save_path)
    save_image(wmf_save_path, save_as, wmf_img)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Depth Refinement")
    parser.add_argument('base_path',
                        default="../dataset/save/07/",
                        help="Base directory")
    args = parser.parse_args()
    
    base_path = args.base_path
    
    main(base_path)