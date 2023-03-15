import urllib
import ftplib
import string
import os

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


def get_list_from_HTTP_UTC(pre, now, ext_list = None):
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
    lines = response_str.split("\\n")
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

    lines = response_str.split("\\n")
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


def download_FITS_UTC():
    import datetime

    pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1, hours = 2)
    now = datetime.datetime.utcnow() - datetime.timedelta(hours = 2)

    list_fits = get_list_from_HTTP_UTC(pre, now, "fits")
    local_dir = "/data/flare_forecast_in/" + now.strftime("%Y%m%d") + "/"
   
    print(len(list_fits))

    for line in list_fits:
        file_index = line.rfind('/') + 1
        local_path = local_dir + line[file_index:]
        rv = download_HTTP_file(line, local_path)
        if (rv == True):
            print ("Downloaded %s. " % (line))
        else:
            print ("Can not Download %s. " % (local_path))       


if __name__ == "__main__" :

    import sys
    import datetime
    import time


    now = datetime.datetime.utcnow()
    str_now = str(now)
    Date, Time = str_now.split(' ')
    now = datetime.datetime.strptime("%s 00:00:00.000000" % (Date), '%Y-%m-%d %H:%M:%S.%f')

    pre = now - datetime.timedelta(days=1)
    post = now
    print(pre)
    print(post)


    import urllib.request

    ################################
    #    get list 2 days before    #
    ################################
    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + pre.strftime("%Y/%m/%d/") 
    try:
        response = urllib.request.urlopen(strurl)
        
        response_str = str(response.read())
        response.close()
    finally:
        list_fits = []

    compare_str = '<td><a href="hmi.M_720s_nrt.' + pre.strftime("%Y%m%d") + '_15'
    lines = response_str.split("\\n")
    print(len(lines))
    index = 0
    for str_line in lines:
        if str_line.find('<td><a href="hmi.M_720s_nrt.') == -1 :
            continue
        else:
            index = str_line.find('<td><a href="hmi.M_720s_nrt.')
            compare_index = str_line.find('_TAI.fits">') - 6

            begin = index + 13
            end = begin + 39
            file_name = str_line[begin:end]
            list_fits.append(strurl + file_name)


    strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + now.strftime("%Y/%m/%d/")
    response = urllib.request.urlopen(strurl)

    response_str = str(response.read())
    response.close()

    lines = response_str.split("\\n")
    index = 0
    for str_line in lines:
        if str_line.find('<td><a href="hmi.M_720s_nrt.') == -1 :
            continue
        else:
            index = str_line.find('<td><a href="hmi.M_720s_nrt.')
            compare_index = str_line.find('_TAI.fits">') - 6

            if (str_line[compare_index:compare_index+2] == '00'):
                begin = index + 13
                end = begin + 39
                file_name = str_line[begin:end]
                list_fits.append(strurl + file_name)

    print(list_fits)






    # hours = datetime.datetime.today().hour

    # pre = datetime.datetime.utcnow() - datetime.timedelta(days = 1, hours = hours)
    # now = datetime.datetime.utcnow() - datetime.timedelta(hours = hours)
    # print(pre)
    # print(now)

    # # import urllib.request

    # ################################
    # #   begin at 15:00 yesterday   #
    # ################################
    # strurl = "http://jsoc.stanford.edu/data/hmi/fits/" + pre.strftime("%Y/%m/%d/") 
    # response = urllib.request.urlopen(strurl)
    # response_str = str(response.read())
    # response.close()
    # list_fits = []

    # lines = response_str.split("\\n")


    # index = 0
    # for str_line in lines:
    #     print(str_line)
    #     if str_line.find('<td><a href="hmi.M_720s_nrt.') == -1 :
    #         continue
    #     else:
    #         index = str_line.find('<td><a href="hmi.M_720s_nrt.')
    #         print(index)
    #         compare_index = str_line.find('_TAI.fits">') - 6

    #         if (str_line[compare_index:compare_index+2] >= '15'):
    #             begin = index + 13
    #             end = begin + 39
    #             file_name = str_line[begin:end]
    #             list_fits.append(strurl + file_name)

    # print(list_fits)
    # for url in list_fits :
    #     print(url)