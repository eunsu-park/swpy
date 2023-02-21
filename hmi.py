import urllib
import ftplib
import string


def make_directory(filepath):
    import os
    filepath = os.path.dirname(filepath) + "/"
    if (os.path.exists(filepath) == False):
        os.makedirs(os.path.dirname(filepath))
    return True


def download_HTTP_file(strSrcUrl, strDstFile):
    import http.client
    import time

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
            conn = http.client.HTTPConnection(domain_name)
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
        except Exception as e :
            print("Exception raised %s." % (e))
        time.sleep(5)

    if (t > 0):
        return False

    make_directory(strDstFile)

    f = open(strDstFile, "wb")
    f.write(contents)
    f.close()
    print("Success downloading the file, " + strSrcUrl + ".")
    return True


def get_list_from_HTTP_hourly(cur, ext_list = None):
    import urllib.request
    list_fits = []

    ################################
    # download fits files.   #
    ################################
    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + cur.strftime("%Y/%m/%d/")

    try:
        response = urllib.request.urlopen(strurl)
        if (response == None):
            return list_fits

        response_str = str(response.read())
        response.close()
        
    except:
        return list_fits

    lines = response_str.split("\n")
    index = 0
    for str_line in lines:
        if str_line.find('<td><a href="hmi.M_720s_nrt.') == -1 :
            continue
        else:
            index = str_line.find('<td><a href="hmi.M_720s_nrt.')

            begin = index + 13
            end = begin + 39
            file_name = str_line[begin:end]
            list_fits.append(strurl + file_name)

    return list_fits




def get_list_from_HTTP(pre, now, ext_list = None):
    import urllib.request

    ################################
    #   begin at 15:00 yesterday   #
    ################################
    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + pre.strftime("%Y/%m/%d/") 
    try:
        response = urllib.request.urlopen(strurl)
        
        if (response == None):
            return ""

        response_str = str(response.read())
        response.close()
    finally:
        list_fits = []

    compare_str = '<td><a href="hmi.M_720s_nrt.' + pre.strftime("%Y%m%d") + '_15'
    lines = response_str.split("\n")
    index = 0
    for str_line in lines:
        if str_line.find('<td><a href="hmi.M_720s_nrt.') == -1 :
            continue
        else:
            index = str_line.find('<td><a href="hmi.M_720s_nrt.')
            compare_index = str_line.find('_TAI.fits">') - 6

            if (str_line[compare_index:compare_index+2] >= '15'):
                begin = index + 13
                end = begin + 39
                file_name = str_line[begin:end]
                list_fits.append(strurl + file_name)

    ###############################
    #   end at 15:00 today        #
    ###############################
    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + now.strftime("%Y/%m/%d/")
    try:
        response = urllib.request.urlopen(strurl)
        if (response == None):
            return ""

        response_str = str(response.read())
        response.close()
    except:
        return list_fits

    lines = response_str.split("\n")
    index = 0
    for str_line in lines:
        if str_line.find('<td><a href="hmi.M_720s_nrt.') == -1 :
            continue
        else:
            index = str_line.find('<td><a href="hmi.M_720s_nrt.')
            compare_index = str_line.find('_TAI.fits">') - 6

            if (str_line[compare_index:compare_index+2] <= '15'):
                begin = index + 13
                end = begin + 39
                file_name = str_line[begin:end]
                list_fits.append(strurl + file_name)

    return list_fits


def download_FITS():
    import datetime

    pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1, hours = 15)
    now = datetime.datetime.utcnow() - datetime.timedelta(hours = 15)

    list_fits = get_list_from_HTTP(pre, now, "fits")
    #local_dir = "/data/flare_forecast_in/" + now.strftime("%Y%m%d") + "/"
    local_dir = "/home/eunsu/Drives/SWPy/hmi/data/flare_forecast_in/" + now.strftime("%Y%m%d") + "/"
   
    print(len(list_fits))

    for line in list_fits:
        file_index = line.rfind('/') + 1
        local_path = local_dir + line[file_index:]
        rv = download_HTTP_file(line, local_path)
        if (rv == True):
            print ("Downloaded %s. " % (line))
        else:
            print ("Can not Download %s. " % (local_path))


def download_FITS_hourly():
    import datetime

    now = datetime.datetime.utcnow()
    list_fits = get_list_from_HTTP_hourly(now, "fits")

#    local_dir = "/data/flare_forecast_in/hourly/" + now.strftime("%Y%m%d") + "/"
    local_dir = "/home/eunsu/Drives/SWPy/hmi/data/flare_forecast_in/hourly/" + now.strftime("%Y%m%d") + "/"
   
    print(len(list_fits))

    for line in list_fits:
        file_index = line.rfind('/') + 1
        local_path = local_dir + line[file_index:]
        rv = download_HTTP_file(line, local_path)
        if (rv == True):
            print ("Downloaded %s. "%line)
        else:
            print ("Can not Download %s. "%local_path)

    if (now.strftime("%H") == "01"):
        pre = now - datetime.timedelta(days = 1)
        list_fits = get_list_from_HTTP_hourly(pre, "fits")

        #local_dir = "/data/flare_forecast_in/hourly/" + pre.strftime("%Y%m%d") + "/"
        local_dir = "/home/eunsu/Drives/SWPy/hmi/data/flare_forecast_in/hourly/" + pre.strftime("%Y%m%d") + "/"
   
        print(len(list_fits))

        for line in list_fits:
            file_index = line.rfind('/') + 1
            local_path = local_dir + line[file_index:]
            rv = download_HTTP_file(line, local_path)
            if (rv == True):
                print ("Downloaded %s. "%line)
            else:
                print ("Can not Download %s. "%local_path)




def upload_FTP():
    import datetime

#    now  = datetime.datetime.today() - datetime.timedelta(days=1)
    now = datetime.datetime.today()
    file_name = now.strftime("%Y%m%d") + ".txt"
    local_path = "/data/flare_forecast_out/" + file_name
    remote_dir = "/data/kasi/flare_forecast/" + now.strftime("%Y") + "/"
    latest_dir = "/data/kasi/flare_forecast/"

    try:
        connect = ftplib.FTP("swc.kasi.re.kr", "swc", "s0s.kasi.2010")
    except Exception, e:
        print e
    else:
        try:
            file = open(local_path, "rb")
        except Exception, e:
            print "File open failed..."
        else:
            connect.cwd(remote_dir)
            try:
                connect.storbinary("STOR " + file_name, file)
            except Exception , e:
                print e
            else:
                file.close()

        try:
            file = open(local_path, "rb")
        except Exception, e:
            print "Latest file open failed..."
        else:
            connect.cwd(latest_dir)
            try:
                connect.storbinary("STOR latest.txt", file)
            except Exception, e:
                print e
            else:
                file.close()
                connect.quit()

    return True



if __name__ == "__main__" :

    import datetime

    ## Test download_HTTP_file ##

    strSrcUrl = "http://swds.kasi.re.kr/data/arm/nasa/sdo/latest_193_1024.jpg"
    strDstFile = "/home/eunsu/Drives/SWPy/hmi/download_HTTP_file/tmp.jpg"

    download_HTTP_file(strSrcUrl, strDstFile)


    ## Test get_list_from_HTTP_hourly ##

    now = datetime.datetime.utcnow()
    list_fits = get_list_from_HTTP_hourly(now, "fits")
    print(list_fits)


    ## Test get_list_from_HTTP ##
    pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1, hours = 15)
    now = datetime.datetime.utcnow() - datetime.timedelta(hours = 15)
    list_fits = get_list_from_HTTP(pre, now, "fits")
    print(list_fits)


    ## Test download_FITS() ##
#    download_FITS()

    ## Test download_FITS_hourly ##
#    download_FITS_hourly()

    ## Test upload_FTP ##
    upload_FTP()