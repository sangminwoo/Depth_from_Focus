from pygco import cut_simple
from utils import *

import argparse
import cv2
import numpy as np

def focus_stack(aligned_img, gaussian_size, laplacian_size):
    imGray = convert_to_grayscale(aligned_img)
    gaussian_img = cv2.GaussianBlur(imGray, (gaussian_size, gaussian_size), 0)
    laplacian_img = cv2.Laplacian(gaussian_img, cv2.CV_64F, ksize=laplacian_size)
    
    return laplacian_img

def focus_measure_cal(cost_volume, kernel_size=9):
    focus_measure = np.zeros_like(cost_volume)
    kernel = np.ones((kernel_size, kernel_size))

    for i in range(len(cost_volume)):
        focus_img = cost_volume[i]
        focus_measure[i] = focus_img*focus_img
        focus_measure[i] = cv2.filter2D(focus_measure[i], -1, kernel)
        
    return focus_measure

def all_in_focus(img_list, cost_volume, kernel_size, gaussian_size):
    bgr_imgs = np.asarray(img_list)
    
    all_in_focus_img = np.zeros_like(bgr_imgs[0])
    height, width, channels = all_in_focus_img.shape
    
    focus_measure = focus_measure_cal(cost_volume, kernel_size)
    argmax = np.argmax(focus_measure, axis=0)
    
    normalized = 255 - (normalize(argmax) * 255)
    depth_map = cv2.GaussianBlur(normalized, (gaussian_size, gaussian_size), 0)
    
    for i in range(height):
        for j in range(width):
            idx = argmax[i, j]
            all_in_focus_img[i, j, :] = bgr_imgs[idx, i, j, :]
    
    return depth_map, all_in_focus_img

"""
def graph_cut(cost_volume, unary_scale, pair_scale, n_iter):
    n = len(cost_volume)
    ii, jj = np.meshgrid(range(n), range(n))
    
    unary_cost = normalize(np.stack(cost_volume, axis=-1)) * unary_scale
    pairwise_cost = np.abs(ii - jj) * pair_scale

    graph_img = cut_simple(unary_cost.astype(np.int32), pairwise_cost.astype(np.int32), n_iter)

    return graph_img
"""

def main(base_path):
    img_path = base_path + "align/"
    focus_save_path  = base_path + "focus_stack/"
    depth_save_path = base_path + "depth_map/"
    all_focus_save_path = base_path + "all_in_focus/"
    graph_save_path = base_path + "graph_cut/"
    wmf_save_path = base_path + "wmf/"
    save_as = "output.jpg"
    
    img_list = read_images_from_path(img_path)
    stacked_focus_imgs = []
    
    print("Stacking focus using LoG ... ")
    for i, aligned_img in enumerate(img_list):
        focus_save_as = "focus_" + str(i) + ".jpg"
        
        laplacian_img = focus_stack(aligned_img, gaussian_size=5, laplacian_size=5)
        stacked_focus_imgs.append(laplacian_img)
        
        print("... Saving images ...")
        save_image(focus_save_path, focus_save_as, laplacian_img)
        
    cost_volume = np.asarray(stacked_focus_imgs)
    
    print("Extracting focus from each images ...")
    depth_map, all_in_focus_img = all_in_focus(img_list, cost_volume, kernel_size=64, gaussian_size=5)
    print("Saving depth-from-focus image : ", depth_save_path)
    save_image(depth_save_path, save_as, depth_map)
    print("Saving all-in-focus image : ", all_focus_save_path)
    save_image(all_focus_save_path, save_as, all_in_focus_img)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Depth from Focus")
    parser.add_argument('base_path',
                        default="../dataset/save/07/",
                        help="Base directory")
    args = parser.parse_args()
    
    base_path = args.base_path
    
    main(base_path)