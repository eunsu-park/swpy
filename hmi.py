import urllib
import ftplib
import string
#import datetime

def download_HTTP_file(strSrcUrl, strDstFile):
    import httplib
    import socket
    import time
    import string

    if (strSrcUrl.find("http://") != 0):
        print("strSrcUrl is invalid url, " + strSrcUrl + ".")
        return False

    i = strSrcUrl.find("/", 7)
    if (i < 9):
        print("strStrUrl is invalid url, " + strSrcUrl + ".")
        return False

    domain_name = strSrcUrl[7:i]
    file_path = strSrcUrl[i:]

    nTrial = 5
    t = 0
    for t in range(1, nTrial):

        try:
            conn = httplib.HTTPConnection(domain_name)
            conn.request("GET", file_path)
            r = conn.getresponse()
            if r.status != 200:
                print(r.status, r.reason)
                print("Can not download the file, " + strSrcUrl + ".")
                conn.close()
            else:
                contents = r.read()
                conn.close()

            t = 0
            break
        except httplib.HTTPException as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.NotConnected as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.InvalidURL as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.UnknownProtocol as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.UnknownTransferEncoding as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.UnimplementedFileMode as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.IncompleteRead as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.ImproperConnectionState as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.CannotSendRequest as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.CannotSendHeader as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.ResponseNotReady as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except httplib.BadStatusLine as msg:
            #nFails = nFails + 1
            AlertMessage(msg)
        except socket.error as e:
            AlertMessage("Socket exception error, %s."%e)
        # finally:
            #nFails = nFails + 1
        #AlertMessage("Unknown exception in DownloadHttpFile().")

#        AlertMessage("It will be start again after several seconds.")
        time.sleep(5)

    if (t > 0):
        return False

    #print (strDstFile)

    make_directory(strDstFile)

    f = open(strDstFile, "w")
    f.write(contents)
    f.close()

    print ("Success downloading the file, " + strSrcUrl + ".")

    return True


def get_list_from_HTTP_hourly(cur, ext_list = None):
    import types
    list = []

    ################################
    # download fits files.   #
    ################################
    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + cur.strftime("%Y/%m/%d/") 
    try:
        response = urllib.urlopen(strurl)
        if (response == None):
            return list

        str = response.read()
        response.close()
        
    except:
        return list

    lines = str.split("\n")
    index = 0
    for str_line in lines:
        if (string.find(str_line, '<td><a href="hmi.M_720s_nrt.') == -1):
            continue
        else:
    #	    print str_line
            index = string.find(str_line, '<td><a href="hmi.M_720s_nrt.')

            begin = index + 13
            end = begin + 39
            file_name = str_line[begin:end]
            list.append(strurl + file_name)

    return list

'''
    ###################################
    # download fits files yesterday.  #
    ###################################
    if (now.strftime("%H") == "01"):
        pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1)

        strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + pre.strftime("%Y/%m/%d/") 
        try:
            response = urllib.urlopen(strurl)
            if (response == None):
                return list

            str = response.read()
            response.close()
        except:
            return list

        lines = str.split("\n")
        index = 0
        for str_line in lines:
            if (string.find(str_line, '<td><a href="hmi.M_720s_nrt.') == -1):
                continue
            else:
    #	    print str_line
                index = string.find(str_line, '<td><a href="hmi.M_720s_nrt.')

                begin = index + 13
                end = begin + 39
                file_name = str_line[begin:end]
    #	        print file_name
                list.append(strurl + file_name)
'''

    



# 2015. 07. 06. modified

def get_list_from_HTTP(pre, now, ext_list = None):
    import types

    ################################
    #   begin at 15:00 yesterday   #
    ################################
    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + pre.strftime("%Y/%m/%d/") 
#    print strurl
    try:
        response = urllib.urlopen(strurl)
        
        if (response == None):
            return ""

        str = response.read()
        response.close()
#	print str
    finally:
        list = []

    compare_str = '<td><a href="hmi.M_720s_nrt.' + pre.strftime("%Y%m%d") + '_15'
    lines = str.split("\n")
    index = 0
    for str_line in lines:
        if (string.find(str_line, '<td><a href="hmi.M_720s_nrt.') == -1):
            continue
        else:
            index = string.find(str_line, '<td><a href="hmi.M_720s_nrt.')
            compare_index = string.find(str_line, '_TAI.fits">') - 6

#	    print str_line[compare_index:compare_index+2]
            if (str_line[compare_index:compare_index+2] >= '15'):
                begin = index + 13
                end = begin + 39
                file_name = str_line[begin:end]
#	        print file_name
                list.append(strurl + file_name)

###############################
#   end at 15:00 today        #
###############################
    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + now.strftime("%Y/%m/%d/")
    try:
        response = urllib.urlopen(strurl)
        if (response == None):
            return ""

        str = response.read()
        response.close()
#       print str
    except:
        return list

    lines = str.split("\n")
    index = 0
    for str_line in lines:
        if (string.find(str_line, '<td><a href="hmi.M_720s_nrt.') == -1):
            continue
        else:
#           print str_line
            index = string.find(str_line, '<td><a href="hmi.M_720s_nrt.')
            compare_index = string.find(str_line, '_TAI.fits">') - 6

            if (str_line[compare_index:compare_index+2] <= '15'):
                begin = index + 13
                end = begin + 39
                file_name = str_line[begin:end]
#	       	print file_name
                list.append(strurl + file_name)


    return list


# 2014.12.02. modified 
'''
def get_list_from_HTTP(pre, now, ext_list = None):
    import types

#    cur = datetime.datetime.utcnow() - datetime.timedelta(days=1)
#    print cur.strftime("%Y/%m/%d")

    try:
        response = urllib.urlopen("http://jsoc.stanford.edu/data/hmi/fits/" + pre.strftime("%Y/%m/%d"))
        if (response == None):
            return ""

        str = response.read()
        response.close()
        print str
    finally:
        list = []
    
    begin = 0
    end = 0
    index1 = 0
    index2 = 0
    index = 0

    lines = str.split("\n")

    for str_line in lines:
        print ("[%d]%s", index, str_line)
#        index = index + 1
#        str_line = lines[index]

        index1 = string.find(str_line, pre[0:11])
        index2 = string.find(str_line, now[0:11])
#        print (str_line, pre[0:11], now[0:11], index1, index2)

        if ((index1 == -1) and (index2 == -1)):
            continue

        if (index1 == -1):
            index = index2
        elif (index2 == -1):
            index = index1

        if ((str_line[index:index+17] >= pre) and (str_line[index:index+17] <= now)):
           # print str_line[index:index+17], str_line
            begin = string.find(str_line, "<a href=\"")
            if (begin == -1):
                continue
            begin = begin + 9
            end = string.find(str_line, "\"", begin)
            if (end == -1):
                continue

            file_name = str_line[begin:end]
            if (string.find(file_name, "hmi") == -1):
                continue

            if (ext_list != None):
                for ext_name in ext_list:
                    if (string.find(file_name, "." + ext_name) != -1):
                        list.append(file_name)
            else:
                list.append(file_name)

    return list
'''



def make_directory(filepath):
    import os

#    print (os.path.dirname(filepath))
    filepath = os.path.dirname(filepath) + "/"
    if (os.path.exists(filepath) == False):
        os.makedirs(os.path.dirname(filepath))
    return True

def download_FITS():
    import datetime

    pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1, hours = 15)
    now = datetime.datetime.utcnow() - datetime.timedelta(hours = 15)
#    pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1)
#    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + pre.strftime("%Y/%m/%d/")

    list = get_list_from_HTTP(pre, now, "fits")

    local_dir = "./data/flare_forecast_in/" + now.strftime("%Y%m%d") + "/"
    ###local_dir = "/data/flare_forecast_in/" + now.strftime("%Y%m%d") + "/"
   
    print (len(list))

    for line in list:
#	print line
#	file_path = strurl + line
        file_index = string.rfind(line, '/') + 1
        local_path = local_dir + line[file_index:]
        rv = download_HTTP_file(line, local_path)
        if (rv == True):
            print ("Downloaded %s. "%line)
        else:
            print ("Can not Download %s. "%local_path)


def download_FITS_hourly():
    import datetime

    now = datetime.datetime.utcnow()
    list = get_list_from_HTTP_hourly(now, "fits")

    local_dir = "./data/flare_forecast_in/hourly/" + now.strftime("%Y%m%d") + "/"
    ###local_dir = "/data/flare_forecast_in/hourly/" + now.strftime("%Y%m%d") + "/"
   
    print (len(list))

    for line in list:
#	print line
#	file_path = strurl + line
        file_index = string.rfind(line, '/') + 1
        local_path = local_dir + line[file_index:]
        rv = download_HTTP_file(line, local_path)
        if (rv == True):
            print ("Downloaded %s. "%line)
        else:
            print ("Can not Download %s. "%local_path)


    if (now.strftime("%H") == "01"):
        pre = now - datetime.timedelta(days = 1)
        list = get_list_from_HTTP_hourly(pre, "fits")

        local_dir = "./data/flare_forecast_in/hourly/" + pre.strftime("%Y%m%d") + "/"
        ###local_dir = "/data/flare_forecast_in/hourly/" + pre.strftime("%Y%m%d") + "/"
   
        print (len(list))

        for line in list:
            file_index = string.rfind(line, '/') + 1
            local_path = local_dir + line[file_index:]
            rv = download_HTTP_file(line, local_path)
            if (rv == True):
                print ("Downloaded %s. "%line)
            else:
                print ("Can not Download %s. "%local_path)

# 2014.12.02. modified.
'''
def download_FITS():
    import datetime

    pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1)
#    pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1, hours = 15)
#    now = datetime.datetime.utcnow() - datetime.timedelta(hours = 15)

#    print pre, now

#    dt_pre = pre.strftime("%d-%b-%Y 10:00")
#    dt_now = now.strftime("%d-%b-%Y 10:59")

#    print dt_pre, dt_now

    list = get_list_from_HTTP(pre, "fits")
    local_dir = "/data/flare_forecast_in/" + datetime.datetime.utcnow().strftime("%Y%m%d") + "/"

    for line in list:
#        print line
        file_path = "http://swrl.njit.edu/hmi/" + line
        local_path = local_dir + line
        rv = download_HTTP_file(file_path, local_path)
        if (rv == True):
            print ("Downloaded %s. "%file_path)
        else:
            print ("Can not downloaded %s. "%local_path)
'''

def upload_FTP():
    import datetime

#    now  = datetime.datetime.today() - datetime.timedelta(days=1)
    now = datetime.datetime.today()
    file_name = now.strftime("%Y%m%d") + ".txt"
    local_path = "./data/flare_forecast_out/" + file_name
    remote_dir = "./data/kasi/flare_forecast/" + now.strftime("%Y") + "/"
    latest_dir = "./data/kasi/flare_forecast/"

    ###local_path = "/data/flare_forecast_out/" + file_name
    ###remote_dir = "/data/kasi/flare_forecast/" + now.strftime("%Y") + "/"
    ###latest_dir = "/data/kasi/flare_forecast/"


    try:
        connect = ftplib.FTP("swc.kasi.re.kr", "swc", "s0s.kasi.2010")
    except Exception as e:
        print (e)
    else:
        try:
            file = open(local_path, "rb")
        except Exception as e:
            print ("File open failed...")
        else:
            connect.cwd(remote_dir)
            try:
                connect.storbinary("STOR " + file_name, file)
            except Exception as e:
                print (e)
            else:
                file.close()

        try:
            file = open(local_path, "rb")
        except Exception as e:
            print ("Latest file open failed...")
        else:
            connect.cwd(latest_dir)
            try:
                connect.storbinary("STOR latest.txt", file)
            except Exception as e:
                print (e)
            else:
                file.close()
                connect.quit()

    return True


def upload_corhole_FTP():
    import datetime
    import os

    now = datetime.datetime.today()
    if (now.strftime("%H") <= "09"):
        now  = datetime.datetime.today() - datetime.timedelta(days=1)
    #now = datetime.datetime.today()
    
        print (now.strftime("%Y%m%d %H%M"))
        file_name = now.strftime("%Y%m%d") + ".txt"
        #file_name = "20160416.txt"

        local_path = "/NAS/hp06/services/corh_aia/" + now.strftime("%Y") + "/" + now.strftime("%Y%m") + "/" + now.strftime("%Y%m%d") + "/"
        remote_dir = "/data/kasi/corh_aia/" + now.strftime("%Y") + "/" + now.strftime("%Y%m%d") + "/"

        local_path = "/NAS/hp06/services/corh_aia/" + now.strftime("%Y") + "/" + now.strftime("%Y%m") + "/" + now.strftime("%Y%m%d") + "/"
        remote_dir = "/data/kasi/corh_aia/" + now.strftime("%Y") + "/" + now.strftime("%Y%m%d") + "/"


    #    latest_dir = "/data/kasi/flare_forecast/"
        #local_path = "/NAS/hp06/services/corh_aia/2016/201604/20160417/"
        try:
            files = os.listdir(local_path)
            os.chdir(local_path)
        except Exception as e:
            print (e)
        return False

    #    rb = check_dir(remote_dir)
    #    if (rb == False):
    #	return False

        try:
            connect = ftplib.FTP("swc.kasi.re.kr", "sos", "dnwnghksrud105")
        except Exception as e:
            print (e)
        return False
    
    else:
        check_dir_rec(connect, remote_dir[1:-1].split('/'))
        connect.cwd(remote_dir)
        for f in files:
            #print "file = ", f
            try:
                    file = open(f, "rb")
            #print "file = ", f
            except Exception as e:
                print ("File open failed...")
            else:
                try:
                    connect.storbinary("STOR " + f, file)
                except Exception as e:
                    print (e)
                else:
                    file.close()

        connect.quit()

    return True

def check_dir(ftp, dir):
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    #print ftp.retrlines('LIST')
    for f in filelist:
	#print "[", f, "]"
        if ( (f.split()[-1] == dir) and (f.find('<DIR>') != -1) ):
	        return True
    return False

def check_dir_rec(ftp, descending_path_split):
    if len(descending_path_split) == 0:
	    return

    #print descending_path_split

    next_level_dir = descending_path_split.pop(0)
    #print "check_dir_rec : ", next_level_dir
    rb = check_dir(ftp, next_level_dir)
    if (rb == False):   
#print next_level_dir
        ftp.mkd(next_level_dir)
        ftp.cwd(next_level_dir)

        check_dir_rec(ftp, descending_path_split)


if __name__ == "__main__":
    import sys
    import datetime
    import time

    #download_FITS_hourly()
    #upload_corhole_FTP()

    if (datetime.datetime.today().hour == 2):
        download_FITS()
    #if (datetime.datetime.today().hour == 7):
    print('here')
    upload_FTP()
    
    #if (datetime.datetime.today().hour == 11):
    #upload_corhole_FTP()
