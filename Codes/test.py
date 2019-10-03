import numpy as np
import cv2
from pygco import cut_simple
from utils import *

def norm_limits(img, lo=0, hi=1):
    _img = img.astype(np.float32)
    i_min, i_max = np.min(_img), np.max(_img)
    return ((_img - i_min) / (i_max - i_min) * (hi - lo)) + lo

def all_in_focus(img_list, unary_scale=2**22, pair_scale=2**12):
    n = len(img_list)
    unary = []
    
    for img in img_list:
        _img = img.astype(np.float32) / 255.
        grad = np.exp(-(cv2.Sobel(_img, cv2.CV_32F, 1, 1)**2))
        unary.append(cv2.GaussianBlur(grad, (9, 9), 0) * unary_scale)

    unary = norm_limits(np.stack(unary, axis=-1)) * unary_scale

    ii, jj = np.meshgrid(range(n), range(n))
    pairwise = np.abs(ii - jj) * pair_scale

    graph_img = cut_simple(unary.astype(np.int32), pairwise.astype(np.int32), n_iter=20)

    aif_img = np.sum([np.where(i == graph_img, img_list[i], 0) for i in range(n)], axis=0, dtype=np.float64)

    return graph_img, aif_img

def main():
    base_path = "../dataset/save/mobo2/test/"
    img_path = "../dataset/05/" #base_path + "align/"
    #gl_save_path = base_path + "focus_stack/focus_"
    focus_save_path = base_path + "all_in_focus/output.jpg"
    graph_save_path = base_path + "graph_cut/output.jpg"
    #depth_save_path = base_path + "depth_map/output144.jpg"
    
    img_paths = find_all_paths(img_path)
    img_list = read_images_from_path(img_paths)
    
    #print("Stacking focus using LoG ... ")
    #lap_imgs = focus_stack(img_list, gl_save_path, blur_size=5, kernel_size=5)
    
    print("Extracting focus from each images ...")
    graph_img, all_in_focus_img = all_in_focus(img_list, unary_scale=2**22, pair_scale=2**12)
        
    print("Saving all-in-focus image : ", focus_save_path);
    save_image(focus_save_path, all_in_focus_img)

    print("Saving graph-cut image : ", graph_save_path);
    save_image(focus_save_path, graph_img)
    
    #print("Saving depth-from-focus image : ", depth_save_path);
    #depth_map = depth_from_focus(argmax, blur_size=5)
    #save_image(depth_save_path, depth_map)
    
if __name__ == '__main__':
    main()

