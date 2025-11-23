import pandas as pd  # 导入pandas用于数据处理
import numpy as np  # 导入numpy用于数值计算
import streamlit as st  # 导入streamlit用于创建交互控件

def create_sidebar_filters(df):
    """
    创建侧边栏过滤器控件
    返回包含用户选择过滤条件的字典 
    """
    st.sidebar.header("🔧 Data Filters")  # 在侧边栏创建过滤器区域标题
    
    min_year = int(df['release_year'].min())  # 获取数据中最小的发布年份
    max_year = int(df['release_year'].max())  # 获取数据中最大的发布年份
    year_range = st.sidebar.slider(
        "Select Release Year Range",  # 滑块标签文本
        min_year, max_year, (min_year, max_year)  # 最小值, 最大值, 默认范围(全选)
    )
    
    max_price = float(df['price'].max())  # 获取数据中最高价格
    price_range = st.sidebar.slider(
        "Select Price Range (USD)",  # 滑块标签文本
        0.0, max_price, (0.0, max_price)  # 最小值, 最大值, 默认范围(0-最高价格)
    )
    
    all_genres = sorted(df['main_genre'].unique())  # 获取所有唯一的游戏类型并排序
    selected_genres = st.sidebar.multiselect(
        "Select Game Genres",  # 多选框标签文本
        all_genres,  # 所有可选的游戏类型列表
        default=all_genres  # 默认选择所有类型
    )
    
    platform_options = st.sidebar.multiselect(
        "Select Supported Platforms",  # 多选框标签文本
        ['Windows', 'Mac', 'Linux'],  # 所有可选的平台列表
        default=['Windows','Mac', 'Linux']  # 默认全选所有平台
    )
    
    return {  # 返回用户选择的所有过滤条件字典
        'year_range': year_range,  # 用户选择的年份范围
        'price_range': price_range,  # 用户选择的价格范围
        'selected_genres': selected_genres,  # 用户选择的游戏类型列表
        'platform_options': platform_options  # 用户选择的平台列表
    }


def apply_filters(df, filters):
    """
    根据侧边栏选择的过滤条件筛选数据
    返回过滤后的DataFrame
    """
    filtered_df = df.copy()  # 创建数据副本，避免修改原始数据
    
    # 应用年份过滤 - 只保留在用户选择年份范围内的游戏
    filtered_df = filtered_df[
        (filtered_df['release_year'] >= filters['year_range'][0]) &  # 年份大于等于选择的最小值
        (filtered_df['release_year'] <= filters['year_range'][1])  # 年份小于等于选择的最大值
    ]
    
    # 应用价格过滤 - 只保留在用户选择价格范围内的游戏
    filtered_df = filtered_df[
        (filtered_df['price'] >= filters['price_range'][0]) &  # 价格大于等于选择的最小值
        (filtered_df['price'] <= filters['price_range'][1])  # 价格小于等于选择的最大值
    ]
    
    # 应用游戏类型过滤 - 如果用户选择了特定类型，只保留这些类型
    if filters['selected_genres']:  # 检查用户是否选择了游戏类型
        filtered_df = filtered_df[filtered_df['main_genre'].isin(filters['selected_genres'])]  # 筛选指定类型的游戏
    
    # 应用平台过滤 - 根据用户选择的平台进行筛选
    platform_filters = []  # 存储平台过滤条件的列表
    if 'Windows' in filters['platform_options']:  # 如果用户选择了Windows平台
        platform_filters.append(filtered_df['windows_support'] == True)  # 添加Windows支持条件
    if 'Mac' in filters['platform_options']:  # 如果用户选择了Mac平台
        platform_filters.append(filtered_df['mac_support'] == True)  # 添加Mac支持条件
    if 'Linux' in filters['platform_options']:  # 如果用户选择了Linux平台
        platform_filters.append(filtered_df['linux_support'] == True)  # 添加Linux支持条件
    
    if platform_filters:  # 如果有平台过滤条件
        platform_filter = platform_filters[0]  # 第一个过滤条件
        for pf in platform_filters[1:]:  # 遍历剩余过滤条件
            platform_filter = platform_filter | pf  # 使用OR逻辑组合条件（支持任一平台即可）
        filtered_df = filtered_df[platform_filter]  # 应用组合过滤条件
    
    return filtered_df  # 返回过滤后的数据

def calculate_key_metrics(df):
    """
    计算关键指标和统计数据
    返回包含各种指标的字典
    """
    metrics = {}  # 存储指标的字典
    
    # 基础统计指标
    metrics['total_games'] = len(df)  # 游戏总数（DataFrame行数）
    metrics['free_game_percentage'] = df['is_free'].mean() * 100  # 免费游戏比例（转换为百分比）
    metrics['avg_rating'] = df['positive_ratio'].mean() * 100  # 平均好评率（转换为百分比）
    metrics['year_range'] = f"{df['release_year'].min()}-{df['release_year'].max()}"  # 时间范围字符串
    
    # 时间趋势相关指标
    yearly_releases = df.groupby('release_year').size().reset_index(name='count')  # 按年份分组统计发布数量
    peak_year = yearly_releases.loc[yearly_releases['count'].idxmax()]  # 找到发布数量最多的年份
    metrics['peak_year'] = int(peak_year['release_year'])  # 高峰年份
    metrics['peak_year_count'] = int(peak_year['count'])  # 高峰年份发布数量
    
    # 价格相关指标
    price_stats = df[df['price'] > 0]  # 只考虑付费游戏（价格大于0）
    metrics['avg_price'] = price_stats['price'].mean()  # 平均价格
    metrics['median_price'] = price_stats['price'].median()  # 价格中位数
    
    # 平台相关指标
    metrics['windows_games'] = df['windows_support'].sum()  # Windows游戏数量
    metrics['mac_games'] = df['mac_support'].sum()  # Mac游戏数量
    metrics['linux_games'] = df['linux_support'].sum()  # Linux游戏数量
    metrics['multi_platform_games'] = df['multi_platform'].sum()  # 多平台游戏数量
    
    # 类型相关指标
    genre_counts = df['main_genre'].value_counts()  # 类型计数（按出现频率排序）
    metrics['top_genres'] = genre_counts.head(5).index.tolist()  # 前5个热门类型列表
    metrics['unique_genres'] = df['main_genre'].nunique()  # 唯一类型数量
    
    # 月度分析相关指标
    monthly_counts = df.groupby('release_month').size()  # 按月份统计游戏数量
    metrics['peak_month'] = int(monthly_counts.idxmax())  # 发布高峰月份（1-12）
    metrics['peak_month_count'] = int(monthly_counts.max())  # 高峰月份的游戏数量
    metrics['slow_month'] = int(monthly_counts.idxmin())  # 发布低谷月份
    metrics['slow_month_count'] = int(monthly_counts.min())  # 低谷月份的游戏数量
    
    return metrics  # 返回包含所有指标的字典