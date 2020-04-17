#!/usr/bin/env python
import sys, math

def get_blast(filename):
    f_list=[]
    d={}
    f=open(filename)
    for line in f:
        v=line.rstrip().split()
        d[v[0]]=d.get(v[0],[])
        d[v[0]].append([float(v[1]),int(v[2])])
    for k in d.keys():
        d[k].sort()
        f_list.append(d[k][0]) #lowest e-value
    return f_list

def get_cm(data,th):
    #CM=[[TP, FP],[FN,TN]]
    #0 = Negatives 1=Positives
    cm=[[0.0,0.0],[0.0,0.0]]
    for i in data:
        #true positive
        if i[0]<th and i[1]==1:
            cm[0][0]=cm[0][0]+1
        #false positve
        if i[0]>=th and i[1]==1:
            cm[1][0]=cm[1][0]+1
        #false negative
        if i[0]<th and i[1]==0:
            cm[0][1]=cm[0][1]+1
        #true negative
        if i[0]>=th and i[1]==0:
            cm[1][1]=cm[1][1]+1
    return cm

#acc=(TP+TN)/(TP+TN+FN+FP)
#it is not so informative
def get_acc(cm):
  return float(cm[0][0]+cm[1][1])/(sum(cm[0])+sum(cm[1]))


#MCC=(TP*TN)-(FP*FN)/sqrt((TP+FP)*(TN+FN)*(TN+FP)*(TN+FN))
#is is more infomrative beacuse not affected by dataset unbalance
def mcc(cm):
  d=(cm[0][0]+cm[1][0])*(cm[0][0]+cm[0][1])*(cm[1][1]+cm[1][0])*(cm[1][1]+cm[0][1])
  return (cm[0][0]*cm[1][1]-cm[0][1]*cm[1][0])/math.sqrt(d)

if __name__=="__main__":
    filename=sys.argv[1]
    th=float(sys.argv[2])
    data=get_blast(filename)
    for i in range(20):
        th=10**-i
        cm=get_cm(data,th)
        print("TH:", th,"ACC: ",get_acc(cm),"MCC: ",mcc(cm), cm)
