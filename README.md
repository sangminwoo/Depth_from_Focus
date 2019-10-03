# Depth_from_Focus

## 1. Image Alignment: Feature based Alignment [1, 2, 3]
---
1) Convert RGB images A and B to grayscale images A’ and B’
2) Detect SIFT features A’ and B’
3) Match features between A’ and B’
4) Compute homography between A’ and B’
5) Align A to B using homography
6) Repeat 1)~5) for all image sequence(focal stack).

---

## 2. Initial depth from focus measure [4,5,6]
Idea) When Images are captured with a small depth of field, objects that are away from the focal plane are out of focus and are perceived as blurry. Thus if we can measure the amount of blur, focus and depth can be measured as well.

A Focus Measure operator calculates the best focused point in the image, i.e. a Focus Measure is defined as a quantity for locally evaluating the sharpness of a pixel.

1) Measure the amount of blur at the edge, and use the zero-crossing of the third derivative to define how much it is blurry.
2) Say the distance between zero-crossing is d. If d is small, it is less blurry. If d is large, it is more blurry.
3) By using this measure, we can detect the focus of each image in sequence of images.
4) Stack all those images to make cost volume.

1) Convert RGB images A to grayscale image A’
2) To Find where the edge is. first use gaussian blur.
3) And then use laplacian filter. So called, LoG(Laplacian of Gaussian).

Elder and Zucker

---

## 3. All-in-focus image [7, 8]
Idea) In all-in-focus imaging, a series of photographs taken of the same objects, on different focal planes, are analyzed to create an entirely in-focus final image. 

Input, Output refinement

---

## 4. Graph-cuts and weighted median filter [9, 10, 11, 12]
Idea) Suppose that each node as pixel and weight of edge as similarity between pixels. Finding the minimum cost to cut is same as finding the most efficient segmentation method.

---

| No. | References |
|:---:|:---:|
|[1] | https://sites.google.com/site/imagealignment/ |
|[2] | https://www.cs.toronto.edu/~urtasun/courses/CV/lecture06.pdf |
|[3] | https://www.learnopencv.com/image-alignment-feature-based-using-opencv-c-python/ |
|[4] | https://www.semanticscholar.org/paper/2-Blur-estimation-using-the-Elder-and-Zucker-method-Zaman/dbf5e58c54fe68591bf749d22b5ac002ca8cfe38 |
|[5] | https://ieeexplore.ieee.org/document/689301 |
|[6] | https://www.sciencedirect.com/science/article/pii/S0031320308000058 |
|[7] | https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=560554 |
|[8] | https://link.springer.com/chapter/10.1007/11559573_22 |
|[9] | https://vision.cs.uwaterloo.ca/code/ |
|[10] | https://peekaboo-vision.blogspot.com/2012/05/graphcuts-for-python-pygco.html |
|[11] | https://github.com/amueller/gco_python |
|[12] | https://github.com/cgearhart/DepthFromDefocus |
