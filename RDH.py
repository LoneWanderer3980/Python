#  插入数据：data,头文件：q,溢出位置图：m
#  q:第一比特：0（左移），1（右移）；8个比特：Tn;8*Tn个比特：Tn个左零点；8个比特：Tp;8*Tp个比特：Tp个右零点；32比特：最后嵌入点坐标（x,y）;
#  M:（Tn+Tp）个（8比特溢出个数n，32*n比特溢出位置）
#  插入数据的位置范围：从第二排到倒数第二排，第二列到倒数第二列

from array import array
import numpy as np
from PIL import Image
from pylab import *
import os

#  获取要插入的信息data，并转化为数字01串
data = []
try:
    with open('data/data.txt', 'r') as binfile:
        contents = binfile.read()
        #  print(contents)
except FileNotFoundError:
    print("sorry,file is not exist")
else:
    for i in range(len(contents)):
        if contents[i] == '0':
            data.append(0)
        else:
            data.append(1)
    binfile.close()
    print(data)

#  需要处理的图像
im = Image.open('img/lenna.bmp')
size_x = im.size[1]
size_y = im.size[0]
print("size_x:{},size_y:{}".format(size_x,size_y))
#  存加密的信息
array_ = array(im)

#  用于预测时计算头文件
changed_ = array_.copy()
changed_ex = []
for i in range(size_x):
    changed_ex.append([])
    for j in range(size_y):
        changed_ex[i].append(0)
#  头文件，位置图
q = ''
M = ''
m = array_.copy()
#  存十进制的溢出点坐标
location_m = []
#  头文件，溢出图的长度
len_q = 0
len_m = 0
#  可存储信息的像素点个数
count = 0
#  画预测直方图
pxx = []
for i in range(500):
    pxx.append(0)
leftnum = 0
rightnum = 0
#  左右零点
left0 = []
right0 = []
#  选取的左右零点数
left = 0
right = 0


#  二进制转化为十进制
def goto_10(aa):
    nn = 0
    for i in range(len(aa)):
        nn = nn * 2 + aa[i]
    return nn


#  判断是否可能为溢出点，是则修改m的值为1
def judge(i, j, k, c):
    if m[i][j] != 0:
        return False
    elif 0 <= changed_[i][j]+k <= 255:
        return True
    else:
        m[i][j] = c
        global len_m
        len_m += 32
        location_m[c].append(i)
        location_m[c].append(j)
        return False


#  边界外移动，k :-1(左)，1（右）
def move(start,end,k,c):
    for i in range(1,size_x-1):
        for j in range(1,size_y-1):
            if start <= changed_ex[i][j] <= end and judge(i,j,k,c):
                changed_ex[i][j] += k
                changed_[i][j] += k


#  测误差为ex且能插入数据的像素点个数
def num(ex,k,c):
    count_ = 0
    for i in range(1,size_x-1):
        for j in range(1,size_y-1):
            if changed_ex[i][j] == ex and judge(i,j,k,c):
                count_ += 1
    return count_


#  建立预测直方图
for i in range(1,size_x-1):
    for j in range(1,size_y-1):
        x = im.getpixel((i, j))
        a = im.getpixel((i, j + 1))
        b = im.getpixel((i + 1, j))
        c = im.getpixel((i + 1, j + 1))
        if c <= min(a, b):
            px = max(a, b)
        elif c >= max(a, b):
            px = min(a, b)
        else:
            px = a + b - c
        ex = x - px
        changed_ex[i][j] = ex
        pxx[ex] += 1
        m[i][j] = 0

#  得出零点集(ex=0不为零点)
for i in range(250):
    if pxx[i] == 0:
        right0.append(i)
    if pxx[-i] == 0:
        left0.append(i)
    if 0 < i < 5:
        leftnum += pxx[-i]
        rightnum += pxx[i]
print("leftnum:{},rightnum:{}".format(leftnum, rightnum))

#  先左移
if leftnum < rightnum:
    q += '0'
    c = 1
    len_q += 1+16
    countneed = 0
    while True:
        location_m.append([])
        if c % 2 == 1:
            move(-left0[left]+1, 2*(-left)-1, -1, c)
            count += num(2*(-left), -1, c)
            left += 1
        else:
            move(2*(right+1), right0[right]-1, 1, c)
            count += num(2*right+1, 1, c)
            right += 1
        c += 1
        len_q += 8
        len_m += 8
        countneed = len(data)+len_q+len_m+32
        if count > countneed:
            break
else:
    #  右移
    q += '1'
    c = 1
    len_q += 1 + 16
    countneed = 0
    while True:
        location_m.append([])
        if c % 2 == 1:
            move(2*right+1, right0[right]-1, 1, c)
            count += num(2*right, 1, c)
            right += 1
        else:
            move(-left0[left]+1, 2*(-left-1), -1, c)
            count += num(2*(-left)-1, -1, c)
            left += 1
        c += 1
        len_q += 8
        len_m += 8
        countneed = len(data) + len_q + len_m + 32
        if count > countneed:
            break


#  头文件信息
q += "{0:b}".format(left).zfill(8)
for i in range(left):
    q += "{0:b}".format(left0[i]).zfill(8)
q += "{0:b}".format(right).zfill(8)
for i in range(right):
    q += "{0:b}".format(right0[i]).zfill(8)
print("len_q:{}, len_m:{}".format(len_q, len_m))
print("left:{},right:{}".format(left, right))

for i in range(left+right):
    n = len(location_m[i])//2
    M += "{0:b}".format(n).zfill(8)
    for j in range(n):
        M += "{0:b}".format(location_m[i][2 * j]).zfill(16)
        M += "{0:b}".format(location_m[i][2 * j + 1]).zfill(16)
print("q:{}".format(q))
print("M:{}".format(M))
print("location_m:{}".format(location_m))


#  插入data
flag = True
z = 0
zz = 0
end_x = 0
end_y = 0
if q[0] == '0':
    #  左移
    for i in range(1,  size_x - 1):
        for j in range(1,  size_y - 1):
            x = int(array_[i][j])
            a = int(array_[i][j + 1])
            b = int(array_[i + 1][j])
            c = int(array_[i + 1][j + 1])
            if c <= min(a, b):
                px = max(a, b)
            elif c >= max(a, b):
                px = min(a, b)
            else:
                px = a + b - c
            ex = x - px
            if m[i][j] == 0:
                if -left < ex <= right:
                    if z < len(data):
                        if -left < ex <= 0:
                            array_[i][j] += ex - data[z]
                            ex = 2 * ex - data[z]
                        elif 0 < ex <= right:
                            array_[i][j] += ex - 1 + data[z]
                            ex = 2 * ex - 1 + data[z]
                        z += 1
                    elif zz < len_q + len_m + 32:
                        if zz == len_q + len_m + 31:
                            end_x = i
                            end_y = j
                            flag = False
                        if -left < ex <= 0:
                            array_[i][j] += ex - array_[1+zz//(size_y-2)][1+zz % (size_y-2)] % 2
                            ex = 2 * ex - array_[1+zz//(size_y-2)][1+zz % (size_y-2)] % 2
                        elif 0 < ex <= right:
                            array_[i][j] += ex - 1 + array_[1+zz//(size_y-2)][1+zz % (size_y-2)] % 2
                            ex = 2 * ex - 1 + array_[1+zz//(size_y-2)][1+zz % (size_y-2)] % 2
                        zz += 1
                elif ex > right:
                    if right == 0 or ex > right0[right-1]:
                        #  无右零点，或大于最后一个右零点
                        continue
                    else:
                        for k in range(right):
                            if ex < right0[k]:
                                array_[i][j] += right - k
                                ex += right - k
                                break
                elif ex <= -left:
                    if ex < -left0[left-1]:
                        continue
                    else:
                        for k in range(left):
                            if ex > -left0[k]:
                                array_[i][j] -= left - k
                                ex -= left - k
                                break
            else:
                #  溢出点
                if m[i][j] % 2 == 1:
                    #  向左会溢出
                    ex -= m[i][j] // 2
                    array_[i][j] -= m[i][j] // 2
                else:
                    ex += (m[i][j]-1) // 2
                    array_[i][j] += (m[i][j]-1) // 2
        if flag == False:
            break
else:
    for i in range(1, size_x - 1):
        for j in range(1, size_y - 1):
            x = int(array_[i][j])
            a = int(array_[i][j + 1])
            b = int(array_[i + 1][j])
            c = int(array_[i + 1][j + 1])
            if c <= min(a, b):
                px = max(a, b)
            elif c >= max(a, b):
                px = min(a, b)
            else:
                px = a + b - c
            ex = x - px
            if m[i][j] == 0:
                if -left <= ex < right:
                    if z < len(data):
                        if -left <= ex < 0:
                            array_[i][j] += ex + 1 - data[z]
                            ex = 2 * ex + 1 - data[z]
                        elif 0 <= ex < right:
                            array_[i][j] += ex + data[z]
                            ex = 2 * ex + data[z]
                        z += 1
                        #  print("z:{},({},{}),ex:{},{}".format(z,i,j,ex,array_[i][j]))
                    elif zz < len_q + len_m + 32:
                        if zz == 0:
                            print("(i,j):({},{})".format(i,j))
                        if zz == len_q + len_m + 31:
                            end_x = i
                            end_y = j
                            flag = False
                        if -left <= ex < 0:
                            array_[i][j] += ex + 1 - array_[1+zz//(size_y-2)][1+zz % (size_y-2)] % 2
                            ex = 2 * ex + 1 - array_[1+zz//(size_y-2)][1+zz % (size_y-2)] % 2
                        elif 0 <= ex < right:
                            array_[i][j] += ex + array_[1+zz//(size_y-2)][1+zz % (size_y-2)] % 2
                            ex = 2 * ex + array_[1+zz//(size_y-2)][1+zz % (size_y-2)] % 2
                        zz += 1
                elif ex > right:
                    if ex > right0[right-1]:
                        continue
                    else:
                        for k in range(right):
                            if ex < right0[k]:
                                array_[i][j] += right - k
                                ex += right - k
                                break
                elif ex <= -left:
                    if left == 0 or ex < -left0[left-1]:
                        #  无左零点，或小于最后一个左零点
                        continue
                    else:
                        for k in range(left):
                            if ex > -left0[k]:
                                array_[i][j] -= left - k
                                ex -= left - k
                                break
            else:
                #  溢出点
                if m[i][j] % 2 == 1:
                    #  向右会溢出
                    ex += m[i][j] // 2
                    array_[i][j] += m[i][j] // 2
                else:
                    ex -= (m[i][j]-1) // 2
                    array_[i][j] -= (m[i][j]-1) // 2
        if flag == False:
            break
q += "{0:b}".format(end_x).zfill(16)
q += "{0:b}".format(end_y).zfill(16)
print("q:{}".format(q))
print("M:{}".format(M))
print("end_x:{}".format(end_x))
print("end_y:{}".format(end_y))


#  LSB插入头文件和溢出图
tempp = 0
flag = True
for i in range(1, size_x - 1):
    for j in range(1, size_y - 1):
        x = int(array_[i][j])
        a = int(array_[i][j + 1])
        b = int(array_[i + 1][j])
        c = int(array_[i + 1][j + 1])
        if c <= min(a, b):
            px = max(a, b)
        elif c >= max(a, b):
            px = min(a, b)
        else:
            px = a + b - c
        ex = x - px
        if tempp < len_q + 32:
            if q[tempp] == '1':
                array_[i][j] = 2 * (array_[i][j]//2) + 1
                ex = 1
            else:
                array_[i][j] = 2 * (array_[i][j]//2)
                ex = 0
        elif tempp < len_q + 32 + len_m:
            if tempp == len_q + 31 + len_m:
                print("LSB最后点插入位置{},{}".format(i,j))
            if M[tempp-len_q-32] == '1':
                array_[i][j] = 2 * (array_[i][j] // 2) + 1
                ex = 1
            else:
                array_[i][j] = 2 * (array_[i][j] // 2)
                ex = 0
        else:
            flag = False
        tempp += 1
    if flag == False:
        break


#  存储数据隐藏后的图片
new_array = np.reshape(array_, im.size)
with open("img/lenna_with_data.bmp", "wb") as fp:
    Image.fromarray(new_array).save(fp)
print("已加密\n")


#  数据恢复
im_cover = Image.open('img/lenna_with_data.bmp')
cover_array = array(im_cover)
size_x_ = im_cover.size[1]
size_y_ = im_cover.size[0]
#  用于存提取的数据
data_ = []
m_ = cover_array.copy()


l_or_r = 0
left_num = -1
right_num = -1
left0_ = []
right0_ = []
end_x_ = 0
end_y_ = 0
l_m_ = []
x_ = []
y_ = []
#  获取头文件信息
print("开始获取头文件")
flag = True
tempp = 0
temp = []
co = 0
t = 0
times = -1
time_ = 0
for i in range(1, size_x_-1):
    for j in range(1, size_y_-1):
        n = cover_array[i][j] % 2
        cover_array[i][j] -= n
        if tempp == 0:
            l_or_r = n
            temp = []
        if 0 < tempp < 9:
            temp.append(n)
        if tempp == 8:
            left_num = goto_10(temp)
            temp = []
        if left_num != -1:
            if 8 < tempp <= 8*left_num+8:
                temp.append(n)
                co += 1
                if co == 8:
                    left0.append(goto_10(temp))
                    temp = []
                    co = 0
            if 8*left_num+17 > tempp > 8*left_num+8:
                temp.append(n)
            if tempp == 8*left_num+16:
                right_num = goto_10(temp)
                temp = []
            if right_num != -1:
                if 8 * (left_num + right_num) + 16 >= tempp > 8 * left_num + 16:
                    temp.append(n)
                    co += 1
                    if co == 8:
                        right0_.append(goto_10(temp))
                        #  print("right_temp:{}".format(temp))
                        #  print("right0_:{}".format(right0_))
                        temp = []
                        co = 0
                elif 8 * (left_num + right_num) + 33 > tempp > 8 * (left_num + right_num) + 16:
                    temp.append(n)
                    co += 1
                    if co == 16:
                        end_x_ = goto_10(temp)
                        #  print("end_x_temp:{}".format(temp))
                        temp = []
                        co = 0
                if 8 * (left_num + right_num) + 49 > tempp >= 8 * (left_num + right_num) + 33:
                    temp.append(n)
                    co += 1
                    if co == 16:
                        end_y_ = goto_10(temp)
                        #  print("end_y_temp:{}".format(temp))
                        temp = []
                        co = 0
                    t = 8 * (left_num + right_num) + 49
                if t != 0 and 0 <= tempp - t < 8:
                    temp.append(n)
                    co += 1
                    if co == 8:
                        l_m_.append(goto_10(temp))
                        temp = []
                        co = 0
                        times += 1
                        if l_m_[times] == 0:
                            t = tempp + 1
                            x_.append([])
                            y_.append([])
                            if times+1 == left_num + right_num:
                                flag = False
                                break
                elif t != 0 and tempp - t >= 8 and times != -1:
                    #  有溢出
                    if 0 <= tempp-t-8 < l_m_[times]*32:
                        if time_ == 0:
                            x_.append([])
                            y_.append([])
                        temp.append(n)
                        co += 1
                        if co == 16:
                            x_[times].append(goto_10(temp))
                            temp = []
                        if co == 32:
                            y_[times].append(goto_10(temp))
                            temp = []
                            co = 0
                            time_ += 1
                            if time_ == l_m_[times]:
                                t = tempp + 1
                                time_ = 0
                                if times+1 == left_num + right_num:
                                    flag = False
                                    break
        tempp += 1
    if flag == False:
        break


count_exchange = tempp + 1
print("count_exchange:{}".format(count_exchange))
print("l_or_r:{}".format(l_or_r))
print("left_num:{}".format(left_num))
print("right_num:{}".format(right_num))
print("left0_:{}".format(left0_))
print("right0_:{}".format(right0_))
print("end_x_:{},end_y_:{}".format(end_x_, end_y_))
for i in range(len(x_)):
    print("位置溢出点：({},{})\n".format(x_[i], y_[i]))

#  构造新位置图
for i in range(1, size_x_-1):
    for j in range(1, size_y_-1):
        m_[i][j] = 0

for i in range(len(l_m_)):
    if l_m_[i] == 0:
        break
    else:
        #  有溢出点
        for j in range(l_m_[i]):
            m_[x_[j]][y_[j]] = i+1


#  提取数据
count_ = 0
if l_or_r == 0:
    #  向左移
    for i in range(end_x_,0,-1):
        for j in range(size_y_-2,0,-1):
            if i == end_x_ and j > end_y_:
                continue
            else:
                x = int(cover_array[i][j])
                a = int(cover_array[i][j+1])
                b = int(cover_array[i+1][j])
                c = int(cover_array[i+1][j+1])
                if c <= min(a, b):
                    px = max(a, b)
                elif c >= max(a, b):
                    px = min(a, b)
                else:
                    px = a + b - c
                ex = x - px
                if (right_num == 0 and ex > 0) or ex < -left0_[left_num-1] or (right_num != 0 and ex > right0_[right_num-1]):
                    continue
                if m_[i][j] == 0:
                    if -2*left_num+1 <= ex <= 2*right_num:
                        if ex > 0:
                            cover_array[i][j] -= ex//2
                            data_.append((ex-1) % 2)
                        else:
                            cover_array[i][j] -= ex//2
                            data_.append(ex % 2)
                        count_ += 1
                        if count_ <= count_exchange:
                            cover_array[1+(count_exchange-count_)//(size_x_-2)][1+(count_exchange-count_) % (size_x-2)] += data_[count_-1]
                            if count_ == count_exchange:
                                data_ = []
                        #  print("count_:{},({},{}),ex:{},{}".format(count_, i, j, ex, cover_array[i][j]))
                    elif ex > 0:
                        for k in range(right_num):
                            if ex <= (right0_[k]-1)+(right_num-k):
                                cover_array[i][j] -= (right_num-k)
                                break
                    elif ex < 0:
                        for k in range(left_num):
                            if ex >= (-left0_[k]+1)-(left_num-k):
                                cover_array[i][j] += (left_num-k)
                                break
                else:
                    if ex <= 0:#  左移溢出(m[i][j] 为奇数)
                        cover_array[i][j] += m[i][j] // 2
                    else:
                        cover_array[i][j] -= (m[i][j]-1) // 2
else:
    for i in range(end_x_, 0, -1):
        for j in range(size_y_-2, 0, -1):
            if i == end_x_ and j > end_y_:
                continue
            else:
                x = int(cover_array[i][j])
                a = int(cover_array[i][j+1])
                b = int(cover_array[i+1][j])
                c = int(cover_array[i+1][j+1])
                if c <= min(a, b):
                    px = max(a, b)
                elif c >= max(a, b):
                    px = min(a, b)
                else:
                    px = a + b - c
                ex = x - px
                if (left_num == 0 and ex < 0) or ex > right0_[right_num-1] or (left_num != 0 and ex < -left0_[left_num-1]):
                    continue
                if m_[i][j] == 0:
                    if -2*left_num <= ex <= 2*right_num-1:
                        if ex >= 0:
                            cover_array[i][j] -= (ex+1)//2
                            data_.append(ex % 2)
                        else:
                            cover_array[i][j] -= (ex+1)//2
                            data_.append((ex+1) % 2)
                        count_ += 1
                        #  print("count_:{},({},{}),ex:{},{}".format(count_, i, j,ex,cover_array[i][j]))
                        if count_ <= count_exchange:
                            cover_array[1+(count_exchange-count_)//(size_x_-2)][1+(count_exchange-count_) % (size_x-2)] += data_[count_-1]
                            if count_ == count_exchange:
                                print("(i,j):({},{})".format(i,j))
                                print("data_temp:{}".format(data_))
                                print("data_len:{}".format(len(data_)))
                                data_ = []
                    elif ex > 0:
                        for k in range(right_num):
                            if ex <= (right0_[k]-1)+(right_num-k):
                                cover_array[i][j] -= (right_num-k)
                                break
                    elif ex < 0:
                        for k in range(left_num):
                            if ex >= (-left0_[k]+1)-(left_num-k):
                                cover_array[i][j] += (left_num-k)
                                break
                else:
                    if ex <= 0:
                        #  左移溢出(m[i][j] 为偶数)
                        cover_array[i][j] += (m[i][j]-1) // 2
                    else:
                        cover_array[i][j] -= m[i][j] // 2

im_cover.save("img/reback.bmp")
print("data:{}".format(contents))
print("len_data:{}".format(len(contents)))


data_get = ''
for i in range(len(data_)):
    if data_[-i-1] == 0:
        data_get += '0'
    elif data_[-i-1] == 1:
        data_get += '1'

print("data_get:{}".format(data_get))
print("len_data_get:{}".format(len(data_get)))

try:
    with open('data/data_get.txt', 'w') as f:
        f.write(data_get)
except FileNotFoundError:
    print("sorry,file is not exist")
finally:
    f.close()
