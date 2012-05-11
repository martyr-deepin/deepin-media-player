# coding:utf-8
#代码编辑器: 后端缓冲区
#间隙缓冲区

''' ..散列表.. '列表里面保存列表...'
[0'行号'] -> 间隙缓冲区 列表 ['a', 'b', '*', '*', 'b', 'c']
[1] ->
[2]
[3]
列表操作: append
        insert
        pop
        remove        
'''

class Buffer(object):
    def __init__(self):
        self.line_num = -1
        self.buffer_dict = []        
        
        
    def utf_8_bool(self, strings):    
        '''判斷是否爲utf-8'''
        if type(strings).__name__ == 'unicode':
            return True
        
        return False    
    
    def insert_line_index_text(self, line_num, index, strings):    
        '''向某行某坐标处->插入字符串'''
        
        if not self.error_msgbox(line_num): # 如果没有指定的行存在
            return None
        
        if not self.utf_8_bool(strings):
            strings = self.string_to_utf_8(strings)
            
        for temp_str in strings:    
            self.buffer_dict[line_num].insert(index, temp_str)
            index += 1
            
        return True        
    
    def error_msgbox(self, line_num):        
        try:
            self.buffer_dict[line_num]
        except:    
            return None
        
        return True
        
    def del_text(self, line_num, start_num, end_num):
        '''删除指定范围的字符串 [end_num > start_num]''' 
        #错误返回 None[覆盖的地方无法到达]: 比如没有的行.
        if not self.error_msgbox(line_num):
            return None
        
        if start_num > end_num: #防止start大于end
            return None
        
        for i in range(start_num, end_num + 1):
            try:
                self.buffer_dict[line_num][i]            
            except:    
                return None
            
        if start_num == end_num:
            del self.buffer_dict[line_num][start_num]
            return True
        
        for i in range(start_num, end_num + 1):
            del self.buffer_dict[line_num][start_num]            
            
        return True
        
    def cover_text(self, line_num, start_num, end_num, strings):    
        '''覆盖指定的缓冲区'''                
        
        #错误返回 None[覆盖的地方无法到达]: 比如没有的行.
        if not self.error_msgbox(line_num):
            return None
        
        if not self.utf_8_bool(strings):
            strings = self.string_to_utf_8(strings)        
            
        #覆盖 start_num 至 end_num 内的缓冲区
        i = 0
        for temp_i in range(start_num, end_num):
            self.buffer_dict[line_num][temp_i] = strings[i]
            i += 1
            
        #将剩下的字符插入 缓冲区.    
        if len(strings) > end_num - start_num:                
            i = len(strings)            
            strings = strings[end_num - start_num:]
            self.insert_line_index_text(line_num, end_num, strings)    
            
        return True 
        
    def create_list(self, line_num):    
        '''不存在则创建.'''
        if not self.error_msgbox(line_num):
            self.buffer_dict.append([])
            self.line_num += 1
            
    def del_line_text(self, line_num):        
        '''删除指定行'''
        del self.buffer_dict[line_num]
        
    def add_line_text(self, line_num, strings):
        '''指定行添加'''
        self.create_list(line_num)                
        for temp_str in self.string_to_utf_8(strings):
            self.buffer_dict[line_num].append(temp_str)
            
        return True    
            
    def string_to_utf_8(self, strings):        
        '''转换成utf-8'''
        return strings.decode("utf-8")
    
    def find_text(self, strings):
        '''查找与strings相同的字符串,返回字符的行号,开始和结束.'''        
        #([字符串,行号,开始列号,结束列号], [],)
        # line_num = 0        
        # 转换字符串
        if not self.utf_8_bool(strings):
            strings = self.string_to_utf_8(strings)                
            
        string_sum = len(strings)    
        save_dict = {}
        save_temp_strs = ""
        
        for line_num in range(0, self.line_num + 1):
            for temp_strs in self.buffer_dict[line_num]:            
                if temp_strs == u'\n':
                    break
                
                for i in range(0, string_sum):
                    try:
                       save_temp_strs  += self.buffer_dict[line_num][self.buffer_dict[line_num].index(temp_strs) + i]
                    except:    
                        break
                    
                if save_temp_strs == strings:    
                    save_dict[line_num] = [save_temp_strs, line_num, 
                                           self.buffer_dict[line_num].index(temp_strs),
                                           self.buffer_dict[line_num].index(temp_strs) + string_sum-1]                    
                save_temp_strs = ""                                
                
        return save_dict
    
    def print_buffer_dict(self):
        '''打印所有字典中的列表'''
        sum = 0
        for key in self.buffer_dict:
            print "self.buffer_dict[" + str(sum) + "]" + "=",
            for temp_str in key:
                print temp_str,
            print ""    
            sum += 1    
                        
            
if __name__ == "__main__":            
    bf = Buffer()
    str1 = "abcd中散了科技列斯卡夫健康\n"
    
    bf.add_line_text(0,str1)
    bf.add_line_text(1, "defghijhlnmopqabc")
    bf.insert_line_index_text(0, 12, "深度")
    bf.cover_text(0, 5, 9, "与林木风我知道的")
    bf.cover_text(2, 1, 2, str1) # start_num : > 1
    # bf.del_line_text(0)
    bf.del_text(1, 16, 17)
    dict = bf.find_text("深度")
    print dict
    bf.print_buffer_dict()

