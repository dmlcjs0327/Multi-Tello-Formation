import cv2
import time
import math


#skeleton node들은 사람의 몸 각 부위를 인지함 (좌/우는 바라보는 쪽에서의 기준)
# 머리:0, 목:1, 가슴: 14, 등:15
# 우측어깨:2, 우측팔꿈치:3, 우측손목:4, 우측엉덩이:8, 우측무릎:9, 우측발목:10
# 좌측어깨:5, 좌측팔꿈치:6, 좌측손목:7, 좌측엉덩이:11, 좌측무릎:12, 좌측발목:13

#클래스 생성 시 실행할 동작 (magic method)
class Tello_Pose:
    def __init__(self):
        
        print("[tello_pose] Tello_Pose 시작")

        # 포즈 인식에 대한 신경망 학습결과 파일의 경로
        self.protoFile = "model/pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
        self.weightsFile = "model/pose/mpi/pose_iter_160000.caffemodel" 
        
        # the skeleton node의 총 개수
        self.nPoints = 15
        
        # 학습결과 읽어오기
        self.net = cv2.dnn.readNetFromCaffe(self.protoFile, self.weightsFile)

        # count the number of frames,and after every certain number of frames
        # is read, frame_cnt will be cleared and recounted.
        self.frame_cnt = 0 
        self.arm_down_45_cnt = 0 # count numbers of the arm_dowm_45 captured in every certain number of frames
        self.arm_flat_cnt = 0    # count numbers of the arm_flat captured in every certain number of frames
        self.arm_V_cnt = 0       # count numbers of the arm_V captured in every certain number of frames
        self.frame_cnt_threshold = 0
        self.pose_captured_threshold = 0
        
        # the period of pose reconigtion,it depends on your computer performance 
        self.period = 0
        # record how many times the period of pose reconigtion is calculated.
        self.period_calculate_cnt =0
        

    #시작과 끝 각도를 계산하는 함수 -> 시작점에서 끝점까지의 cw 각도
    def getAngle(self, start, end):
        #start: 시작 포인트의 좌표 [x,y]
        #end: 끝 포인트의 좌표 [x,y]

        angle = int(math.atan2((start[1] - end[1]), (start[0] - end[0])) * 180 / math.pi)
        return angle 


    #팔을 45도로 내리고 있는 자세인지 확인하는 함수
    def is_arms_down_45(self, points):
        #points: skeleton node들의 좌표
        """
                | 
              / | \
               / \

        """
        determin_angle = 25 #인정할 오차범위각
        
        #우측에 대해 평가
        right = False
        if points[2] and points[3] and points[4]: #우측 어깨(2)-팔꿈치(3)-손목(4) 노드가 있으면,
            shoulder_angle = self.getAngle(points[2], points[3]) #어깨-팔꿈치 사이의 각도를 계산
           
            if -60 < shoulder_angle < -20: #+- 15도 범위에 있으면
                elbow_angle = self.getAngle(points[3], points[4]) #팔꿈치-손목 사이의 각도를 계산
                
                #팔을 쭉 핀 상태이므로, 두 각도가 비슷할 것
                if abs(elbow_angle - shoulder_angle) < determin_angle: right = True

        #좌측에 대해 평가
        left = False
        if points[5] and points[6] and points[7]: #좌측 어깨(5)-팔꿈치(5)-손목(7) 노드가 있으면,
            shoulder_angle = self.getAngle(points[5], points[6]) #어깨-팔꿈치 사이의 각도를 계산
            if shoulder_angle < 0: shoulder_angle += 360
          
            if 200 < shoulder_angle < 240: #+- 15도 범위에 있으면
                elbow_angle = self.getAngle(points[6], points[7]) #팔꿈치-손목 사이의 각도를 계산
                if elbow_angle < 0: elbow_angle += 360
                
                #팔을 쭉 핀 상태이므로, 두 각도가 비슷할 것
                if abs(elbow_angle - shoulder_angle) < determin_angle: left = True
                
        # 둘 다 일치하면 해당 자세로 인식
        if left and right: return True
        else: return False


    #팔을 수평으로 펴고 있는 자세인지 확인하는 함수(수평보다 약간 위로 올려야 인식 잘 됨)
    def is_arms_flat(self, points):
        #points: skeleton node들의 좌표
        """
         _ _|_ _
            |
           / \
        """
        determin_angle = 25 #인정할 오차범위각
        
        #우측에 대해 평가
        right = False
        if points[2] and points[3] and points[4]: #우측 어깨(2)-팔꿈치(3)-손목(4) 노드가 있으면,
            shoulder_angle = self.getAngle(points[2], points[3]) #어깨-팔꿈치 사이의 각도를 계산
            
            if -10 < shoulder_angle < 40: #+- 25도 범위에 있으면 (수평으로 펴기 어려우므로 오차범위를 크게 준다)
                elbow_angle = self.getAngle(points[3], points[4]) #팔꿈치-손목 사이의 각도를 계산
                
                #팔을 쭉 핀 상태이므로, 두 각도가 비슷할 것
                if abs(elbow_angle - shoulder_angle) < determin_angle: right = True
           
        #좌측에 대해 평가
        left = False
        if points[5] and points[6] and points[7]: #좌측 어깨(5)-팔꿈치(5)-손목(7) 노드가 있으면,
            shoulder_angle = self.getAngle(points[5], points[6]) #어깨-팔꿈치 사이의 각도를 계산           
            if shoulder_angle < 0: shoulder_angle += 360            
            
            if 140 < shoulder_angle < 190: #+- 25도 범위에 있으면 (수평으로 펴기 어려우므로 오차범위를 크게 준다)
                elbow_angle = self.getAngle(points[6], points[7]) #팔꿈치-손목 사이의 각도를 계산
                if elbow_angle < 0: elbow_angle += 360
                
                #팔을 쭉 핀 상태이므로, 두 각도가 비슷할 것
                if abs(elbow_angle - shoulder_angle) < determin_angle: left = True
                
        # 둘 다 일치하면 해당 자세로 인식
        if left and right: return True
        else: return False


    #팔을 V자로 펴고 있는 자세인지 확인하는 함수
    def is_arms_V(self, points):
        #points: skeleton node들의 좌표
        """
           |
         \/|\/
          / \
        """
        
        #우측에 대한 평가
        right = False
        if points[2] and points[3] and points[4]: #우측 어깨(2)-팔꿈치(3)-손목(4) 노드가 있으면,
            shoulder_angle = self.getAngle(points[2], points[3]) #어깨-팔꿈치 사이의 각도를 계산

            if -60 < shoulder_angle < -20: #+- 15도 범위에 있으면
                elbow_angle = self.getAngle(points[3], points[4]) #팔꿈치-손목 사이의 각도를 계산
                
                if 0 < elbow_angle < 90 : right = True #올라가는 모양이면 승인

        #좌측에 대한 평가
        left = False
        if points[5] and points[6] and points[7]:
            shoulder_angle = self.getAngle(points[5], points[6])
            if shoulder_angle < 0: shoulder_angle += 360
            
            if 200 < shoulder_angle < 240: #+- 15도 범위에 있으면
                elbow_angle = self.getAngle(points[6], points[7]) #팔꿈치-손목 사이의 각도를 계산
                
                if 90 < elbow_angle < 180: left = True #올라가는 모양이면 승인

        # 둘 다 일치하면 해당 자세로 인식
        if left and right: return True
        else: return False
        

    def detect(self, frame):
        try:
            # h264 decoded frame (cv2.bilateralFilter 적용한 상태)
            frameHeight = frame.shape[0]
            frameWidth = frame.shape[1]

            prob_threshold = 0.05 

            draw_skeleton_flag = False

            # inWidth와 inHeight보다 이미지가 크면, 정확도가 증가하지만 시간이 오래 걸림
            # inWidth와 inHeight보다 이미지가 작으면, 정확도는 감소하지만 시간이 빨라짐
            # 테스트해보면서 최적값을 알아서 찾아보시길~
            inWidth = 168
            inHeight = 168
            
            inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),(0, 0, 0), swapRB=False, crop=False) #4차원 blob(전처리된 이미지) 생성
            self.net.setInput(inpBlob)
            
            # 신경망이 값을 도출하는 시간을 계산
            period_starttime = time.time()
            output = self.net.forward() #계산
            period_endtime = time.time()
            
            # 6번 계산 후 평균값 저장
            if self.period_calculate_cnt <= 5 :
                self.period = self.period + period_endtime - period_starttime
                self.period_calculate_cnt += 1
                
                if self.period_calculate_cnt == 6 : #6번 측정하면 평균값으로 갱신
                    self.period = self.period / 6

                    # 연산 속도에 따라, 자세를 결정하기 위한 프레임 측정 횟수를 산출        
                    if self.period < 0.3:
                        self.frame_cnt_threshold = 5
                        self.pose_captured_threshold = 4
                        
                    elif self.period >= 0.3 and self.period <0.6:
                        self.frame_cnt_threshold = 4
                        self.pose_captured_threshold = 3
                        
                    elif self.period >= 0.6:
                        self.frame_cnt_threshold = 2
                        self.pose_captured_threshold = 2
                        
                    print("[tello_pose] frame_cnt_threshold={}, pose_captured_threshold={}".format(self.frame_cnt_threshold, self.pose_captured_threshold))

            H = output.shape[2]
            W = output.shape[3]

            # Empty list to store the detected keypoints
            points = []


            for i in range(self.nPoints):
                # confidence map of corresponding body's part.
                probMap = output[0, i, :, :]

                # Find global maxima of the probMap.
                minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

                # Scale the point to fit on the original image
                x = (frameWidth * point[0]) / W
                y = (frameHeight * point[1]) / H
                
                if prob > prob_threshold:
                    points.append((int(x), int(y)))
                    draw_skeleton_flag = True
                else:
                    points.append(None) 
                    draw_skeleton_flag = False

            # check the captured pose
            if self.is_arms_down_45(points):
                self.arm_down_45_cnt += 1
                print("[tello_pose] arm down cnt: {}, frame_cnt: {}".format(self.arm_down_45_cnt, self.frame_cnt))

            if self.is_arms_flat(points):
                self.arm_flat_cnt += 1
                print("[tello_pose] arm flat cnt: {}, frame_cnt: {}".format(self.arm_flat_cnt, self.frame_cnt))

            if self.is_arms_V(points):
                self.arm_V_cnt += 1
                print("[tello_pose] arm V cnt: {}, frame_cnt: {}".format(self.arm_V_cnt, self.frame_cnt))

            self.frame_cnt += 1
        
            # check whether pose control command are generated once for 
            # certain times of pose recognition   
            cmd = ''
            recog_btn = False
            if self.period_calculate_cnt >= 6 and self.frame_cnt >= self.frame_cnt_threshold:
                if self.arm_down_45_cnt >= self.pose_captured_threshold:
                    print("[tello_pose] moveback(down) recognition: {}".format(self.arm_down_45_cnt))
                    cmd = 'moveback'
                    recog_btn = True
                    
                elif self.arm_flat_cnt >= self.pose_captured_threshold:
                    print("[tello_pose] moveforward(forward) recognition: {}".format(self.arm_flat_cnt))
                    cmd = 'moveforward'
                    recog_btn = True
                    
                elif self.arm_V_cnt >= self.pose_captured_threshold :
                    print("[tello_pose] land(V) recognition: {}".format(self.arm_V_cnt))
                    cmd = 'land'
                    recog_btn = True
                
                if recog_btn:
                    self.frame_cnt = 0
                    self.arm_down_45_cnt = 0
                    self.arm_flat_cnt = 0
                    self.arm_V_cnt = 0
                
        except Exception as e:
            print("[tello_pose] Error: {}".format(e))

        return cmd,draw_skeleton_flag,points
