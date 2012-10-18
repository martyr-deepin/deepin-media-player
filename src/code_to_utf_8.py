import chardet    
    
def auto_decode(s):    
    ''' auto detect the code and return unicode object. '''
    encoding = "gbk"
    try:
        unicode_code = s.decode(encoding)
    except:    
        try:
            encoding = chardet.detect(s)["encoding"]
        except:    
            return s
        else:
            return s.decode(encoding).encode("utf-8")
    else:    
        return unicode_code.encode("utf-8")
