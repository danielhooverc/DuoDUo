from flask import Flask, render_template, request, redirect, url_for, session, flash,make_response,jsonify
import mysql.connector
from datetime import timedelta
from datetime import datetime
import pandas as pd
from io import BytesIO
# ========================================
import os



# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(hours=1)  # 设置Session有效期为1小时
# app.permanent_session_lifetime = timedelta(minutes=1)
# 数据库配置
db_config = {
    'host': '192.168.1.102',
    'user': 'root',
    'password': '000000',
    'database': 'duoduo'
}

# 连接到MySQL数据库
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# 主页面
@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        user_id = request.form.get('user_id')

        # 检查UserID是否为空
        if not user_id:
            flash("Please enter your UserID", "error")
            return render_template('homepage.html')

        # 查询数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, user_name FROM user_info WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()

        # 检查UserID是否存在
        if not user:
            flash("UserID does not exist!", "error")
            return render_template('homepage.html')

        #登录后清除之前所有残留的Session信息
        session.clear()
        # 保存用户信息到Session中
        session['UserID'] = user[0]
        session['UserName'] = user[1]
        session['search_type']='None'


        # 跳转到新页面
        return redirect(url_for('receiving_list'))


        #*********************************************************************************************
        # 模拟仓库数据
        # import warehouse_layout as wl
        # rows = 5
        # bays = 4
        # levels = 3
        # positions = 4
        # # 这里的参数可以根据实际仓库布局进行调整
        # warehouse_layout = wl.generate_warehouse_layout(rows, bays, levels, positions)
        #return render_template('warehouse_layout.html', warehouse=warehouse_layout, levels=levels)
        # *********************************************************************************************

    return render_template('homepage.html')


# Daily Receiving List 页面
@app.route('/receiving', methods=['GET', 'POST'])
def receiving_list():


# ******************************************************************************
# 说明：
#  1. 获取页面提交参数有两种POST表单提交,GET链接提交；
#
#  2.POST表单提交
#     from flask import request
#     param = request.form.get('param_name')  # 获取单个POST参数
#     all_params = request.form # 获取所有POST参数
#     # 遍历所有POST参数
#     for key, value in all_params.items():
#         print(f"{key}: {value}")
#
#  3. GET链接提交
#     from flask import request
#     param = request.args.get('param_name') # 获取单个GET参数
#     all_params = request.args  # 获取所有GET参数
#     # 遍历所有GET参数
#     for key, value in all_params.items():
#         print(f"{key}: {value}")

#  4.同时处理GET和POST请求:
#    if request.method == 'POST':
#       param = request.form.get('param_name') # 处理POST请求
#    else:
#      param = request.args.get('param_name')  # 处理GET请求
#*********************************************************************************


    # print('-------获取所有Session--------------')
    # print('the number of session=', len(session))
    # for key, value in session.items():
    #     print(f"{key}: {value}")
    #
    # print('-------获取所有POST参数--------------')
    # for key, value in request.form.items():
    #     print(f"{key}: {value}")
    #
    # print('-------获取所有GET参数--------------')
    # for key, value in request.args.items():
    #     print(f"{key}: {value}")


    # ================================================
    # 获取当前 session 中的用户名
    username = session.get('UserName')


    # 获取所有用户名;用于页面的下拉框
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_name FROM user_info ORDER BY user_name")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()


    if request.method == 'POST':
        # 获取表单控件的值，如果表单没有提供这些字段，将它们初始化为空字符串或其他合适的默认值
        record_date = request.form.get('record_date', '')
        record_date_end = request.form.get('record_date_end', '')
        receiving_date = request.form.get('receiving_date', '')
        receiving_date_end = request.form.get('receiving_date_end', '')
        receiving_type = request.form.get('receiving_type', '')
        option_name = request.form.get('name', '')
        finale_id = request.form.get('finale_id', '')
        sn = request.form.get('sn', '')
        tracking_number = request.form.get('tracking_number', '')
    else:
        # 如果不是 POST 请求（即 GET 请求时），初始化这些变量为空字符串或默认值
        record_date = ''
        record_date_end = ''
        receiving_date = ''
        receiving_date_end = ''
        receiving_type = ''
        option_name = ''
        finale_id = ''
        sn = ''
        tracking_number = ''

    #********************************************************************
    # 此处先读取HTML的GET链接提交；如果获取为空值，则设置为默认值
    # request.args.get()为获取方式
    # 有3个请求是链接提交：点击字段排序；点击页码，选择每页显示页数
    # ********************************************************************

    # 1.获取每页显示条数，优先从请求参数获取，否则使用 session 中保存的值，默认为 20
    if 'per_page' in request.args:
        per_page = int(request.args.get('per_page', 20))
        session['per_page'] = per_page  # 保存到 session 中
    else:
        per_page = session.get('per_page', 20)  # 从 session 获取

    page = int(request.args.get('page', 1))  # 当前页数，默认为第一页
    offset = (page - 1) * per_page  # 计算偏移量

    # 获取排序字段和顺序
    sort = request.args.get('sort', 'RecordDate')  # 默认按 RecordDate 排序
    order = request.args.get('order', 'desc')  # 默认降序

    # 初始化查询条件
    search_query = " WHERE 1=1 "
    search_params = []


    # 如果是提交表单查询：通用查询和普通查询
    if request.method == 'POST':
        #先把之前保存在session中的查询条件清除
        session.pop('search_query', None)  # 移除session中的search_query
        session.pop('search_params', None)  # 移除session中的search_params

        # 如果是通用搜索
        if request.form.get('search_type') == 'universal':
            # print('search_type= universal')
            # 重新设置session中的搜索类型
            session['search_type']='universal'

            #获取表单控件值
            search_info=request.form.get('search_info')
            if search_info:
                session['search_info']=search_info
                search_fields = [
                    'ReceivingType', 'Name', 'PONumber', 'FinaleID', 'PartNo', 'SN',
                    'TrackingNumber', 'ReceivedStatus', 'ReceivingNotes', 'Location',
                    'Master', 'POStatus'
                ]
                search_conditions = []
                for field in search_fields:
                    search_conditions.append(f"{field} LIKE %s")
                    search_params.append(f"%{search_info}%")

                search_query += " AND (" + " OR ".join(search_conditions) + ")"

        # 如果是普通搜索
        elif request.form.get('search_type') == 'normal':
            # print('search_type= normal')
            # 重新设置session中的搜索类型
            session['search_type'] = 'normal'
            # 获取表单控件值
            record_date =  request.form.get('record_date')
            record_date_end = request.form.get('record_date_end')

            receiving_date =  request.form.get('receiving_date')
            receiving_date_end = request.form.get('receiving_date_end')

            receiving_type = request.form.get('receiving_type')
            name =  request.form.get('name')
            finale_id =  request.form.get('finale_id')
            sn =  request.form.get('sn')
            tracking_number = request.form.get('tracking_number')

            # 动态构建查询;其中finale_id，sn,tracking_number可以进行模糊查询
            if record_date and not record_date_end:
                search_query += " AND DATE(RecordDate) = %s "
                search_params.append(record_date)
            elif not record_date and record_date_end:
                search_query += " AND DATE(RecordDate) = %s "
                search_params.append(record_date_end)
            elif record_date and record_date_end:
                search_query += " AND (DATE(RecordDate) >= %s and (DATE(RecordDate)<= %s))"
                search_params.extend([record_date, record_date_end])


            if receiving_date and not receiving_date_end:
                search_query += " AND DATE(ReceivingDate) = %s "
                search_params.append(receiving_date)
            elif not receiving_date and receiving_date_end:
                search_query += " AND DATE(ReceivingDate) = %s "
                search_params.append(receiving_date_end)
            elif receiving_date and receiving_date_end:
                search_query += " AND (DATE(ReceivingDate) >= %s and DATE(ReceivingDate)<= %s)"
                search_params.extend([receiving_date,receiving_date_end])


            if receiving_type:
                search_query += " AND ReceivingType = %s "
                search_params.append(receiving_type)
            if name:
                search_query += " AND Name = %s "
                search_params.append(name)
            if finale_id:
                search_query += " AND FinaleID LIKE %s "
                search_params.append(f"%{finale_id}%")
            if sn:
                search_query += " AND SN LIKE %s "
                search_params.append(f"%{sn}%")
            if tracking_number:
                search_query += " AND TrackingNumber LIKE %s "
                search_params.append(f"%{tracking_number}%")

        # 重新将查询条件存储在 session 中，以便分页和表头排序时重用
        session['search_query'] = search_query
        session['search_params'] = search_params

    #如果是登录首次查询，默认显示登录人的记录
    elif session['search_type'] == 'None':
        print('search_type= None')
        search_query += " AND Name = %s "
        search_params.append(username)
        # 将查询条件存储在 session 中，以便分页时重用
        session['search_query'] = search_query
        session['search_params'] = search_params
    else:
        # print('search_type= session')
        # 非 POST 请求时，从 session 中获取查询条件和参数
        search_query = session.get('search_query', " WHERE 1=1 ")
        search_params = session.get('search_params', [])
        # 将查询条件存储在 session 中，以便分页时重用
        session['search_query'] = search_query
        session['search_params'] = search_params


    # 将排序子句附加到查询条件上
    search_query += f" ORDER BY {sort} {order}"
    print(search_query)
    # 查询数据库并分页显示
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #将搜索的参数search_params对应匹配到search_query字串中；同时加入每页显示条数和偏移量
    cursor.execute(f"SELECT * FROM daily_receiving {search_query} LIMIT %s OFFSET %s", (*search_params, per_page, offset))
    records = cursor.fetchall()

    # 查询记录总数，用于分页计算
    cursor.execute(f"SELECT COUNT(*) as count FROM daily_receiving {search_query}", search_params)
    total_records = cursor.fetchone()['count']
    conn.close()

    # 计算总页数
    total_pages = (total_records + per_page - 1) // per_page


    # 渲染模板
    return render_template('receiving_list.html',
                           record_date=record_date,
                           record_date_end=record_date_end,
                           receiving_date=receiving_date,
                           receiving_date_end=receiving_date_end,
                           receiving_type=receiving_type,
                           option_name=option_name,
                           finale_id=finale_id,
                           sn=sn,
                           tracking_number=tracking_number,
                           records=records,
                           page=page,
                           per_page=per_page,  # 将 per_page 每页显示条数传递给模板
                           total_pages=total_pages,
                           total_records=total_records,
                           username=username,
                           names=names,
                           sort=sort,
                           order=order)


@app.route('/add', methods=['GET', 'POST'])
def add_record():
    #首先定义是否保存成功参数为False；如果保存无误再赋值True
    success = "None"

    # 获取 URL 参数; 这是为了返回receiving_list.html时；保持原有的显示数据集
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 20)
    sort = request.args.get('sort', 'RecordDate')
    order = request.args.get('order', 'desc')
    duplicate_message = ""

    if request.method == 'POST':
        #获取表单数据(一共17个字段)
        receiving_date = request.form.get('receiving_date')
        receiving_type = request.form.get('receiving_type')
        ponumber = request.form.get('ponumber')
        finale_id = request.form.get('finale_id')
        part_no = request.form.get('part_no', None)  # 允许为空的字段可以使用 .get
        sn = request.form.get('sn')

        #处理数值字段为空自动补0
        total_received_qty = request.form.get('total_received_qty', '0') or '0'
        total_order_qty = request.form.get('total_order_qty', '0') or '0'
        unit_weight = request.form.get('unit_weight', '0') or '0'

        tracking_number = request.form.get('tracking_number')
        received_status = request.form.get('received_status', None)  # 允许为空的字段
        receiving_notes = request.form.get('receiving_notes', None)
        location = request.form.get('location')
        master = request.form.get('master')

        unit_dimension = request.form.get('unit_dimension')
        packing_dimension_per_unit = request.form.get('packing_dimension_per_unit')
        po_status = request.form.get('po_status', None)

        # 获取当前时间和用户名
        record_date = datetime.now()
        name = session.get('UserName')

        if name is None :
            return render_template('add_record.html')


        #链接数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否需要忽略重复
        ignore_sn = request.form.get('ignore_sn_duplicates',None)
        ignore_tracking_number = request.form.get('ignore_tracking_duplicates',None)

        #如果要求检查sn重复性，并且sn不为空；检查 Serial Number 是否重复
        duplicate_sn_records=[]
        duplicate_tracking_records=[]
        if not ignore_sn and sn:
            duplicate_sn_records = check_duplicates(conn, 'SN', sn,-1)
        # 如果要求检查Tracking Number重复性，并且Tracking Number不为空； 检查 Tracking Number 是否重复
        if not ignore_tracking_number and tracking_number:
            duplicate_tracking_records = check_duplicates(conn, 'TrackingNumber', tracking_number,-1)

        # 如果有重复记录，弹出窗口显示重复信息
        if duplicate_sn_records or duplicate_tracking_records:
            if duplicate_sn_records:
                duplicate_message += "Duplicate Serial Number(s) found:\n"
                for record in duplicate_sn_records:
                    duplicate_message += f"{record}\n"

            if duplicate_tracking_records:
                duplicate_message += "\nDuplicate Tracking Number(s) found:\n"
                for record in duplicate_tracking_records:
                    duplicate_message += f"{record}\n"

            duplicate_message +="you can either choose to ignore duplicates or return to modify them again!"
            success="False"
            return jsonify({'success': success, 'duplicate_message': duplicate_message})


        # 如果不检查重复性就直接执行SQL插入操作
        cursor.execute('''
            INSERT INTO daily_receiving 
            (RecordDate, ReceivingDate, ReceivingType, Name, PONumber, FinaleID, PartNo, SN, Total_Received_QTY, 
            Total_Order_QTY, TrackingNumber, ReceivedStatus, ReceivingNotes, Location, Master, UnitWeight, 
            UnitDimension, Packing_Dimension_Per_Unit, POStatus) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (record_date, receiving_date, receiving_type, name, ponumber, finale_id, part_no, sn, total_received_qty,
              total_order_qty, tracking_number, received_status, receiving_notes, location, master, unit_weight,
              unit_dimension, packing_dimension_per_unit, po_status))

        conn.commit()
        conn.close()

        success = "True"
        return jsonify({'success': success})

    #如果不是提交表单；则直接导向页面
    return render_template('add_record.html',
                           success=success,
                           page=page,
                           per_page=per_page,  # 将 per_page 每页显示条数传递给模板
                           sort=sort,
                           order=order,
                           duplicate_message=duplicate_message)



# 编辑记录的路由
@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 获取 URL 参数; 这是为了返回receiving_list.html时；保持原有的显示数据集
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 20)
    sort = request.args.get('sort', 'RecordDate')
    order = request.args.get('order', 'desc')


    if request.method == 'POST':
        # 从表单中获取更新后的数据
        receiving_date = request.form['receiving_date']
        receiving_type = request.form['receiving_type']
        ponumber = request.form['ponumber']
        finale_id = request.form['finale_id']
        part_no = request.form['part_no']
        sn = request.form['sn']
        total_received_qty = request.form['total_received_qty']
        total_order_qty = request.form['total_order_qty']
        tracking_number = request.form['tracking_number']
        received_status = request.form.get('received_status', None)
        receiving_notes = request.form.get('receiving_notes', None)
        location = request.form['location']
        master = request.form['master']
        unit_weight = request.form['unit_weight']
        unit_dimension = request.form['unit_dimension']
        packing_dimension_per_unit = request.form['packing_dimension_per_unit']
        po_status = request.form.get('po_status', None)


        #=--------------------------检查是否需要忽略重复------------------------------------
        ignore_sn = request.form.get('ignore_sn_duplicates', None)
        ignore_tracking_number = request.form.get('ignore_tracking_duplicates', None)

        # 如果要求检查sn重复性，并且sn不为空；检查 Serial Number 是否重复
        duplicate_sn_records = []
        duplicate_tracking_records = []
        if not ignore_sn and sn:
            duplicate_sn_records = check_duplicates(conn, 'SN', sn, record_id)
        # 如果要求检查Tracking Number重复性，并且Tracking Number不为空； 检查 Tracking Number 是否重复
        if not ignore_tracking_number and tracking_number:
            duplicate_tracking_records = check_duplicates(conn, 'TrackingNumber', tracking_number, record_id)

        # 如果有重复记录，弹出窗口显示重复信息
        duplicate_message = ""
        if duplicate_sn_records or duplicate_tracking_records:
            if duplicate_sn_records:
                duplicate_message += "Duplicate Serial Number(s) found:\n"
                for record in duplicate_sn_records:
                    duplicate_message += f"{record}\n"

            if duplicate_tracking_records:
                duplicate_message += "\nDuplicate Tracking Number(s) found:\n"
                for record in duplicate_tracking_records:
                    duplicate_message += f"{record}\n"

            duplicate_message += "you can either choose to ignore duplicates or return to modify them again!"
            return jsonify({'success': 'False', 'duplicate_message': duplicate_message})
        #-----------------------------------------------------------------------------------------------------------

        # 更新数据库中的记录
        cursor.execute('''
            UPDATE daily_receiving
            SET ReceivingDate = %s, ReceivingType = %s, PONumber = %s, FinaleID = %s, PartNo = %s, SN = %s, 
                Total_Received_QTY = %s, Total_Order_QTY = %s, TrackingNumber = %s, ReceivedStatus = %s, 
                ReceivingNotes = %s, Location = %s, Master = %s, UnitWeight = %s, UnitDimension = %s, 
                Packing_Dimension_Per_Unit = %s, POStatus = %s
            WHERE RecordID = %s
        ''', (receiving_date, receiving_type, ponumber, finale_id, part_no, sn, total_received_qty, total_order_qty,
              tracking_number, received_status, receiving_notes, location, master, unit_weight, unit_dimension,
              packing_dimension_per_unit, po_status, record_id))

        conn.commit()
        conn.close()


        return jsonify({
                        'success': 'True',
                        'duplicate_message': duplicate_message,
                        'page':page,
                        'per_page':per_page,
                        'sort':sort,
                        'order':order
                       })

    # 如果是 GET 请求，加载当前记录并显示编辑页面
    cursor.execute('SELECT * FROM daily_receiving WHERE RecordID = %s', (record_id,))
    record = cursor.fetchone()
    conn.close()

    # return jsonify({'success': True, 'message': 'Record updated successfully!'})

    return render_template('edit_record.html',
                           success='None',
                           record=record,
                           page=page,
                           per_page=per_page,  # 将 per_page 每页显示条数传递给模板
                           sort=sort,
                           order=order)



# 新增和更新记录时先检查是否有'SN' 或 'TrackingNumber'重复记录
def check_duplicates(conn,field_name,values,record_id):
    # ************************************************************
    # 检查数据库中指定字段是否有重复值，并返回重复记录的相关信息
    # :param conn: 数据库连接对象
    # :param field_name: 要检查的字段名 ('SN' 或 'TrackingNumber')
    # :param values: 要检查的值列表
    # :return: 重复记录信息
    # ************************************************************
    cursor = conn.cursor()
    duplicate_records = []


    # ********************************************************************************************************************************
    # 分割字符串并清理每个值的前后空格和换行符
    # 使用f'%{value}%'来格式化字符串，但可能存在换行符或其他不可见字符（如空格）在value里。
    # 因为values_list是从values.split("\n")生成的，这种分割可能会导致每个value含有不可见的字符（如空行或尾部空格）导致添加通配符后输出不正确。
    # 因此在分割values_list后，应该对每个value使用strip()进行清理，去除前后的空格或换行符。确保它们在插入到SQL语句时是干净的字符串。
    # ********************************************************************************************************************************
    values_list = [value.strip() for value in values.split("\n") if value.strip()]

    for value in values_list:
       if not value:  # 跳过空行
         continue



       # 添加通配符到参数
       param = f'%{value}%'

       #如果是新增状态；record_id为-1；否则为修改判断
       if record_id == -1:
           query = f'SELECT * FROM daily_receiving WHERE {field_name} LIKE %s'
           params = (param,)
       else:
           query = f'SELECT * FROM daily_receiving WHERE RecordID <> %s AND {field_name} LIKE %s'
           params = (record_id, param)


       cursor.execute(query, params)
       result = cursor.fetchall()
       if result:
          duplicate_records.append(value)

    return duplicate_records


from urllib.parse import urlparse, parse_qs
@app.route('/delete_records', methods=['POST'])
def delete_records():
    # 使用request.referrer来获取之前页面的URL，然后从中提取需要的参数：
    # 获取 referrer URL
    referrer = request.referrer
    # 解析 URL 参数
    parsed_url = urlparse(referrer)
    query_params = parse_qs(parsed_url.query)

    # 提取参数，使用默认值
    page = query_params.get('page', ['1'])[0]
    per_page = query_params.get('per_page', ['20'])[0]
    sort = query_params.get('sort', ['RecordDate'])[0]
    order = query_params.get('order', ['desc'])[0]


    selected_records = request.form.getlist('selected_records')  # Get list of selected records
    if selected_records:
        placeholders = ', '.join(['%s'] * len(selected_records))  # Create placeholders for SQL
        query = f"DELETE FROM daily_receiving WHERE RecordID IN ({placeholders})"  # SQL query

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, tuple(selected_records))  # Execute the query with the selected records
        conn.commit()
        conn.close()

        flash(f'Successfully deleted {len(selected_records)} record(s).')
    else:
        flash('No records selected for deletion.')

    # return redirect(url_for('receiving_list'))  # Redirect back to the receiving list page
    # 重定向时包含这些参数
    return redirect(url_for('receiving_list', page=page, per_page=per_page, sort=sort, order=order))

import pandas as pd
from flask import make_response, request, session
from io import BytesIO

@app.route('/download', methods=['GET'])
def download_receiving_list():
    # 重新执行与 receiving_list 类似的查询，确保获取的是完整的数据集，而不是分页数据
    search_query = " WHERE 1=1 "
    search_params = []

    # 获取过滤条件
    record_date = request.args.get('record_date')
    receiving_date = request.args.get('receiving_date')
    receiving_type = request.args.get('receiving_type')
    name = request.args.get('name')
    finale_id = request.args.get('finale_id')
    sn = request.args.get('sn')
    tracking_number = request.args.get('tracking_number')

    # 动态构建查询
    if record_date:
        search_query += " AND RecordDate = %s "
        search_params.append(record_date)
    if receiving_date:
        search_query += " AND ReceivingDate = %s "
        search_params.append(receiving_date)
    if receiving_type:
        search_query += " AND ReceivingType = %s "
        search_params.append(receiving_type)
    if name:
        search_query += " AND Name = %s "
        search_params.append(name)
    if finale_id:
        search_query += " AND FinaleID LIKE %s "
        search_params.append(f"%{finale_id}%")
    if sn:
        search_query += " AND SN LIKE %s "
        search_params.append(f"%{sn}%")
    if tracking_number:
        search_query += " AND TrackingNumber LIKE %s "
        search_params.append(f"%{tracking_number}%")

    # 查询数据库获取完整数据集
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM daily_receiving {search_query} ORDER BY RecordDate DESC", search_params)
    records = cursor.fetchall()
    conn.close()

    if not records:
        return "没有数据可以下载", 400  # 如果没有数据，则返回错误

    # 使用 pandas 创建 DataFrame
    df = pd.DataFrame(records)


    # 移除 RecordID 列
    if 'RecordID' in df.columns:
        df = df.drop(columns=['RecordID'])

    # 使用 BytesIO 创建一个内存缓冲区来保存 Excel 文件
    output = BytesIO()

    # 将数据写入缓冲区的 Excel 文件中
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    # 将缓冲区的位置移回到开始，准备将其作为响应返回
    output.seek(0)

    # 返回 Excel 文件作为下载响应
    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=receiving_list.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return response




# ***********************************
# google表格处理
# ***********************************
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


# 追加数据到Google Sheets
def append_to_google_sheets(data):

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet_id = "11JY8BsLhBKZnGA5C5v05DYMoC3e-tiQou8rYsHYLDbc"

    # 获取第一个工作表
    worksheet = client.open_by_key(sheet_id).sheet1

    # 获取 T 列（第 20 列）的所有值
    record_ids = worksheet.col_values(20)  # 20 表示第 20 列，即 T 列; 也可以写成worksheet.get('T:T')

    # 创建一个字典将Google Sheet中的行号和Record_id进行对应{r_id:index+1},key是record_id；value是index+1
    # 加1的目的是因为Python中的列表索引从0开始；而Google Sheet的行号从1开始；要获得Record_ID对应的Sheet行号就需要加1
    id_to_row = {r_id : index+1 for index, r_id in enumerate(record_ids) if r_id}
    # 下面是通俗化的写法；
    # id_to_row = {}  # Initializes an empty dictionary.
    # for index, record_id in enumerate(record_ids):  # enumerate是获取列表中的元素；同时获取索引号；而不是通常意义的取列表中的两个元素
    #     if record_id:
    #         id_to_row[record_id] = record_id + 1





    # ************************************************************************************************************
    #  gspread 是一个封装了 Google Sheets API 的库，它简化了许多操作
    #  Google Sheets API 的原生格式是一个两个k:v对的字典：{ 'range': f'A{row_num}','values': [data_row[...]] }
    #  调用 gspread的update方法进行更行操作时，简化了形式直接输入两者值即可
    #  worksheet.update('A1', 'value')
    #  但是如果是批量更行；gspred需要使用Google Sheet API原生格式；将每行的两个K:V对字典；放到一个List中；然后进行批量更新
    #  worksheet.batch_update(data)
    #  这个data列表的每一个元素就是一个字典；包含两个K:V对{ 'range': f'A{row_num}','values': [data_row[...]] }
    # ************************************************************************************************************


    # 检查并更新或追加数据到修改列表和新增列表
    updated_rows = []
    new_rows = []

    for data_row in data:
        data_row = [str(value) for value in data_row]  #将数据全部转换成字符型
        record_id = data_row[-1]  #数据库中获取的Record_id，在上游函数中已经放置在了最后一列

        if not record_id:
            print(f"Skipping row due to missing RecordID")
            continue

        #如果record_id存在，就加入更新列表；否则加入新增列表
        if record_id in id_to_row:
            #如果数据库中的record_id存在于Google Sheet中；那么就从字典中把行号取出来
            row_num = id_to_row[record_id]
            #字典的第一个K:V是指定每一个行的起始列为A列；第二个K:V是每列数据的列表
            updated_rows.append({
                'range': f'A{row_num}',
                'values': [data_row[:-1]]
            })
        else:
            # 添加新行
            new_rows.append(data_row)





    # 批量更新现有行
    if updated_rows:
        worksheet.batch_update(updated_rows)

    # 批量添加新行
    # worksheet.append_rows()方法中的value_input_option参数有两个主要选项值：'RAW'  'USER_ENTERED' 这些选项的含义如下：
    # 'RAW': 数据会被按原样插入，不进行任何转换。
    # 例如，如果你输入"=1+1"，它会被当作文本字符串处理，而不是公式。日期会被存储为它们的字符串表示形式。
    #
    # 'USER_ENTERED':数据会被解释为用户在Google Sheets UI中手动输入的值。会尝试自动转换数据类型。
    # 例如，"=1+1" 会被解释为公式，日期字符串可能会被转换为日期格式。
    # 默认情况下，如果不指定 value_input_option，gspread 会使用 'RAW'

    if new_rows:
        worksheet.append_rows(new_rows, value_input_option='RAW')

    return {
        'updates': {
            'updatedRows': len(updated_rows),
            'appendedRows': len(new_rows)
        }
    }



@app.route('/add_to_google_sheets', methods=['POST'])
def add_to_google_sheets():
    record_date = request.form.get('record_date')
    record_date_end = request.form.get('record_date_end')

    print("record_date=",record_date,"   record_date_end",record_date_end)
    name = request.form.get('name')

    print(f"Fetching records for date: {record_date} and name: {name}")

    # 查询数据库获取符合条件的记录
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM daily_receiving WHERE Name = %s"
    params = [name]

    if record_date and record_date_end:
        query += " AND DATE(RecordDate) BETWEEN %s AND %s"
        params.extend([record_date, record_date_end])
    elif record_date and not record_date_end:
        query += " AND DATE(RecordDate) = %s"
        params.append(record_date)
    elif not record_date and record_date_end:
        query += " AND DATE(RecordDate) = %s"
        params.append(record_date_end)

    print(query)
    cursor.execute(query, params)
    records = cursor.fetchall()
    conn.close()

    print(f"Number of records fetched: {len(records)}")

    if records:
        # 重新排列数据，将 RecordID 放到最后
        rearranged_records = []
        for record in records:
            try:
                record_id = record.pop('RecordID')
                record_list = list(record.values())
                # 确保所有 datetime 对象都被转换为字符串；其中ReceivingDate只取月日年
                record_list = [
                    value.strftime('%Y/%m/%d') if isinstance(value, datetime) else str(value)
                    for key, value in zip(record.keys(), record_list)
                ]

                record_list.append(str(record_id))
                rearranged_records.append(record_list)
            except Exception as e:
                print(f"Error processing record: {str(e)}")
                print(f"Problematic record: {record}")

        print(f"Number of rearranged records: {len(rearranged_records)}")

        try:
            # 调用将数据追加到Google Sheets的函数
            result = append_to_google_sheets(rearranged_records)
            flash(f'Successfully added/updated {result["updates"]["updatedRows"]} rows '
                  f'and appended {result["updates"]["appendedRows"]} new rows to Google Sheets.')

            return jsonify({'success': True, 'message': f'Successfully added/updated {result["updates"]["updatedRows"]} rows '
                                                        f'and appended {result["updates"]["appendedRows"]} new rows to Google Sheets.'})
        except Exception as e:
            error_message= str(e)
            print(f"Error in append_to_google_sheets: {error_message}")
            flash(f'Error occurred while adding to Google Sheets: {str(e)}')
            print(f"Error in append_to_google_sheets: {error_message}")
            if '502' in error_message:
                return jsonify({
                    'success': False,
                    'message': 'Google Sheets is temporarily unavailable. Please try again in a few minutes.'
                }), 502
            else:
                return jsonify({
                    'success': False,
                    'message': f'Error occurred while adding to Google Sheets: {error_message}'
                }), 500
    else:
        flash('No records found for the specified Record Date and Name.')
        return jsonify({'success': False, 'message': 'No records found for the specified Record Date and Name.'})
    # return redirect(url_for('receiving_list'))



# 启动Flask应用
if __name__ == '__main__':
    app.run(debug=True)
