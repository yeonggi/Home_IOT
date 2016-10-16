import sqlite3
import os

class DBProc:
    def __init__(self):
        pass

    def DBSelectAll(self,db_file_name,db_name):
        conn = sqlite3.connect(db_file_name)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        query = 'SELECT * FROM %s ORDER BY ID' % db_name

        type_list = []
        for i in c.execute('PRAGMA TABLE_INFO(wheather_info)'):
            type_list.append(str(i[1]))

        print type_list
        for i in c.execute(query):
            print i
        conn.close()

    def DBSelectAllOrderBy(self,db_file_name,db_name, order_key):
        conn = sqlite3.connect(db_file_name)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        query = 'SELECT * FROM %s ORDER BY %s' % (db_name,order_key)
        q_list = c.execute(query)

        for i in c.execute(query):
            print i
        conn.close()

    def DBCreate(self, db_file_name, db_name, Argument):
        conn = sqlite3.connect(db_file_name)
        c = conn.cursor()
        index = db_file_name.rfind('/')

        if index == -1:
            for i in os.listdir(os.getcwd()):
                if i == db_file_name:
                   pass
        else:
            for i in os.listdir(db_file_name[:index]):
                if i == db_file_name[index+1:]:
                    pass


        table_list = c.execute('SELECT name FROM sqlite_master WHERE type = "table"')
        table_list = table_list.fetchall()

        print table_list
        for i in table_list:
            if i[0] == db_name:
                print 'Table_exsit'
                return

        print 'Create DB Table '
        creat_txt = 'CREATE TABLE %s (' % db_name
        creat_txt += 'ID INT PRIMARY KEY, '
        creat_txt += ','.join(Argument)
        creat_txt += ')'

        c.execute(creat_txt)
        conn.commit()
        conn.close()

    def DBInsert(self,db_file_name,db_name,db_contents):
        conn = sqlite3.connect(db_file_name)
        c = conn.cursor()

        total_count = 0
        for i in c.execute('SELECT count(ID) FROM %s'%db_name):
            total_count = i[0]

        insert_txt = 'INSERT INTO %s VALUES (' % db_name
        q_list = []
        list_cont = [int(total_count)+1] + list(db_contents)
        tuple_cont = tuple(list_cont)
        for i in range(len(tuple_cont)):
            q_list.append('?')
        insert_txt += ','.join(q_list)
        insert_txt += ')'
        c.execute(insert_txt, tuple_cont)
        conn.commit()
        conn.close()

    def DBInsertMany(self,db_file_name,db_name,unique_para,db_contents):
        conn = sqlite3.connect(db_file_name)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        total_count = 0
        for i in c.execute('SELECT count(ID) FROM %s'%db_name):
            total_count = i[0]

        type_list = []
        name_list = []
        for i in c.execute('PRAGMA TABLE_INFO(wheather_info)'):
            name_list.append(str(i[1]))
            type_list.append(str(i[2]))

        flag = 0
        unique_para_col_index = 0
        columns = name_list
        for i in columns:
            if unique_para == i:
                unique_para_col_index = flag
                break
            flag += 1

        if flag == len(columns):
            print 'There are no Colum at DB '
            return 0
        up_str = str()
        inset_query = list()
        index = 0
        rst = 0
        org_total = total_count
        for input_list_tuple in db_contents:
            index = 0
            for current_list in c.execute('SELECT * FROM %s ORDER BY %s' % (db_name, unique_para)):
                if input_list_tuple[unique_para_col_index-1] == current_list[unique_para_col_index]:
                    db_list = [current_list[0]] + list(input_list_tuple)
                    db_list = tuple(db_list)
                    for j in range(len(columns)):
                        if type_list[j] == 'text':
                            up_str += columns[j] + '=' + '"'+str(db_list[j])+'"' + ','
                        else:
                            up_str +=  columns[j] + '=' + str(db_list[j])+','

                    query = 'UPDATE %s SET %s WHERE %s = "%s"' %  (
                        db_name,up_str[0:len(up_str)-1], columns[unique_para_col_index],input_list_tuple[unique_para_col_index-1])
                    c.execute(query)
                    break
                index += 1

            if index == org_total:
                total_count += 1
                db_list = [total_count] + list(input_list_tuple)
                db_list = tuple(db_list)
                inset_query.append(db_list)

        insert_txt = 'INSERT INTO %s VALUES (' % db_name
        q_list = []
        for i in range(len(columns)):
            q_list.append('?')
        insert_txt += ','.join(q_list)
        insert_txt += ')'
        c.executemany(insert_txt, inset_query)
        conn.commit()
        conn.close()

    def DBDelete(self,db_file_name,db_name, db_key, val):
        conn = sqlite3.connect(db_file_name)
        c = conn.cursor()

        total_count = 0
        for i in c.execute('SELECT count(ID) FROM %s'%db_name):
            total_count = i[0]

        try:
            c.execute('delete from %s where %s=%d'%(db_name,db_key, val))
        except:
            print 'Delete Fail No data'
        conn.commit()
        if val == total_count:
            pass
        elif val < total_count:
            for i in range(val,total_count):
                c.execute('UPDATE %s SET ID = %d WHERE ID = %d ' %(db_name,i,i+1))

        # need update ID
        conn.commit()
        conn.close()

    def DBDeleteRange(self,db_file_name,db_name, db_key, id_start, id_end):
        pass
        
if __name__ == "__main__":
    DB_weather = DBProc()
    arg = ('Date text', 'Wheather text', 'Temp real')
    DB_weather.DBCreate('Wheather.db', 'wheather_info',  arg)

    contents = [('2016-03-04 10:00','Cloud', 4.4)
                ,('2016-03-05 12:00','Clear', -21)
                ,('2016-03-06 01:00','Rain', 123)
                ,('2016-03-07 10:00','Wind', 34.234)
                ,('2016-03-08 00:00', 'Storm', -14)
                ,('2016-02-3 14:00', 'Cloud', 2)
                ,('2016-03-12 10:00', 'Cloud', 4.4)
                , ('2016-03-14 12:00', 'Clear', -21)
                , ('2016-03-15 01:00', 'Rain', 123)
                , ('2016-03-16 10:00', 'Wind', 34.234)
                , ('2016-03-17 00:00', 'Storm', -14)
                , ('2016-03-18 14:00', 'Cloud', 2)
                , ('2016-03-19 15:00', 'Clear', -21)
                , ('2016-03-20 06:00', 'Rain', 123)
                , ('2016-03-21 17:00', 'Wind', 34.234)
                , ('2016-03-22 08:00', 'Storm', -14)
                , ('2016-03-24 19:00', 'Cloud', 2)
                , ('2016-03-26 14:00', 'Cloud', 4.4)
                , ('2016-03-27 13:00', 'Clear', -21)
                , ('2016-03-28 02:00', 'Rain', 123)
                , ('2016-03-29 13:00', 'Wind', 34.234)
                , ('2016-03-30 03:00', 'Storm', -14)
                , ('2016-03-31 14:00', 'Cloud', 2)
                ]


    contents_up = [('2016-03-06 01:00','FUCK', 4.4)
                ,('2016-03-07 10:00','FUCK', -21)
                ,('2016-03-08 00:00','FUCK', 123)
                ,('2016-03-09 14:00','FUCK', 34.234)
                ,('2016-03-10 00:00', 'df', -14)
                ,('2016-03-11 14:00', 'df', 2)]
    #DB_weather.DBInsert('Wheather.db', 'wheather_info',contesnt_s)
    #for i in range(7):
    #DB_weather.DBDelete('Wheather.db', 'wheather_info','ID', 7)
    DB_weather.DBInsertMany('Wheather.db', 'wheather_info', 'Date' ,contents)
    DB_weather.DBSelectAll('Wheather.db', 'wheather_info')
