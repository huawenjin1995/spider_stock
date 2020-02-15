
import arrow, calendar
from datetime import datetime

def getDateList(start_date, end_date):
    '''

    :param start_date: 开始日期，例如：‘2015-01-25’
    :param end_date: 截止日期，例如：‘2020-01-06’
    :return: 返回开始日期——截止日期间的所有日期
    '''
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    date_list = []
    if start > end:
        return date_list
    else:
        for r in arrow.Arrow.range('day', start, end):
            date = arrow.get(r).format('YYYY-MM-DD')
            # print(date)
            # print(type(date))
            if datetime.strptime(date, '%Y-%m-%d').weekday() not in (5, 6):
                date_list.append(date)
        return date_list

# def isLeapYear(year):
#     '''
#     通过判断闰年，获取年份years下一年的总天数
#     :param years: 年份，int
#     :return:days_sum，一年的总天数
#     '''
#     # 断言：年份不为整数时，抛出异常。
#     assert isinstance(year, int), "请输入整数年，如 2018"
#
#     if calendar.isleap(year):  # 判断是否是闰年
#         # print(years, "是闰年")
#         days_sum = 366
#         return days_sum
#     else:
#         # print(years, '不是闰年')
#         days_sum = 365
#         return days_sum
#
#
# def getAllDayPerYear(years):
#     '''
#     获取一年的所有日期
#     :param years:年份
#     :return:全部日期列表
#     '''
#     beg_date = '%s-1-1' % years
#     a = 0
#     all_date_list = []
#     days_sum = isLeapYear(int(years))
#     print()
#     while a < days_sum:
#         b = arrow.get(beg_date).shift(days=a).format("YYYY-MM-DD")
#         a += 1
#         all_date_list.append(b)
#     # print(all_date_list)
#     return all_date_list
#
#
# def getTotalDates(start_date, end_date):
#     start_year = arrow.get(start_date)


if __name__ == '__main__':

    list = getDateList('1986-03-01', '1986-03-09')
    for date in list:
        print(date)

