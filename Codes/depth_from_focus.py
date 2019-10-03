import cv2
import numpy as np
from pygco import cut_simple
from utils import *

def focus_stack(img_list, gl_save_path, gaussian_size, laplacian_size):
    stacked_focus_imgs = []
    
    for i, aligned_img in enumerate(img_list):
        save_path = gl_save_path + str(i) + ".jpg"
        
        imGray = convert_to_grayscale(aligned_img)
        gaussian_img = cv2.GaussianBlur(imGray, (gaussian_size, gaussian_size), 0)
        laplacian_img = cv2.Laplacian(gaussian_img, cv2.CV_64F, ksize=laplacian_size)
        stacked_focus_imgs.append(laplacian_img)
        
        print("... Saving images ...")
        save_image(save_path, laplacian_img)
    
    cost_volume = np.asarray(stacked_focus_imgs)
    return cost_volume

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

def graph_cut(cost_volume, unary_scale, pair_scale, n_iter):
    n = len(cost_volume)
    ii, jj = np.meshgrid(range(n), range(n))
    
    unary_cost = normalize(np.stack(cost_volume, axis=-1)) * unary_scale
    pairwise_cost = np.abs(ii - jj) * pair_scale

    graph_img = cut_simple(unary_cost.astype(np.int32), pairwise_cost.astype(np.int32), n_iter)

    return graph_img, aif_img

def weighted_median_filter(img)
    wmf_img = np.zeros_like(img)
    
    height, width, _ = img.shape
    MARGIN = int(kernel_size/2)
    medIdx = int(np.sum(WEIGHTS) - 1) / 2)
    
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

def main():
    base_path = "../dataset/save/mobo2/"
    img_path = "../dataset/05/" #base_path + "align/"
    focus_save_path = base_path + "focus_stack/focus_"
    depth_save_path = base_path + "depth_map/output196.jpg"
    all_focus_save_path = base_path + "all_in_focus/output196.jpg"
    graph_save_path = base_path + "graph_cut/output.jpg"
    wmf_save_path = base_path + "wmf/output.jpg"
    
    img_paths = find_all_paths(img_path)
    img_list = read_images_from_path(img_paths)
    
    print("Stacking focus using LoG ... ")
    cost_volume = focus_stack(img_list, focus_save_path, gaussian_size=5, laplacian_size=5)
    
    print("Extracting focus from each images ...")
    depth_map, all_in_focus_img = all_in_focus(img_list, cost_volume, kernel_size=196, gaussian_size=5)
    print("Saving depth-from-focus image : ", depth_save_path)
    save_image(depth_save_path, depth_map)
    print("Saving all-in-focus image : ", all_focus_save_path)
    save_image(all_focus_save_path, all_in_focus_img)
    
    print("Obtaining graph-cut depth-map ... It'll take a while ...")
    graph_img = graph_cut(cost_volume, unary_scale=2*22, pair_scale=2**12, n_iter=10)
    print("Saving graph-cut depth-map : ", graph_save_path)
    save_image(graph_save_path, graph_img)graph_cut
    
    print("Obtaining weighted median filtered depth-map ...")
    wmf_img = weighted_median_filter(graph_img, kernel_size=7)
    print("Saving weighted-median-filtered depth map : ", wmf_save_path)
    save_image(wmf_save_path, wmf_img)
    
if __name__ == '__main__':
    main()