from Tkinter import *
import math, random, threading, time, stat
import os 
import subprocess
import atexit 




class Monitor:

    go = 0
    def __init__(self, root):
        self.gf = self.makeGraph(root)
        self.cf = self.makeControls(root)
        self.gf.pack()
        self.cf.pack()
        self.Reset() 

    def makeGraph(self, frame):
        self.sw = 1000
        self.h = 200
        self.top = 2
        gf = Canvas(frame, width=self.sw, height=self.h+10,
                    bg="#000", bd=0, highlightthickness=0)
        gf.p = PhotoImage(width=2*self.sw, height=self.h)
        self.item = gf.create_image(0, self.top, image=gf.p, anchor=NW)
        return(gf)

    def makeControls(self, frame):
        cf = Frame(frame, borderwidth=1, relief="raised")
        Button(cf, text="Run", command=self.Run).grid(column=2, row=2)
        Button(cf, text="Stop", command=self.Stop).grid(column=4, row=2)
        Button(cf, text="Reset", command=self.Reset).grid(column=6, row=2)
        
        self.k1 = Label(cf,text="RENDER")
        self.k1.grid(column= 1, row =6)
        self.k1.config(fg = '#ff4')
        self.k1.data = Label(cf,text="")
        self.k1.data.grid(column = 2, row=6)

        self.k2 = Label(cf, text="VIDEO")
        self.k2.grid(column=3, row =6)
        self.k2.config(fg = '#ff0000')
        self.k2.data = Label(cf,text="")
        self.k2.data.grid(column = 4, row=6)
        

        
        self.k4 = Label(cf,text="VIDEO2")
        self.k4.grid(column=5, row=6)
        self.k4.config(fg = '#0000ff')
        self.k4.data = Label(cf,text="")
        self.k4.data.grid(column=6, row = 6)

        self.k3 = Label(cf, text="VIDEO_E")
        self.k3.grid (column=7, row=6)
        self.k3.config(fg = '#080')
        self.k3.data = Label(cf,text="")
        self.k3.data.grid(column= 8, row=6)

        self.gf.create_text(10,10,anchor="nw",text="100%", fill="#ff0000")
        self.gf.create_text(10,self.h -10,anchor="sw",text="0%", fill="#ff0000")
        
        return(cf)

    def Run(self):
        self.go = 1
        for t in threading.enumerate():
            if t.name == "_gen_":
                print("already running")
                return

        print "Creating Pipe"
        self.fifo = '/tmp/myfifo' 
        try: 
    		os.unlink(self.fifo)
        	os.mkfifo(self.fifo)
        except OSError, e: 
        	os.mkfifo(self.fifo)
        
        print "Pipe Created"
        threading.Thread(target=self.do_start, name="_gen_").start()
        self.pro = subprocess.Popen("./metrics_monitor", shell=True)


    def Stop(self):
        if self.go == 1: 
           self.pro.terminate()
           os.unlink(self.fifo)
        self.go = 0
       
        for t in threading.enumerate():
            if t.name == "_gen_":
            	print str(t)
                t.join(1.0)
             

    def Reset(self):
        self.Stop()
        self.clearstrip(self.gf.p, '#000')

    def do_start(self):       
        metrics = []
        fifo = open(self.fifo, "r")
        while self.go:      
            try: 
                line = fifo.readline()
                if line != "": 
                    del metrics[:]
                    fields = line.split(",")
                    for data in fields:
                            idx = data.find(":") 
                            label = data[0:idx]
                            metric= float(data[idx+1:-1])
                            metrics.append(metric)
                            #print "Appending " + str(metric) 
                    y3 =  metrics[0] / 100  
                    y4 =  metrics[1] / 100  
                    y5 =  metrics[2] / 100  
                    y6 =  metrics[3] / 100  
                    self.k1.data.config(text = str(metrics[0]))
                    self.k2.data.config(text = str(metrics[1]))
                    self.k3.data.config(text = str(metrics[2]))
                    self.k4.data.config(text = str(metrics[3]))
                    self.scrollstrip(self.gf.p,(y3,.25,y4,y5,y6,0.75),('#ff4','#f40','#ff0000','#080','#0000ff','#080'),'#000')
            	else:
            		self.go = 0

            except: 
                print "Could not read pipe"



    def clearstrip(self, p, color):  # Fill strip with background color
        self.bg = color              # save background color for scroll
        self.data = None             # clear previous data
        self.x = 0
        p.tk.call(p, 'put', color, '-to', 0, 0, p['width'], p['height'])

    def scrollstrip(self, p, data, colors, bar=""):   # Scroll the strip, add new data
        
     
        
        self.x = (self.x + 1) % self.sw               # x = double buffer position
        bg = bar if bar else self.bg
        p.tk.call(p, 'put', bg, '-to', self.x, 0, self.x+1, self.h)
        p.tk.call(p, 'put', bg, '-to', self.x+self.sw, 0, self.x+self.sw+1, self.h)
        self.gf.coords(self.item, -1-self.x, self.top)  # scroll to just-written column
        if not self.data:
            self.data = data
        for d in range(len(data)):
            y0 = int((self.h-1) * (1.0-self.data[d]))   # plot all the data points
            y1 = int((self.h-1) * (1.0-data[d]))
     
            ya, yb = sorted((y0, y1))
            for y in range(ya, yb+1):                   # connect the dots
                p.put(colors[d], (self.x,y))
                p.put(colors[d], (self.x+self.sw,y))
        self.data = data            # save for next call
    


def main():
    root = Tk()
    root.title("GPU Metrics Monitor")
    app = Monitor(root)
    root.mainloop()

main()
