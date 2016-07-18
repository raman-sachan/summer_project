#Download the phue library first from the git repo. link https://github.com/studioimaginaire/phue

#Visit: developers.meethue.com
#login with following credentials: user: r.sachan  pwd: cubical@2016

import sys
import requests
import logging
import random
import time
import pprint
import dictionary
import collections
import urllib
import json


#getting the ip of hue brdige from the given link
url = 'https://www.meethue.com/api/nupnp'
txt = urllib.urlopen(url).read()
d = txt.strip('[]')
e = json.loads(d)
ip = e["internalipaddress"]

#https://github.com/studioimaginaire/phue/issues/48
#editing the hidden file .python_hue to constantly update the ip in the file with the above generated ip
register={}
register[ip]={}
register[ip]["username"]="OhmEbO9DJAsbXy9744O8UWjrpsm-paFchX2sCAq7"
json.dump(register, open(".python_hue",'w'))

time.sleep(1)

from phue import Bridge
logging.basicConfig()          #I don't know the use of this line
b= Bridge(ip)
b.connect()

lights= b.get_light()
groups= b.get_group()
dic={}
dic.clear()


#This function is for creating a dictionary
def dic_function (_device_id,_isActive,_dim,_hue,_sat,_bri,_reach):

	dic[_device_id]={}
	dic[_device_id]["state_dict"]={}
        dic[_device_id]["state_dict"]["isActive"]=_isActive
	dic[_device_id]["state_dict"]["isReachable"]=_reach
	dic[_device_id]["state_dict"]["dimming"]=_dim
	dic[_device_id]["state_dict"]["params"]={}
	dic[_device_id]["state_dict"]["params"]["h"]=_hue
	dic[_device_id]["state_dict"]["params"]["s"]=_sat
	dic[_device_id]["state_dict"]["params"]["v"]=_bri
		


def get_api():             #returns a big dictionary from where we can browse and retrieve the required data
    return b.get_api()

def scale_hsv( x, a, b, a1, b1):      #scaling parameters on different scale a,b old values to a1,b1 new values
    m= ((x - a) / (b-a)) * (b1-a1) + a1
    return int(m)

def hsv_off(idd):
	b.set_light(idd, 'on',False)

def hsv_on(idd):
	b.set_light(idd,'on',True)

def hsvgrp_on(idd):
	b.set_group(idd,'on',True)

def hsvgrp_off(idd):
        b.set_group(idd, 'on',False)

def set_v(a,c):
	b.set_light(a,'bri',c)

def set_grp_v(a,c):
    b.set_group(a,'bri',c)


#sending the actual parameters to the bridge
def set_hsv( a,c,d,e ):
        if c<65536:
                if d<256:
                        if e<256:
                                command = {'hue':c,'sat':d,'bri':e}
                                b.set_light(a, command)
                        else:
                                print 'v should be between(0-255)'
                else:
                    print 's should be between(0-255)'
        else:
                print 'h should be between(0-63000)'


def set_hsv_group( a,c,d,e ):
        if c<65536:
                if d<256:
                        if e<256:
                                command = {'hue':c,'sat':d,'bri':e}
                                b.set_group(a, command)
                        else:
                                print 'v should be between(0-255)'
                else:
                    print 's should be between(0-255)'
        else:
                print 'h should be between(0-63000)'

#updating the dictionary of lights/groups with a sub dictionary (here _dic)
def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

# In the apply_hue_state function before the #################### part we create the dictionary for lights(including all the bulbs) with all the parameters
# in the required format(1-100 scale). Here h is that final dictionary 
def apply_hue_state(_bridgeIP,_id1,_dic):
	huedic={}
	huedic=get_api()
	global dic
	dic={}
	dic.clear()
	index = 0
	global h
	h={}
        for key  in huedic[u'lights']:
                id = huedic[u'lights'][unicode(key)][u'name']
                on= huedic[u'lights'][unicode(key)][u'state'][u'on']
                hue= huedic[u'lights'][unicode(key)][u'state'][u'hue']
                if(hue==0 or hue==65535):
                        hue = scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                else:
                        hue = scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                        hue = hue+1
#               hue=scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                bri= huedic[u'lights'][unicode(key)][u'state'][u'bri']
                if(bri==0 or bri==254):
                        bri = scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                else:
                        bri = scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                        bri = bri+1
#               bri= scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                sat= huedic[u'lights'][unicode(key)][u'state'][u'sat']
                if(sat==0 or sat==254):
                        sat = scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                else:
                        sat = scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                        sat = sat+1
#               sat= scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                reach= huedic[u'lights'][unicode(key)][u'state'][u'reachable']
#                dim = scale_hsv(bri,1.0,100.0,100.0,1.0)
                dim=100-bri
                dic_function(id,on,dim,hue,sat,bri,reach)
                dic[int(key)]=dic.pop(lights[key][u'name'])

	h=dic
#   pp = pprint.PrettyPrinter(indent=4)
#	pp.pprint(h)
        
	##################################################################################
	_id=int(_id1)
	if(huedic[u'lights'][unicode(_id)][u'state'][u'reachable']==True):
		# all the following are the initial parameters di,iai,vi,hi,si and final parameters after updating the dictionary is df,iaf,vf,hf,sf
		di=h[_id]["state_dict"]["dimming"]
		iai=h[_id]["state_dict"]["isActive"]
                vi=h[_id]["state_dict"]["params"]["v"]
		hi=h[_id]["state_dict"]["params"]["h"]
		si=h[_id]["state_dict"]["params"]["s"]

                update(h[_id]["state_dict"],_dic)
                if   (_dic.has_key('dimming')==True  and _dic["params"].has_key('v')==False):
			if(_dic["dimming"]!=100):
                        	h[_id]["state_dict"]["params"]["v"]=100-_dic["dimming"]
				print("yes1")
                        	error="success"
			else:
				h[_id]["state_dict"]["isActive"]=False
				print("yes2")	
                                h[_id]["state_dict"]["params"]["v"]=vi
                                h[_id]["state_dict"]["params"]["h"]=hi
                                h[_id]["state_dict"]["params"]["s"]=si

                elif (_dic.has_key('dimming')==False and _dic["params"].has_key('v')==True):
                        h[_id]["state_dict"]["dimming"]=100-_dic["params"]["v"]
                        error="success"
			print("yes3")
                elif (_dic.has_key('dimming')==True  and _dic["params"].has_key('v') ==True):
                        if (_dic["dimming"]+_dic["params"]["v"]==100):
	                        if(_dic["dimming"]!=100):
					h[_id]["state_dict"]["dimming"]=_dic["dimming"]
        	                        h[_id]["state_dict"]["params"]["v"]=_dic["params"]["v"]
                	                error="success"
					print("yes4")
                        	else:
					print ("yes5")
                                	h[_id]["state_dict"]["isActive"]=False
                			h[_id]["state_dict"]["params"]["v"]=vi
                			h[_id]["state_dict"]["params"]["h"]=hi
                			h[_id]["state_dict"]["params"]["s"]=si
					error=("success,toggeled isActive")

                        else:
				print("yes6")
                                h[_id]["state_dict"]["params"]["v"]=_dic["params"]["v"]
				h[_id]["state_dict"]["dimming"]=100-_dic["params"]["v"]
                                error="Error: error may occur due to dimming and v parameters conflict,Priority given to v"
                else:
                        error=("success")
 

                iaf = h[_id]["state_dict"]["isActive"]
                df = h[_id]["state_dict"]["dimming"]
                hf = h[_id]["state_dict"]["params"]["h"]
                hf = scale_hsv(hf, 1.0, 100.0, 0.0, 65535.0)
                vf = h[_id]["state_dict"]["params"]["v"]
                vf = scale_hsv(vf, 1.0, 100.0, 0.0, 254.0)
                sf = h[_id]["state_dict"]["params"]["s"]
                sf = scale_hsv(sf, 1.0, 100.0, 0.0, 254.0)
		if(iai==True and iaf==True):
			if (di!=100 and df==100):
				h[_id]["state_dict"]["isActive"]=False
#				set_v(_id,vf)
				hsv_off(_id)
			elif(di!=100 and df!=100):
				set_hsv(_id,hf,sf,vf)
			elif(di==100 and df!=100):
				hsv_on(_id)
				time.sleep(1)
				set_hsv(_id,hf,sf,vf)
			else:
				print("dimming parameter still 100")		
		elif(iai==True and iaf==False):
#			set_v(_id,vf)
			hsv_off(_id)
			h[_id]["state_dict"]["isActive"]=False
		elif(iai==False and iaf==True):
			hsv_on(_id)
			time.sleep(1)
                        if (di!=100 and df==100):
                                h[_id]["state_dict"]["isActive"]=False
#                                set_v(_id,vf)
                                hsv_off(_id)
                        elif(di!=100 and df!=100):
                                set_hsv(_id,hf,sf,vf)
                        elif(di==100 and df!=100):
                                hsv_on(_id)
                                time.sleep(1)
                                set_hsv(_id,hf,sf,vf)
                        else:
                                print("dimming parameter still 100")

		else:
			print("bulb is still off")
                time.sleep(1)
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(h)
                return True,error
        else:
#                pp = pprint.PrettyPrinter(indent=4)
#                pp.pprint(h)
                return False,"Bulb not reachable"



def apply_huegrp_state(_bridgeIP,_id2,_dic):
        huedic={}
        huedic=get_api()
	global dic
        dic={}
        dic.clear()
        index = 0
        g={}
        for key  in huedic[u'groups']:
                id = huedic[u'groups'][unicode(key)][u'name']
                on= huedic[u'groups'][unicode(key)][u'action'][u'on']
                hue= huedic[u'groups'][unicode(key)][u'action'][u'hue']
                if(hue==0 or hue==65535):
                        hue = scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                else:
                        hue = scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                        hue = hue+1
#               hue=scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                bri= huedic[u'groups'][unicode(key)][u'action'][u'bri']
                if(bri==0 or bri==254):
                        bri = scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                else:
                        bri = scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                        bri = bri+1
#               bri= scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                sat= huedic[u'groups'][unicode(key)][u'action'][u'sat']
                if(sat==0 or sat==254):
                        sat = scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                else:
                        sat = scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                        sat = sat+1
#               sat= scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                reach= huedic[u'groups'][unicode(key)][u'state'][u'any_on']
                dim = 100-bri
                dic_function(id,on,dim,hue,sat,bri,reach)
                dic[int(key)]=dic.pop(lights[key][u'name'])

        g=dic
	#######################################################################################
	_id=int(_id2)
        if(huedic[u'groups'][unicode(_id)][u'state'][u'any_on']==True):
                di=g[_id]["state_dict"]["dimming"]
                iai=g[_id]["state_dict"]["isActive"]
                vi=g[_id]["state_dict"]["params"]["v"]
                hi=g[_id]["state_dict"]["params"]["h"]
                si=g[_id]["state_dict"]["params"]["s"]

                update(g[_id]["state_dict"],_dic)
                if   (_dic.has_key('dimming')==True  and _dic["params"].has_key('v')==False):
                        if(_dic["dimming"]!=100):
                                g[_id]["state_dict"]["params"]["v"]=100-_dic["dimming"]
                                print("yes1")
                                error="success"
                        else:
                                g[_id]["state_dict"]["isActive"]=False
                                print("yes2")
                                g[_id]["state_dict"]["params"]["v"]=vi
                                g[_id]["state_dict"]["params"]["h"]=hi
                                g[_id]["state_dict"]["params"]["s"]=si

                elif (_dic.has_key('dimming')==False and _dic["params"].has_key('v')==True):
                        g[_id]["state_dict"]["dimming"]=100-_dic["params"]["v"]
                        error="success"
                        print("yes3")
                elif (_dic.has_key('dimming')==True  and _dic["params"].has_key('v') ==True):
                        if (_dic["dimming"]+_dic["params"]["v"]==100):
                                if(_dic["dimming"]!=100):
                                        g[_id]["state_dict"]["dimming"]=_dic["dimming"]
                                        g[_id]["state_dict"]["params"]["v"]=_dic["params"]["v"]
                                        error="success"
                                        print("yes4")
                                else:
                                        print ("yes5")
                                        g[_id]["state_dict"]["isActive"]=False
                                        g[_id]["state_dict"]["params"]["v"]=vi
                                        g[_id]["state_dict"]["params"]["h"]=hi
                                        g[_id]["state_dict"]["params"]["s"]=si
                                        error=("success,toggeled isActive")

                        else:
                                print("yes6")
                                g[_id]["state_dict"]["params"]["v"]=_dic["params"]["v"]
                                g[_id]["state_dict"]["dimming"]=100-_dic["params"]["v"]
                                error="Error: error may occur due to dimming and v parameters conflict,Priority given to v"
                else:
                        error=("success")


                iaf = g[_id]["state_dict"]["isActive"]
                df = g[_id]["state_dict"]["dimming"]
                hf = g[_id]["state_dict"]["params"]["h"]
                hf = scale_hsv(hf, 1.0, 100.0, 0.0, 65535.0)
                vf = g[_id]["state_dict"]["params"]["v"]
                vf = scale_hsv(vf, 1.0, 100.0, 0.0, 254.0)
                sf = g[_id]["state_dict"]["params"]["s"]
                sf = scale_hsv(sf, 1.0, 100.0, 0.0, 254.0)
                print "iai",iai,"   iaf",iaf
                if(iai==True and iaf==True):
                        if (di!=100 and df==100):
                                hsvgrp_off(_id)
                                g[_id]["state_dict"]["isActive"]=False
                        elif(di!=100 and df!=100):
                                set_hsvgrp(_id,hf,sf,vf)
                        elif(di==100 and df!=100):
                                hsvgrp_on(_id)
                                time.sleep(1)
                                set_hsvgrp(_id,hf,sf,vf)
                        else:
                                print("dimming parameter still 100")
                elif(iai==True and iaf==False):
                        hsvgrp_off(_id)
                        g[_id]["state_dict"]["isActive"]=False
                elif(iai==False and iaf==True):
                        hsvgrp_on(_id)
                        time.sleep(1)
                        if (di!=100 and df==100):
                                hsvgrp_off(_id)
                                g[_id]["state_dict"]["isActive"]=False
                        elif(di!=100 and df!=100):
                                set_hsvgrp(_id,hf,sf,vf)
                        elif(di==100 and df!=100):
                                hsvgrp_on(_id)
                                time.sleep(1)
                                set_hsvgrp(_id,hf,sf,vf)
                        else:
                                print("dimming parameter still 100")

                else:
                        print("group(bulb) is still off")
                time.sleep(1)
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(g)
                return True,error
        else:
#                pp = pprint.PrettyPrinter(indent=4)
#                pp.pprint(h)
                return False,"group(Bulb) not reachable"



def fetch_huegrp_state(_bridgeIP):
        huedic={}
        huedic=get_api()
	global dic
        dic={}
	dic.clear()
        for key  in huedic[u'groups']:
                id = huedic[u'groups'][unicode(key)][u'name']
		
                on= huedic[u'groups'][unicode(key)][u'action'][u'on']
                hue= huedic[u'groups'][unicode(key)][u'action'][u'hue']
                if(hue==0 or hue==65535):
                        hue = scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                else:
                        hue = scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                        hue = hue+1
#                hue=scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                bri= huedic[u'groups'][unicode(key)][u'action'][u'bri']
                if(bri==0 or bri==254):
                        bri = scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                else:
                        bri = scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                        bri = bri+1
#                bri= scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                sat= huedic[u'groups'][unicode(key)][u'action'][u'sat']
                if(sat==0 or sat==254):
                        sat = scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                else:
                        sat = scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                        sat = sat+1
#                sat= scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                reach= huedic[u'groups'][unicode(key)][u'state'][u'any_on']
                dim = 100-bri
                dic_function(id,on,dim,hue,sat,bri,reach)
                dic[int(key)]=dic.pop(lights[key][u'name'])
        return dic


def fetch_hue_state(bridgeIP):
	huedic={}
	huedic=get_api()
	global dic
	dic={}
	dic.clear()
	for key  in huedic[u'lights']:
		id = huedic[u'lights'][unicode(key)][u'name']
		on= huedic[u'lights'][unicode(key)][u'state'][u'on']
		hue= huedic[u'lights'][unicode(key)][u'state'][u'hue']
		if(hue==0 or hue==65535):
			hue = scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
		else:
                        hue = scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
                        hue = hue+1
#		hue=scale_hsv(hue, 0.0, 65535.0, 1.0, 100.0)
		bri= huedic[u'lights'][unicode(key)][u'state'][u'bri']
                if(bri==0 or bri==254):
                        bri = scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                else:
                        bri = scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
                        bri = bri+1
#		bri= scale_hsv(bri, 0.0, 254.0, 1.0, 100.0)
		sat= huedic[u'lights'][unicode(key)][u'state'][u'sat']
                if(sat==0 or sat==254):
                        sat = scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                else:
                        sat = scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
                        sat = sat+1
#		sat= scale_hsv(sat, 0.0, 254.0, 1.0, 100.0)
		reach= huedic[u'lights'][unicode(key)][u'state'][u'reachable']
#		dim = scale_hsv(bri,1.0,100.0,100.0,1.0)
		dim = h[int(key)]["state_dict"]["dimming"]
		dic_function(id,on,dim,hue,sat,bri,reach)
		dic[int(key)]=dic.pop(lights[key][u'name'])
        return dic
#	return h
