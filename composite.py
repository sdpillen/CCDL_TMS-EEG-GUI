"""
Simple Python RDA client for the RDA tcpip interface of the BrainVision Recorder
It reads all the information from the recorded EEG,
prints EEG and marker information to the console and calculates and
prints the average power every second


Brain Products GmbH
Gilching/Freiburg, Germany
www.brainproducts.com

"""

# needs socket and struct library
from socket import *
from struct import *
import time
nowtime = time.time()


import wx
from threading import Thread
import time
import os
#
initialization = False

wildcard = "EEG raw data (*.eeg)|*.eeg|"    \
           "Comma Separated Values File (*.csv)|*.csv|"       \
           "All files (*.*)|*.*"

TMS_Mark = False


# Marker class for storing marker information

        
        
        
#This will be made into the mechanism by which files are recorded.
class testThread(Thread):
    def __init__(self, parent):
        self.parent = parent
        Thread.__init__(self)
        self.start()
        
    def run(self):
        self.TMS_Mark = False
        global nowtime
    # Marker class for storing marker information
        class Marker:
            def __init__(self):
                self.position = 0
                self.points = 0
                self.channel = -1
                self.type = ""
                self.description = ""

        # Helper function for receiving whole message
        def RecvData(socket, requestedSize):
            returnStream = ''
            while len(returnStream) < requestedSize:
                databytes = socket.recv(requestedSize - len(returnStream))
                if databytes == '':
                    raise RuntimeError, "connection broken"
                returnStream += databytes
         
            return returnStream   

            
        # Helper function for splitting a raw array of
        # zero terminated strings (C) into an array of python strings
        def SplitString(raw):
            stringlist = []
            s = ""
            for i in range(len(raw)):
                if raw[i] != '\x00':
                    s = s + raw[i]
                else:
                    stringlist.append(s)
                    s = ""

            return stringlist
            

        # Helper function for extracting eeg properties from a raw data array
        # read from tcpip socket
        def GetProperties(rawdata):

            # Extract numerical data
            (channelCount, samplingInterval) = unpack('<Ld', rawdata[:12])

            # Extract resolutions
            resolutions = []
            for c in range(channelCount):
                index = 12 + c * 8
                restuple = unpack('<d', rawdata[index:index+8])
                resolutions.append(restuple[0])

            # Extract channel names
            channelNames = SplitString(rawdata[12 + 8 * channelCount:])

            return (channelCount, samplingInterval, resolutions, channelNames)

        # Helper function for extracting eeg and marker data from a raw data array
        # read from tcpip socket       
        def GetData(rawdata, channelCount):

            # Extract numerical data
            (block, points, markerCount) = unpack('<LLL', rawdata[:12])

            # Extract eeg data as array of floats
            data = []
            for i in range(points * channelCount):
                index = 12 + 4 * i
                value = unpack('<f', rawdata[index:index+4])
                data.append(value[0])

            # Extract markers
            markers = []
            index = 12 + 4 * points * channelCount
            for m in range(markerCount):
                markersize = unpack('<L', rawdata[index:index+4])

                ma = Marker()
                (ma.position, ma.points, ma.channel) = unpack('<LLl', rawdata[index+4:index+16])
                typedesc = SplitString(rawdata[index+16:index+markersize[0]])
                ma.type = typedesc[0]
                ma.description = typedesc[1]

                markers.append(ma)
                index = index + markersize[0]

            return (block, points, markerCount, data, markers)


        ##############################################################################################
        #
        # Main RDA routine
        #
        ##############################################################################################
        global filename
        # Create a tcpip socket
        con = socket(AF_INET, SOCK_STREAM)
        # Connect to recorder host via 32Bit RDA-port
        # adapt to your host, if recorder is not running on local machine
        # change port to 51234 to connect to 16Bit RDA-port
        con.connect(("localhost", 51244))
        f = open(filename, 'w')
        # Flag for main loop
        finish = False

        # data buffer for calculation, empty in beginning
        data1s = []

        # block counter to check overflows of tcpip buffer
        lastBlock = -1

        #### Main Loop ####
        while not finish:

            # Get message header as raw array of chars
            rawhdr = RecvData(con, 24)

            # Split array into usefull information id1 to id4 are constants
            (id1, id2, id3, id4, msgsize, msgtype) = unpack('<llllLL', rawhdr)

            # Get data part of message, which is of variable size
            rawdata = RecvData(con, msgsize - 24)

            # Perform action dependend on the message type
            if msgtype == 1:
                # Start message, extract eeg properties and display them
                (channelCount, samplingInterval, resolutions, channelNames) = GetProperties(rawdata)
                # reset block counter
                lastBlock = -1

                print "Start"
                print "Number of channels: " + str(channelCount)
                print "Sampling interval: " + str(samplingInterval)
                print "Resolutions: " + str(resolutions)
                print "Channel Names: " + str(channelNames)
                for x in channelNames: 
                    f.write(x + ',')
                f.write('Trigger\n') 

            elif msgtype == 4:
                # Data message, extract data and markers
                (block, points, markerCount, data, markers) = GetData(rawdata, channelCount)

                # Check for overflow
                if lastBlock != -1 and block > lastBlock + 1:
                    print "*** Overflow with " + str(block - lastBlock) + " datablocks ***" 
                lastBlock = block

                # Print markers, if there are some in actual block
                if markerCount > 0:
                    for m in range(markerCount):
                        print "Marker " + markers[m].description + " of type " + markers[m].type

                # Put data at the end of actual buffer
                data1s.extend(data)
                
                #This will write the file I opened in the begining.
                #for a in range(0,9)
                counter = 0
                for item in data:
                    counter = counter+1
                    f.write(str(item))
                    f.write(',')
                    if counter == 32:
                        if self.TMS_Mark == True:
                            print 'checkarooni'
                            self.TMS_Mark = False
                            f.write('1')
                        else:
                            f.write('0')
                        f.write('\n')
                        counter = 0
                
                # If more than 1s of data is collected, calculate average power, print it and reset data buffer
                if len(data1s) > channelCount * 1000000 / samplingInterval:
                    index = int(len(data1s) - channelCount * 1000000 / samplingInterval)
                    data1s = data1s[index:]

                    avg = 0
                    # Do not forget to respect the resolution !!!
                    for i in range(len(data1s)):
                        avg = avg + data1s[i]*data1s[i]*resolutions[i % channelCount]*resolutions[i % channelCount]
                    # print ' '
                    # print data[0:9]
                    # print data[63:72]	
                    # print ' '
                    avg = avg / len(data1s)
                    print "Average power: " + str(avg)
                    print time.time() - nowtime
                    nowtime = time.time()
                    print len(data1s)

                    data1s = []
                    

            elif msgtype == 3:
                # Stop message, terminate program
                print "Stop"
                finish = True

        # Close tcpip connection
        con.close()
        f.close()

class testGUI(wx.Frame): 
    def __init__(self): 
        wx.Frame.__init__(self, None, -1, "EEG/TMS Panel", size=(500,270)) 
        panel = wx.Panel(self, -1)

        self.buttonFilename = wx.Button(panel, -1, label="Choose Filename", pos=(30,30))
        self.FileText = wx.StaticText(panel, label="Filename:", pos = (30, 60))
        
        self.buttonConnect = wx.Button(panel, -1, label="Connect to BrainVision", pos=(30,120))
        self.buttonRecord = wx.Button(panel, -1, label="Begin EEG Recording", pos=(30,150))
        self.buttonTrigger = wx.Button(panel, -1, label="Send TMS Pulse", pos=(360,150))
        panel.Bind(wx.EVT_BUTTON, self.Filename, id=self.buttonFilename.GetId())
        panel.Bind(wx.EVT_BUTTON, self.Connect, id=self.buttonConnect.GetId())
        panel.Bind(wx.EVT_BUTTON, self.Record, id=self.buttonRecord.GetId())
        panel.Bind(wx.EVT_BUTTON, self.Trigger, id=self.buttonTrigger.GetId())
        
        
        
        self.buttonConnect.Disable()
        self.buttonRecord.Disable()
        
    def startThread(self, event):
        self.the_thread = testThread(self)

    def changeVar(self, event):
        # DO SOMETHING HERE THAT CHANGES 'x' IN THREAD TO 2...
        self.the_thread.value = 2

    def Record(self, event):
        placeholder = True
    def Connect(self, event):
        self.the_thread = testThread(self)
        
    def Trigger(self, event):
        print('check')
        self.the_thread.TMS_Mark = True

    
    def Filename(self, event):
        """
        
        Opens up a file saving dialog when the "File" button is pressed.
        """
        global filename
        dlg = wx.FileDialog(self, message="Save EEG data as ...",
                            defaultDir=os.getcwd(), defaultFile="",
                            wildcard=wildcard, style=wx.SAVE)

        dlg.SetFilterIndex(1)

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            fname = dlg.GetPath()
        dlg.Destroy()
        
        # If the filename exists, ask for confirmation
        if os.path.exists( fname ):
            dlg = wx.MessageDialog(self, "File already exists. Overwrite?",
                                   "Potential problem with file",
                                   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION
                                   )

            response = dlg.ShowModal()
            if response == wx.ID_YES:
                filename = fname

            elif response == wx.ID_NO:
                self.filename = None
            
        else:
            # If the file does not exists, we can proceed
            filename = fname
        self.FileText.label = "Filename1: "
        print(["Filename: " + fname])
        self.buttonConnect.Enable()
        self.Refresh()
        self.Update()
        #NFT.OutputFilename = fname[:-4] + 'MetaData.csv'
        #NFT.ExperimentOutputName = fname[:-4] + 'ContRec.csv'
        #self.update_interface()
        #NFT.CustomName = True

if __name__ == '__main__': 
    app = wx.App(redirect=False)
    frame = testGUI() 
    frame.Show(True) 
    app.MainLoop()            
            

# Helper function for receiving whole message
def RecvData(socket, requestedSize):
    returnStream = ''
    while len(returnStream) < requestedSize:
        databytes = socket.recv(requestedSize - len(returnStream))
        if databytes == '':
            raise RuntimeError, "connection broken"
        returnStream += databytes
 
    return returnStream   

    
# Helper function for splitting a raw array of
# zero terminated strings (C) into an array of python strings
def SplitString(raw):
    stringlist = []
    s = ""
    for i in range(len(raw)):
        if raw[i] != '\x00':
            s = s + raw[i]
        else:
            stringlist.append(s)
            s = ""

    return stringlist
    

# Helper function for extracting eeg properties from a raw data array
# read from tcpip socket
def GetProperties(rawdata):

    # Extract numerical data
    (channelCount, samplingInterval) = unpack('<Ld', rawdata[:12])

    # Extract resolutions
    resolutions = []
    for c in range(channelCount):
        index = 12 + c * 8
        restuple = unpack('<d', rawdata[index:index+8])
        resolutions.append(restuple[0])

    # Extract channel names
    channelNames = SplitString(rawdata[12 + 8 * channelCount:])

    return (channelCount, samplingInterval, resolutions, channelNames)

# Helper function for extracting eeg and marker data from a raw data array
# read from tcpip socket       
def GetData(rawdata, channelCount):

    # Extract numerical data
    (block, points, markerCount) = unpack('<LLL', rawdata[:12])

    # Extract eeg data as array of floats
    data = []
    for i in range(points * channelCount):
        index = 12 + 4 * i
        value = unpack('<f', rawdata[index:index+4])
        data.append(value[0])

    # Extract markers
    markers = []
    index = 12 + 4 * points * channelCount
    for m in range(markerCount):
        markersize = unpack('<L', rawdata[index:index+4])

        ma = Marker()
        (ma.position, ma.points, ma.channel) = unpack('<LLl', rawdata[index+4:index+16])
        typedesc = SplitString(rawdata[index+16:index+markersize[0]])
        ma.type = typedesc[0]
        ma.description = typedesc[1]

        markers.append(ma)
        index = index + markersize[0]

    return (block, points, markerCount, data, markers)



# Close tcpip connection
con.close()
f.close()

