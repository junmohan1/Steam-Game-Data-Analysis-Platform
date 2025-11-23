import pandas as pd  # 导入pandas用于数据处理
import numpy as np  # 导入numpy用于数值计算
import plotly.express as px  # 导入plotly.express用于快速创建交互式图表
import plotly.graph_objects as go  # 导入plotly.graph_objects用于创建自定义图表
from plotly.subplots import make_subplots  # 导入make_subplots用于创建多子图图表
import streamlit as st  # 导入streamlit用于数据质量显示

def create_all_visualizations(df):
    """
    创建所有可视化图表
    返回包含所有图表的字典
    """
    visuals = {}  # 存储所有图表的字典
    
    # 1. 游戏发布数量年度趋势分析
    yearly_releases = df.groupby('release_year').size().reset_index(name='count')  # 按年份分组统计游戏发布数量
    yearly_releases = yearly_releases[yearly_releases['release_year'] >= 1990]  # 过滤有效年份（1990年及以后）
    fig1 = px.line(yearly_releases, x='release_year', y='count',  # 创建折线图，x轴为年份，y轴为发布数量
                  title='📈 游戏发布数量年度趋势分析',  # 图表标题
                  labels={'release_year': '发布年份', 'count': '发布数量'},  # 轴标签重命名
                  markers=True)  # 显示数据点标记
    fig1.update_traces(line=dict(width=3))  # 设置线条粗细为3
    visuals['time_trend'] = fig1  # 将图表存储到字典中，键为'time_trend'
    
    # 2. 价格与销量关系分析
    price_analysis_df = df[(df['price'] >= 0) & (df['price'] <= 100) & (df['owners_median'] > 0)]  # 过滤有效数据：价格0-100，销量大于0
    fig2 = px.scatter(price_analysis_df, x='price', y='owners_median',  # 创建散点图，x轴为价格，y轴为销量
                     hover_data=['name'],  # 悬停时显示游戏名称
                     title='💰 游戏价格与销量关系分析',  # 图表标题
                     labels={'price': '价格 (美元)', 'owners_median': '销量估计'},  # 轴标签重命名
                     opacity=0.6)  # 设置点透明度为0.6
    fig2.update_traces(marker=dict(size=8))  # 设置点大小为8
    visuals['price_vs_sales'] = fig2  # 将图表存储到字典中，键为'price_vs_sales'
    
    # 3. 好评率与游戏时长关系分析
    engagement_df = df[(df['average_playtime'] > 0) & (df['total_ratings'] > 10)]  # 过滤有效数据：游戏时长大于0，总评价数大于10
    fig3 = px.scatter(engagement_df, x='positive_ratio', y='average_playtime',  # 创建散点图，x轴为好评率，y轴为游戏时长
                     hover_data=['name'],  # 悬停时显示游戏名称
                     title='⏱️ 游戏好评率与玩家参与度关系分析',  # 图表标题
                     labels={'positive_ratio': '好评率', 'average_playtime': '平均游戏时长(分钟)'},  # 轴标签重命名
                     opacity=0.6)  # 设置点透明度为0.6
    fig3.update_traces(marker=dict(size=8, color='green'))  # 设置点大小为8，颜色为绿色
    visuals['rating_vs_playtime'] = fig3  # 将图表存储到字典中，键为'rating_vs_playtime'
    
    # 4. 游戏类型分布分析
    genre_counts = df['main_genre'].value_counts().head(15)  # 获取前15个游戏类型的数量统计
    genre_df = pd.DataFrame({  # 创建新的DataFrame用于绘图
        'genre': genre_counts.index,  # 游戏类型名称
        'count': genre_counts.values  # 游戏数量
    })
    fig4 = px.bar(genre_df, 
                 x='count',  # X轴：游戏数量
                 y='genre',  # Y轴：游戏类型
                 orientation='h',  # 水平方向条形图
                 title='🎮 最受欢迎的游戏类型分布Top10',  # 图表标题
                 labels={'count': '游戏数量', 'genre': '游戏类型'},  # 轴标签重命名
                 color='count',  # 根据数量值着色
                 color_continuous_scale='viridis')  # 使用viridis颜色方案
    fig4.update_layout(showlegend=False)  # 隐藏图例
    visuals['genre_distribution'] = fig4  # 将图表存储到字典中，键为'genre_distribution'
    
    # 5. 发行商分析
    publisher_stats = df.groupby('publisher').agg({  # 按发行商分组统计
        'name': 'count',  # 游戏数量
        'positive_ratio': 'mean',  # 平均好评率
        'owners_median': 'mean'  # 平均销量
    }).reset_index()  # 重置索引，将分组键变为列
    publisher_stats = publisher_stats.rename(columns={'name': 'game_count'})  # 重命名列，避免歧义
    top_publishers = publisher_stats.nlargest(15, 'game_count')  # 取前15名发行商（按游戏数量排序）
    fig5 = px.bar(top_publishers, 
                 x='game_count',  # X轴：发行游戏数量
                 y='publisher',   # Y轴：发行商名称
                 orientation='h',  # 水平方向条形图
                 title='🏢 发行游戏数量最多的发行商Top15',  # 图表标题
                 labels={'game_count': '发行游戏数量', 'publisher': '发行商'},  # 轴标签重命名
                 color='game_count',  # 根据数量值着色
                 color_continuous_scale='plasma')  # 使用plasma颜色方案
    visuals['publisher_analysis'] = fig5  # 将图表存储到字典中，键为'publisher_analysis'
    
    # 6. 平台支持分析
    platform_stats = pd.DataFrame({  # 创建平台统计DataFrame
        '平台': ['Windows', 'Mac', 'Linux'],  # 平台名称
        '支持游戏数量': [  # 各平台支持的游戏数量
            df['windows_support'].sum(),  # Windows支持数量
            df['mac_support'].sum(),  # Mac支持数量
            df['linux_support'].sum()  # Linux支持数量
        ]
    })
    fig6 = px.pie(platform_stats, values='支持游戏数量', names='平台',  # 创建饼图，值为数量，名为平台
                 title='💻 各平台游戏支持情况分布',  # 图表标题
                 color='平台',  # 按平台着色
                 color_discrete_map={'Windows': 'blue', 'Mac': 'gray', 'Linux': 'yellow'})  # 自定义平台颜色
    fig6.update_traces(textposition='inside', textinfo='percent+label')  # 设置文本显示在内部，显示百分比和标签
    visuals['platform_support'] = fig6  # 将图表存储到字典中，键为'platform_support'
    
    # 7. 免费与付费游戏对比分析
    free_paid_comparison = df.groupby('is_free').agg({  # 按是否免费分组
        'positive_ratio': 'mean',  # 平均好评率
        'average_playtime': 'mean',  # 平均游戏时长
        'owners_median': 'mean',  # 平均销量
        'name': 'count'  # 游戏数量
    }).reset_index()  # 重置索引
    free_paid_comparison = free_paid_comparison.rename(columns={'name': 'game_count'})  # 重命名列，避免歧义
    free_paid_comparison['类型'] = free_paid_comparison['is_free'].map({True: '免费游戏', False: '付费游戏'})  # 映射类型名称
    
    fig7 = make_subplots(rows=1, cols=3,  # 创建1行3列的子图布局
                        subplot_titles=('平均好评率', '平均游戏时长(分钟)', '平均销量'),  # 子图标题
                        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]])  # 所有子图都是条形图
    
    fig7.add_trace(go.Bar(x=free_paid_comparison['类型'],  # X轴为游戏类型
                         y=free_paid_comparison['positive_ratio'],  # Y轴为好评率
                         marker_color=['lightblue', 'lightcoral']),  # 自定义颜色
                  row=1, col=1)  # 第1行第1列位置
    
    fig7.add_trace(go.Bar(x=free_paid_comparison['类型'],  # X轴为游戏类型
                         y=free_paid_comparison['average_playtime'],  # Y轴为游戏时长
                         marker_color=['lightblue', 'lightcoral']),  # 自定义颜色
                  row=1, col=2)  # 第1行第2列位置
    
    fig7.add_trace(go.Bar(x=free_paid_comparison['类型'],  # X轴为游戏类型
                         y=free_paid_comparison['owners_median'],  # Y轴为销量
                         marker_color=['lightblue', 'lightcoral']),  # 自定义颜色
                  row=1, col=3)  # 第1行第3列位置
    
    fig7.update_layout(title_text='🆓 免费游戏 vs 💰 付费游戏全方位对比分析',  # 主标题
                      showlegend=False,  # 隐藏图例
                      height=500)  # 设置图表高度
    visuals['free_vs_paid'] = fig7  # 将图表存储到字典中，键为'free_vs_paid'

    # 8. 月度发布趋势分析
    monthly_counts = df.groupby('release_month').size().reset_index(name='game_count')  # 按月份分组统计游戏数量
    monthly_counts = monthly_counts.sort_values('release_month')  # 按月份数字排序（1月到12月）
    
    fig8 = px.bar(monthly_counts, 
                 x='release_month',  # X轴：月份（1-12）
                 y='game_count',     # Y轴：游戏发布数量
                 title='📅 各月份游戏发布数量分析',  # 图表标题
                 labels={'release_month': '月份', 'game_count': '游戏发布数量'},  # 轴标签重命名
                 color='game_count',  # 根据数量着色
                 color_continuous_scale='blues')  # 使用蓝色渐变颜色方案
    
    peak_month = monthly_counts.loc[monthly_counts['game_count'].idxmax()]  # 找到游戏数量最多的月份
    peak_month_num = int(peak_month['release_month'])  # 高峰月份的数字
    peak_month_count = int(peak_month['game_count'])   # 高峰月份的游戏数量
    
    fig8.update_layout(
        xaxis=dict(tickmode='linear', dtick=1),  # 设置X轴刻度为整数，每个月份都显示
        showlegend=False  # 隐藏图例
    )
    
    fig8.add_annotation(
        x=peak_month_num,  # 标注位置：高峰月份
        y=peak_month_count,  # 标注位置：高峰数量
        text=f"高峰: {peak_month_count}款",  # 标注文本
        showarrow=True,  # 显示箭头指向数据点
        arrowhead=2,  # 箭头样式
        bgcolor="yellow"  # 标注背景色
    )
    
    visuals['monthly_analysis'] = fig8  # 将图表存储到字典中，键为'monthly_analysis'
    visuals['peak_month_info'] = (peak_month_num, peak_month_count)  # 存储高峰月份信息供分析使用
    
    return visuals  # 返回包含所有图表的字典

def create_small_multiples(df):
    """
    创建小倍数图替代地图（因为没有地理字段）
    返回小倍数图表对象
    """
    top_genres = df['main_genre'].value_counts().head(6).index.tolist()  # 获取前6个热门类型
    genre_subset = df[df['main_genre'].isin(top_genres)]  # 筛选这些类型的数据
    
    fig = px.scatter(genre_subset, 
                    x='price',  # X轴：价格
                    y='positive_ratio',  # Y轴：好评率
                    color='main_genre',  # 按类型着色
                    facet_col='main_genre',  # 按类型分面（创建多个子图）
                    facet_col_wrap=3,  # 每行显示3个子图
                    hover_data=['name', 'release_year'],  # 悬停显示的信息
                    title="📊 热门游戏类型：价格 vs 好评率多维度对比",  # 图表标题
                    labels={'price': '价格 (美元)', 'positive_ratio': '好评率'})  # 轴标签重命名
    
    fig.update_layout(height=600)  # 设置图表高度
    return fig  # 返回图表对象

def create_data_quality_section(df):
    """
    创建数据质量检查部分
    显示数据完整性、缺失值、重复值等信息
    """
    st.header("📊 Data Quality Report")  # 数据质量部分的主标题
    
    col1, col2, col3 = st.columns(3)  # 创建三列布局显示关键质量指标
    
    with col1:
        missing_data = df.isnull().sum()  # 计算每列的缺失值数量
        total_cells = np.prod(df.shape)  # 计算总单元格数（行数×列数）
        missing_percentage = (missing_data.sum() / total_cells) * 100  # 计算缺失值百分比
        st.metric("Total Missing Values", f"{missing_percentage:.2f}%")  # 显示缺失值比例指标
    
    with col2:
        duplicates = df.duplicated().sum()  # 计算完全重复的记录数量
        st.metric("Duplicate Records", duplicates)  # 显示重复记录数指标
    
    with col3:
        complete_rows = df.notnull().all(axis=1).sum()  # 计算完整记录数（没有任何缺失值的行）
        completeness = (complete_rows / len(df)) * 100  # 计算完整记录百分比
        st.metric("Complete Records", f"{completeness:.2f}%")  # 显示完整性指标
    
    st.subheader("Detailed Data Quality Metrics")  # 详细的数据质量分析子标题
    
    missing_stats = pd.DataFrame({
        'Column Name': df.columns,  # 所有列名
        'Missing Count': df.isnull().sum().values,  # 每列的缺失值数量
        'Missing Percentage': (df.isnull().sum() / len(df) * 100).values  # 每列的缺失值百分比
    })
    missing_stats = missing_stats[missing_stats['Missing Count'] > 0]  # 只显示有缺失值的列
    
    if len(missing_stats) > 0:  # 如果有缺失值
        st.write("**Missing Values by Column:**")  # 表格标题
        st.dataframe(missing_stats, use_container_width=True)  # 显示缺失值统计表格
    else:
        st.success("✅ No missing values found")  # 如果没有缺失值，显示成功消息
    
    st.subheader("Data Validation Checks")  # 数据验证检查子标题
    
    validation_checks = [  # 定义数据验证检查项列表
        ("Prices are non-negative", (df['price'] >= 0).all()),  # 检查所有价格是否都非负
        ("Positive ratings between 0-1", ((df['positive_ratio'] >= 0) & (df['positive_ratio'] <= 1)).all()),  # 检查好评率范围
        ("Playtime is non-negative", (df['average_playtime'] >= 0).all()),  # 检查游戏时长非负
        ("Release dates are reasonable", (df['release_year'] >= 1990).all())  # 检查发布日期合理性
    ]
    
    for check_name, check_result in validation_checks:  # 遍历每个验证检查项
        if check_result:  # 如果检查通过
            st.success(f"✅ {check_name}")  # 显示成功图标和检查名称
        else:  # 如果检查失败
            st.error(f"❌ {check_name}")  # 显示错误图标和检查名称