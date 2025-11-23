import pandas as pd  # 导入pandas用于数据处理
import streamlit as st  # 导入streamlit用于缓存装饰器

@st.cache_data  # 使用streamlit缓存装饰器，避免重复加载数据，提升应用性能
def load_and_preprocess_data():
    """
    加载CSV数据并进行预处理
    返回处理后的DataFrame
    """
    # 使用绝对路径直接读取数据文件
    df = pd.read_csv('C:/Users/ASUS/unit/project/steam.csv')  # 使用绝对路径读取steam.csv数据文件
    
    # 数据预处理 - 日期处理
    df['release_date'] = pd.to_datetime(df['release_date'])  # 将release_date列转换为datetime格式
    df['release_year'] = df['release_date'].dt.year  # 从日期中提取发布年份，创建新列
    df['release_month'] = df['release_date'].dt.month  # 从日期中提取发布月份，创建新列
    df['release_year_month'] = df['release_date'].dt.to_period('M')  # 从日期中提取年月周期，创建新列
    
    # 数据预处理 - 评价相关计算
    df['total_ratings'] = df['positive_ratings'] + df['negative_ratings']  # 计算总评价数（好评+差评）
    df['positive_ratio'] = df['positive_ratings'] / df['total_ratings']  # 计算好评率（好评数/总评价数）
    df['positive_ratio'] = df['positive_ratio'].fillna(0)  # 处理空值，将NaN好评率填充为0
    
    # 数据预处理 - 销量数据处理函数
    def parse_owners(owners_str):
        """
        处理owners字段,将范围字符串转换为中值
        例如: "1000000-2000000" -> 1500000
        """
        try:
            if '-' in str(owners_str):  # 检查是否为范围格式（包含连字符）
                low, high = owners_str.split('-')  # 分割字符串，获取下限和上限
                return (int(low) + int(high)) / 2  # 返回范围中值作为估计销量
            else:
                return float(owners_str)  # 直接转换数字格式的销量
        except:
            return 0  # 异常情况返回0
    
    df['owners_median'] = df['owners'].apply(parse_owners)  # 应用销量处理函数，创建销量中值列
    
    # 数据预处理 - 游戏类型处理
    df['main_genre'] = df['genres'].str.split(';').str[0]  # 提取第一个类型作为主要游戏类型
    
    # 数据预处理 - 平台支持分析
    df['windows_support'] = df['platforms'].str.contains('windows')  # 检查是否支持Windows平台
    df['mac_support'] = df['platforms'].str.contains('mac')  # 检查是否支持Mac平台
    df['linux_support'] = df['platforms'].str.contains('linux')  # 检查是否支持Linux平台
    df['multi_platform'] = (df['windows_support'].astype(int) +  # 判断是否为多平台游戏（支持2个及以上平台）
                           df['mac_support'].astype(int) + 
                           df['linux_support'].astype(int)) >= 2
    
    df['is_free'] = df['price'] == 0  # 价格为0的游戏标记为免费游戏
    
    return df  # 返回处理后的DataFrame