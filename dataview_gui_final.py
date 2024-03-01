#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# data opener and viewer

#import sys
import os
import glob as gb
import struct
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog as fd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading
import matplotlib.style as mplstyle
import matplotlib
matplotlib.use("TkAgg") #TkAgg Qt5Agg
import time
import queue
import concurrent.futures


mplstyle.use([ "fast"]) #"ggplot",

class Dataview:
    def __init__(self, root):
        self.root = root
        self.root.title("STM tapping data analysis for acq files")
        self.root.geometry("1500x1000+20+20")
        #self.root.minsize(1600, 1080)
         

        # Create a Scrollbar
        self.scrollbar = tk.Scrollbar(root, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.scrollbar_x = tk.Scrollbar(root, orient="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")

        # Create a Canvas y
        #self.canvas = tk.Canvas(self.root, yscrollcommand=self.scrollbar.set)
        # Canvas for x y
        self.canvas = tk.Canvas(self.root, yscrollcommand=self.scrollbar.set, xscrollcommand=self.scrollbar_x.set)


        #self.canvas.place(x=0,y=0,height=1200,width=1560)
        self.canvas.pack(side="left", fill="both", expand=True)



        # Configure the scrollbar to control the canvas
        self.scrollbar.config(command=self.canvas.yview)

        self.scrollbar_x.config(command=self.canvas.xview)

        # Create a frame to contain the widgets
        self.frame = tk.Frame(self.canvas)
        #self.frame.config(bg='orange')
        self.canvas.create_window(0, 0, window=self.frame, anchor="nw",width=1860, height=1200)

        self.Allfont = ("Helvetica", 10)

        self.L1 = tk.Label(self.frame)
        self.L1.place(x=10, y=20, height=21, width=472)
        # self.L1.configure(activebackground="#f9f9f9") 
        # self.L1.configure(anchor='w')
        # self.L1.configure(background="#d9d9d9")
        # self.L1.configure(compound='left')
        # self.L1.configure(disabledforeground="#a3a3a3")
        # self.L1.configure(foreground="#000000")
        # self.L1.configure(highlightbackground="#d9d9d9")
        #self.L1.configure(font = self.Allfont)
        self.L1.configure(
            text="""input amp calibration functions I(A)-u(V). For 10 nA/V linear amp: 1.0e-8*x """
        )
       
        self.func1 = tk.Entry(self.frame)
        self.func1.place(x=10, y=40, height=25, width=550)
        self.func1.configure(background="white")
        self.func1.configure(disabledforeground="#a3a3a3")
        self.func1.configure(font = self.Allfont)
        self.func1.configure(foreground="#000000")
        self.func1.configure(highlightbackground="#d9d9d9")
        self.func1.configure(highlightcolor="black")
        self.func1.configure(insertbackground="black")
        self.func1.configure(selectbackground="#c4c4c4")
        self.func1.configure(selectforeground="black")
        self.func1.insert(
            -1,
            "10**(-11.21424+0.1395725*x-1.094852*x**2-0.5402152*x**3+7.14779*x**4-0.5614631*x**5-12.67024*x**6+15.2086*x**7-8.695341*x**8+2.863893*x**9-0.5560622*x**10+0.0593169*x**11-0.002687445*x**12)",
        )

        self.dirlo = tk.Entry(self.frame)
        self.dirlo.place(x=10, y=80, height=25, width=400)
        self.dirlo.configure(font = self.Allfont)
   
        self.loadii = tk.Button(self.frame)
        self.loadii.place(x=430, y=80, height=30, width=91)
        self.loadii.configure(activebackground="beige")
        self.loadii.configure(background="#3498DB")
        self.loadii.configure(borderwidth="2")
        self.loadii.configure(command=self.select_file)
        self.loadii.configure(compound="left")
        self.loadii.configure(foreground="#ffffff")
        self.loadii.configure(font = self.Allfont)
        self.loadii.configure(text="""load acq dir""")

        self.Daplot = tk.Button(self.frame)
        self.Daplot.place(x=550, y=80, height=30, width=101)
        self.Daplot.configure(activebackground="beige")
        self.Daplot.configure(background="#3498DB")
        self.Daplot.configure(font = self.Allfont)
        self.Daplot.configure(command=lambda: [self.updateplot(), self.allhistplot()])
        self.Daplot.configure(compound="left")
        self.Daplot.configure(foreground="#ffffff")
        self.Daplot.configure(text="""plot single trace""")

        self.inputnum = tk.Entry(self.frame)
        self.inputnum.place(x=550, y=150, height=25, width=71)
        self.inputnum.insert(-1, 0)
        self.inputnum.configure(font = self.Allfont)

        self.totnum = tk.Entry(self.frame)
        self.totnum.place(x=650, y=150, height=25, width=71)
        self.totnum.configure(font = self.Allfont)

        self.slash1 = tk.Label(self.frame)
        self.slash1.place(x=630, y=150, height=25, width=20)
        self.slash1.configure(font = self.Allfont)
        # self.slash1.configure(anchor='w')
        # self.slash1.configure(background="#262626")
        self.slash1.configure(compound="left")
        # self.slash1.configure(foreground="#ffffff")
        self.slash1.configure(text="""/""")

        self.Next = tk.Button(self.frame)
        self.Next.place(x=650, y=200, height=30, width=60)
        self.Next.configure(activebackground="beige")
        self.Next.configure(background="#3498DB")
        self.Next.configure(font = self.Allfont)
        self.Next.configure(command=lambda: [self.next(), self.updateplot(), self.allhistplot()])
        self.Next.configure(compound="left")
        self.Next.configure(foreground="#ffffff")
        self.Next.configure(text="""next""")

        self.Back = tk.Button(self.frame)
        self.Back.place(x=550, y=200, height=30, width=60)
        self.Back.configure(activebackground="beige")
        self.Back.configure(background="#3498DB")
        self.Back.configure(font = self.Allfont)
        self.Back.configure(command=lambda: [self.back(), self.updateplot(),self.allhistplot()])
        self.Back.configure(compound="left")
        self.Back.configure(foreground="#ffffff")
        self.Back.configure(text="""back""")

        self.dirlabl = tk.Entry(self.frame)
        self.dirlabl.place(x=10, y=115, height=25, width=400)
        self.dirlabl.configure(font = self.Allfont)

        self.showdire = tk.Label(self.frame)
        self.showdire.place(x=410, y=115, height=25, width=100)
        # self.slash1.configure(activebackground="#f9f9f9")
        self.slash1.configure(font = self.Allfont)
        # self.showdire.configure(background="#262626")
        self.showdire.configure(compound="left")
        # self.slash1.configure(foreground="#ffffff")
        self.showdire.configure(text="""file name""")

        self.Datacut1 = tk.Label(self.frame)
        self.Datacut1.place(x=600, y=40, height=25, width=55)
        self.Datacut1.configure(text="""data cut""")
        self.Datacut1.configure(background="#d9d9d9")
        self.Datacut1.configure(font = self.Allfont)
        self.Datacut1input = tk.Entry(self.frame)
        self.Datacut1input.place(x=660, y=40, height=25, width=50)
        self.Datacut1input.insert(-1, 0)
        self.Datacut1input.configure(font = self.Allfont)

        self.Save1 = tk.Button(self.frame)
        self.Save1.place(x=520, y=760, height=30, width=150)
        self.Save1.configure(activebackground="beige")
        self.Save1.configure(background="#3498DB")
        self.Save1.configure(font = self.Allfont)
        self.Save1.configure(command=self.savecurrentdata)
        self.Save1.configure(compound="left")
        self.Save1.configure(foreground="#ffffff")
        self.Save1.configure(text="""save current data as txt""")

        # self.diresave = tk.Entry(self)
        # self.diresave.place(x=10, y=800,height=25, width=400)

        self.Framefig = tk.Frame(self.frame)
        self.Framefig.place(x=13, y=150, height=650, width=500)
        self.Framefig.configure(relief="groove")
        self.Framefig.configure(borderwidth="2")
    

        self.Framlog = tk.Frame(self.frame)
        self.Framlog.place(x=530, y=240, height=500, width=220)
        self.Framlog.configure(relief="groove")
        self.Framlog.configure(borderwidth="2")
        # self.Framlog.configure(relief="groove")

        self.Biaslabel = tk.Label(self.Framlog)
        self.Biaslabel.place(x=5, y=5, height=25, width=70)
        self.Biaslabel.configure(compound="left")
        self.Biaslabel.configure(text="""bias (V)""")
        self.Biaslabel.configure(font = self.Allfont)
        self.Biaslabel.configure(background="#d9d9d9")

        self.Biasinput = tk.Entry(self.Framlog)
        self.Biasinput.place(x=5, y=35, height=25, width=70)
        self.Biasinput.insert(-1, 0.1)
        self.Biasinput.configure(font = self.Allfont)

        self.Rampratelabel = tk.Label(self.Framlog)
        self.Rampratelabel.place(x=110, y=5, height=25, width=90)
        self.Rampratelabel.configure(compound="left")
        self.Rampratelabel.configure(text="""ramp rate (V/s)""")
        self.Rampratelabel.configure(background="#d9d9d9")
        self.Rampratelabel.configure(font = self.Allfont)

        self.Ramprateinput = tk.Entry(self.Framlog)
        self.Ramprateinput.place(x=110, y=35, height=25, width=70)
        self.Ramprateinput.insert(-1, 50)
        self.Ramprateinput.configure(font = self.Allfont)

        self.Piezosensitivity = tk.Label(self.Framlog)
        self.Piezosensitivity.place(x=5, y=75, height=25, width=135)
        self.Piezosensitivity.configure(font = self.Allfont)
        self.Piezosensitivity.configure(text="""piezo sensitivity (nm/V)""")
        self.Piezosensitivity.configure(background="#d9d9d9")

        self.Piezosensitivityinput = tk.Entry(self.Framlog)
        self.Piezosensitivityinput.place(x=40, y=105, height=25, width=70)
        self.Piezosensitivityinput.insert(-1, 2)
        self.Piezosensitivityinput.configure(font = self.Allfont)

        self.Offsetlabel = tk.Label(self.Framlog)
        self.Offsetlabel.place(x=150, y=75, height=25, width=60)
        self.Offsetlabel.configure(font = self.Allfont)
        self.Offsetlabel.configure(text="""offset""")
        self.Offsetlabel.configure(background="#d9d9d9")
        self.Offsetinput = tk.Entry(self.Framlog)
        self.Offsetinput.place(x=150, y=105, height=25, width=60)
        self.Offsetinput.insert(-1, 0)
        self.Offsetinput.configure(font = self.Allfont)

        self.che50 = tk.IntVar()
        self.che51 = tk.IntVar()
        self.che52 = tk.IntVar()
        self.che53 = tk.IntVar()
        self.che54 = tk.IntVar()

        self.Conductanceplot = tk.Checkbutton(self.Framlog)
        self.Conductanceplot.place(x=10, y=200, height=25, width=140)
        self.Conductanceplot.configure(activebackground="beige")
        self.Conductanceplot.configure(activeforeground="black")
        self.Conductanceplot.configure(anchor="w")
        self.Conductanceplot.configure(font = self.Allfont)
        self.Conductanceplot.configure(compound="left")
        self.Conductanceplot.configure(disabledforeground="#a3a3a3")
        self.Conductanceplot.configure(foreground="#000000")
        self.Conductanceplot.configure(highlightbackground="#d9d9d9")
        self.Conductanceplot.configure(highlightcolor="black")
        self.Conductanceplot.configure(justify="left")
        self.Conductanceplot.configure(selectcolor="#d9d9d9")
        self.Conductanceplot.configure(text="""conductance plot """)
        self.Conductanceplot.configure(variable=self.che50)
        # self.Conductanceplot.configure(command=self.updateplot)

        self.Showhistplot = tk.Checkbutton(self.Framlog)
        self.Showhistplot.place(x=10, y=170, height=25, width=100)
        self.Showhistplot.configure(activebackground="beige")
        self.Showhistplot.configure(activeforeground="black")
        self.Showhistplot.configure(anchor="w")
        self.Showhistplot.configure(font = self.Allfont)
        self.Showhistplot.configure(compound="left")
        self.Showhistplot.configure(disabledforeground="#a3a3a3")
        self.Showhistplot.configure(foreground="#000000")
        self.Showhistplot.configure(highlightbackground="#d9d9d9")
        self.Showhistplot.configure(highlightcolor="black")
        self.Showhistplot.configure(justify="left")
        self.Showhistplot.configure(selectcolor="#d9d9d9")
        self.Showhistplot.configure(text="""show hist """)
        self.Showhistplot.configure(variable=self.che51)
        # self.Showhistplot.configure(command=self.updateplot)

        self.Binhist = tk.Checkbutton(self.Framlog)
        self.Binhist.place(x=120, y=170, height=25, width=70)
        self.Binhist.configure(activebackground="beige")
        self.Binhist.configure(activeforeground="black")
        self.Binhist.configure(anchor="w")
        self.Binhist.configure(font = self.Allfont)
        self.Binhist.configure(compound="left")
        self.Binhist.configure(disabledforeground="#a3a3a3")
        self.Binhist.configure(foreground="#000000")
        self.Binhist.configure(highlightbackground="#d9d9d9")
        self.Binhist.configure(highlightcolor="black")
        self.Binhist.configure(justify="left")
        self.Binhist.configure(selectcolor="#d9d9d9")
        self.Binhist.configure(text="""C1 hist """)
        self.Binhist.configure(variable=self.che54)
        # self.Binhist.configure(command=self.updateplot)

        self.Xaxisdis = tk.Checkbutton(self.Framlog)
        self.Xaxisdis.place(x=10, y=230, height=25, width=140)
        self.Xaxisdis.configure(activebackground="beige")
        self.Xaxisdis.configure(activeforeground="black")
        self.Xaxisdis.configure(anchor="w")
        self.Xaxisdis.configure(font = self.Allfont)
        self.Xaxisdis.configure(compound="left")
        self.Xaxisdis.configure(disabledforeground="#a3a3a3")
        self.Xaxisdis.configure(foreground="#000000")
        self.Xaxisdis.configure(highlightbackground="#d9d9d9")
        self.Xaxisdis.configure(highlightcolor="black")
        self.Xaxisdis.configure(justify="left")
        self.Xaxisdis.configure(selectcolor="#d9d9d9")
        self.Xaxisdis.configure(text="""x-axis in nm """)
        self.Xaxisdis.configure(variable=self.che52)
        # self.Xaxisdis.configure(command=self.updateplot)

        self.Addline = tk.Checkbutton(self.Framlog)
        self.Addline.place(x=10, y=260, height=25, width=140)
        self.Addline.configure(activebackground="beige")
        self.Addline.configure(activeforeground="black")
        self.Addline.configure(anchor="w")
        self.Addline.configure(font = self.Allfont)
        self.Addline.configure(compound="left")
        self.Addline.configure(disabledforeground="#a3a3a3")
        self.Addline.configure(foreground="#000000")
        self.Addline.configure(highlightbackground="#d9d9d9")
        self.Addline.configure(highlightcolor="black")
        self.Addline.configure(justify="left")
        self.Addline.configure(selectcolor="#d9d9d9")
        self.Addline.configure(text="""add horizontal line """)
        self.Addline.configure(variable=self.che53 )
        self.Addline.configure(command=self.updateplot)


        self.Y1label = tk.Label(self.Framlog)
        self.Y1label.place(x=10, y=285, height=25, width=19)
        self.Y1label.configure(compound="left")
        self.Y1label.configure(text="""y1:""")
        self.Y1label.configure(font = self.Allfont)
        self.Y1input = tk.Entry(self.Framlog)
        self.Y1input.place(x=40, y=285, height=25, width=60)
        self.Y1input.insert(-1, 0)
        self.Y1input.configure(font = self.Allfont)

        self.Y2label = tk.Label(self.Framlog)
        self.Y2label.place(x=120, y=285, height=25, width=19)
        self.Y2label.configure(compound="left")
        self.Y2label.configure(text="""y2:""")
        self.Y2label.configure(font = self.Allfont)
        self.Y2input = tk.Entry(self.Framlog)
        self.Y2input.place(x=150, y=285, height=25, width=60)
        self.Y2input.insert(-1, 0)
        self.Y2input.configure(font = self.Allfont)

        self.Plotmultidata = tk.Button(self.Framlog)
        self.Plotmultidata.place(x=10, y=350, height=30, width=170)
        self.Plotmultidata.configure(activebackground="beige")
        self.Plotmultidata.configure(background="#3498DB")
        self.Plotmultidata.configure(font = self.Allfont)
        self.Plotmultidata.configure(command=self.mutiplot)
        self.Plotmultidata.configure(compound="left")
        self.Plotmultidata.configure(foreground="#ffffff")
        self.Plotmultidata.configure(text="""plot multidata""")

        self.Multidatainput = tk.Entry(self.Framlog)
        self.Multidatainput.place(x=10, y=390, height=25, width=170)
        self.Multidatainput.insert(-1, "0 1")
        self.Multidatainput.configure(font = self.Allfont)
        ### from here data sorting codes
     

        self.HistLabel1 = tk.Label(self.frame)
        self.HistLabel1.place(x=770, y=15, height=25, width=90)
        self.HistLabel1.configure(compound="left")
        self.HistLabel1.configure(text="""data range set""")
        self.HistLabel1.configure(background="#f0bc2e")
        self.HistLabel1.configure(font = self.Allfont)

        self.selected_function = tk.IntVar()
        self.selected_function.set(1)

        self.LogRadiobutton1 = tk.Radiobutton(self.frame, value=1)
        self.LogRadiobutton1.place(x=860, y=15, height=25, width=70)
        self.LogRadiobutton1.configure(font = self.Allfont)
        self.LogRadiobutton1.configure(text="log amp")
        self.LogRadiobutton1.configure(background="#d9d9d9")
        self.LogRadiobutton1.configure(variable=self.selected_function)
        self.LogRadiobutton1.configure(command=self.radiobuttonselection)

        self.LinRadiobutton1 = tk.Radiobutton(self.frame, value=2)
        self.LinRadiobutton1.place(x=935, y=15, height=25, width=90)
        self.LinRadiobutton1.configure(font = self.Allfont)
        self.LinRadiobutton1.configure(background="#d9d9d9")
        self.LinRadiobutton1.configure(text="linear amp")
        self.LinRadiobutton1.configure(variable=self.selected_function)
        self.LinRadiobutton1.configure(command=self.radiobuttonselection)
        
        ## 
        ##set general distance and current range for hostogram plot

        self.Dislow = tk.Label(self.frame)
        self.Dislow.place(x=1030, y=15, height=25, width=65)
        self.Dislow.configure(text="""x_low(nm):""")
        self.Dislow.configure(font = self.Allfont)
        self.Dislowinput = tk.Entry(self.frame)
        self.Dislowinput.place(x=1099, y=15, height=25, width=50)
        self.Dislowinput.insert(-1, -0.5)
        self.Dislowinput.configure(font = self.Allfont)

        self.Dishigh = tk.Label(self.frame)
        self.Dishigh.place(x=1155, y=15, height=25, width=65)
        self.Dishigh.configure(text="""x_high(nm):""")
        self.Dishigh.configure(font = self.Allfont)
        self.Dishighinput = tk.Entry(self.frame)
        self.Dishighinput.place(x=1225, y=15, height=25, width=50)
        self.Dishighinput.insert(-1, 4)
        self.Dishighinput.configure(font = self.Allfont)

        self.G0low = tk.Label(self.frame)
        self.G0low.place(x=1280, y=15, height=25, width=55)
        self.G0low.configure(text="""y_low(G):""")
        self.G0low.configure(font = self.Allfont)
        self.G0lowinput = tk.Entry(self.frame)
        self.G0lowinput.place(x=1340, y=15, height=25, width=60)
        self.G0lowinput.insert(-1, -6.09)
        self.G0lowinput.configure(font = self.Allfont)

        self.G0high = tk.Label(self.frame)
        self.G0high.place(x=1410, y=15, height=25, width=60)
        self.G0high.configure(text="""y_high(G):""")
        self.G0high.configure(font = self.Allfont)
        self.G0highinput = tk.Entry(self.frame)
        self.G0highinput.place(x=1475, y=15, height=25, width=50)
        self.G0highinput.insert(-1, 0.04)
        self.G0highinput.configure(font = self.Allfont)

        self.Framesort = tk.Frame(self.frame)
        self.Framesort.place(x=770, y=50, height=190, width=780)
        self.Framesort.configure(relief="groove")
        self.Framesort.configure(borderwidth="2")

        self.X_zero = tk.Label(self.Framesort)
        self.X_zero.place(x=5, y=5, height=25, width=60)
        self.X_zero.configure(text="""x_zero(G):""")
        self.X_zero.configure(font = self.Allfont)
        self.X_zeroinput = tk.Entry(self.Framesort)
        self.X_zeroinput.place(x=70, y=5, height=25, width=50)
        self.X_zeroinput.insert(-1, -0.1)
        self.X_zeroinput.configure(font = self.Allfont)

        self.X_bin = tk.Label(self.Framesort)
        self.X_bin.place(x=130, y=5, height=25, width=40)
        self.X_bin.configure(text="""x_bin:""")
        self.X_bin.configure(font = self.Allfont)
        self.X_bininput = tk.Entry(self.Framesort)
        self.X_bininput.place(x=175, y=5, height=25, width=50)
        self.X_bininput.insert(-1, 300)
        self.X_bininput.configure(font = self.Allfont)

        self.Y_bin = tk.Label(self.Framesort)
        self.Y_bin.place(x=230, y=5, height=25, width=40)
        self.Y_bin.configure(text="""y_bin:""")
        self.Y_bin.configure(font = self.Allfont)
        self.Y_bininput = tk.Entry(self.Framesort)
        self.Y_bininput.place(x=275, y=5, height=25, width=50)
        self.Y_bininput.insert(-1, 300)
        self.Y_bininput.configure(font = self.Allfont)

        
        self.Cutsort = tk.Label(self.Framesort)
        self.Cutsort.place(x=330, y=5, height=25, width=25)
        self.Cutsort.configure(text="""cut:""")
        self.Cutsort.configure(font = self.Allfont)
        self.Cutsortinput = tk.Entry(self.Framesort)
        self.Cutsortinput.place(x=360, y=5, height=25, width=50)
        self.Cutsortinput.insert(-1, 0)
        self.Cutsortinput.configure(font = self.Allfont)

        self.ThreadNumber = tk.Label(self.Framesort)
        self.ThreadNumber.place(x=430, y=5, height=25, width=95)
        self.ThreadNumber.configure(text="""thread number:""")
        self.ThreadNumber.configure(background="#d9d9d9")
        self.ThreadNumber.configure(font = self.Allfont)
        self.ThreadNumberinput = tk.Entry(self.Framesort)
        self.ThreadNumberinput.place(x=530, y=5, height=25, width=55)
        self.ThreadNumberinput.insert(-1, 1)
        self.ThreadNumberinput.configure(font = self.Allfont)

        self.Loadoldpara = tk.Button(self.Framesort)
        self.Loadoldpara.place(x=550, y=45, height=30, width=160)
        self.Loadoldpara.configure(activebackground="beige")
        self.Loadoldpara.configure(background="#3498DB")
        self.Loadoldpara.configure(font = self.Allfont)
        self.Loadoldpara.configure(command=self.loadprevious)
        self.Loadoldpara.configure(compound="left")
        self.Loadoldpara.configure(foreground="#ffffff")
        self.Loadoldpara.configure(text="""load previous parameters""")

        self.Histsort = tk.Button(self.Framesort)
        self.Histsort.place(x=560, y=80, height=30, width=120)
        self.Histsort.configure(activebackground="beige")
        self.Histsort.configure(background="#3498DB")
        self.Histsort.configure(font = self.Allfont)
        self.Histsort.configure(command=self.threadhist2dsort)  ##threadhist2dsort   hist2dsort
        self.Histsort.configure(compound="left")
        self.Histsort.configure(foreground="#ffffff")
        self.Histsort.configure(text="""data sorting""")

        self.MonitorLabel = tk.Label(self.Framesort)
        self.MonitorLabel.place(x=530, y=115, height=25, width=200)
        #self.MonitorLabel.configure(background="#d9d9d9")
        #self.MonitorLabel.configure(text="time: 11 s. Click plot histograms")
        

        self.Yieldlabel = tk.Label(self.Framesort)
        self.Yieldlabel.place(x=550, y=150, height=25, width=62)
        self.Yieldlabel.configure(text="""yield is %:""")
        self.Yieldlabel.configure(font = self.Allfont)
        self.Yieldinput = tk.Entry(self.Framesort)
        self.Yieldinput.place(x=616, y=150, height=25, width=55)
        self.Yieldinput.configure(font = self.Allfont)


        ############  Plot histograms settings     #############

        self.Plothistogram = tk.Button(self.frame)
        self.Plothistogram.place(x=1450, y=250, height=30, width=100)
        self.Plothistogram.configure(activebackground="beige")
        self.Plothistogram.configure(background="#3498DB")
        self.Plothistogram.configure(font = self.Allfont)
        self.Plothistogram.configure(command=self.plothists)
        self.Plothistogram.configure(compound="left")
        self.Plothistogram.configure(foreground="#ffffff")
        self.Plothistogram.configure(text="""plot histograms""")

        ### 2d setting

        self.T2dset = tk.Label(self.frame)  
        self.T2dset.place(x=770, y=250, height=31, width=22)
        self.T2dset.configure(text="""2D""")
        self.T2dset.configure(font = self.Allfont)
        self.T2dset.configure(wraplength=1)
        self.T2dset.configure(background="#f0bc2e")


        self.X_01 = tk.Label(self.frame)   # for distance
        self.X_01.place(x=800, y=240, height=20, width=25)
        self.X_01.configure(text="""x_1:""")
        self.X_01.configure(font = self.Allfont)
        self.X_01input = tk.Entry(self.frame)
        self.X_01input.place(x=830, y=240, height=20, width=40)
        self.X_01input.insert(-1, 4)
        self.X_01input.configure(font = self.Allfont)

        self.X_00 = tk.Label(self.frame)   # for distance
        self.X_00.place(x=800, y=265, height=20, width=25)
        self.X_00.configure(text="""x_0:""")
        self.X_00.configure(font = self.Allfont)
        self.X_00input = tk.Entry(self.frame)
        self.X_00input.place(x=830, y=265, height=20, width=40)
        self.X_00input.insert(-1, -0.5)
        self.X_00input.configure(font = self.Allfont)

        self.Y_01 = tk.Label(self.frame)   # for distance
        self.Y_01.place(x=880, y=240, height=20, width=25)
        self.Y_01.configure(text="""y_1:""")
        self.Y_01.configure(font = self.Allfont)
        self.Y_01input = tk.Entry(self.frame)
        self.Y_01input.place(x=910, y=240, height=20, width=40)
        self.Y_01input.insert(-1, 0.1)
        self.Y_01input.configure(font = self.Allfont)

        self.Y_00 = tk.Label(self.frame)   # for distance
        self.Y_00.place(x=880, y=265, height=20, width=25)
        self.Y_00.configure(text="""y_0:""")
        self.Y_00.configure(font = self.Allfont)
        self.Y_00input = tk.Entry(self.frame)
        self.Y_00input.place(x=910, y=265, height=20, width=40)
        self.Y_00input.insert(-1, -6.09)
        self.Y_00input.configure(font = self.Allfont)

        self.Z_01 = tk.Label(self.frame)   # for distance
        self.Z_01.place(x=960, y=240, height=20, width=25)
        self.Z_01.configure(text="""z_1:""")
        self.Z_01.configure(font = self.Allfont)
        self.Z_01input = tk.Entry(self.frame)
        self.Z_01input.place(x=990, y=240, height=20, width=40)
        self.Z_01input.insert(-1, 10)
        self.Z_01input.configure(font = self.Allfont)

        self.Z_00 = tk.Label(self.frame)   # for distance
        self.Z_00.place(x=960, y=265, height=20, width=25)
        self.Z_00.configure(text="""z_0:""")
        self.Z_00.configure(font = self.Allfont)
        self.Z_00input = tk.Entry(self.frame)
        self.Z_00input.place(x=990, y=265, height=20, width=40)
        self.Z_00input.insert(-1, 0)
        self.Z_00input.configure(font = self.Allfont)
        
        self.Colorpick = tk.Label(self.frame)   # for distance
        self.Colorpick.place(x=1040, y=240, height=18, width=70)
        self.Colorpick.configure(text="""color pick""")
        self.Colorpick.configure(background="#d9d9d9")
        self.Colorpick.configure(font = self.Allfont)
        self.Color2d = ttk.Combobox(self.frame)
        self.Color2d.place(x=1040, y=260, height=25, width=85)
        self.Color2d.configure(font = self.Allfont)
        self.Color2d.configure(takefocus="")
        self.Color2d['values']=('Greens','Reds','Oranges','flag', 'prism', 'ocean', 'gist_earth', 'terrain',
                      'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',
                      'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet')
        self.Color2d.current(0)
        #self.Color2d.bind("<<ComboboxSelected>>",self.plothists)

        ##### 1d plot coordinate setting
        self.Y1dset = tk.Label(self.frame)  
        self.Y1dset.place(x=1210, y=250, height=29, width=22)
        self.Y1dset.configure(text="""1D""")
        self.Y1dset.configure(font = self.Allfont)
        self.Y1dset.configure(wraplength=1)
        self.Y1dset.configure(background="#f0bc2e")


        self.X1d_01 = tk.Label(self.frame)   # for distance
        self.X1d_01.place(x=1250, y=240, height=20, width=25)
        self.X1d_01.configure(text="""x_1:""")
        self.X1d_01.configure(font = self.Allfont)
        self.X1d_01input = tk.Entry(self.frame)
        self.X1d_01input.place(x=1280, y=240, height=20, width=40)
        self.X1d_01input.insert(-1,0.04)
        self.X1d_01input.configure(font = self.Allfont)

        self.X1d_00 = tk.Label(self.frame)   # for distance
        self.X1d_00.place(x=1250, y=265, height=20, width=25)
        self.X1d_00.configure(text="""x_0:""")
        self.X1d_00.configure(font = self.Allfont)
        self.X1d_00input = tk.Entry(self.frame)
        self.X1d_00input.place(x=1280, y=265, height=20, width=40)
        self.X1d_00input.insert(-1, -6.09)
        self.X1d_00input.configure(font = self.Allfont)

        self.Y1d_01 = tk.Label(self.frame)   # for distance
        self.Y1d_01.place(x=1330, y=240, height=20, width=25)
        self.Y1d_01.configure(text="""y_1:""")
        self.Y1d_01.configure(font = self.Allfont)
        self.Y1d_01input = tk.Entry(self.frame)
        self.Y1d_01input.place(x=1360, y=240, height=20, width=40)
        self.Y1d_01input.insert(-1, 1000)
        self.Y1d_01input.configure(font = self.Allfont)

        self.Y1d_00 = tk.Label(self.frame)   # for distance
        self.Y1d_00.place(x=1330, y=265, height=20, width=25)
        self.Y1d_00.configure(text="""y_0:""")
        self.Y1d_00.configure(font = self.Allfont)
        self.Y1d_00input = tk.Entry(self.frame)
        self.Y1d_00input.place(x=1360, y=265, height=20, width=40)
        self.Y1d_00input.insert(-1, 0)
        self.Y1d_00input.configure(font = self.Allfont)



        ############  Plot histograms settings     #############
        
        ############  Constraint1 start      #############
        self.Constraint1 = tk.Frame(self.Framesort)
        self.Constraint1.place(x=5, y=40, height=130, width=250)
        self.Constraint1.configure(relief="groove")
        self.Constraint1.configure(borderwidth="2")

        self.Constraint1Label = tk.Label(self.Constraint1)
        self.Constraint1Label.place(x=90, y=0, height=25, width=65)
        self.Constraint1Label.configure(text="""constraint 1""")
        self.Constraint1Label.configure(font = self.Allfont)

        self.X_highlimit = tk.Label(self.Constraint1)   # for distance
        self.X_highlimit.place(x=2, y=30, height=25, width=65)
        self.X_highlimit.configure(text="""x_highlimit:""")
        self.X_highlimit.configure(font = self.Allfont)
        self.X_highlimitinput = tk.Entry(self.Constraint1)
        self.X_highlimitinput.place(x=70, y=30, height=25, width=40)
        self.X_highlimitinput.insert(-1, 0.5)
        self.X_highlimitinput.configure(font = self.Allfont)

        self.X_lowlimit = tk.Label(self.Constraint1)
        self.X_lowlimit.place(x=2, y=65, height=25, width=60)
        self.X_lowlimit.configure(text="""x_lowlimit:""")
        self.X_lowlimit.configure(font = self.Allfont)
        self.X_lowlimitinput = tk.Entry(self.Constraint1)
        self.X_lowlimitinput.place(x=70, y=65, height=25, width=40)
        self.X_lowlimitinput.insert(-1, 0.01)
        self.X_lowlimitinput.configure(font = self.Allfont)

        self.Y_highlimit = tk.Label(self.Constraint1)   # for distance
        self.Y_highlimit.place(x=115, y=30, height=25, width=65)
        self.Y_highlimit.configure(text="""y_highlimit:""")
        self.Y_highlimit.configure(font = self.Allfont)
        self.Y_highlimitinput = tk.Entry(self.Constraint1)
        self.Y_highlimitinput.place(x=182, y=30, height=25, width=55)
        self.Y_highlimitinput.insert(-1, -3)
        self.Y_highlimitinput.configure(font = self.Allfont)

        self.Y_lowlimit = tk.Label(self.Constraint1)
        self.Y_lowlimit.place(x=115, y=65, height=25, width=60)
        self.Y_lowlimit.configure(text="""y_lowlimit:""")
        self.Y_lowlimit.configure(font = self.Allfont)
        self.Y_lowlimitinput = tk.Entry(self.Constraint1)
        self.Y_lowlimitinput.place(x=182, y=65, height=25, width=55)
        self.Y_lowlimitinput.insert(-1, -4)
        self.Y_lowlimitinput.configure(font = self.Allfont)

        self.Binconstraint1 = tk.Label(self.Constraint1)
        self.Binconstraint1.place(x=2, y=95, height=25, width=60)
        self.Binconstraint1.configure(text="""box_bin:""")
        self.Binconstraint1.configure(font = self.Allfont)
        self.Binc1input = tk.Entry(self.Constraint1)
        self.Binc1input.place(x=70, y=95, height=25, width=40)
        self.Binc1input.insert(-1, 50)
        self.Binc1input.configure(font = self.Allfont)

        self.Minstepcount = tk.Label(self.Constraint1)
        self.Minstepcount.place(x=115, y=95, height=25, width=63)
        self.Minstepcount.configure(text="""min_count:""")
        self.Minstepcount.configure(font = self.Allfont)
        self.Minstepcountinput = tk.Entry(self.Constraint1)
        self.Minstepcountinput.place(x=182, y=95, height=25, width=55)
        self.Minstepcountinput.insert(-1, 2)
        self.Minstepcountinput.configure(font = self.Allfont)

        ############  Constraint1  end      #############

        ############  Constraint2  start      #############
        self.Constraint2 = tk.Frame(self.Framesort)
        self.Constraint2.place(x=270, y=40, height=130, width=250)
        self.Constraint2.configure(relief="groove")
        self.Constraint2.configure(borderwidth="2")

        self.Constraint2Label = tk.Label(self.Constraint2)
        self.Constraint2Label.place(x=90, y=0, height=25, width=69)
        self.Constraint2Label.configure(text="""constraint 2""")
        self.Constraint2Label.configure(font = self.Allfont)

        self.X_highlimit2 = tk.Label(self.Constraint2)   # for distance
        self.X_highlimit2.place(x=2, y=30, height=25, width=65)
        self.X_highlimit2.configure(text="""x_highlimit:""")
        self.X_highlimit2.configure(font = self.Allfont)
        self.X_highlimitinput2 = tk.Entry(self.Constraint2)
        self.X_highlimitinput2.place(x=70, y=30, height=25, width=40)
        self.X_highlimitinput2.insert(-1, 1)
        self.X_highlimitinput2.configure(font = self.Allfont)

        self.X_lowlimit2 = tk.Label(self.Constraint2)
        self.X_lowlimit2.place(x=2, y=65, height=25, width=60)
        self.X_lowlimit2.configure(text="""x_lowlimit:""")
        self.X_lowlimit2.configure(font = self.Allfont)
        self.X_lowlimitinput2 = tk.Entry(self.Constraint2)
        self.X_lowlimitinput2.place(x=70, y=65, height=25, width=40)
        self.X_lowlimitinput2.insert(-1, -0.5)
        self.X_lowlimitinput2.configure(font = self.Allfont)

        self.Y_highlimit2 = tk.Label(self.Constraint2)   # for distance
        self.Y_highlimit2.place(x=115, y=30, height=25, width=65)
        self.Y_highlimit2.configure(text="""y_highlimit:""")
        self.Y_highlimit2.configure(font = self.Allfont)
        self.Y_highlimitinput2 = tk.Entry(self.Constraint2)
        self.Y_highlimitinput2.place(x=183, y=30, height=25, width=55)
        self.Y_highlimitinput2.insert(-1, -1)
        self.Y_highlimitinput2.configure(font = self.Allfont)

        self.Y_lowlimit2 = tk.Label(self.Constraint2)
        self.Y_lowlimit2.place(x=115, y=65, height=25, width=60)
        self.Y_lowlimit2.configure(text="""y_lowlimit:""")
        self.Y_lowlimit2.configure(font = self.Allfont)
        self.Y_lowlimitinput2 = tk.Entry(self.Constraint2)
        self.Y_lowlimitinput2.place(x=183, y=65, height=25, width=55)
        self.Y_lowlimitinput2.insert(-1, -2)
        self.Y_lowlimitinput2.configure(font = self.Allfont)

        ############  Constraint2 end       #############

        ############  Hists plot frame       #############

        self.Histfram = tk.Frame(self.frame)
        self.Histfram.place(x=770, y=290, height=520, width=780)
        self.Histfram.configure(relief="groove")
        self.Histfram.configure(borderwidth="2")

        self.fig2d, self.ax2d = plt.subplots(figsize=(3.8, 5))
        self.fig2d.subplots_adjust(top=0.94, bottom=0.1, left=0.16, right=0.97)
        self.figure_canvas2d = FigureCanvasTkAgg(self.fig2d, master=self.Histfram)

        self.toolbar2d = NavigationToolbar2Tk(self.figure_canvas2d, self.Histfram)
        self.toolbar2d.update()

        self.toolbar2d.place(x=0, y=0)  # (row=0, column=0, rowspan=5)

        #self.ax2d.set_title("hist2d")
        self.ax2d.set_ylabel("conductance")
        self.ax2d.set_xlabel("distance")
        self.figure_canvas2d.get_tk_widget().place(
            x=1, y=12
        )  # padx=5, pady=20, side=tk.LEFT

        self.fig1dh, self.ax1dh = plt.subplots(figsize=(3.9, 5))
        self.fig1dh.subplots_adjust(top=0.94, bottom=0.1, left=0.16, right=0.97)
        self.figure_canvas1dh = FigureCanvasTkAgg(self.fig1dh, master=self.Histfram)

        self.toolbar1dh = NavigationToolbar2Tk(self.figure_canvas1dh, self.Histfram)
        self.toolbar1dh.update()

        self.toolbar1dh.place(x=385, y=0)  # (row=0, column=0, rowspan=5)

        #self.ax2d.set_title("hist2d")
        self.ax1dh.set_ylabel("counts")
        self.ax1dh.set_xlabel("conductance")
        self.figure_canvas1dh.get_tk_widget().place(
            x=385, y=12
        )  # padx=5, pady=20, side=tk.LEFT


        ############  Hists plot frame       #############

        ############# bin hist   ########################

        self.Binhistlabel = tk.Label(self.frame)   # for distance
        self.Binhistlabel.place(x=620, y=900, height=25, width=120)
        self.Binhistlabel.configure(text="""constraint1 hist""")
        self.Binhistlabel.configure(background="#d9d9d9")
        self.Binhistlabel.configure(font = self.Allfont)

        self.Binhist = tk.Frame(self.frame)
        self.Binhist.place(x=770, y=810, height=220, width=780)
        self.Binhist.configure(relief="groove")
        self.Binhist.configure(borderwidth="2")

        self.figbin2d, self.axbin2d = plt.subplots(figsize=(3.7, 2.1))
        self.figbin2d.subplots_adjust(top=0.94, bottom=0.1, left=0.16, right=0.97)
        self.figure_canvasbin2d = FigureCanvasTkAgg(self.figbin2d, master=self.Binhist)

        #self.toolbarbin2d = NavigationToolbar2Tk(self.figure_canvasbin2d, self.Binhist)
        #self.toolbarbin2d.update()

        #self.toolbarbin2d.place(x=0, y=0)  # (row=0, column=0, rowspan=5)

        #self.ax2d.set_title("hist2d")
        #self.axbin2d.set_ylabel("conductance")
        #self.axbin2d.set_xlabel("distance")
        self.figure_canvasbin2d.get_tk_widget().place(
            x=1, y=0
        )  # padx=5, pady=20, side=tk.LEFT

        self.figbin1dh, self.axbin1dh = plt.subplots(figsize=(3.7, 2.1))
        self.figbin1dh.subplots_adjust(top=0.94, bottom=0.1, left=0.16, right=0.97)
        self.figure_canvasbin1dh = FigureCanvasTkAgg(self.figbin1dh, master=self.Binhist)

        #self.toolbarbin1dh = NavigationToolbar2Tk(self.figure_canvasbin1dh, self.Binhist)
        #self.toolbarbin1dh.update()

        #self.toolbarbin1dh.place(x=385, y=0)  # (row=0, column=0, rowspan=5)

        #self.ax2d.set_title("hist2d")
        #self.ax1dh.set_ylabel("counts")
        #self.ax1dh.set_xlabel("conductance")
        self.figure_canvasbin1dh.get_tk_widget().place(
            x=385, y=0)





        ################### bin hist ##################


        ############  Single trace plot       #############

        self.fig, self.ax = plt.subplots(figsize=(4.5, 6.1))
        self.fig.subplots_adjust(top=0.94, bottom=0.1, left=0.16, right=0.96)
        self.figure_canvas = FigureCanvasTkAgg(self.fig, master=self.Framefig)

        self.toolbar = NavigationToolbar2Tk(self.figure_canvas, self.Framefig)
        self.toolbar.update()

        self.toolbar.place(x=10, y=10)  # (row=0, column=0, rowspan=5)

        # self.ax.set_title("single trace")
        self.ax.set_ylabel("conductance")
        self.ax.set_xlabel("time")
        self.figure_canvas.get_tk_widget().place(
            x=30, y=30
        )  # padx=5, pady=20, side=tk.LEFT

    

        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    ### select and load a file directory
    def select_file(self):
        # self.dirname =fd.askdirectory()
        self.dirlo.delete(0, "end")
        self.totnum.delete(0, "end")
        dirname = fd.askdirectory(title="select a directory")
        fulllen = dirname + "/*.acq"
        datanum = sorted(gb.glob(fulllen))
        lennum = len(datanum)
        self.dirlo.insert(END, dirname)
        self.totnum.insert(END, lennum)

    ### function for converting string input to a real function
    def volagetocurrent(self, t):
        x = t
        strfunc = eval(self.func1.get())
        return strfunc

    # def reffunc(self,x):
    #    return 2*x

    def updateplot(self):
        self.dirlabl.delete(0, "end")
        self.ax.clear()
        self.ax1dh.clear()
        self.ax2d.clear()
        dirname = self.dirlo.get()
        datacut1 = int(self.Datacut1input.get())
        acqfull = dirname + "/*.acq"
        dataall = sorted(gb.glob(acqfull))
        getnum = int(self.inputnum.get())
        self.dirlabl.insert(END, os.path.basename(dataall[getnum]))
        binary = open(dataall[getnum], "rb").read()
        number_of_points = struct.unpack("@I", binary[0:4])[0]
        datafile = struct.unpack(
            "@" + "d" * number_of_points, binary[4 : 4 + number_of_points * 8]
        )
        time_interval = struct.unpack("@d", binary[4 + number_of_points * 8 + 16 :])[0]
        df = pd.DataFrame(
            {
                "time": [time_interval * i for i in range(number_of_points)],
                "current": datafile,
            }
        )
        datay = abs(df["current"])[datacut1:]
        datax = abs(df["time"])[datacut1:]
        ### full dadta fie
        # print('total data number is:  ', len(dataall))
        if self.che50.get(): ### conductance
            piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
            vbias = float(self.Biasinput.get())  ## V
            ramprate = float(self.Ramprateinput.get())  ## V/s
            gnaught = 7.748091729 * 10 ** (
                -5
            )  # simens in unit  2e**2/h, quantum conductance  I/V
            gfactor = 1 / (vbias * gnaught)
            pomin = np.where(datay == min(datay[: len(datay) - 1]))[0][0]-1
            datay01 = datay[:pomin]
            logcurrent = np.log10(self.volagetocurrent(datay01) * gfactor)

            dis = datax * ramprate * piezosensitivity
            
            if self.che52.get():
                self.ax.plot(dis[:pomin], logcurrent)
                if self.che53.get():
                    y1get=eval(self.Y1input.get())
                    y2get=eval(self.Y2input.get())
                    self.ax.plot(dis[:pomin], np.full(len(dis[:pomin]),y1get),linestyle="--")
                    self.ax.plot(dis[:pomin], np.full(len(dis[:pomin]),y2get),linestyle="--")
                # self.ax.plot(
                #    dis[:pomin], np.ones(len(dis[:pomin])), linestyle="--"
                # )  ##axhline(0.5, linestyle='--')

                self.ax.set_xlabel("distance (nm)")
            else:
                self.ax.plot(datax[:pomin], logcurrent)
                if self.che53.get():
                    y1get=eval(self.Y1input.get())
                    y2get=eval(self.Y2input.get())
                    self.ax.plot(datax[:pomin], np.full(len(datax[:pomin]),y1get),linestyle="--")
                    self.ax.plot(datax[:pomin], np.full(len(datax[:pomin]),y2get),linestyle="--")
                self.ax.set_xlabel("time (s)")
            self.ax.set_ylabel("log (G/G0)")
        else:
            if self.che52.get():
                piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
                ramprate = float(self.Ramprateinput.get())  ## V/s
                dis = datax * ramprate * piezosensitivity
                self.ax.plot(dis, datay)
                if self.che53.get():
                    y1get=eval(self.Y1input.get())
                    y2get=eval(self.Y2input.get())
                    self.ax.plot(dis, np.full(len(dis),y1get),linestyle="--")
                    self.ax.plot(dis, np.full(len(dis),y2get),linestyle="--")
                self.ax.set_xlabel("distance (nm)")
            else:
                self.ax.plot(datax, datay)
                if self.che53.get():
                    y1get=eval(self.Y1input.get())
                    y2get=eval(self.Y2input.get())
                    self.ax.plot(datax, np.full(len(datax),y1get),linestyle="--")
                    self.ax.plot(datax, np.full(len(datax),y2get),linestyle="--")
                self.ax.set_xlabel("time (s)")
            self.ax.set_ylabel("output voltage (V)")

        self.figure_canvas.draw()

        #self.dirlabl.insert(END, os.path.basename(dataall[getnum]))
        
    #def on_button_click(self):
    #   threading.Thread(target=self.updateplot).start() 
    
    def hist1dupdateplot(self):
        self.ax1dh.clear()

        dirname3 = self.dirlo.get()
        datacut3 = int(self.Datacut1input.get())
        acqfull3 = dirname3 + "/*.acq"
        dataall3 = sorted(gb.glob(acqfull3))
        getnum3 = int(self.inputnum.get())
        binary = open(dataall3[getnum3], "rb").read()
        number_of_points = struct.unpack("@I", binary[0:4])[0]
        datafile = struct.unpack(
            "@" + "d" * number_of_points, binary[4 : 4 + number_of_points * 8]
        )
        time_interval = struct.unpack("@d", binary[4 + number_of_points * 8 + 16 :])[0]
        df = pd.DataFrame(
            {
                "time": [time_interval * i for i in range(number_of_points)],
                "current": datafile,
            }
        )
        datay3 = abs(df["current"])[datacut3:]
        #datax3 = abs(df["time"])[datacut3:]

        y_low1=eval(self.G0lowinput.get())
        y_high1=eval(self.G0highinput.get())
        y_bin1=int(self.Y_bininput.get())

        vbias = float(self.Biasinput.get())  ## V
        
        gnaught = 7.748091729 * 10 ** (-5)  # simens in unit  2e**2/h, quantum conductance  I/V
        gfactor = 1 / (vbias * gnaught)
        pomin = np.where(datay3 == min(datay3[: len(datay3) - 1]))[0][0]-1
        datay31 = datay3[:pomin]
        logcurrent = np.log10(self.volagetocurrent(datay31) * gfactor)
        #pomin = np.where(logcurrent == min(logcurrent[: len(logcurrent) - 1]))[0][0]
        #binspace = np.logspace(np.log10(y_low1),np.log10(y_high1),y_bin1)
        binspace = np.linspace(y_low1,y_high1,y_bin1)
        hist1y = np.histogram(logcurrent, bins=binspace, density=False)[0]
        histx = binspace[1:] - (binspace[1] - binspace[0])/2
        
        x1d00 = eval(self.X1d_00input.get())
        x1d01 = float(self.X1d_01input.get())
        y1d00 = float(self.Y1d_00input.get())
        y1d01 = float(self.Y1d_01input.get())
       

        self.ax1dh.plot(histx, hist1y) ###  need more precision
        self.ax1dh.set_xlabel('Conductance ($G/G_0$)')
        self.ax1dh.set_ylabel('Counts (arb. units)')
      
        self.ax1dh.set_ylim(y1d00,y1d01)
        self.ax1dh.set_xlim(x1d00,x1d01)
        #plt.rc('font', size=20)          # controls default text sizes
        #plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
        #self.ax2d.rc('ytick', labelsize=20) 
        ###frame and ticks 
        self.ax1dh.spines['top'].set_linewidth(1)
        self.ax1dh.spines['right'].set_linewidth(1)
        self.ax1dh.spines['bottom'].set_linewidth(1)
        self.ax1dh.spines['left'].set_linewidth(1)
        self.ax1dh.xaxis.set_tick_params(width=1)
        self.ax1dh.yaxis.set_tick_params(which='both',width=1)
        self.ax1dh.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        #self.fig1dh.savefig('h1d.jpg',dpi=600)
        self.figure_canvas1dh.draw()

    #### hist2d plot
    def hist2dupdateplot(self):
        self.ax2d.clear()
        self.ax1dh.clear()
        dirname3 = self.dirlo.get()
        datacut3 = int(self.Datacut1input.get())
        acqfull3 = dirname3 + "/*.acq"
        dataall3 = sorted(gb.glob(acqfull3))
        getnum3 = int(self.inputnum.get())
        binary = open(dataall3[getnum3], "rb").read()
        number_of_points = struct.unpack("@I", binary[0:4])[0]
        datafile = struct.unpack(
            "@" + "d" * number_of_points, binary[4 : 4 + number_of_points * 8]
        )
        time_interval = struct.unpack("@d", binary[4 + number_of_points * 8 + 16 :])[0]
        df = pd.DataFrame(
            {
                "time": [time_interval * i for i in range(number_of_points)],
                "current": datafile,
            }
        )
        datay4 = abs(df["current"])
        
        x_low1=float(self.Dislowinput.get())
        x_high1=float(self.Dishighinput.get())
        y_low1=eval(self.G0lowinput.get())
        y_high1=eval(self.G0highinput.get())
        x_zero=float(self.X_zeroinput.get())
        x_bin1=int(float(self.X_bininput.get()))
        y_bin1=int(float(self.Y_bininput.get()))
        
        vbias = float(self.Biasinput.get())  ## V
        gnaught = 7.748091729 * 10 ** (-5)  # simens in unit  2e**2/h, quantum conductance  I/V
        gfactor = 1 / (vbias * gnaught)
        piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
        ramprate = float(self.Ramprateinput.get())  ## V/s 
        pomin = np.where(datay4 == min(datay4[: len(datay4) - 1]))[0][0]-1
        datay41 = datay4[datacut3:pomin]
        datay3 = np.log10(self.volagetocurrent(datay41) * gfactor) 
        datax3 = abs(df["time"])[datacut3:pomin]
        #binspace = np.logspace(np.log10(y_low1),np.log10(y_high1),y_bin1)
        binx = np.linspace(x_low1,x_high1,x_bin1)
        biny = np.linspace(y_low1,y_high1,y_bin1)
        x00 = float(self.X_00input.get())
        x01 = float(self.X_01input.get())
        y00 = eval(self.Y_00input.get())
        y01 = float(self.Y_01input.get())
        z00 = float(self.Z_00input.get())
        z01 = float(self.Z_01input.get())
      
        if datay4[1]>datay4[len(datay4)-1]: ### simple filtering data    
            postot=np.where(datay3>=x_zero)[0]
            if len(postot)<=1:
                pos = 0
            else:
                pos = max(postot)
            dis = datax3*ramprate*piezosensitivity
            dis1 = dis-dis[pos+datacut3]
            h2d = np.histogram2d(dis1, datay3, bins=(binx, biny), density=False)
            h2d2=h2d[0].T
       
        X, Y = np.meshgrid(binx, biny)
        self.ax2d.pcolormesh(X, Y, h2d2,cmap=self.Color2d.get(),vmin = z00, vmax =z01)  #,vmin = 0, vmax = 10
        self.ax2d.set_xlabel('distance (nm)')
        self.ax2d.set_ylabel('log ($G/G_0$)')
        self.ax2d.set_ylim(y00,y01)
        self.ax2d.set_xlim(x00,x01)
        #plt.rc('font', size=20)          # controls default text sizes
        #plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
        #self.ax2d.rc('ytick', labelsize=20) 
        ###frame and ticks 
        self.ax2d.spines['top'].set_linewidth(1)
        self.ax2d.spines['right'].set_linewidth(1)
        self.ax2d.spines['bottom'].set_linewidth(1)
        self.ax2d.spines['left'].set_linewidth(1)
        self.ax2d.xaxis.set_tick_params(width=1)
        self.ax2d.yaxis.set_tick_params(which='both',width=1)
        #self.fig2d.savefig('h2d.jpg',dpi=600)
        #self.fig2d.savefig('h2d.jpg',dpi=600)
        self.figure_canvas2d.draw()

        ### 1d hist plot
     
        #datax3 = abs(df["time"])[datacut3:]

        #hist1y = np.histogram(datay3, bins=biny, density=False)[0]
        hist1y = h2d2.sum(axis=1)
        histx = biny[1:] - (biny[1] - biny[0])/2
        
        x1d00 = eval(self.X1d_00input.get())
        x1d01 = float(self.X1d_01input.get())
        y1d00 = float(self.Y1d_00input.get())
        y1d01 = float(self.Y1d_01input.get())
       

        self.ax1dh.plot(histx, hist1y) ###  need more precision
        self.ax1dh.set_xlabel('log ($G/G_0$)')
        self.ax1dh.set_ylabel('counts (arb. units)')
      
        self.ax1dh.set_ylim(y1d00,y1d01)
        self.ax1dh.set_xlim(x1d00,x1d01)
        #plt.rc('font', size=20)          # controls default text sizes
        #plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
        #self.ax2d.rc('ytick', labelsize=20) 
        ###frame and ticks 
        self.ax1dh.spines['top'].set_linewidth(1)
        self.ax1dh.spines['right'].set_linewidth(1)
        self.ax1dh.spines['bottom'].set_linewidth(1)
        self.ax1dh.spines['left'].set_linewidth(1)
        self.ax1dh.xaxis.set_tick_params(width=1)
        self.ax1dh.yaxis.set_tick_params(which='both',width=1)
        self.ax1dh.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        #self.fig1dh.savefig('h1d.jpg',dpi=600)
        self.figure_canvas1dh.draw()

    def binhistplot(self):
        self.axbin2d.clear()
        self.axbin1dh.clear()
        dirname3 = self.dirlo.get()
        datacut3 = int(self.Datacut1input.get())
        acqfull3 = dirname3 + "/*.acq"
        dataall3 = sorted(gb.glob(acqfull3))
        getnum3 = int(self.inputnum.get())
        binary = open(dataall3[getnum3], "rb").read()
        number_of_points = struct.unpack("@I", binary[0:4])[0]
        datafile = struct.unpack(
            "@" + "d" * number_of_points, binary[4 : 4 + number_of_points * 8]
        )
        time_interval = struct.unpack("@d", binary[4 + number_of_points * 8 + 16 :])[0]
        df = pd.DataFrame(
            {
                "time": [time_interval * i for i in range(number_of_points)],
                "current": datafile,
            }
        )
        datay4 = abs(df["current"])

        x_lowlimit1=float(self.X_lowlimitinput.get())
        x_highlimit1=float(self.X_highlimitinput.get())
        y_lowlimit1=float(self.Y_lowlimitinput.get())
        y_highlimit1=float(self.Y_highlimitinput.get())
        bin_c1=int(float(self.Binc1input.get()))
        x_zero=float(self.X_zeroinput.get())
        
        vbias = float(self.Biasinput.get())  ## V
        gnaught = 7.748091729 * 10 ** (-5)  # simens in unit  2e**2/h, quantum conductance  I/V
        gfactor = 1 / (vbias * gnaught)
        piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
        ramprate = float(self.Ramprateinput.get())  ## V/s 
        pomin = np.where(datay4 == min(datay4[: len(datay4) - 1]))[0][0]-1
        datay41 = datay4[datacut3:pomin]
        datay3 = np.log10(self.volagetocurrent(datay41) * gfactor) 
        datax3 = abs(df["time"])[datacut3:pomin]
        #binspace = np.logspace(np.log10(y_low1),np.log10(y_high1),y_bin1)
        binx = np.linspace(x_lowlimit1,x_highlimit1,bin_c1)
        biny = np.linspace(y_lowlimit1,y_highlimit1,bin_c1)
       
        if datay4[1]>datay4[len(datay4)-1]: ### simple filtering data    
            postot=np.where(datay3>=x_zero)[0]
            if len(postot)<=1:
                pos = 0
            else:
                pos = max(postot)
            dis = datax3*ramprate*piezosensitivity
            dis1 = dis-dis[pos+datacut3]
            h2d = np.histogram2d(dis1, datay3, bins=(binx, biny), density=False)
            h2d2=h2d[0].T
       
        X, Y = np.meshgrid(binx, biny)
        self.axbin2d.pcolormesh(X, Y, h2d2)  #,vmin = 0, vmax = 10
        #self.axbin2d.set_xlabel('distance (nm)')
        #self.ax2d.set_ylabel('log ($G/G_0$)')
        #self.ax2d.set_ylim(y00,y01)
        #self.ax2d.set_xlim(x00,x01)
        #plt.rc('font', size=20)          # controls default text sizes
        #plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
        #self.ax2d.rc('ytick', labelsize=20) 
        ###frame and ticks 
        #self.ax2d.spines['top'].set_linewidth(1)
        #self.ax2d.spines['right'].set_linewidth(1)
        #self.ax2d.spines['bottom'].set_linewidth(1)
        #self.ax2d.spines['left'].set_linewidth(1)
        #self.ax2d.xaxis.set_tick_params(width=1)
        #self.ax2d.yaxis.set_tick_params(which='both',width=1)
        #self.fig2d.savefig('h2d.jpg',dpi=600)
        #self.fig2d.savefig('h2d.jpg',dpi=600)
        self.figure_canvasbin2d.draw()

        ### 1d hist plot
     
        #datax3 = abs(df["time"])[datacut3:]

        #hist1y = np.histogram(datay3, bins=biny, density=False)[0]
        hist1y = h2d2.sum(axis=1)
        histx = biny[1:] - (biny[1] - biny[0])/2
        

        self.axbin1dh.plot(histx, hist1y) ###  need more precision
        #self.ax1dh.set_xlabel('log ($G/G_0$)')
        #self.ax1dh.set_ylabel('counts (arb. units)')
      
        #self.ax1dh.set_ylim(y1d00,y1d01)
        #self.ax1dh.set_xlim(x1d00,x1d01)
        #plt.rc('font', size=20)          # controls default text sizes
        #plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
        #self.ax2d.rc('ytick', labelsize=20) 
        ###frame and ticks 
        #self.ax1dh.spines['top'].set_linewidth(1)
        #self.ax1dh.spines['right'].set_linewidth(1)
        #self.ax1dh.spines['bottom'].set_linewidth(1)
        #self.ax1dh.spines['left'].set_linewidth(1)
        #self.ax1dh.xaxis.set_tick_params(width=1)
        #self.ax1dh.yaxis.set_tick_params(which='both',width=1)
        #self.ax1dh.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        #self.fig1dh.savefig('h1d.jpg',dpi=600)
        self.figure_canvasbin1dh.draw()



        

    def allhistplot(self):
        if self.che51.get():
            self.hist2dupdateplot()
            #self.hist2dupdateplot
        if self.che54.get():
            self.binhistplot()
        

    def mutiplot(self):
        mutidatanum = self.Multidatainput.get()
        datacut1 = int(self.Datacut1input.get())
        mutidatanum_list = [int(i) for i in mutidatanum.split()]
        #self.dirlabl.delete(0, "end")
        self.ax.clear()
        dirname = self.dirlo.get()
        acqfull = dirname + "/*.acq"
        dataall = sorted(gb.glob(acqfull))
        for tracenum in mutidatanum_list:
            binary = open(dataall[tracenum], "rb").read()
            number_of_points = struct.unpack("@I", binary[0:4])[0]
            datafile = struct.unpack(
                "@" + "d" * number_of_points, binary[4 : 4 + number_of_points * 8]
            )
            time_interval = struct.unpack(
                "@d", binary[4 + number_of_points * 8 + 16 :]
            )[0]
            df = pd.DataFrame(
                {
                    "time": [time_interval * i for i in range(number_of_points)],
                    "current": datafile,
                }
            )
            datay = abs(df["current"])[datacut1:]
            datax = abs(df["time"])[datacut1:]
            if self.che50.get():
                piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
                vbias = float(self.Biasinput.get())  ## V
                ramprate = float(self.Ramprateinput.get())  ## V/s
                gnaught = 7.748091729 * 10 ** (
                    -5
                )  # simens in unit  2e**2/h, quantum conductance  I/V
                gfactor = 1 / (vbias * gnaught)
                logcurrent = np.log10(self.volagetocurrent(datay) * gfactor)
                pomin = np.where(logcurrent == min(logcurrent[: len(logcurrent) - 1]))[
                    0
                ][0]
                dis = datax * ramprate * piezosensitivity
                
                if self.che52.get():
                    self.ax.plot(dis[:pomin], logcurrent[:pomin])
                    # self.ax.plot(
                    #    dis[:pomin], np.ones(len(dis[:pomin])), linestyle="--"
                    # )  ##axhline(0.5, linestyle='--')

                    self.ax.set_xlabel("distance (nm)")
                else:
                    self.ax.plot(datax[:pomin], logcurrent[:pomin])
                    self.ax.set_xlabel("time (s)")
                self.ax.set_ylabel(" log(G/G0)")
            else:
                if self.che52.get():
                    piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
                    ramprate = float(self.Ramprateinput.get())  ## V/s
                    dis = datax * ramprate * piezosensitivity
                    self.ax.plot(dis, datay)
                    self.ax.set_xlabel("distance (nm)")
                else:
                    self.ax.plot(datax, datay)
                    self.ax.set_xlabel("time (s)")
                self.ax.set_ylabel("output voltage (V)")
            '''
            if self.che51.get():
                self.ax.set_yscale("log")
            else:
                self.ax.set_yscale("linear")
            '''
        self.figure_canvas.draw()
    




    def next(self):
        dirname1 = self.dirlo.get()
        acqfull1 = dirname1 + "/*.acq"
        dataall1 = sorted(gb.glob(acqfull1))
        getnum1 = int(self.inputnum.get())
        if getnum1 <= len(dataall1) - 2:
            getnum1 = getnum1 + 1
        else:
            getnum1 = getnum1

        self.inputnum.delete(0, "end")
        self.inputnum.insert(END, getnum1)

    def back(self):
        getnum2 = int(self.inputnum.get())
        if getnum2 >= 1:
            getnum2 = getnum2 - 1
        else:
            getnum2 = getnum2

        self.inputnum.delete(0, "end")
        self.inputnum.insert(END, getnum2)

    def savecurrentdata(self):
        new_folder_name = "outputdata"
        direget1 = self.dirlo.get()
        os.chdir(direget1)
        acqfull1 = direget1 + "/*.acq"
        dataall1 = sorted(gb.glob(acqfull1))
        getnum1 = int(self.inputnum.get())
        binary1 = open(dataall1[getnum1], "rb").read()
        number_of_points1 = struct.unpack("@I", binary1[0:4])[0]
        datafile1 = struct.unpack(
            "@" + "d" * number_of_points1, binary1[4 : 4 + number_of_points1 * 8]
        )
        time_interval1 = struct.unpack("@d", binary1[4 + number_of_points1 * 8 + 16 :])[
            0
        ]
        df1 = pd.DataFrame(
            {
                "time": [time_interval1 * i for i in range(number_of_points1)],
                "current": datafile1,
            }
        )
        datay1 = abs(df1["current"])
        datax1 = abs(df1["time"])  #### get raw data with abs values
        totdata = np.column_stack((datax1, datay1))

        piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
        vbias = float(self.Biasinput.get())  ## V
        ramprate = float(self.Ramprateinput.get())  ## V/s
        gnaught = 7.748091729 * 10 ** (
            -5
        )  # simens in unit  2e**2/h, quantum conductance  I/V
        gfactor = 1 / (vbias * gnaught)
        
        pomin1 = np.where(datay1 == min(datay1[: len(datay1) - 1]))[0][0]-1
        datay11 = datay1[:pomin1]

        logcurrent1 = np.log10(self.volagetocurrent(datay11) * gfactor)

        dis1 = datax1 * ramprate * piezosensitivity
        totdata2 = np.column_stack((dis1[:pomin1], logcurrent1))

        currentdire = os.getcwd()
        new_folder_path = os.path.join(currentdire, new_folder_name)
        if not os.path.exists(new_folder_path):
            os.mkdir("outputdata")
            print(f"Folder '{new_folder_name}' created successfully.")
        else:
            print(f"Folder '{new_folder_name}' already exists.")

        os.chdir("outputdata")
        filename1 = self.dirlabl.get()
        file_name_without_extension = os.path.splitext(filename1)[0]
        file_new_name = file_name_without_extension + ".txt"
        file_new_name_2 = file_name_without_extension + "_G" + ".txt"
        np.savetxt(file_new_name, totdata, delimiter=" ")
        np.savetxt(file_new_name_2, totdata2, delimiter=" ")
        print("file saved successfully")
    
    ### starting from here is the data sorting function
    def radiobuttonselection(self):
        if self.selected_function.get() == 1:
            self.Dislowinput.delete(0, "end")
            self.Dishighinput.delete(0, "end")
            self.G0lowinput.delete(0, "end")
            self.G0highinput.delete(0, "end")

            self.Dislowinput.insert(-1, -0.5)
            self.Dishighinput.insert(-1, 4)
            self.G0lowinput.insert(-1, -6.09)
            self.G0highinput.insert(-1, 0.04)
        elif self.selected_function.get() ==2:
            self.G0lowinput.delete(0, "end")
            self.G0highinput.delete(0, "end")
            self.G0lowinput.insert(-1, -6.4)
            self.G0highinput.insert(-1, -1.8)
    
    def histsortlog(self, diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2):
        direget2 = self.dirlo.get()
        piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
        vbias = float(self.Biasinput.get())  ## V
        ramprate = float(self.Ramprateinput.get())  ## V/s
        gnaught = 7.748091729 * 10 ** (
            -5
        )  # simens in unit  2e**2/h, quantum conductance  I/V
        gfactor = 1 / (vbias * gnaught)
        os.chdir(direget2)
        acqfull2 = direget2 + "/*.acq"
        dataall2 = sorted(gb.glob(acqfull2))
        tracenumber = len(dataall2)
        binx = np.linspace(lowdistance,highdistance,bindistance)
        #biny = np.logspace(np.log10(lowcurrent),np.log10(highcurrent),bincurrent)
        biny = np.linspace(lowcurrent,highcurrent,bincurrent)
        hist2dall = np.zeros((tracenumber, bindistance-1 , bincurrent-1))
        #binytemp = np.logspace(np.log10(lowculimit),np.log10(highculimit),binlimit)
        binytemp = np.linspace(lowculimit,highculimit,binlimit)
        #binytemp2 = np.logspace(np.log10(lowculimit2),np.log10(highculimit2),binlimit)
        binytemp2 = np.linspace(lowculimit2,highculimit2,binlimit)
        i=0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        for filename in dataall2:
            binary = open(filename, "rb").read()
            number_of_points = struct.unpack("@I", binary[0:4])[0]
            datafile = struct.unpack("@"+"d"*number_of_points, binary[4:4+number_of_points*8])
            time_interval = struct.unpack("@d", binary[4 + number_of_points * 8 + 16:])[0]
            df = pd.DataFrame({"time" : [time_interval * i for i in range(number_of_points)], "current" : datafile})
            datay = abs(df['current'])
            #logcu=(1.2*np.exp(8.6982*datay-31.2896)+5.053*10**-12*datay+4.673*10**-12)*gfactor

            pomin=np.where(datay==min(datay[:len(datay)-1]))[0][0]-1
            datay1=np.log10(self.volagetocurrent(datay[cut:pomin])*gfactor)
            datax1=df['time']
            datax1=datax1[cut:pomin]
            if datay[1]>datay[len(datay)-1]: ### simple filtering data   
                postot=np.where(datay1>=diszero)[0]
                if len(postot)<=1:
                    pos = 0
                else:
                    pos = max(postot)
                dis = datax1*ramprate*piezosensitivity
                dis1 = dis-dis[pos+cut]
                h2dtemp2 = np.histogram2d(dis1, datay1, bins=(binx, binytemp2), density=density)
                dissum2 = h2dtemp2[0].sum(axis=1)
                if max(dissum2) == 0:
                    h2dtemp = np.histogram2d(dis1, datay1, bins=(binx, binytemp), density=density)
                elif max(dissum2) > 0:
                    dispo2  = binx[1:][max(np.where(dissum2>0)[0])]
                    if dispo2 > lowdis2 and dispo2 < highdis2:
                        h2dtemp = np.histogram2d(dis1, datay1, bins=(binx, binytemp), density=density)
                    else:
                        continue

                if max(h2dtemp[0].sum(axis=0)) > lowstep:             ####### second condition sorting
                    dissum = h2dtemp[0].sum(axis=1)
                    dispo  = binx[1:][max(np.where(dissum>0)[0])]
                    if dispo > lowdis and dispo < highdis:
                        h2di = np.histogram2d(dis1, datay1, bins=(binx, biny), density=density)
                        if(h2di[0].max() != 0): 
                            hist2dall[i] = h2di[0] / h2di[0].max()   ###normalize
                            i = i+1
            
        hist2dx = binx
        hist2dy = biny ## plot in conductance G/G0
        return hist2dall[0:i], hist2dx, hist2dy, len(dataall2)


    ####### new thread function###################
    def histsortthread(self, dataall2,diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2):
        
        piezosensitivity = float(self.Piezosensitivityinput.get())  ## nm/V
        vbias = float(self.Biasinput.get())  ## V
        ramprate = float(self.Ramprateinput.get())  ## V/s
        gnaught = 7.748091729 * 10 ** (
            -5
        )  # simens in unit  2e**2/h, quantum conductance  I/V
        gfactor = 1 / (vbias * gnaught)
        tracenumber = len(dataall2)
        binx = np.linspace(lowdistance,highdistance,bindistance)
        #biny = np.logspace(np.log10(lowcurrent),np.log10(highcurrent),bincurrent)
        biny = np.linspace(lowcurrent,highcurrent,bincurrent)
        hist2dall = np.zeros((tracenumber, bindistance-1 , bincurrent-1))
        #binytemp = np.logspace(np.log10(lowculimit),np.log10(highculimit),binlimit)
        binytemp = np.linspace(lowculimit,highculimit,binlimit)
        #binytemp2 = np.logspace(np.log10(lowculimit2),np.log10(highculimit2),binlimit)
        binytemp2 = np.linspace(lowculimit2,highculimit2,binlimit)
        i=0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        for filename in dataall2:
            binary = open(filename, "rb").read()
            number_of_points = struct.unpack("@I", binary[0:4])[0]
            datafile = struct.unpack("@"+"d"*number_of_points, binary[4:4+number_of_points*8])
            time_interval = struct.unpack("@d", binary[4 + number_of_points * 8 + 16:])[0]
            df = pd.DataFrame({"time" : [time_interval * i for i in range(number_of_points)], "current" : datafile})
            datay = abs(df['current'])
            #logcu=(1.2*np.exp(8.6982*datay-31.2896)+5.053*10**-12*datay+4.673*10**-12)*gfactor
            

            pomin=np.where(datay==min(datay[:len(datay)-1]))[0][0]-1
            
            datay1=np.log10(self.volagetocurrent(datay[cut:pomin])*gfactor)
            datax1=df['time']
            datax1=datax1[cut:pomin]
            if datay[1]>datay[len(datay)-1]: ### simple filtering data   
                postot=np.where(datay1>=diszero)[0]
                if len(postot)<=1:
                    pos = 0
                else:
                    pos = max(postot)
                dis = datax1*ramprate*piezosensitivity
                dis1 = dis-dis[pos+cut]
                h2dtemp2 = np.histogram2d(dis1, datay1, bins=(binx, binytemp2), density=density)
                dissum2 = h2dtemp2[0].sum(axis=1)
                if max(dissum2) == 0:
                    h2dtemp = np.histogram2d(dis1, datay1, bins=(binx, binytemp), density=density)
                elif max(dissum2) > 0:
                    dispo2  = binx[1:][max(np.where(dissum2>0)[0])]
                    if dispo2 > lowdis2 and dispo2 < highdis2:
                        h2dtemp = np.histogram2d(dis1, datay1, bins=(binx, binytemp), density=density)
                    else:
                        continue

                if max(h2dtemp[0].sum(axis=0)) > lowstep:             ####### second condition sorting
                    dissum = h2dtemp[0].sum(axis=1)
                    dispo  = binx[1:][max(np.where(dissum>0)[0])]
                    if dispo > lowdis and dispo < highdis:
                        h2di = np.histogram2d(dis1, datay1, bins=(binx, biny), density=density)
                        if(h2di[0].max() != 0): 
                            hist2dall[i] = h2di[0] / h2di[0].max()   ###normalize
                            i = i+1
            
        hist2dx = binx
        hist2dy = biny ## plot in conductance G/G0
        return hist2dall[0:i], hist2dx, hist2dy, len(dataall2)
    
    
    def histsortloglinear(self, diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2):
        #direget2 = self.dirlo.get()
        piezosensitivity = 2  ## nm/V
        vbias = 0.1 ## V
        ramprate =100  ## V/s
        gnaught = 7.748091729 * 10 ** (
            -5
        )  # simens in unit  2e**2/h, quantum conductance  I/V
        gfactor = 1 / (vbias * gnaught)
        #os.chdir(direget2)
        #acqfull2 = direget2 + "/*.acq"
        dataall2 = sorted(gb.glob('*.acq'))
        tracenumber = len(dataall2)
        binx = np.linspace(lowdistance,highdistance,bindistance)
        #biny = np.logspace(np.log10(lowcurrent),np.log10(highcurrent),bincurrent)
        biny = np.linspace(lowcurrent,highcurrent,bincurrent)
        hist2dall = np.zeros((tracenumber, bindistance-1 , bincurrent-1))
        #binytemp = np.logspace(np.log10(lowculimit),np.log10(highculimit),binlimit)
        binytemp = np.linspace(lowculimit,highculimit,binlimit)
        #binytemp2 = np.logspace(np.log10(lowculimit2),np.log10(highculimit2),binlimit)
        binytemp2 = np.linspace(lowculimit2,highculimit2,binlimit)
        i=0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        for filename in dataall2:
            binary = open(filename, "rb").read()
            number_of_points = struct.unpack("@I", binary[0:4])[0]
            datafile = struct.unpack("@"+"d"*number_of_points, binary[4:4+number_of_points*8])
            time_interval = struct.unpack("@d", binary[4 + number_of_points * 8 + 16:])[0]
            df = pd.DataFrame({"time" : [time_interval * i for i in range(number_of_points)], "current" : datafile})
            datay = abs(df['current'])
            #logcu=(1.2*np.exp(8.6982*datay-31.2896)+5.053*10**-12*datay+4.673*10**-12)*gfactor

            pomin=np.where(datay==min(datay[:len(datay)-1]))[0][0]-1
            datay1=np.log10(self.volagetocurrent(datay[cut:pomin])*gfactor)
            datax1=df['time']
            datax1=datax1[cut:pomin]
            if datay[1]>datay[len(datay)-1]: ### simple filtering data   
                postot=np.where(datay1>=diszero)[0]
                if len(postot)<=1:
                    pos = 0
                else:
                    pos = max(postot)
                dis = datax1*ramprate*piezosensitivity
                dis1 = dis-dis[pos+cut]
                h2dtemp2 = np.histogram2d(dis1, datay1, bins=(binx, binytemp2), density=density)
                dissum2 = h2dtemp2[0].sum(axis=1)
                if max(dissum2) == 0:
                    h2dtemp = np.histogram2d(dis1, datay1, bins=(binx, binytemp), density=density)
                elif max(dissum2) > 0:
                    dispo2  = binx[1:][max(np.where(dissum2>0)[0])]
                    if dispo2 > lowdis2 and dispo2 < highdis2:
                        h2dtemp = np.histogram2d(dis1, datay1, bins=(binx, binytemp), density=density)
                    else:
                        continue

                if max(h2dtemp[0].sum(axis=0)) > lowstep:             ####### second condition sorting
                    dissum = h2dtemp[0].sum(axis=1)
                    dispo  = binx[1:][max(np.where(dissum>0)[0])]
                    if dispo > lowdis and dispo < highdis:
                        h2di = np.histogram2d(dis1, datay1, bins=(binx, biny), density=density)
                        if(h2di[0].max() != 0): 
                            hist2dall[i] = h2di[0] / h2di[0].max()   ###normalize
                            i = i+1
            
        hist2dx = binx
        hist2dy = biny ## plot in conductance G/G0
        return hist2dall[0:i], hist2dx, hist2dy, len(dataall2)


 
    
    def testfunc(self, x, y):
        return x+y
    
    ##### thread numbers included ################### 
    def threadhist2dsort(self):
        nthread=int(self.ThreadNumberinput.get())

        #if self.selected_function.get() == 1: ## log amp
        x_low1=float(self.Dislowinput.get())
        x_high1=float(self.Dishighinput.get())
        y_low1=float(self.G0lowinput.get())
        y_high1=float(self.G0highinput.get())
        x_zero=float(self.X_zeroinput.get())
        x_bin1=int(float(self.X_bininput.get()))
        y_bin1=int(float(self.Y_bininput.get()))
        cutsort=int(float(self.Cutsortinput.get()))
        
        x_lowlimit1=float(self.X_lowlimitinput.get())
        x_highlimit1=float(self.X_highlimitinput.get())
        y_lowlimit1=float(self.Y_lowlimitinput.get())
        y_highlimit1=float(self.Y_highlimitinput.get())
        bin_c1=int(float(self.Binc1input.get()))
        min_step_count=int(float(self.Minstepcountinput.get()))
        x_lowlimit2=float(self.X_lowlimitinput2.get())
        x_highlimit2=float(self.X_highlimitinput2.get())
        y_lowlimit2=float(self.Y_lowlimitinput2.get())
        y_highlimit2=float(self.Y_highlimitinput2.get())
        


        #direget2 = self.dirlo.get()
        #os.chdir(direget2)
        #acqfull2 = direget2 + "/*.acq"
        #dataall21 = sorted(gb.glob(acqfull2))

        #tracenumber = len(dataall21)

        ####### do not use 2

        if nthread == 2:
            self.MonitorLabel.configure(text="""please input 1""")
            #start_time = time.time()
            #que = queue.Queue() 
            #threads_list = []
            #start = time.time()
            #dataall3 = dataall21[0:(tracenumber//2)+1]
            #dataall4 = dataall21[(tracenumber//2)+1:]
            
            #t10 = threading.Thread(target=lambda q, diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2: q.put(self.histsortlog(diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2)), args=(que,x_zero, y_bin1, x_bin1, y_low1, y_high1, x_low1, x_high1, False, y_lowlimit1, y_highlimit1, y_lowlimit2, y_highlimit2, bin_c1, cutsort, min_step_count, x_lowlimit1, x_highlimit1, x_lowlimit2, x_highlimit2))

            #t10 = threading.Thread(target=lambda q, dataall2,diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2: q.put(self.histsortthread(dataall2,diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2)), args=(que, dataall3,x_zero, y_bin1, x_bin1, y_low1, y_high1, x_low1, x_high1, False, y_lowlimit1, y_highlimit1, y_lowlimit2, y_highlimit2, bin_c1, cutsort, min_step_count, x_lowlimit1, x_highlimit1, x_lowlimit2, x_highlimit2))
            #t20 = threading.Thread(target=lambda q,  dataall2,diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2: q.put(self.histsortthread(dataall2,diszero, bincurrent, bindistance, lowcurrent, highcurrent , lowdistance, highdistance, density, lowculimit, highculimit, lowculimit2, highculimit2, binlimit, cut, lowstep,lowdis, highdis,lowdis2,highdis2)), args=(que, dataall4,x_zero, y_bin1, x_bin1, y_low1, y_high1, x_low1, x_high1, False, y_lowlimit1, y_highlimit1, y_lowlimit2, y_highlimit2, bin_c1, cutsort, min_step_count, x_lowlimit1, x_highlimit1, x_lowlimit2, x_highlimit2))
            #t10.start()
            #t20.start()
            #t10.join()
            #t20.join()
            #result = que.get()
            #try:
               # self.MonitorLabel.configure(text="""running...""")
               # root.update()
               # with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    #future = executor.submit(self.histsortloglinear,300,100,10**-7,1.1,-0.5,4)
                #    future = executor.submit(self.histsortloglinear, x_zero, y_bin1, x_bin1, y_low1, y_high1, x_low1, x_high1, False, y_lowlimit1, y_highlimit1, y_lowlimit2, y_highlimit2, bin_c1, cutsort, min_step_count, x_lowlimit1, x_highlimit1, x_lowlimit2, x_highlimit2)
                    #future = executor.submit(self.histsortlog, x_zero, y_bin1, x_bin1, y_low1, y_high1, x_low1, x_high1, False, y_lowlimit1, y_highlimit1, y_lowlimit2, y_highlimit2, bin_c1, cutsort, min_step_count, x_lowlimit1, x_highlimit1, x_lowlimit2, x_highlimit2)
                    #future = executor.submit(self.testfunc, 1,2)
                    #executor.shutdown(wait=False)
                #    return_value = future.result()
                    
                #    print(return_value[0])
    

                    
            #except Exception as e:
                #self.MonitorLabel.configure(text="""error""")
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #self.MonitorLabel.configure(text=f"time: {elapsed_time:.2f} s. click plot histograms")
            
            
        elif nthread == 1:
            start_time = time.time()
            try:

                self.MonitorLabel.configure(text="""running...""")
                self.root.update()
                hist2d, x, y, leng =self.histsortlog(x_zero, y_bin1, x_bin1, y_low1, y_high1, x_low1, x_high1, False, y_lowlimit1, y_highlimit1, y_lowlimit2, y_highlimit2, bin_c1, cutsort, min_step_count, x_lowlimit1, x_highlimit1, x_lowlimit2, x_highlimit2)
            except Exception as e:
                self.MonitorLabel.configure(text="""error""")
                    
            new_folder_name = "outputdata"
            direget2 = self.dirlo.get()
            os.chdir(direget2)
            currentdire = os.getcwd()
            new_folder_path = os.path.join(currentdire, new_folder_name)
            if not os.path.exists(new_folder_path):
                os.mkdir("outputdata")
                print(f"Folder '{new_folder_name}' created successfully.")
            else:
                print(f"Folder '{new_folder_name}' already exists.")

            os.chdir("outputdata") 
            hist2dsave = "hist2d.txt"
            xsave = "x.txt"
            ysave = "y.txt"
            hist1dsave = "hist1d.txt"
            #parametersave = {'x_low':x_low1,'x_high':x_high1, 'y_low':y_low1, 'y_high':y_high1, 'x_zero':x_zero, 'x_bin':x_bin1, 'y_bin':y_bin1, 'cut':cutsort, 'x_highlimit1':x_highlimit1, 'x_lowlimit1':x_lowlimit1, 'y_highlimit1':y_highlimit1, 'y_lowlimit1':y_lowlimit1,'box_bin':bin_c1,'min_count':min_step_count,'x_highlimit2':x_highlimit2, 'x_lowlimit2':x_lowlimit2, 'y_highlimit2':y_highlimit2, 'y_lowlimit2':y_highlimit2}
            parametersave = [x_low1,x_high1, y_low1, y_high1, x_zero, x_bin1, y_bin1, cutsort, x_highlimit1,x_lowlimit1, y_highlimit1, y_lowlimit1,bin_c1,min_step_count,x_highlimit2, x_lowlimit2, y_highlimit2, y_lowlimit2]
            hist1dtot = np.column_stack((y[1:],  hist2d.sum(axis=0).T.sum(axis=1)))
            np.savetxt(hist2dsave, hist2d.sum(axis=0).T, delimiter=" ")
            np.savetxt(xsave, x, delimiter=" ")
            np.savetxt(ysave, y, delimiter=" ")
            np.savetxt(hist1dsave, hist1dtot, delimiter=" ")
            #np.save("parametersave.npy",parametersave)
            np.savetxt("parametersave.txt",parametersave)
            print("file saved successfully")
            
            self.Yieldinput.delete(0, "end")
            self.Yieldinput.insert(END, 100*hist2d.shape[0]/leng)
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.MonitorLabel.configure(text=f"time: {elapsed_time:.2f} s. click plot histograms")





    def hist2dsort(self):
        #if self.selected_function.get() == 1: ## log amp
        x_low1=float(self.Dislowinput.get())
        x_high1=float(self.Dishighinput.get())
        y_low1=float(self.G0lowinput.get())
        y_high1=float(self.G0highinput.get())
        x_zero=float(self.X_zeroinput.get())
        x_bin1=int(float(self.X_bininput.get()))
        y_bin1=int(float(self.Y_bininput.get()))
        cutsort=int(float(self.Cutsortinput.get()))
        
        x_lowlimit1=float(self.X_lowlimitinput.get())
        x_highlimit1=float(self.X_highlimitinput.get())
        y_lowlimit1=float(self.Y_lowlimitinput.get())
        y_highlimit1=float(self.Y_highlimitinput.get())
        bin_c1=int(float(self.Binc1input.get()))
        min_step_count=int(float(self.Minstepcountinput.get()))
        x_lowlimit2=float(self.X_lowlimitinput2.get())
        x_highlimit2=float(self.X_highlimitinput2.get())
        y_lowlimit2=float(self.Y_lowlimitinput2.get())
        y_highlimit2=float(self.Y_highlimitinput2.get())
        start_time = time.time()
        try:

            self.MonitorLabel.configure(text="""running...""")
            self.root.update()
            hist2d, x, y, len =self.histsortlog(x_zero, y_bin1, x_bin1, y_low1, y_high1, x_low1, x_high1, False, y_lowlimit1, y_highlimit1, y_lowlimit2, y_highlimit2, bin_c1, cutsort, min_step_count, x_lowlimit1, x_highlimit1, x_lowlimit2, x_highlimit2)
        except Exception as e:
            self.MonitorLabel.configure(text="""error""")
                
        new_folder_name = "outputdata"
        direget2 = self.dirlo.get()
        os.chdir(direget2)
        currentdire = os.getcwd()
        new_folder_path = os.path.join(currentdire, new_folder_name)
        if not os.path.exists(new_folder_path):
            os.mkdir("outputdata")
            print(f"Folder '{new_folder_name}' created successfully.")
        else:
            print(f"Folder '{new_folder_name}' already exists.")

        os.chdir("outputdata") 
        hist2dsave = "hist2d.txt"
        xsave = "x.txt"
        ysave = "y.txt"
        hist1dsave = "hist1d.txt"
        #parametersave = {'x_low':x_low1,'x_high':x_high1, 'y_low':y_low1, 'y_high':y_high1, 'x_zero':x_zero, 'x_bin':x_bin1, 'y_bin':y_bin1, 'cut':cutsort, 'x_highlimit1':x_highlimit1, 'x_lowlimit1':x_lowlimit1, 'y_highlimit1':y_highlimit1, 'y_lowlimit1':y_lowlimit1,'box_bin':bin_c1,'min_count':min_step_count,'x_highlimit2':x_highlimit2, 'x_lowlimit2':x_lowlimit2, 'y_highlimit2':y_highlimit2, 'y_lowlimit2':y_highlimit2}
        parametersave = [x_low1,x_high1, y_low1, y_high1, x_zero, x_bin1, y_bin1, cutsort, x_highlimit1,x_lowlimit1, y_highlimit1, y_lowlimit1,bin_c1,min_step_count,x_highlimit2, x_lowlimit2, y_highlimit2, y_lowlimit2]
        hist1dtot = np.column_stack((y[1:],  hist2d.sum(axis=0).T.sum(axis=1)))
        np.savetxt(hist2dsave, hist2d.sum(axis=0).T, delimiter=" ")
        np.savetxt(xsave, x, delimiter=" ")
        np.savetxt(ysave, y, delimiter=" ")
        np.savetxt(hist1dsave, hist1dtot, delimiter=" ")
        #np.save("parametersave.npy",parametersave)
        np.savetxt("parametersave.txt",parametersave)
        print("file saved successfully")
        
        self.Yieldinput.delete(0, "end")
        self.Yieldinput.insert(END, 100*hist2d.shape[0]/len)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.MonitorLabel.configure(text=f"time: {elapsed_time:.2f} s. click plot histograms")
    

        #elif self.selected_function.get() ==2: ## linear amp
        #    print(2) 

    def loadprevious(self):
        new_folder_name = "outputdata"
        direget2 = self.dirlo.get()
        os.chdir(direget2)
        currentdire = os.getcwd()
        new_folder_path = os.path.join(currentdire, new_folder_name)
        os.chdir(direget2)
        if not os.path.exists(new_folder_path):
                print("Error, no folder")
        else:
            os.chdir("outputdata")
        previous_para = np.loadtxt("parametersave.txt")

        self.Dislowinput.delete(0,"end")
        self.Dishighinput.delete(0,"end")
        self.G0lowinput.delete(0,"end")
        self.G0highinput.delete(0,"end")
        self.X_zeroinput.delete(0,"end")
        self.X_bininput.delete(0,"end")
        self.Y_bininput.delete(0,"end")
        self.Cutsortinput.delete(0,"end")
       
        self.X_lowlimitinput.delete(0,"end")
        self.X_highlimitinput.delete(0,"end")
        self.Y_lowlimitinput.delete(0,"end")
        self.Y_highlimitinput.delete(0,"end")
        self.Binc1input.delete(0,"end")
        self.Minstepcountinput.delete(0,"end")
        self.X_lowlimitinput2.delete(0,"end")
        self.X_highlimitinput2.delete(0,"end")
        self.Y_lowlimitinput2.delete(0,"end")
        self.Y_highlimitinput2.delete(0,"end")

        ######## insert #########
        self.Dislowinput.insert(-1,previous_para[0])
        self.Dishighinput.insert(-1,previous_para[1])
        self.G0lowinput.insert(-1,previous_para[2])
        self.G0highinput.insert(-1,previous_para[3])
        self.X_zeroinput.insert(-1,previous_para[4])
        self.X_bininput.insert(-1,previous_para[5])
        self.Y_bininput.insert(-1,previous_para[6])
        self.Cutsortinput.insert(-1,previous_para[7])
       
        
        self.X_highlimitinput.insert(-1,previous_para[8])
        self.X_lowlimitinput.insert(-1,previous_para[9])
        
        self.Y_highlimitinput.insert(-1,previous_para[10])
        self.Y_lowlimitinput.insert(-1,previous_para[11])
        self.Binc1input.insert(-1,previous_para[12])
        self.Minstepcountinput.insert(-1,previous_para[13])
        
        self.X_highlimitinput2.insert(-1,previous_para[14])
        self.X_lowlimitinput2.insert(-1,previous_para[15])
        
        self.Y_highlimitinput2.insert(-1,previous_para[16])
        self.Y_lowlimitinput2.insert(-1,previous_para[17])



    def plothists(self):
        self.ax2d.clear()
        self.ax1dh.clear()
        new_folder_name = "outputdata"
        direget2 = self.dirlo.get()
        os.chdir(direget2)
        currentdire = os.getcwd()
        new_folder_path = os.path.join(currentdire, new_folder_name)
        os.chdir(direget2)
        if not os.path.exists(new_folder_path):
                print("Error, no folder")
        else:
            os.chdir("outputdata")
        hist2data = np.loadtxt("hist2d.txt")
        xdata = np.loadtxt("x.txt")
        ydata = np.loadtxt("y.txt")
        X, Y = np.meshgrid(xdata, ydata)   ## log (G/G0)
        x00 = float(self.X_00input.get())
        x01 = float(self.X_01input.get())
        y00 = eval(self.Y_00input.get())
        y01 = float(self.Y_01input.get())
        z00 = float(self.Z_00input.get())
        z01 = float(self.Z_01input.get())

        x1d00 = eval(self.X1d_00input.get())
        x1d01 = float(self.X1d_01input.get())
        y1d00 = float(self.Y1d_00input.get())
        y1d01 = float(self.Y1d_01input.get())
       
        

        self.ax2d.pcolormesh(X, Y, hist2data,cmap=self.Color2d.get(),vmin = z00, vmax =z01)  #,vmin = 0, vmax = 10
        self.ax2d.set_xlabel('Distance (nm)')
        self.ax2d.set_ylabel('log ($G/G_0$)')
        #self.ax2d.set_yscale('log')
        self.ax2d.set_ylim(y00,y01)
        self.ax2d.set_xlim(x00,x01)
        #plt.rc('font', size=20)          # controls default text sizes
        #plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
        #self.ax2d.rc('ytick', labelsize=20) 
        ###frame and ticks 
        self.ax2d.spines['top'].set_linewidth(1)
        self.ax2d.spines['right'].set_linewidth(1)
        self.ax2d.spines['bottom'].set_linewidth(1)
        self.ax2d.spines['left'].set_linewidth(1)
        self.ax2d.xaxis.set_tick_params(width=1)
        self.ax2d.yaxis.set_tick_params(which='both',width=1)
        self.fig2d.savefig('h2d.jpg',dpi=600)
        self.fig2d.savefig('h2d.jpg',dpi=600)
        self.figure_canvas2d.draw()

        ## 1d hist plot

        self.ax1dh.plot(ydata[1:], hist2data.sum(axis=1)) ###  need more precision
        self.ax1dh.set_xlabel('log ($G/G_0$)')
        self.ax1dh.set_ylabel('Counts (arb. units)')
        #self.ax1dh.set_xscale('log')
        self.ax1dh.set_ylim(y1d00,y1d01)
        self.ax1dh.set_xlim(x1d00,x1d01)
        #plt.rc('font', size=20)          # controls default text sizes
        #plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
        #self.ax2d.rc('ytick', labelsize=20) 
        ###frame and ticks 
        self.ax1dh.spines['top'].set_linewidth(1)
        self.ax1dh.spines['right'].set_linewidth(1)
        self.ax1dh.spines['bottom'].set_linewidth(1)
        self.ax1dh.spines['left'].set_linewidth(1)
        self.ax1dh.xaxis.set_tick_params(width=1)
        self.ax1dh.yaxis.set_tick_params(which='both',width=1)
        self.ax1dh.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        self.fig1dh.savefig('h1d.jpg',dpi=600)
        self.figure_canvas1dh.draw()
    
    ## for extral quit button
    def quit(self):
        self.root.quit()
   



        
def quitme():
    root.quit()
    root.destroy()

         
'''
def main():
    root = tk.Tk()
    app = Dataview(root)
    root.protocol("WM_DELETE_WINDOW", quit)
    root.mainloop()
'''

if __name__ == "__main__":
    root = tk.Tk()
    app = Dataview(root)
    root.protocol("WM_DELETE_WINDOW", quitme)
    root.mainloop()
