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


def get_movie_name(qvod_url):
    url = qvod_url.replace("qvod://", "")
    return url.split("|")[2]

def get_hash_str(qvod_url):
    url = qvod_url.replace("qvod://", "")
    return url.split("|")[1]
    
    
def check_qvod_url(qvod_url):
    qvod_url_bool = False
    if qvod_url != None:
        if qvod_url.startswith("qvod:") and qvod_url.endswith("|"):
            temp_list = qvod_url.split("|")
            if len(temp_list) >= 3:
                qvod_url_bool = True
                
    return qvod_url_bool            


if __name__ == "__main__":
    test_url = "qvod://1234261716|202C8A841C0715CD03CAEF631A8E73E9F4D156E2|将爱进行到底DVD.rmvb|"
    print check_qvod_url(test_url);
    
