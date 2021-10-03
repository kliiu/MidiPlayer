#from mutagen.easyid3 import EasyID3
import pygame
import base64
import io
from music21 import *
import pretty_midi
import os
import traceback
import glob
import tkinter
import threading
from tkinter.filedialog import *
from mttkinter import mtTkinter as tk
import tkinter.messagebox
pygame.init()


class FrameApp(Frame):
    def __init__(self,master):
        super(FrameApp, self).__init__(master)
        
        self.grid()
        self.paused = False
        self.playlist = list()
        self.actual_song = 0

        self.b1 = Button(self, text="播放", command=lambda :self.thread_it(self.play_music),width=120,bg='lightpink')
        self.b1.grid(row=1, column=0)

        self.b2 = Button(self, text="前一首", command=lambda:self.thread_it(self.previous_song),width=120,bg='palevioletred')
        self.b2.grid(row=2, column=0)

        self.b3 = Button(self, text="暂停", command=lambda:self.thread_it(self.toggle), width=120,bg='lightpink')
        self.b3.grid(row=3, column=0)

        self.b4 = Button(self, text="下一首", command=lambda:self.thread_it(self.next_song), width=120,bg='palevioletred')
        self.b4.grid(row=4, column=0)

        self.b5 = Button(self, text="添加至播放列表", command=self.add_to_list,width=120,bg='lightpink')
        self.b5.grid(row=5, column=0)
        
        self.b6=Button(self,text="转为C调",command=lambda:self.thread_it(self.transpose_to_c),width=120,bg='palevioletred')
        self.b6.grid(row=6, column=0)
         
        self.b7=Button(self,text="变换速度",command=lambda:self.thread_it(self.tempo_transpose),width=120,bg='pink')
        self.b7.grid(row=7, column=0)
        
        self.b8=Button(self,text="将midi转为txt",command=lambda:self.thread_it(self.midi_to_txt),width=120,bg='palevioletred')
        self.b8.grid(row=8, column=0)

        self.b9=Button(self,text="将txt转为midi",command=lambda:self.thread_it(self.text2midi),width=120,bg='pink')
        self.b9.grid(row=9, column=0)
        

        self.label1 = Label(self)
        self.label1.grid(row=10, column=0)
        self.output = Text(self, wrap=WORD, width=110,bg='white')
        self.output.grid(row=18, column=0)

        # set event to not predefined value in pygame
        self.SONG_END = pygame.USEREVENT + 1

        # TODO: Make progressbar, delete songs from playlist, amplify volume

    def add_to_list(self):
        """
        Opens window to browse data on disk and adds selected songs to play list
        :return: None
        """
        directory = askopenfilenames()
        # appends song directory on disk to playlist in memory
        for song_dir in directory:
            print(song_dir)
            self.playlist.append(song_dir)
        self.output.delete(0.0, END)

        for key, item in enumerate(self.playlist):
            # appends song to textbox
            song_data = (str(key + 1)+' : '+str(item))
            self.output.insert(END, song_data + '\n')

    def song_data(self):
        """
        Makes string of current playing song data over the text box
        :return: string - current song data
        """
        song = self.playlist[self.actual_song]
        song_data = "正在播放: " + str(song)
        return song_data
    

    def thread_it(self,func):#多线程
        '''将函数打包进线程'''
        # 创建
        t = threading.Thread(target=func) 
        # 守护 !!!
        t.setDaemon(True) 
        # 启动
        t.start()
        # 阻塞--卡死界面！
        # t.join()
    def play_music(self):
        """
        Loads current song, plays it, sets event on song finish
        :return: None
        """
        mid_file=self.playlist[self.actual_song]
        mid64=base64.encodebytes(open(mid_file, 'rb').read()).decode("utf8")
        
        directory = self.playlist[self.actual_song]
        pygame.mixer.music.load(directory)
        pygame.mixer.music.play(1, 0.0)
        pygame.mixer.music.set_endevent(self.SONG_END)
        self.paused = False
        self.label1['text'] = self.song_data()
        # create a memory file object
        
        midi_bytes = base64.b64decode(mid64.encode())
        music_file = io.BytesIO(midi_bytes)

        freq = 44100    # audio CD quality
        bitsize = -16   # unsigned 16 bit
        channels = 2    # 1 is mono, 2 is stereo
        buffer = 1024   # number of samples
        pygame.mixer.init(freq, bitsize, channels, buffer)

        # optional volume 0 to 1.0
        pygame.mixer.music.set_volume(0.8)
        
        pygame.mixer.music.load(music_file)
        clock = pygame.time.Clock()
        pygame.mixer.music.play()
        # check if playback has finished
        while pygame.mixer.music.get_busy():
            clock.tick(30)
        pygame.mixer.music.set_endevent(self.SONG_END)
        self.paused = False
        self.label1['text'] = self.song_data()
    def check_music(self):
        """
        Listens to END_MUSIC event and triggers next song to play if current 
        song has finished
        :return: None
        """
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.next_song()

    def toggle(self):
        """
        Toggles current song
        :return: None
        """
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        elif not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def get_next_song(self):
        """
        Gets next song number on playlist
        :return: int - next song number
        """
        if self.actual_song + 2 <= len(self.playlist):
            return self.actual_song + 1
        else:
            return 0

    def next_song(self):
        """
        Plays next song
        :return: None
        """
        self.actual_song = self.get_next_song()
        self.play_music()

    def get_previous_song(self):
        """
        Gets previous song number on playlist and returns it
        :return: int - prevoius song number on playlist
        """
        if self.actual_song - 1 >= 0:
            return self.actual_song - 1
        else:
            return len(self.playlist) - 1
    def previous_song(self):
        """
        Plays prevoius song
        :return: 
        """
        self.actual_song = self.get_previous_song()
        self.play_music()
    def transpose_to_c(self):
        tkinter.messagebox.showinfo('提示', '选择想要转换的文件所在的文件夹及保存路径')
        directory=askdirectory()
        midipath =directory+'/*.mid' #MIDI数据集的存放路径
        midi_path=glob.glob(midipath)
        #tkinter.messagebox.showinfo('提示', '选择保存路径')
        transpose_root_dir = askdirectory()#转换后的保存路径
        for midi in midi_path:#使用一个参数midi在这个路径中循环，得到每个文件的路径
            name_1 = midi.split('\\')[-1]
            name_2 = name_1.split('.')[0]
            #设置保存的文件名
            transposed_path = os.path.join(transpose_root_dir + '/' + name_2 + '_to_c.mid')

            stream = converter.parse(midi)#把midi数据通过music21中的converter函数转换为stream格式

            midi_key = stream.analyze('key')#分析调式
            # print(estimate_key)
            midi_tone, midi_mode = (midi_key.tonic, midi_key.mode)#midi_key中有两个值，分别传到前面两个参数中

            c_key = key.Key('C', 'major')#定义需要转换到的调式

            c_tone, c_mode = (c_key.tonic, c_key.mode)

            margin = interval.Interval(midi_tone, c_tone)#计算调式之间的距离

            semitones = margin.semitones

            mid = pretty_midi.PrettyMIDI(midi)
            for instr in mid.instruments:#对每个轨道进行循环
                if not instr.is_drum:#如果不是鼓，就进行转换
                    for note in instr.notes:#对这一轨里面的每一个音符进行转换
                        if note.pitch + semitones < 128 and note.pitch + semitones > 0:
                            note.pitch += semitones

            mid.write(transposed_path)
        tkinter.messagebox.showinfo('提示', '转换成功')
            # new_stream = converter.parse(transposed_path)
            # new_key = new_stream.analyze('key')
            # print(new_key)
    def tempo_transpose(self):#把midi的速度转换到想要的速度上
        speed=self.getInput('提示','输入速度值')
        tkinter.messagebox.showinfo('提示', '选择想要转换的文件所在的文件夹')
        directory=askdirectory()
        midipath =directory+'/*.mid' #MIDI数据集的存放路径
        midi_path=glob.glob(midipath)
        tkinter.messagebox.showinfo('提示', '选择保存路径')
        transpose_root_dir = askdirectory()#转换后的保存路径
        i = 1
        def get_tempo(path):#获取midi数据的速度
                pm = pretty_midi.PrettyMIDI(path)
                _, tempo = pm.get_tempo_changes()#第一个参数没用，只要第二个参数
                return tempo.tolist()
        for midi in midi_path:#对每个midi文件进行处理
            name_1 = midi.split('\\')[-1]
            name_2 = name_1.split('.')[0]
            # 设置保存的文件名
            transposed_path = os.path.join(transpose_root_dir + '/' + name_2 + 'to_'+str(speed)+'.mid')
            i=i+1
           
            original_tempo = get_tempo(midi)[0]#得到所选的midi数据的速度
            print("%s的原始速度为：%s"%(midi,original_tempo))
            changed_rate = original_tempo / float(speed) #得到和想要的速度的比例

            pm = pretty_midi.PrettyMIDI(midi)
            for instr in pm.instruments:
                for note in instr.notes:#对每个音符进行放缩
                    note.start *= changed_rate
                    note.end *= changed_rate

            pm.write(transposed_path)
        tkinter.messagebox.showinfo('提示', '转换成功')
            # print("tempo transpose fallished") 
    def getInput(self,title, message):#得到输入值
        def return_callback(event):
            root.quit()
        def close_callback():
            tkMessageBox.showinfo('message', 'no click...')
        root = Tk(className=title)
        root.wm_attributes('-topmost', 1)
        screenwidth, screenheight = root.maxsize()
        width = 300
        height = 100
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        root.geometry(size)
        root.resizable(0, 0)
        lable = Label(root, height=2)
        lable['text'] = message
        lable.pack()
        entry = Entry(root)
        entry.bind('<Return>', return_callback)
        entry.pack()
        entry.focus_set()
        root.protocol("WM_DELETE_WINDOW", close_callback)
        root.mainloop()
        str = entry.get()
        root.destroy()
        return str
    def midi_to_txt(self):
        tkinter.messagebox.showinfo('提示', '选择想要转换的文件所在的文件夹')
        directory=askdirectory()
        midipath =directory+'/*.mid' #MIDI数据集的存放路径
        midi_path=glob.glob(midipath)
        tkinter.messagebox.showinfo('提示', '选择保存路径')
        transpose_root_dir = askdirectory()#转换后的保存路径
        ifs = []
        track=1
        for midi1 in midi_path:  # 使用一个参数midi在这个路径中循环，得到每个文件的路径
            name_1 = midi1.split('\\')[-1]
            name_2 = name_1.split('.')[0]
            # 设置保存的文件名
            transposed_path = os.path.join(transpose_root_dir + '/' + name_2 + '_to_txt.txt')
            # print(transposed_path)
            mf = midi.MidiFile()
            mf.open(midi1)
            mf.read()
            mf.close()
            # stream = converter.parse(midi)
            notes = []
            mt = mf.tracks[track]
            stream2 = midi.translate.midiTrackToStream(mt)
            # chords = []
            parts = instrument.partitionByInstrument(stream2)
            for part in parts.parts:
                if 'Piano' in str(part):
                    notes_to_parse = part.recurse()  # 递归
                elif parts:
                    notes_to_parse = parts.parts[0].recurse()  # 纯音符组成
                else:
                    notes_to_parse = stream.flat.notes

                list_time = []
                for element in notes_to_parse:
                    time = element.duration.quarterLength
                    if time != 0:
                        list_time.append(time)
                        min_time = min(list_time)

                for element in notes_to_parse:  # notes本身不是字符串类型
                    # 如果是note类型，取它的音高(pitch)
                    if isinstance(element, note.Note):
                        # 格式例如：E6
                        notes.append(str(element.pitch))
                        # ifs.append(str(element.pitch))
                        f = int(element.duration.quarterLength/min_time)
                        for i in range(f):
                            notes.append(str("-"))
                            # ifs.append(str(element.pitch))
                    # elif isinstance(element, chord.Chord):
                    #     # 转换后格式：45.21.78(midi_number)
                    #     chords.append('.'.join(str(n) for n in element.normalOrder))
            # text_save(transposed_path,notes)
            def text_save(filename, data):#filename为写入CSV文件的路径，data为要写入数据列表.
                file = open(filename,'a')
                # file.write('<s>')
                for i in range(len(data)):
                    s = str(data[i]).replace('[','').replace(']','')#去除[],这两行按数据不同，可以选择
                    s = s.replace("'",'').replace(',','')   #去除单引号，逗号，每行末尾追加换行符
                    file.write(s)
                    file.write('\t')
                    #16个音符分为一小节
                    # if((i+1) % 16 == 0):
                    #     file.write('\n')
                # file.write('<e>')
                file.write('\n')
                file.close()
            
            text_save(transposed_path, notes)
            print("%s SAVE2TXT"%midi1)
        tkinter.messagebox.showinfo('提示', '转换成功')
        # return ifs
            # print(notes)
            # print(chords)
        #读取文件数据保存为列表
    def loadDatadet(self,infile):
        with open(infile,'r') as f:
            sourceInLine=f.readlines()
            dataset=[]
            for line in sourceInLine:
                curLine=line.strip().split(" ")
                dataset.extend(curLine)
        # print(dataset)
        return dataset

    #把txt文件转化为midi
    def text2midi(self):
        tkinter.messagebox.showinfo('提示', '选择想要转换的文件所在的文件夹')
        txtpath=askdirectory()+'/*.txt'
        txt_path=glob.glob(txtpath)
        tkinter.messagebox.showinfo('提示', '选择保存路径')
        savepath=askdirectory()
        #txt_path为txt文件的路径
        #save_path为保存路径，格式为 r'路径地址'
        for txt1 in txt_path:  # 使用一个参数midi在这个路径中循环，得到每个文件的路径
            name_1 = txt1.split('\\')[-1]
            name_2 = name_1.split('.')[0]
            save_path = os.path.join(savepath + '/' + name_2 + '_to_mid.mid')
            #先使用loadDatadet函数读取文件保存为note1
            note1 = self.loadDatadet(txt1)
            #定义一个空的stream
            note1 = note1[0].strip().split('\t')
            stream1 = stream.Stream()

            #使用enumerate函数在note1中循环提取每个value和其下标key
            for key, value in enumerate(note1):
                # print(key, value)
                #如果为'-'（延音符），跳过本次循环
                if value == '-':
                    continue
                elif value == '^':
                    if key + 1 < len(note1):
                        if note1[key + 1] != '^':
                            f = note.Rest()
                            f.duration.quarterLength = 1
                            stream1.append(f)
                        else:
                            f = note.Rest()
                            time = 0
                            for i in range(key + 1, len(note1), 1):
                                time += 1
                                if note1[i] != '^':
                                    f.duration.quarterLength = time
                                    stream1.append(f)
                                    time = 0
                                    break
                                else:
                                    continue
                else:
                    #这里是让键值不能大于序列长度
                    if key + 1 < len(note1):
                        #如果下一个符号的值不是为'-',说明不需要延音
                        if note1[key + 1] != '-':
                            f = note.Note(value)
                            f.duration.quarterLength = 2
                            stream1.append(f)
                        else:
                            # 如果下一个符号的值为'-',说明需要延音
                            f = note.Note(value)
                            time = 0
                            #计算需要延音的时长
                            for i in range(key + 1, len(note1), 1):
                                time += 1
                                if note1[i] != '-':
                                    f.duration.quarterLength = time
                                    stream1.append(f)
                                    time = 0
                                    break
                                else:
                                    continue
            #生成一个乐谱对象
            score = stream.Score()
            #添加声部，给声部命名
            part = stream.Part()
            part.partName = 'generation Part'
            #加入stream
            part.append(stream1)
            #声部加入乐谱中
            score.insert(0, part)
            # 添加题目、作者等元数据
            score.insert(0, metadata.Metadata())
            score.metadata.title = 'lyc_generation'
            score.metadata.composer = 'genertion composer'
            #写入文件
            score.write('midi', fp=save_path)
            print('转换成功')
        tkinter.messagebox.showinfo('提示', '转换成功')


root = tk.Tk()
screenwidth, screenheight = root.maxsize()
width = 850
height =600
size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
root.geometry(size)
root.resizable(0, 0)
root.geometry("850x600")
app = FrameApp(root)
def callback():
        print("~被调用啦~")

menubar=tk.Menu(root)
menubar.add_command(label="Hello",command=callback)
menubar.add_command(label='quit',command=root.quit)

root.config(menu=menubar)
while True:
    # runs mainloop of program
    app.check_music()
    app.update()

