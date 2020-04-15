import cv2 as cv
import numpy as np

class Distinguish_Light:

    def __init__(self):
        self.height = 100
        self.width = 50

    def dectorcolor(self, image):
        if image.all() == None:
            raise ValueError("dectorcolor(): empty iamge")
            return -1
        hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        # Min and max HSV values
        red_min = np.array([0,5,46])
        red_max = np.array([10, 255, 255])
        red_min2 = np.array([156,5,46])
        red_max2 = np.array([180, 255, 255])

        yellow_min = np.array([20, 5, 150])
        yellow_max = np.array([30, 255, 255])


        green_min = np.array([35, 5, 45])
        green_max = np.array([90, 255, 255])

        #get the color object
        red_thresh = cv.inRange(hsv_image, red_min, red_max) + cv.inRange(hsv_image, red_min2, red_max2)
        yellow_thresh = cv.inRange(hsv_image, yellow_min, yellow_max)
        green_thresh = cv.inRange(hsv_image, green_min, green_max)


        # medianBlur create white and black image used to count pixels
        red_blur = cv.medianBlur(red_thresh, 9)  # ksize must be odd
        yellow_blur = cv.medianBlur(yellow_thresh, 9)
        green_blur = cv.medianBlur(green_thresh, 9)


        red = cv.countNonZero(red_blur)
        yellow = cv.countNonZero(yellow_blur)
        green = cv.countNonZero(green_blur)

        lightColor = max(red, yellow, green)
        #print("%d:%d:%d"%(red, yellow, green))
        if lightColor > 60: # ignore invalid result
            if lightColor == red:
                return 0
            elif lightColor == yellow:
                return 1
            elif lightColor == green:
                return 2
        else:
            return -1

    def detectShape(self, image):
        """

        :param image:
        :return: 0: red; 1: yellow; 2:green; -1: unknown
        """
        #(height, width) = image.shape[:2]
        image = cv.resize(image,(self.width, self.height))
        gray = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
        #cv.imshow("gray", gray)
        # 霍夫圆环检测
        circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, 7, param1=40, param2=20,minRadius=5, maxRadius=20)
        red = 0
        yellow = 0
        green = 0
        if circles is not None:
            circles = np.around(circles)
            for i in circles.astype(int)[0,:]:
                #print("i: ", i)
                if i[1] < i[2]:
                    i[1] = i[2]
                roi = image[(i[1] - i[2]):(i[1]+i[2]), (i[0]-i[2]):(i[0]+i[2])]
                #cv.imshow('roi'+str(i), roi)
                color = self.dectorcolor(roi)
                if color == 0:
                    red += 1
                elif color == 1:
                    yellow += 1
                elif color == 2:
                    green += 1
            max_color = max(red, yellow, green)
            if red == max_color:
                return 0
            elif yellow == max_color:
                return 1
            elif green == max_color:
                return 2
            else:
                return -1
        else:
            return -1

if __name__ == "__main__":
    image = cv.imread("./test1.PNG")
    print(image)
    image = cv.resize(image, (50, 100), interpolation=cv.INTER_AREA)
    cv.imshow("traffic light", image)
    #dectorcolor(image)
    detectShape(image, 1)
    cv.waitKey(0)