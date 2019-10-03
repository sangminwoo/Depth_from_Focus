import cv2
import numpy as np

from utils import *

def focus_stack(img_list, gl_save_path, blur_size, kernel_size):
    stacked_focus_imgs = []
    
    for i, aligned_img in enumerate(img_list):
        save_path = gl_save_path + str(i) + ".jpg"
        
        imGray = convert_to_grayscale(aligned_img)
        gaussian_img = cv2.GaussianBlur(imGray, (blur_size, blur_size), 0)
        laplacian_img = cv2.Laplacian(gaussian_img, cv2.CV_64F, ksize=kernel_size)
        stacked_focus_imgs.append(laplacian_img)
        
        print("... Saving images ...")
        save_image(save_path, laplacian_img)
        
    return stacked_focus_imgs

def focus_measure_cal(cost_volume, kernel_size):
    focus_measure = np.zeros_like(cost_volume)
    kernel = np.ones((kernel_size, kernel_size))

    for i in range(len(cost_volume)):
        focus_img = cost_volume[i]
        focus_measure[i] = focus_img*focus_img
        focus_measure[i] = cv2.filter2D(focus_measure[i], -1, kernel)
        
    return focus_measure

def all_in_focus(img_list, stacked_focus_imgs):
    cost_volume = np.asarray(stacked_focus_imgs)
    bgr_imgs = np.asarray(img_list)
    
    all_in_focus_img = np.zeros_like(bgr_imgs[0])
    height, width, channels = all_in_focus_img.shape
    
    focus_measure = focus_measure_cal(cost_volume, kernel_size=196)
    argmax = np.argmax(focus_measure, axis=0)
    
    
    
    for i in range(height):
        for j in range(width):
            idx = argmax[i, j]
            all_in_focus_img[i, j, :] = bgr_imgs[idx, i, j, :]
            
    return all_in_focus_img, argmax
    
def depth_from_focus(argmax, blur_size):
    maxIdx, minIdx = np.max(argmax), np.min(argmax)
    normalized = 255-(argmax /(maxIdx - minIdx) * 255)
    depth_map = cv2.GaussianBlur(normalized, (blur_size, blur_size), 0)
    return depth_map

def main():
    base_path = "../dataset/save/mobo2/"
    img_path = "../dataset/05/" #base_path + "align/"
    gl_save_path = base_path + "focus_stack/focus_"
    focus_save_path = base_path + "all_in_focus/output144.jpg"
    depth_save_path = base_path + "depth_map/output144.jpg"
    
    img_paths = find_all_paths(img_path)
    img_list = read_images_from_path(img_paths)
    
    print("Stacking focus using LoG ... ")
    lap_imgs = focus_stack(img_list, gl_save_path, blur_size=5, kernel_size=5)
    
    print("Extracting focus from each images ...")
    all_in_focus_img, argmax = all_in_focus(img_list, lap_imgs)
            
    print("Saving all-in-focus image : ", focus_save_path);
    save_image(focus_save_path, all_in_focus_img)
    
    print("Saving depth-from-focus image : ", depth_save_path);
    depth_map = depth_from_focus(argmax, blur_size=5)
    save_image(depth_save_path, depth_map)
    
if __name__ == '__main__':
    main()