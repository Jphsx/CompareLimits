#limits_mbin1.json
#limits_mbin2.json
#limits_nominal.json



import json
import ROOT
import math

def loadjson(fjson):
    with open(fjson) as f:
        data = json.load(f)
        label_list=[]
        for point in data:
            x = point.split("0",1)
            MDOWN = float(x[1])
            MUP = (float(point)-MDOWN)/10000.
            DM = MUP-MDOWN 
            #dMh.Fill(DM)
            label_dm = (str(MUP).split('.')[0])+"_"+(str(MDOWN).split('.')[0])+"_"+(str(DM).split('.')[0])
            label_key = (str(point).split('.'))[0]
            value = data[point]
            value = value["exp0"]
            label_list.append([label_key,label_dm,MUP,MDOWN, DM, value]) 
        
        return label_list


def sortlabel(label_list):
    label_list = sorted( label_list, key=lambda x: (x[2],x[4]) )
    return label_list


def makehists(label_list, pts_per_hist=20):
    npts = len(label_list)
    nhists = int(math.ceil(float(npts)/pts_per_hist))+1
    hlist=[]
    #print("makehists",npts,nhists)
    for x in range(0,nhists):
        h = ROOT.TH1D("h"+str(x), "exp0", pts_per_hist,0,1)
        hlist.append(h)

    return hlist


def fillHists1(label_list, hlist, pts_per_hist=20):
    ihist=0
    ibin=1
    #print(len(label_list))
    for i,x in enumerate(label_list):
       # print(ibin,ihist,i,len(label_list))
        if ibin > pts_per_hist:
            ibin=1
            ihist = ihist+1
        hlist[ihist].SetBinContent(ibin,float(x[5]))
        hlist[ihist].GetXaxis().SetBinLabel(ibin,str(x[1]))
        ibin=ibin+1
       
def writeHists(outname, hlist, mode="RECREATE"):
    outfile = ROOT.TFile(outname,mode)
    for x in hlist:
        outfile.WriteTObject(x)
    outfile.Close()


def runjson(jsonfile,outfile, PTS_PER_HIST):
    run = loadjson(jsonfile)
    run = sortlabel(run)
    hlist = makehists(run,PTS_PER_HIST)
    fillHists1(run,hlist,PTS_PER_HIST)
    writeHists(outfile,hlist)
    return run,hlist

def fillCompare(alldata, mXLdata, allhist,mXLname, pts_per_hist=20):
    #clone allhist
    mxlhist = []
    for h in allhist:
        hclone = h.Clone()
        hclone.SetName(hclone.GetName()+mXLname)
        mxlhist.append(hclone)

    ihist = 0
    ibin = 1
    for i,x in enumerate(alldata):
        if ibin > pts_per_hist:
            ibin=1
            ihist = ihist+1
        
        content = -1    
        for y in mXLdata:
            if str(y[1]) == str(x[1]): #matching label
                content = float(y[5])
                print("found match", y[1], x[1])

        mxlhist[ihist].SetBinContent(ibin,content)
        ibin=ibin+1
    
    return mxlhist

def get_data_container(files,outroots,npts_per_hist):
    container=[]
    for i,f in enumerate(files):
        container.append( runjson(files[i],outroots[i],npts_per_hist))

    return container



############################
#Start - define the limit json and labels
#Use the first entry as reference for masspoint matching
###########################

FileList = ["./limits/BF_B5-3_TChiWZ17.json","./limits/BF_B6-1_TChiWZ17.json"];
LabelList = ["TEST1","TEST2"];
OutRootList = ["r1.root","r2.root"];
NPointsPerHist = 30
USECOMP=False

data_hist_container= get_data_container(FileList, OutRootList, NPointsPerHist)



#print(data_hist_container)
#exit()

#do matching -- is this necessary anymore?
#refence with index0
comps= []

for i,x in enumerate(data_hist_container):
    if i ==0:
        continue
    comps.append( fillCompare( data_hist_container[0][0] , x[0], data_hist_container[0][1], "H"+str(i), NPointsPerHist  ))

            


for i,x in enumerate(OutRootList):
    writeHists(x, data_hist_container[i][1])



colorset = [1,2,4,6,1,5]
markerset =[20,22,23,39,28,42]


#format and super impose plots into TCanvas and save into new rootfile
def superHists(hlistset, colorset,markerset, idx):
    can = ROOT.TCanvas(str(idx),str(idx))
    leg = ROOT.TLegend(0.1,0.7,0.48,0.9)
    #make all always first 
    #hlistset[0][idx].SetMarkerStyle(20)
    #hlistset[0][idx].SetMarkerColor
    for i,hlist in enumerate(hlistset):
        hlistset[i][idx].SetMarkerStyle(markerset[i])
        hlistset[i][idx].SetMarkerSize(2)
        hlistset[i][idx].SetLineColor(colorset[i])
        hlistset[i][idx].SetMarkerColor(colorset[i])
        leg.AddEntry(hlistset[i][idx],LabelList[i],"lp")
        if i==0 :
            hlistset[i][idx].GetXaxis().SetLabelSize(0.025)
            hlistset[i][idx].Draw("P")
        if i>0 :
            hlistset[i][idx].Draw("P SAME")
    leg.Draw()
    return can,leg


#can,leg = superHists([allhist,m0L_comp,m1L_comp,m2L_comp,m3L_comp], colorset,markerset, 0)
#can,leg = superHists([allhist,mbinhist1,mbinhist2],colorset,markerset,0)
#can, leg = superHists([allhist,mbinhist1],colorset,markerset,0)
#can, leg = superHists([nomhist,b32hist],colorset,markerset,0)

drawlist = []
nomhist = data_hist_container[i][1]
histlist = []
if USECOMP == False:
    for h in data_hist_container:
        histlist.append(h[1])    
if USECOMP:
    histlist = comps

for i in range(0,len(nomhist)):
    drawlist.append( superHists(histlist,colorset,markerset,i))

print("Generating allplots")
allplots = ROOT.TFile("allplots.root","RECREATE")
for can in drawlist:
    allplots.WriteTObject(can[0])

allplots.Close()




