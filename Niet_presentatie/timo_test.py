import numpy as np
import math
import matplotlib.pyplot as plt
from tqdm import tqdm

xy=np.array ([[6,6]])#start coordinate
d=4#dimension
working =[]
test =[]
test1=[]
for n in tqdm(range(1296,15,-1)):#range of n values
    for p in range(2,int(n/2+1)):
        for q in range(p+1,int(n/2+1)):
            for r in range(q+1,int(n/2+1)):
                test.append ([p,q,r]) #set of all possibilities
    for k in range(math.floor(n/xy[-1][0]+1),4000):
        for q in test:
            f=0
            for i in range(1,k):
                working =[(i*q[0])%n,(i*q[1])%n,(i*q[2])%n]
                #working needs to be changed for more q’s
                true=0
                for a in working:
                    if a>=k and n-k>=a:
                        true=1
                if true==0:
                    f=1
                    break
            if f==0:
                k1=k
                n1=n
                test1.append(q)
        if test1==[]:
            if k>math.floor(n/xy[-1][0]+1):
                xy=np.append(xy ,[[n1/k1,n1**(1/d)]],axis=0)
            break
        test=list(test1)
        test1=[]
    test =[]
xy=np.flip(xy ,0)

#Plotting the results
plt.plot(xy[:,0],xy[:,1],marker='o',linestyle='None')
plt.show()