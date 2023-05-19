# [header를 프린트 할 때 정제된 형식으로 표출하고싶다]
# 1. header_preview 함수를 따로 구현한다
# 2. !header 클래스를 만든 다음에 __repr__함수 구현?

import numpy as np
from dataset.lib.header import Header
import dataset.lib.structured_array as strc_array
from dataset.lib.utilities import *
import textwrap

def goes_open(filepath):
    check_value_type(filepath, str, "goes_open")
    check_file(filepath, "goes_open")

    with open(filepath, 'r') as f:
        goes = None
        
        data_list = f.readline()
        if("Gp_part" in data_list):
            goes = Particle(filepath)
        elif("Gp_xr" in data_list):
            goes = Xray(filepath)
        elif("Gp_mag" in data_list):
            goes = Geomag(filepath)
        else:
            raise Exception(textwrap.dedent("""\
                                            Can't determine goes data type.
                                            \tCheck 'data_list' value in the file.\
                                            """))

    return goes
        
class _Goes():
    """
    Parameters
    ----------
    filepath: str
    names: tuple
        field names of data
    formats: tuple
        formats of data
    """
    def __init__(self, filepath, names, formats):
        #
        # Change print options of numpy
        np.set_printoptions(precision=25, threshold=20)
        
        #
        # init variable
        self.header = None
        self.data = None
        self.header_str = None
        self.filepath = filepath

        self._names = names
        self._formats = formats

        #
        # create header, data and header_str
        header_lines, data_lines = self._load(filepath)
        hd = self._parsing_header(header_lines)
        data = self._parsing_data(data_lines, names, formats)        
        header = self._add_info_to_header(hd, data)
        
        #
        # set basic member variable
        self.header = header
        self.data = data
        self.header_str = header_lines
        
    

    def __repr__(self):
        rep = textwrap.dedent("""\
            {obj_type}
            -----------------------------------
            header:\t\t dict
            data:\t\t structured array(np.ndarray)
            header_str:\t list\
            """).format(obj_type=type(self))
        return rep
    
    def info(self):
        header = self.header
        data = self.data

        check_value_type(header, Header, "info")
        check_value_type(data, np.ndarray, "info")

        fields = data.dtype.names
        data_num = data.size * len(fields)

        info = textwrap.dedent("""\
            Title:\t\t\t {title}
            Obs start date:\t\t {obs_start_date}
            Obs start date:\t\t {obs_end_date}
            Institute:\t\t {institute}
            Instrument:\t\t {instrument}
            Fields:\t\t\t {fields}
            Dimension:\t\t {shape}
            Data num:\t\t {data_num}
            Object:\t\t\t {object}
            Longitude of SAT:\t {location}
            Source:\t\t\t {src}
            {data}\
            """).format(title=header["Title"],
                        obs_start_date=header["Obs_start_date"],
                        obs_end_date=header["Obs_end_date"],
                        institute=header["Institute"],
                        instrument=header["Source"],
                        fields=fields,
                        shape=data.shape,
                        data_num=data_num,
                        object=header["Object"],
                        location=header["Location"],
                        src=header["Src_url"],
                        data=data
                        )
        print(info)

    # @property
    # def size(self):
    #     return np.shape(self.data)
    
    # @property
    # def columns(self):
    #     return self.data.dtype.names

    ############## header ##################
    """
    def header_preview(self):
        format = "{0}: {1}\n"
        
        content =""
        for key, value in self.header.items():
            content += format.format(key, value)
        return content
    """
    ########################################    

    def _add_info_to_header(self, header, data):
        """
        Parameters
        ----------
        header: dict
        
        Returns
        -------
        header: dict
        """

        check_value_type(header, dict, "_add_info_to_header")
        check_value_type(data, np.ndarray, "_add_info_to_header")

        #
        # add info from header info
        header["Title"] = header["Note"].pop()
        """
        interval = header["filename"].split(".txt")[0][-2:]
        time_itv, time_unit = int(interval[0]), interval[1]
        if(time_unit == "m"):
            time_itv *= 60
        header["time_interval"] = time_itv
        """

        #
        # goes common info
        header["Institute"] = "Noaa"
        header["Object"] = "Sun"
        header["Src_url"] = "https://services.swpc.noaa.gov/json/goes/primary"
        header["Comment"] = ""
        header["History"] = ""
        header["Keycomments"] = {
                                "Location": "Longitude of satellite.",
                                }
        #
        # add info from data
        # NOTE: column명이 바뀌면 에러남 / 무슨 형태로 저장하지? (현재: np.datetime64)
        if("Date" in data.dtype.names):
            header["Obs_start_date"] = str(data["Date"][0])
            header["Obs_end_date"] = str(data["Date"][-1])

        return header

    # NOTE
    # - header_delimiters: goes에 맞게 하드 코딩?
    # - goes 말고도 다른 곳에서도 쓰일 가능성이 있을까?
    #    (+) header, data의 페어가 여러개라면?
    def _load(self, filepath):
        """
        Parameters
        ----------
        filepath: str
            filepath to read
        
        Returns
        -------
        header_lines: list
            lines of header
        data_lines: list
            lines of data
        """
        check_value_type(filepath, str, "_load")
        check_file(filepath, "_load")

        header_delimiters = ["#", ":"]
        header_lines = []
        data_lines = []

        with open(filepath, "r") as f:
            # NOTE: f.readlines(): contains "\n"
            for line in f.read().splitlines():
                if(line[0] in header_delimiters):
                    header_lines.append(line)
                    continue
                data_lines.append(line)
        return header_lines, data_lines

    # TODO: Label, Units -> dict형태로 보여주는 것이 좋은지 질문할 것
    def _parsing_header(self, header_lines):
        """
        Parameters
        ----------
        header_lines: list
            lines of header
        
        Returns
        -------
        header: dict
        """
        check_value_type(header_lines, list, "_parsing_header")

        header_delimiters=["#", ":"]
        dict_delimiter = ":"
        ############## header ##################
        header = Header()
        # header = {}
        ########################################
        notes = []
        labels = []
        units = []
        prev_key = ""
        
        # NOTE
        # 1. key, value는 모두 구분자, 양옆 whitespace를 제외한다.
        # 2. column 정보는 포함하지 않음
        # 3. header와 data를 나누는 구분자(------)는 포함하지 않음
        # 4. key, value 형태인 line의 바로 뒷 line이 앞에 whitespace를 2 이상 가지고 있다면(맨 앞의 :,# 같은 구분자 제외)
        #    앞의 key에 해당하는 value라고 간주함.
        #    -> 이어지는 value라고 생각되어지지 않는 경우:
        #       1) 앞의 whitespace가 1개 이하인 경우
        #       2) 빈 줄이 한개 이상인 경우
        #    (+) value를 이어붙일 떄 앞에 whitespace 하나 추가한다
        #        ex) {'key':'value value'}
        # 5. key, value 형태가 아닌 line은 모두 'Note' key에 넣는다
        for i, line in enumerate(header_lines):
            # Remove header delimiters and both leading and trailing whitespace.
            if(any(dlmt == line[0] for dlmt in header_delimiters)):
                line = line[1:]
            
            if(len(line)-len(line.lstrip()) < 2):
                prev_key = ""

            # remove whitespace of head and tail
            line = line.strip()
            
            # Skip from column to end.
            if(i >= len(header_lines)-3):
                continue

            if(line == ""):
                prev_key == ""
                continue

            # Put anything that is not in the key-value form in 'note'.
            if(dict_delimiter not in line):
                # add unfinished value of prev key
                if(prev_key != ""):
                    line = " {}".format(line)
                    if(prev_key == "Label"):
                        labels.append(labels.pop() + line)
                    elif(prev_key == "Units"):
                        units.append(units.pop() + line)
                    else:
                        header[prev_key] += line
                    continue

                notes.append(line)
                continue

            key, value = line.split(dict_delimiter, 1)
            key = key.strip()
            value = value.strip()

            if(key == "Label"):
                labels.append(value)
            elif(key == "Units"):
                units.append(value)
            else:
                header[key] = value
            
            prev_key = key

        header["Note"] = notes
        header["Label"] = labels
        header["Units"] = units

        return header

    def _parsing_data(self, data_lines, names, formats):
        """
        Parameters
        ----------
        data_lines: list
            lines of data
        names: tuple
            data columnes
        formats: tuple
            data type for each data column

        Returns
        -------
        data: list
            data: np.ndarray
        """
        check_value_type(data_lines, list, "_parsing_data")
        check_value_type(names, tuple, "_parsing_data")
        check_value_type(formats, tuple, "_parsing_data")

        data = []
        date_format = "{0}-{1}-{2}T{3}:{4}"

        for line in data_lines:
            if(line.strip == ""):
                continue
            
            values = line.split()
            Y, m, d, HM = values.pop(0), values.pop(0), values.pop(0), values.pop(0)
            H, M = HM[:2], HM[2:]
            # date = datetime(int(Y), int(m), int(d), int(H), int(M))
            date = date_format.format(Y, m, d, H, M)
            


            data_tuple = (date,)
            for value in values:
                data_tuple += (value,)
            
            data.append(data_tuple)
        data = np.array(data, dtype={'names':names, 'formats':formats})

        return data

    '''
    # NOTE: 보류
    def convert_object_to_datetime(self, obj):
        """
        Parameters
        ----------
        obj: np.datetime64, str
        
        Returns
        -------
        result: datetime.datetime
        """
        result = None
        if(isinstance(obj, np.datetime64)):
            ts = (obj - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's') 
            result = datetime.utcfromtimestamp(ts)
        elif(isinstance(obj, str)):
            try:
                result = datetime.strptime(obj, "%Y-%m-%d %H:%M UTC")
            except:
                try:
                    result = parse(obj)
                except:
                    result = None
        return result
    '''

    def plot(self):
        pass

class Particle(_Goes):
    """
    Parameters
    ----------
    filepath: str
    """
    def __init__(self, filepath):
        names = ("Date", "Satellite No", "P>1", "P>5", "P>10", "P>30", "P>50", "P>60", "P>100", "P>500", "E>2.0")
        # float 데이터 나타낼 수 있는게 이게 한계인가?
        # formats = ("object", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")
        formats = ("datetime64[s]", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")

        super().__init__(filepath, names, formats)

        # self._cls_title = "Particle"


class Xray(_Goes):
    """
    Parameters
    ----------
    filepath: str
    """
    def __init__(self, filepath):
        names = ("Date", "Satellite No", "Short", "Long")
        formats = ("datetime64[s]", "i4", "f8", "f8")
        
        super().__init__(filepath, names, formats)

class Geomag(_Goes):
    """
    Parameters
    ----------
    filepath: str
    """
    def __init__(self, filepath):
        names = ("Date", "Satellite No", "Hp", "He", "Hn", "total", "arcjet_flag")
        formats = ("datetime64[s]", "i4", "f8", "f8", "f8", "f8", "i4")
        
        super().__init__(filepath, names, formats)