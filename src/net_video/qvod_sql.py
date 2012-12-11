#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

SQL_CONNECT_STATE = 0
SQL_CONNECT_SQLLIT = 0
SQL_CONNECT_MYSQL = 1

if SQL_CONNECT_STATE == SQL_CONNECT_SQLLIT:
    try:
        import sqlite
    except Exception, e:    
        print "python-sqllit [error]", e
# elif SQL_CONNECT_STATE == SQL_CONNECT_MYSQL:
#     try:
#         import mysql
#     except Exception, e:
#         print "python-mysqldb [error]", e
        
        
class QvodSql(object):
    def __init__(self):
        self.sql_conn = None
        self.sql_cur = None
        
    def open(self, sql_file_path):
        return self.__connect(sql_file_path) # conn sql file.
    
    def create_table(self, table): # create database table.
        sql_create_cmd = "create table %s "
        sql_create_cmd += "(id integer primary key, "
        sql_create_cmd += "name text, " # 影片名称
        sql_create_cmd += "area text, " # 地区.
        sql_create_cmd += "actor text, "# 影片演员.
        sql_create_cmd += "direct text, "# 影片导演.
        sql_create_cmd += "type text, "# 类型.
        sql_create_cmd += "date text, "# 上映日期.
        sql_create_cmd += "image text, "# 图片地址.
        sql_create_cmd += "state text, "# 影片状态.
        sql_create_cmd += "qvod_addr text, "# qvod 地址.
        sql_create_cmd += "other text)" # 备注信息.
        return self.execute(sql_create_cmd % (table))
    
    def del_table(self, table): # delete database table.       
        sql_del_cmd = "drop table %s" % (table)
        return self.execute(sql_del_cmd)
        
    def insert_data(self, table, info):
        sql_insert_cmd = "insert into %s values (null, " % (table)
        sql_insert_cmd += "'" + info.name + "'" + ", "
        sql_insert_cmd += "'" + info.area + "'" + ", "
        sql_insert_cmd += "'" + info.actor + "'" + ", "
        sql_insert_cmd += "'" + info.direct + "'" + ", "
        sql_insert_cmd += "'" + info.type + "'" + ", "
        sql_insert_cmd += "'" + info.date + "'" + ", "       
        sql_insert_cmd += "'" + info.image + "'" + ", "
        sql_insert_cmd += "'" + info.state + "'" + ", "
        sql_insert_cmd += "'" + info.qvod_addr + "'" + ", "
        sql_insert_cmd += "'" + info.other + "'"
        sql_insert_cmd += ")"
        return self.execute(sql_insert_cmd)
    
    def select_data(self, table, sql_select_cmd=""):
        return self.execute("select * from %s %s" % (table, sql_select_cmd))
        
    def clear_data(self, table):
        return self.execute("delete from %s where id > 0" % (table))
    
    def execute(self, sql_cmd): # run sql cmd.
        if self.sql_cur and self.sql_conn:
            if SQL_CONNECT_STATE == SQL_CONNECT_SQLLIT:
                try:
                    self.sql_cur.execute(sql_cmd)
                    self.sql_conn.commit()
                    return True
                except Exception, e:    
                    print "execute [error]:", e
                    return False
        return False        
                    
    def get_query_data(self):
        return self.sql_cur.fetchall()
    
    def get_query_count(self, table_name):
        try:
            qvod_sql.execute("select count(*) from %s" % (table_name))
            return self.sql_cur.fetchone()[0]
        except Exception, e:
            print "get_query_count[error]:", e
            return 0;
    
    def __connect(self, sql_file_path):
        if SQL_CONNECT_STATE == SQL_CONNECT_SQLLIT:
            try:
               self.sql_conn = sqlite.connect(sql_file_path)
               if self.sql_conn:
                   self.sql_cur = self.sql_conn.cursor()
                   return True
               else:
                   return False
            except Exception, e:
                print "sqllit [error]:", e
                return False
        # elif SQL_CONNECT_STATE == SQL_CONNECT_MYSQL:
            # return None
        # elif

    def close(self):        
        if SQL_CONNECT_STATE == SQL_CONNECT_SQLLIT:
            if self.sql_conn and self.sql_cur:
                self.sql_cur.close()
                self.sql_conn.close()                
                print "close : sql_conn and sql_cur."
                
class QvodInfo(object):
    def __init__(self):
        self.name = "功夫"
        self.area = "中国"
        self.actor = "深度"
        self.direct = "深度"
        self.type = "历史片"
        self.date = "3000年上映"
        self.image = "我来看看"
        self.state = "100年"
        self.qvod_addr = "qvod://2u3012jfdklsjfdsklfjdsklfjsdlkfdsl.rvmbjfldksfj|,qvod://fdsjflksjdfklsdjflkdsf.rvcfjd|,qvod://djkfljsdkfsdjlfksjdfkldsjflkdsjflksdfjsldfjk|,qvod://dsjfklsdjflsdkrmvbdfsjklfjdslkfj|,qvod://dsjfkldsfjlskdfjsldkfjsdklfjklsdfjkldsfjslakfjklsdfjslkdfj|"
        self.other = "Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境Linux Deepin是中国最大的LINUX发行版，统治中国LINUX桌面环境"
                
if __name__ == "__main__":        
    qvod_sql = QvodSql()
    if qvod_sql.open("db_media.db"):
        print "链接成功!!"        
        # qvod_sql.execute("create table medias (name varchar(5000), addr varchar(500000))")
        # qvod_sql.create_table("medias")
        print "test count:", qvod_sql.get_query_count("medias")
        # qvod_sql.del_table("medias")
        # info = QvodInfo()
        # qvod_sql.insert_data("medias", info)
        # qvod_sql.select_data("medias")
        # qvod_sql.clear_data("medias")
        # for i in qvod_sql.get_query_data():
        #     print i[0]
        #     print i[1]
        #     print i[2]
        #     print i[3]
        #     print i[4]
        #     print i[5]
        #     print i[6]
        #     print i[7]
        #     print i[8]
        #     print i[9]
        #     print i[10]
        # close qvod_sql.
        qvod_sql.close()
    else:    
        print "链接失败!!"
    # qvod_sql.exe
