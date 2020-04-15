import tkinter as tk
import cv2 as cv
from PIL import Image, ImageTk
from tkinter import messagebox, ttk
import tkinter.font as font
import time
import random
import os
import sys
import subprocess
import shlex
import opencv_yolo
from playsound import playsound


class Application(tk.Frame):
    def __init__(self, master=None):

        super().__init__(master)

        self.master = master
        self.pack()
        self.photo_index = 0  # the index of photo in snapshot folder
        self.sw = self.winfo_screenwidth()
        self.sh = self.winfo_screenheight()
        self.wx = 800  # TODO: change the value to screen size after we finish design
        self.wh = 600  # TODO: change the value to screen size after we finish design
        self.canvas_width = int(self.wx * 0.8)
        self.canvas_height = int(self.wh * 0.8)
        self.window_geo()
        self.creat_widgets()
        self.capture = VideoCapture(0)
        self.oy = opencv_yolo.Detect_Traffic_Light()
        self.trafficlightstatus = ['Red Light', 'Yellow Light', 'Green Light']
        self.voice_path = "./voice/"
        self.voice_file = ['red.mp3', 'yellow.mp3', 'green.mp3']
        self.color = ['red', 'yellow', 'green']


    def window_geo(self):
        self.master.geometry("%dx%d+%d+%d" % (self.wx, self.wh, (self.sw - self.wx) / 2, (self.sh - self.wh) / 2 - 100))

    def creat_widgets(self):
        self.tab = ttk.Notebook(self.master, height=int(self.wh * 0.9))
        self.tab_home = ttk.Frame(self.tab)
        self.tab_photo = ttk.Frame(self.tab)
        self.tab_setting = ttk.Frame(self.tab)
        self.tab.add(self.tab_home, text='Home')
        self.tab.add(self.tab_photo, text='Album')
        self.tab.add(self.tab_setting, text='Setting')
        self.tab.pack(side='top', fill='x')

        self.alert_label = tk.Label(self.master, text='Alert: ******', height=int(self.wh * 0.1),
                                    width=int(self.wx * 0.8), fg='black')
        self.alert_label.pack(side='top')

        ###### widgets in first tab ######
        self.canvas = tk.Canvas(self.tab_home, bg='black', height=self.canvas_height, width=self.canvas_height)
        self.canvas.pack(anchor='n')
        self.creat_snapshot_btn()

        ###### widgets in second tab ######
        self.label = tk.Label(self.tab_photo, height=self.canvas_height, width=self.canvas_height)
        self.label.pack()
        self.creat_album_btn()
        self.tab.bind("<<NotebookTabChanged>>", lambda event: self.show_photos(event, index=0))

        ###### widgets in second tab ######
        self.creat_setting_btn()

    def show_video(self):
        ret, frame = self.capture.get_frame()
        if not ret:
            raise ValueError('video read frame error')
            return
        frame = cv.flip(frame, 1)
        cv2image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        self.image_file = ImageTk.PhotoImage(img, width=self.canvas_width, height=self.canvas_height)
        self.canvas.create_image(self.canvas_width / 2, self.canvas_height / 2, anchor='center',
                                 image=self.image_file, )
        trafficlight = self.oy.detect_image(image=frame)
        text = ''
        for status in trafficlight:
            if status != -1:
                text += self.trafficlightstatus[status]
                text += '; '
                playsound(os.path.join(self.voice_path, self.voice_file[status]))
                self.chang_alert(text, self.color[status])
        self.canvas.after(1, self.show_video)

    def show_image(self, image_path):
        image = cv.imread(image_path)
        image =cv.resize(image, (self.canvas_width, self.canvas_height))
        cv2image = cv.cvtColor(image, cv.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        self.image_file = ImageTk.PhotoImage(img, width=self.canvas_width, height=self.canvas_height)
        self.canvas.create_image(0,0, anchor='nw', image=self.image_file)
        trafficlight = self.oy.detect_image(image=image)
        text = ''
        for status in trafficlight:
            if status != -1:
                text += self.trafficlightstatus[status]
                text += '; '
                playsound(os.path.join(self.voice_path, self.voice_file[status]))
                self.chang_alert(text, self.color[status])
        # self.canvas.after(1, self.show_video)

    def creat_snapshot_btn(self):
        self.snapshot_btn = tk.Button(self.tab_home, text='shot', width=int(self.wx * 0.2 / 10),
                                      height=int(self.wh * 0.1 / 10),
                                      bg='green', command=lambda: self.snapShot())
        self.snapshot_btn.pack()

    def creat_album_btn(self):
        self.album_frame = tk.Frame(self.tab_photo, height=int(self.wh * 0.1))
        self.album_frame.pack(fill='x', side='top')

        self.album_pre_btn = tk.Button(self.album_frame, text='Previous', width=int(self.wx * 0.1 / 10),
                                       height=int(self.wh * 0.1 / 10),
                                       command=lambda: self.show_photos(index=-1))
        self.album_next_btn = tk.Button(self.album_frame, text='Next', width=int(self.wx * 0.1 / 10),
                                        height=int(self.wh * 0.1 / 10),
                                        command=lambda: self.show_photos(index=1))

        self.album_pre_btn.pack(side='left', padx=int(self.wh * 0.2))
        self.album_next_btn.pack(side='right', padx=int(self.wh * 0.2))

    def creat_setting_btn(self):
        print('setting')
        setting_font = font.Font(size=int(self.wx * 0.1 / 6), weight='bold', family='Helvetica')
        self.power_off_btn = tk.Button(self.tab_setting, text='Power Off', font=setting_font,
                                       width=int(self.wx * 0.1 / 2), height=int(self.wh * 0.1 / 15),
                                       command=lambda: self.power_off())
        self.power_off_btn.grid(row=0, column=0)
        self.tab_setting.grid_rowconfigure(0, weight=1)
        self.tab_setting.grid_columnconfigure(0, weight=1)

    def power_off(self):
        if sys.platform.startswith('linux'):
            cmd = shlex.split("sudo shutdown -h now")
            subprocess.call(cmd)
        elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
            os.system('shutdown /p')

    def show_photos(self, event=None, index=0):
        index = self.photo_index + index
        file_path = os.getcwd() + '\\snapshot'
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        if len(os.listdir(file_path)) == 0:
            self.label['text'] = 'Album is empty'
            self.album_pre_btn['state'] = 'disabled'
            self.album_next_btn['state'] = 'disabled'
            return
        else:
            self.photo_index = index
            self.album_pre_btn['state'] = 'normal'
            self.album_next_btn['state'] = 'normal'
            if index == 0:
                self.album_pre_btn['state'] = 'disable'
            if index == len(os.listdir(file_path)) - 1:
                self.album_next_btn['state'] = 'disable'
            imglist = [image for image in os.listdir(file_path)]
            print('state1: ', self.album_pre_btn['state'])
            print('state2: ', self.album_pre_btn['state'])
            print(imglist, ',', index)
            image = Image.open(os.path.join(file_path, imglist[index]))
            image = ImageTk.PhotoImage(image)
            self.label['image'] = image
            self.label.photo = image

    def creat_file_name(self, prefix='Driver2.0', suffix=None):
        secondsSinceEpoch = time.time()
        localTime = time.localtime(secondsSinceEpoch)
        random.seed(secondsSinceEpoch)
        return prefix + ('_%d%d%d%d%d%d' % (localTime.tm_year, localTime.tm_mon, localTime.tm_mday,
                                            localTime.tm_hour, localTime.tm_min, localTime.tm_sec)) \
               + str(random.randint(1000, 9999)) + '.' + suffix

    def chang_alert(self, text, bg=None, fg=None):
        """
        Use this function to change alert
        """
        self.alert_label['text'] = text
        self.alert_label['bg'] = bg

    def snapShot(self):
        ret, frame = self.capture.get_frame()
        if not ret:
            raise ValueError('video read frame error')
            return
        frame = cv.flip(frame, 1)
        file_name = self.creat_file_name(prefix='snapshot', suffix='jpg')
        file_path = os.getcwd() + '\\snapshot'
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        save_status = cv.imwrite(os.path.join(file_path, file_name), frame)
        if not save_status:
            self.creat_messagebox('Save Photo', 'Fail to save')
        self.creat_messagebox('Save Photo', 'Save successfully')

    def creat_messagebox(self, title=None, message=None):
        self.master.messagebox = tk.messagebox.showinfo(title, message)


class VideoCapture:
    def __init__(self, video_id=0):
        self.vid = cv.VideoCapture(video_id)
        if not self.vid.isOpened():
            raise ValueError('Unable to open video source', video_id)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return ret, frame
            else:
                return ret, None

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


root = tk.Tk()
app = Application(master=root)
app.show_video()
#img_path = "./test date/"

#app.show_image(os.path.join(img_path, "yellow.jpg"))
app.mainloop()
cv.destroyAllWindows()
