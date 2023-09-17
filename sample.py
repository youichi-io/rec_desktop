import os
import time
from threading import Thread

from PIL import ImageGrab
import PySimpleGUI as sg
import fnmatch
import cv2
import numpy as np

status = {"is_rec": False,
          "now_rec": False,
          "window_info": None,
          "fourcc": None,
          "mov_name": None,
          "end": False,
          "video": None}



def define_gui_layout(window_name="sample"):
    
    layout = [
        [sg.Canvas(size=(400, 400), background_color='green', key='canvas')],
        [sg.Button('Rec')],
        ]
    
    window = sg.Window(window_name,
                       layout,
                       margins=(0, 0),
                       transparent_color='green',
                       alpha_channel=1,
                       grab_anywhere=True,
                       resizable=True,
                       finalize=True,
                       keep_on_top=True) # disable_close=True
    window["canvas"].expand(expand_x=True, expand_y=True)
    canvas = window['canvas']
    return layout, window, canvas

def screenshot(window):
    # window.refresh()
    lx, ly = window.CurrentLocation()
    x, y = window.size
    # coord = ((lx+7, ly, (x+5+lx+5), (y+ly+30)))
    coord = ((lx+10, ly+30, (x+lx), (y+ly)))
    img = ImageGrab.grab(coord)
    img = np.array(img, dtype=np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

def rec():
    global status
    fps = 30.0
    
    while True:
        if status["end"]:
            break
        if status["is_rec"] and status["now_rec"]==False:
            status["now_rec"] = True
            name = status["mov_name"]
            fourcc = status["fourcc"]
            img = screenshot(status["window_info"])
            h,w = img.shape[:2]
            video = cv2.VideoWriter(name, fourcc, fps, (w,h))
            status["video"] = video
        elif status["is_rec"] and status["now_rec"]:
            img = screenshot(status["window_info"])
            status["video"].write(img)
        elif status["is_rec"]==False and status["now_rec"]:
            status["now_rec"] = False
            video.release()
            status["video"].release()
        
        time.sleep(1/fps)

def main():
    global status
    layout, window, canvas = define_gui_layout()
    status["window_info"] = window
    #動画保存時の形式を設定
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    status["fourcc"] = fourcc
    
    th1 = Thread(target=rec)
    th1.start()
    
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED :
            break
        
        # Screen shot GUI events
        elif event == 'Rec':
            if status["is_rec"] == False:
                status["mov_name"] = f"{time.time()}.mp4"
                status["is_rec"] = True
            else:
                status["is_rec"] = False
                
    
    status["end"] = True
    th1.join()
    if status["video"] is not None:
        status["video"].release()
    window.close()
    del window

if __name__ == "__main__":
    main()