# import the opencv library
import cv2
import mediapipe as mp
import time


class handDetector():
    def __init__(self, mode = False, maxHands = 2, model_complexity = 1, detectionCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.model_complexity = model_complexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.model_complexity, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    #find the hands on the img
    def findHands(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        self.results = self.hands.process(imgRGB)
        num_hands = 0
        #gets the different landmark and draw them
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if(draw):
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
                num_hands += 1
        
        
        
        return img, num_hands

    #gets the position of the landmark
    def findPosition(self, img, handNo = 0, draw = True):

        landmark_list = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y*h)
                landmark_list.append([id, cx,cy])
                if draw:
                    cv2.circle(img, (cx,cy), 25, (255, 0 ,255), cv2.FILLED)
        return landmark_list

def main():

    #start camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    c_time = 0
    p_time = 0
    detector = handDetector()
    while True:
        successs, img = cap.read()
        img = cv2.flip(img,1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw = False)
        if(len(lmList) != 0):
            print(lmList[9])

        #gets fps on top left
        c_time = time.time()
        fps = 1/(c_time - p_time)
        p_time = c_time

        #display fps
        cv2.putText(img, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__": main()