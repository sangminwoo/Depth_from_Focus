from __future__ import print_function
from utils import *
import cv2
import numpy as np

def compute_descriptors(imGray):
    sift = cv2.xfeatures2d.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(imGray, None)
    print("keypoints: {}, descriptors: {}".format(len(keypoints), descriptors.shape))
    return keypoints, descriptors

def create_matcher(trees, checks):
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=trees)
    search_params = dict(checks=checks)
    
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    return matcher

def find_good_matches_loc(matcher, keypoints1, descriptors1, keypoints2, descriptors2, factor):
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)
    good_matches = []
    
    for m, n in matches:
        if m.distance < factor * n.distance:
            good_matches.append(m)
            
    points1 = np.float32([keypoints1[match.queryIdx].pt for match in good_matches]).reshape(-1, 1, 2)
    points2 = np.float32([keypoints2[match.trainIdx].pt for match in good_matches]).reshape(-1, 1, 2)
    return good_matches, points1, points2

def draw_matches(i, folder, img1, keypoints1, img2, keypoints2, matches):
    imMatches = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches, None, flags=2)
    cv2.imwrite("../dataset/save/" + folder + "matches/matches_" + str(i) + ".jpg", imMatches)

def apply_homography(img1, img2, points1, points2):
    height, width, channels = img2.shape
    homography, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
    im1Reg = cv2.warpPerspective(img1, homography, (width, height))
    return im1Reg

def align_im1_to_im2(i, folder, img1, img2):
    img1Gray = convert_to_grayscale(img1)
    img2Gray = convert_to_grayscale(img2)

    keypoints1, descriptors1 = compute_descriptors(img1Gray)
    keypoints2, descriptors2 = compute_descriptors(img2Gray)

    matcher = create_matcher(trees=5, checks=50)
    good_matches, points1, points2 = find_good_matches_loc(matcher, keypoints1, descriptors1, keypoints2, descriptors2, factor=0.7)
    draw_matches(i, folder, img1, keypoints1, img2, keypoints2, good_matches)
    
    im1Reg = apply_homography(img1, img2, points1, points2)

    return im1Reg

def main():
    folder = "07/"
    img_path = "../dataset/" + folder
    all_files = find_all_files(img_path)
    
    for i in range(len(all_files)-1):
        source_img_path = img_path + all_files[i]
        target_img_path = img_path + all_files[i+1]
        save_path = "../dataset/save/" + folder + "align/align_" + str(i) + ".jpg"
        
        print("Reading a source image : ", source_img_path)
        source_img = read_image(source_img_path)
    
        print("Reading a target image : ", target_img_path);
        target_img = read_image(target_img_path)
    
        print("Aligning images ...")
        aligned_img = align_im1_to_im2(i, folder, source_img, target_img)

        print("Saving an aligned image : ", save_path);
        save_image(save_path, aligned_img)
        
        print("\n")

if __name__ == '__main__':
    main()