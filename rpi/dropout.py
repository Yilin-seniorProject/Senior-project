import cv2

def drop_img(img_1, img_2):
    orb = cv2.ORB_create()
    kp_1, des_1 = orb.detectAndCompute(img_1, None)
    kp_2, des_2 = orb.detectAndCompute(img_2, None)

    if des_1 is None or des_2 is None:
       return False
    
    sim_Thres = 0.1*len(kp_1)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = False)
    matches = bf.knnMatch(des_1, des_2, k=2)
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:  # Lowe's ratio test
            good_matches.append(m)
    if len(good_matches) > sim_Thres:
        return True
    else:
        return False

if __name__ =='__main__':

    img_1 = cv2.imread(r'rpi/static/imgs/img0117_153242.jpg')
    img_2 = cv2.imread(r'rpi/static/imgs/img0117_153242.jpg')
    print(drop_img(img_1, img_2))
