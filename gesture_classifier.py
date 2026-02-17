# import random
# from domain import Move

# class ThumbDetector:
#     THUMB_TIP = 4
#     THUMB_IP = 3
#     THUMB_MCP = 2
#     WRIST = 0
#     INDEX_MCP = 5

#     def __init__(self, threshold_up=0.15, threshold_down=0.15):
#         self.threshold_up = threshold_up
#         self.threshold_down = threshold_down

#     def is_thumbs_up(self, landmarks):
#         if not landmarks or len(landmarks) < 21:
#             return False
        
#         thumb_tip = landmarks[self.THUMB_TIP]
#         thumb_ip = landmarks[self.THUMB_IP]
#         wrist = landmarks[self.WRIST]
#         index_mcp = landmarks[self.INDEX_MCP]

#         thumb_higher_than_wrist = (wrist[1] - thumb_tip[1]) > self.threshold_up
#         thumb_higher_than_index = (index_mcp[1] - thumb_tip[1]) > 0.05

#         thumb_extended = thumb_ip[1] > thumb_tip[1]

#         return thumb_higher_than_wrist and thumb_higher_than_index and thumb_extended
    
#     def is_thumbs_down(self, landmarks):
#         if not landmarks or len(landmarks) < 21:
#             return False
        
#         thumb_tip = landmarks[self.THUMB_TIP]
#         thumb_ip = landmarks[self.THUMB_IP]
#         wrist = landmarks[self.WRIST]
#         index_mcp = landmarks[self.INDEX_MCP]

#         thumb_lower_than_wrist = (thumb_tip[1] - wrist[1]) > self.threshold_down
#         thumb_lower_than_index = (thumb_tip[1] -  index_mcp[1]) > 0.05

#         thumb_extended = thumb_tip[1] > thumb_ip[1] 

#         return thumb_lower_than_index and thumb_lower_than_wrist and thumb_extended
    
# class MockClassifier: 
#     def __init__(self):
#         self.moves= list(Move)

#     def classify(self, landmarks): ## poki co randomowe przypisywanie ruchow
#         if not landmarks:
#             return None

#         return random.choice(self.moves)
