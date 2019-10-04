from __future__ import print_function
from utils import *

import argparse
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

def apply_homography(img1, img2, points1, points2):
    height, width, channels = img2.shape
    homography, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
    aligned_img = cv2.warpPerspective(img1, homography, (width, height))
    return aligned_img

def align_im1_to_im2(img1, img2):
    img1Gray = convert_to_grayscale(img1)
    img2Gray = convert_to_grayscale(img2)

    keypoints1, descriptors1 = compute_descriptors(img1Gray)
    keypoints2, descriptors2 = compute_descriptors(img2Gray)

    matcher = create_matcher(trees=5, checks=50)
    good_matches, points1, points2 = find_good_matches_loc(matcher, keypoints1, descriptors1, keypoints2, descriptors2, factor=0.7)
    
    imMatches = cv2.drawMatches(img1, keypoints1, img2, keypoints2, good_matches, None, flags=2)
    aligned_img = apply_homography(img1, img2, points1, points2)

    return imMatches, aligned_img

def main(img_path, save_path, match_path):
    all_files = find_all_files(img_path)
    
    for i in range(len(all_files)-1):
        source_img_path = img_path + all_files[i]
        target_img_path = img_path + all_files[i+1]
        match_save_as = "matches_" + str(i) + ".jpg" 
        align_save_as = "align_" + str(i) + ".jpg"
        
        print("Reading a source image : ", source_img_path)
        source_img = read_image(source_img_path)
    
        print("Reading a target image : ", target_img_path);
        target_img = read_image(target_img_path)
    
        print("Aligning images ...")
        imMatches, aligned_img = align_im1_to_im2(source_img, target_img)

        print("Saving an feature matching image : ", save_path);
        save_image(match_path, match_save_as, imMatches)

        print("Saving an aligned image : ", save_path);
        save_image(save_path, align_save_as, aligned_img)
        
        print("\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Image Alignment")
    parser.add_argument('img_path',
                        default="../dataset/07/",
                        help="Input images directory")
    parser.add_argument('save_path',
                        default="../dataset/save/07/align/",
                        help="Directory for saving aligned images")
    parser.add_argument('match_save_path',
                        default="../dataset/save/07/matches/",
                        help="Directory for saving matched features between images")
    args = parser.parse_args()
    
    img_path = args.img_path
    save_path = args.save_path
    match_save_path = args.match_save_path
    
    main(img_path, save_path, match_save_path)