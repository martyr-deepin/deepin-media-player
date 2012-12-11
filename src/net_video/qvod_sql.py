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
        sql_create_cmd = "create table %s (id int not null primary key auto_increment,name varchar(500),type varchar(200),zone varchar(200),date varchar(200),img_url varchar(1000),qvod_url varchar(20000),desc varchar(5000),md5sum varchar(200))" % (table)
        return self.execute(sql_create_cmd)
    
    def del_table(self, table): # delete database table.       
        sql_del_cmd = "drop table %s" % (table)
        return self.execute(sql_del_cmd)
        
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
        
    def query_data(self, sql_query_cmd):
        return self.execute(sql_query_cmd)
        
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
                
if __name__ == "__main__":        
    qvod_sql = QvodSql()
    if qvod_sql.open("db_media.db"):
        print "链接成功!!"        
        # qvod_sql.execute("create table medias (name varchar(5000), addr varchar(500000))")
        # qvod_sql.create_table("medias")
        print "test count:", qvod_sql.get_query_count("medias")
        # qvod_sql.del_table("medias")
        # for i in range(0, 600):
        #     print "inser ", i
            # qvod_sql.execute("insert into medias values('fdjsfldfjsdlkfjsdlkfjsdjfkldsjflskfjksdlfjl', 'qvod://fjsdklfjsdlkfsjdlkfjsdlkfjsdklfjsdklfjsdlkfjsdlkfjdslkfjsdlkfjsdlkfjdslkfjsdklfjsdlkfjsdlkfjdsklfjsdlkfjsdklfjsdlkfjsldkfjldkf,qvod://fsdjfklsdjflsdkfjdsl.rvmsdfksdjflksdjflksdjflksfj,qvod://fdsjfklsdjflksdfjlsdkfjsdlkfjsdklfjsdlkfjsdklfsjdklfdsf,qvod://fjdsklfdsjlfksjdlfksdjlf,qvod://fjdsklfjsdlfjsdlfsdjfr.v|,qvod://djfsdklfjsldkfjdslkfjkf|%s')"%(i))
        # close qvod_sql.
        qvod_sql.close()
    else:    
        print "链接失败!!"
    # qvod_sql.exe
