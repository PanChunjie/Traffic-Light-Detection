import cv2 as cv
import numpy as np
import trafficlight


class Detect_Traffic_Light:

    def __init__(self):
        self.confThreshold = 0.5  # Confidence threshold
        self.nmsThreshold = 0.4  # Non-maximum suppression threshold
        self.inWidth = 320  # width of network's input image
        self.inpHeight = 320  # Height of network's input image
        self.classFile = "./yolov3/coco.names"
        self.classes = None
        self.modelConfiguration = "./yolov3/yolov3.cfg"
        self.modelWeights = "./yolov3/yolov3.weights"
        self.init_yolo()
        self.tl = trafficlight.Distinguish_Light()
    def init_yolo(self):
        with open(self.classFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')
        # give the configuration and weights file for the model
        # and load the network using them
        self.net = cv.dnn.readNetFromDarknet(self.modelConfiguration, self.modelWeights)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)

    def getOutputsNames(self, net):
        layersNames = net.getLayerNames()
        # Get the names of the output layers, i.e. the layers with unconnected outputs
        return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    def detect_image(self, image_path = None, image = None):
        if image_path != None:
            img = cv.imread(image_path)
        else:
            img = image
        if img.all() == None:
            raise ValueError("No available image")
            return
        blob = cv.dnn.blobFromImage(img, 1 / 255, (self.inWidth, self.inpHeight), [0, 0, 0], 1, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.getOutputsNames(self.net))
        image_list = self.postprocess(img, outs)
        trafficlightstatus = []
        for im in image_list:
            trafficlightstatus.append(self.tl.detectShape(image = im))
        return trafficlightstatus

    def postprocess(self, frame, outs):
        """
        Remove the bounding boxes with low confidence using non-maxima suppression
        :param frame:
        :param outs:
        :return: cropped traffic light image
        """
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]

        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []  # class id
        confidences = []
        boxes = []  # info of predicted bounding box
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > self.confThreshold:
                    center_x = int(detection[0] * frame_width)
                    center_y = int(detection[1] * frame_height)
                    width = int(detection[2] * frame_width)
                    height = int(detection[3] * frame_height)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)
        light_image = []
        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            if classIds[i] == 9:
                #self.drawPred(classIds[i], confidences[i], left, top, left + width, top + height, frame)
                crop_img = frame[top:top + height, left:left + width]
                light_image.append(cv.resize(crop_img, (50, 100), interpolation=cv.INTER_AREA))
        return light_image

    def drawPred(self, classId, conf, left, top, right, bottom, frame):
        """
        Draw the predicted bounding box
        """
        # Draw a bounding box.
        cv.rectangle(frame, (left, top), (right, bottom), (0, 0, 255))

        label = '%.2f' % conf

        # Get the label for the class name and its confidence
        if self.classes:
            assert (classId < len(self.classes))
            label = '%s:%s' % (self.classes[classId], label)

        # Display the label at the top of the bounding box
        labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 1, 3)
        top = max(top, labelSize[1])
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))

if __name__ == "__main__":
    test_image = "D:\School11111111111111111111111111111\Capstone\OIDv4_ToolKit\OID\Dataset\\train\Traffic light\\1b3d6094e5ab242b.jpg"
    detector = Detect_Traffic_Light()
    light_image = detector.detect_image(test_image)
    for image in light_image:
        cv.imshow("traffic light", image)
        #tl.detectShape(image, 1)
        cv.waitKey()



# cv.namedWindow("object detection", cv.WINDOW_NORMAL)
# #cv.resizeWindow("object detection", 300, 400)
# #imga = cv.resize(img, (300, 400))
# cv.imshow("object detection", img)
# cv.waitKey()
# cv.imwrite("object-detection.jpg", img)
# cv.destroyAllWindows()

# t, _ = net.getPerfProfile()
# label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
# cv.putText(img, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
# cv.imwrite(test_image, img.astype(np.uint8))
