#!/usr/bin/env python3
import rospy
import bluetooth
import select
import rospy 
from std_msgs.msg import String
from rssi.msg import Num
import subprocess
import numpy
from scipy.optimize import minimize

class Rssi():
    def __init__(self):
        #n=3
        
        self.rate = rospy.Rate(1) #1 hz 
        self.device = Num()
        #rospy.Subscriber("device",Num, self.callback)
        self.config = rospy.get_param('/consensus_params')
        self.name = rospy.get_namespace().strip('/')   
        print(self.name)
        
        self.index = int(self.config['mapping'].index(self.name))  
        n=int(self.config['broj_uredaja'])
        self.A = numpy.zeros((n,n))
        self.X = numpy.zeros((n,2))
        matrix = []
        for i in range(n):
            matrix.append([0] * n)
        print(matrix)
        print(self.A)
        callback_number=0 
        subprocess.run(['sudo','hciconfig','hciX','piscan'])
        pub = rospy.Publisher("device",Num,queue_size=1)
        # Create subscribers.
        for connected, to in zip(self.config['adjacency'][self.index], self.config['mapping']):
            if connected:
                rospy.Subscriber('/{}/device'.format(to), Num, self.callback, queue_size=3)
                
                
    def callback(self,data):
        self.pose=data
        callback_number=callback_number+1
        if data.name.find("rpi")!=-1:
           # if data.name.find("rpi0")!=-1:
           #     rpix=0
           # if data.name.find("rpi1")!=-1:
           #     rpix=1
           # if data.name.find("rpi2")!=-1:
           #     rpix=2
                #ime=data.name.replace("rpi", "")
                #name=ime.replace("\nhci0","")
            duljina=len(data.name)     
            for i in range(duljina):
                if data.name[i]=="r":
                    if data.name[i+1]=="p":
                        if data.name[i+2]=="i":
                            rpix=int(data.name[i+3])
            sender=data.sender.replace("rpi", "")
            
            senderID=int(sender)
            udaljenost=10**((-62-data.rssi)/(10*2))
            temp=self.A[senderID][rpix]+(udaljenost+self.A[senderID][rpix])/2
            self.A[senderID][rpix]=temp
            
            
        if callback_number>10:
            
            x0=numpy.zeros((1,n*2-3))
            bnds = ((0, None), (0, None))
            sol=minimize(objective,x0)
            est=sol.x
            X_est=[[0,0],[0,est[0]]]
            est=numpy.delete(est,0)
            X_est.append(numpy.reshape(est,(1,2)))
            print(X_est)
            #print(sol.fun)
        
        print("A=", self.A)
        
        
    def run(self):
        
        while not rospy.is_shutdown():

            result = subprocess.run(['sudo','btmgmt','find'], stdout=subprocess.PIPE)
            result=result.stdout.decode('UTF-8')
            #print(result)
            lista = result.split(" ")
            #print(lista)
            device=Num()
            length=len(lista)
            for i in range(length):
            
                if lista[i]=="rssi":
                    device.rssi=int(lista[i+1])
                            
                if lista[i]=="\nname":
                    device.name=lista[i+1] 
                    device.sender=self.name
                    
                    pub.publish(device)

            self.rate.sleep()
            
def objective(x):
        Y=self.A
        n = len(Y)
        X=[[0, 0] ,[0, x[0]]]
        x=numpy.delete(x,0)
        X.append(numpy.reshape(x,(1,2)))
        mse = 0
        c = 0
        for i in range(n):
            for j in range(n):
                if (i != j):
                    d = numpy.linalg.norm(numpy.subtract(X[i], X[j]))
                    if Y[i][j] > 0:
                        
                        mse = mse + (d - float(Y[i][j]))** 2
                        c = c + 1
        mse = mse / c
        return mse
        
       
if __name__ == '__main__':
    rospy.init_node('pyclass')
    pub = rospy.Publisher("device",Num,queue_size=1)
    try:
        ne = Rssi()
        ne.run()
    except rospy.ROSInterruptException:pass

