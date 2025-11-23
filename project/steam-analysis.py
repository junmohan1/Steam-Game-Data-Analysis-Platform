# steam-analysis.py
# Steam游戏数据分析平台 - 完整的Streamlit网页应用
# streamlit run C:\Users\ASUS\unit\project\steam-analysis.py

# 导入必要的库
import pandas as pd  # 数据处理和分析
import numpy as np  # 数值计算
import matplotlib.pyplot as plt  # 数据可视化
import seaborn as sns  # 统计可视化
import plotly.express as px  # 交互式图表
import plotly.graph_objects as go  # 自定义交互式图表
from plotly.subplots import make_subplots  # 创建子图
import warnings  # 警告处理
import streamlit as st  # 网页应用框架

# 忽略警告信息，保持输出整洁
warnings.filterwarnings('ignore')

# 设置中文字体支持，防止中文显示乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 使用缓存装饰器提高数据加载性能
@st.cache_data
def load_and_preprocess_data():
    """
    加载CSV数据并进行预处理
    返回处理后的DataFrame
    """
    # 读取steam.csv数据文件
    df = pd.read_csv('C:/Users/ASUS/unit/project/steam.csv')
    
    # 数据预处理 - 日期处理
    df['release_date'] = pd.to_datetime(df['release_date'])  # 转换日期格式为对象列
    df['release_year'] = df['release_date'].dt.year  # 创建新列并提取年份
    df['release_month'] = df['release_date'].dt.month  # 创建新列并提取月份
    df['release_year_month'] = df['release_date'].dt.to_period('M')  # 创建新列并提取年月
    
    # 数据预处理 - 评价相关计算
    df['total_ratings'] = df['positive_ratings'] + df['negative_ratings']  # 计算总评价数
    df['positive_ratio'] = df['positive_ratings'] / df['total_ratings']  # 计算好评率
    df['positive_ratio'] = df['positive_ratio'].fillna(0)  # 处理空值
    
    # 数据预处理 - 销量数据处理函数
    def parse_owners(owners_str):
        """
        处理owners字段,将范围字符串转换为中值
        例如: "1000000-2000000" -> 1500000
        """
        try:
            if '-' in str(owners_str):  # 检查是否为范围格式
                low, high = owners_str.split('-')  # 分割字符串
                return (int(low) + int(high)) / 2  # 返回中值
            else:
                return float(owners_str)  # 直接转换数字
        except:
            return 0  # 异常情况返回0
    
    # 应用销量处理函数
    df['owners_median'] = df['owners'].apply(parse_owners)
    
    # 数据预处理 - 游戏类型处理
    df['main_genre'] = df['genres'].str.split(';').str[0]  # 提取第一个类型作为主要类型
    
    # 数据预处理 - 平台支持分析
    df['windows_support'] = df['platforms'].str.contains('windows')  # 检查Windows支持
    df['mac_support'] = df['platforms'].str.contains('mac')  # 检查Mac支持
    df['linux_support'] = df['platforms'].str.contains('linux')  # 检查Linux支持
    # 判断是否为多平台游戏（支持2个及以上平台）
    df['multi_platform'] = (df['windows_support'].astype(int) + 
                           df['mac_support'].astype(int) + 
                           df['linux_support'].astype(int)) >= 2
    
    # 数据预处理 - 免费游戏标识
    df['is_free'] = df['price'] == 0  # 价格为0的游戏标记为免费
    
    return df

def create_sidebar_filters(df):
    """
    创建侧边栏过滤器控件
    返回包含用户选择过滤条件的字典 
    """
    # 在侧边栏创建过滤器区域标题
    st.sidebar.header("🔧 数据过滤器")
    
    # 年份范围选择器 - 用户可以选择分析的时间范围
    min_year = int(df['release_year'].min())  # 获取数据中最小的年份
    max_year = int(df['release_year'].max())  # 获取数据中最大的年份
    year_range = st.sidebar.slider(
        "选择发布年份范围",  # 滑块标签
        min_year, max_year, (min_year, max_year)  # 最小值, 最大值, 默认范围
    )
    
    # 价格范围选择器 - 用户可以选择分析的价格区间
    max_price = float(df['price'].max())  # 获取数据中最高价格
    price_range = st.sidebar.slider(
        "选择价格范围 (美元)",  # 滑块标签
        0.0, max_price, (0.0, max_price)  # 最小值, 最大值, 默认范围(0-最高价格)
    )
    
    # 游戏类型多选框 - 用户可以选择要分析的游戏类型
    all_genres = sorted(df['main_genre'].unique())  # 获取所有唯一的游戏类型并排序
    selected_genres = st.sidebar.multiselect(
        "选择游戏类型",  # 多选框标签
        all_genres,  # 所有可选的游戏类型
        default=all_genres  # 默认选择前10个类型
    )
    
    # 平台支持多选框 - 用户可以选择要分析的平台
    platform_options = st.sidebar.multiselect(
        "选择支持平台",  # 多选框标签
        ['Windows', 'Mac', 'Linux'],  # 所有可选的平台
        default=['Windows','Mac', 'Linux']  # 默认全选
    )
    
    # 返回用户选择的所有过滤条件
    return {
        'year_range': year_range,  # 用户选择的年份范围
        'price_range': price_range,  # 用户选择的价格范围
        'selected_genres': selected_genres,  # 用户选择的游戏类型
        'platform_options': platform_options  # 用户选择的平台
    }

def apply_filters(df, filters):
    """
    根据侧边栏选择的过滤条件筛选数据
    返回过滤后的DataFrame
    """
    filtered_df = df.copy()  # 创建数据副本，避免修改原始数据
    
    # 应用年份过滤 - 只保留在用户选择年份范围内的游戏
    filtered_df = filtered_df[
        (filtered_df['release_year'] >= filters['year_range'][0]) & 
        (filtered_df['release_year'] <= filters['year_range'][1])
    ]
    
    # 应用价格过滤 - 只保留在用户选择价格范围内的游戏
    filtered_df = filtered_df[
        (filtered_df['price'] >= filters['price_range'][0]) & 
        (filtered_df['price'] <= filters['price_range'][1])
    ]
    
    # 应用游戏类型过滤 - 如果用户选择了特定类型，只保留这些类型
    if filters['selected_genres']:
        filtered_df = filtered_df[filtered_df['main_genre'].isin(filters['selected_genres'])]
    
    # 应用平台过滤 - 根据用户选择的平台进行筛选
    platform_filters = []  # 存储平台过滤条件
    if 'Windows' in filters['platform_options']:
        platform_filters.append(filtered_df['windows_support'] == True)
    if 'Mac' in filters['platform_options']:
        platform_filters.append(filtered_df['mac_support'] == True)
    if 'Linux' in filters['platform_options']:
        platform_filters.append(filtered_df['linux_support'] == True)
    
    # 如果有平台过滤条件，应用这些条件
    if platform_filters:
        platform_filter = platform_filters[0]  # 第一个过滤条件
        for pf in platform_filters[1:]:  # 遍历剩余过滤条件
            platform_filter = platform_filter | pf  # 使用OR逻辑组合条件
        filtered_df = filtered_df[platform_filter]  # 应用组合过滤条件
    
    return filtered_df  # 返回过滤后的数据

def create_all_visualizations(df):
    """
    创建所有可视化图表
    返回包含所有图表的字典
    """
    visuals = {}  # 存储所有图表的字典
    
    # 1. 游戏发布数量年度趋势分析
    yearly_releases = df.groupby('release_year').size().reset_index(name='count')  # 按年份分组计数
    yearly_releases = yearly_releases[yearly_releases['release_year'] >= 1990]  # 过滤有效年份
    fig1 = px.line(yearly_releases, x='release_year', y='count',  # 创建折线图
                  title='📈 游戏发布数量年度趋势分析',
                  labels={'release_year': '发布年份', 'count': '发布数量'},
                  markers=True)  # 显示数据点
    fig1.update_traces(line=dict(width=3))  # 设置线条粗细
    visuals['time_trend'] = fig1  # 存储图表
    
    # 2. 价格与销量关系分析
    price_analysis_df = df[(df['price'] >= 0) & (df['price'] <= 100) & (df['owners_median'] > 0)]  # 过滤有效数据
    fig2 = px.scatter(price_analysis_df, x='price', y='owners_median',  # 创建散点图
                     hover_data=['name'],  # 悬停显示游戏名
                     title='💰 游戏价格与销量关系分析',
                     labels={'price': '价格 (美元)', 'owners_median': '销量估计'},
                     opacity=0.6)  # 设置透明度
    fig2.update_traces(marker=dict(size=8))  # 设置点大小
    visuals['price_vs_sales'] = fig2
    
    # 3. 好评率与游戏时长关系分析
    engagement_df = df[(df['average_playtime'] > 0) & (df['total_ratings'] > 10)]  # 过滤有效数据
    fig3 = px.scatter(engagement_df, x='positive_ratio', y='average_playtime',  # 创建散点图
                     hover_data=['name'],
                     title='⏱️ 游戏好评率与玩家参与度关系分析',
                     labels={'positive_ratio': '好评率', 'average_playtime': '平均游戏时长(分钟)'},
                     opacity=0.6)
    fig3.update_traces(marker=dict(size=8, color='green'))  # 设置点样式
    visuals['rating_vs_playtime'] = fig3
    
    # 4. 游戏类型分布分析 - 修复后的代码
    genre_counts = df['main_genre'].value_counts().head(15)  # 获取前15个游戏类型
    # 创建DataFrame来存储类型和数量，这是正确的参数格式
    genre_df = pd.DataFrame({
        'genre': genre_counts.index,
        'count': genre_counts.values
    })
    fig4 = px.bar(genre_df, 
                 x='count',  # X轴：游戏数量
                 y='genre',  # Y轴：游戏类型
                 orientation='h',  # 水平方向
                 title='🎮 最受欢迎的游戏类型分布Top10',
                 labels={'count': '游戏数量', 'genre': '游戏类型'},
                 color='count',  # 根据数量着色
                 color_continuous_scale='viridis')  # 使用viridis颜色方案
    fig4.update_layout(showlegend=False)  # 隐藏图例
    visuals['genre_distribution'] = fig4
    
    # 5. 发行商分析 - 修复后的代码
    publisher_stats = df.groupby('publisher').agg({  # 按发行商分组统计
        'name': 'count',  # 游戏数量，使用正确的语法
        'positive_ratio': 'mean',  # 平均好评率
        'owners_median': 'mean'  # 平均销量
    }).reset_index()
    # 重命名列以便在图表中使用
    publisher_stats = publisher_stats.rename(columns={'name': 'game_count'})
    top_publishers = publisher_stats.nlargest(15, 'game_count')  # 取前15名发行商
    fig5 = px.bar(top_publishers, 
                 x='game_count',  # X轴：发行游戏数量
                 y='publisher',   # Y轴：发行商名称
                 orientation='h',  # 水平方向
                 title='🏢 发行游戏数量最多的发行商Top15',
                 labels={'game_count': '发行游戏数量', 'publisher': '发行商'},
                 color='game_count',  # 根据数量着色
                 color_continuous_scale='plasma')  # 使用plasma颜色方案
    visuals['publisher_analysis'] = fig5
    
    # 6. 平台支持分析
    platform_stats = pd.DataFrame({  # 创建平台统计DataFrame
        '平台': ['Windows', 'Mac', 'Linux'],
        '支持游戏数量': [
            df['windows_support'].sum(),  # Windows支持数量
            df['mac_support'].sum(),  # Mac支持数量
            df['linux_support'].sum()  # Linux支持数量
        ]
    })
    fig6 = px.pie(platform_stats, values='支持游戏数量', names='平台',  # 创建饼图
                 title='💻 各平台游戏支持情况分布',
                 color='平台',  # 按平台着色
                 color_discrete_map={'Windows': 'blue', 'Mac': 'gray', 'Linux': 'yellow'})  # 自定义颜色
    fig6.update_traces(textposition='inside', textinfo='percent+label')  # 设置文本显示
    visuals['platform_support'] = fig6
    
    # 7. 免费与付费游戏对比分析 - 修复后的代码
    free_paid_comparison = df.groupby('is_free').agg({  # 按是否免费分组
        'positive_ratio': 'mean',  # 平均好评率
        'average_playtime': 'mean',  # 平均游戏时长
        'owners_median': 'mean',  # 平均销量
        'name': 'count'  # 游戏数量，使用正确的语法
    }).reset_index()
    # 重命名列以便在图表中使用
    free_paid_comparison = free_paid_comparison.rename(columns={'name': 'game_count'})
    free_paid_comparison['类型'] = free_paid_comparison['is_free'].map({True: '免费游戏', False: '付费游戏'})  # 映射类型名称
    
    # 创建多子图对比分析
    fig7 = make_subplots(rows=1, cols=3,  # 1行3列布局
                        subplot_titles=('平均好评率', '平均游戏时长(分钟)', '平均销量'),  # 子图标题
                        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]])  # 所有子图都是条形图
    
    # 添加好评率子图
    fig7.add_trace(go.Bar(x=free_paid_comparison['类型'],  # X轴为游戏类型
                         y=free_paid_comparison['positive_ratio'],  # Y轴为好评率
                         marker_color=['lightblue', 'lightcoral']),  # 自定义颜色
                  row=1, col=1)  # 第1行第1列
    
    # 添加游戏时长子图
    fig7.add_trace(go.Bar(x=free_paid_comparison['类型'],  # X轴为游戏类型
                         y=free_paid_comparison['average_playtime'],  # Y轴为游戏时长
                         marker_color=['lightblue', 'lightcoral']),  # 自定义颜色
                  row=1, col=2)  # 第1行第2列
    
    # 添加销量子图
    fig7.add_trace(go.Bar(x=free_paid_comparison['类型'],  # X轴为游戏类型
                         y=free_paid_comparison['owners_median'],  # Y轴为销量
                         marker_color=['lightblue', 'lightcoral']),  # 自定义颜色
                  row=1, col=3)  # 第1行第3列
    
    fig7.update_layout(title_text='🆓 免费游戏 vs 💰 付费游戏全方位对比分析',  # 主标题
                      showlegend=False,  # 隐藏图例
                      height=500)  # 设置图表高度
    visuals['free_vs_paid'] = fig7

    # 8. 月度发布趋势分析
    # 按月份统计游戏发布数量，分析各月发布趋势
    monthly_counts = df.groupby('release_month').size().reset_index(name='game_count')  # 按月份分组统计游戏数量
    # 确保月份顺序正确（1月到12月）
    monthly_counts = monthly_counts.sort_values('release_month')  # 按月份数字排序
    
    # 创建月度发布趋势柱状图 - 使用柱状图因为月份是离散的分类数据
    fig8 = px.bar(monthly_counts, 
                 x='release_month',  # X轴：月份（1-12）
                 y='game_count',     # Y轴：游戏发布数量
                 title='📅 各月份游戏发布数量分析',
                 labels={'release_month': '月份', 'game_count': '游戏发布数量'},
                 color='game_count',  # 根据数量着色，颜色越深表示发布越多
                 color_continuous_scale='blues')  # 使用蓝色渐变颜色方案
    
    # 找到发布高峰月份 - 用于后续分析结论
    peak_month = monthly_counts.loc[monthly_counts['game_count'].idxmax()]  # 找到游戏数量最多的月份
    peak_month_num = int(peak_month['release_month'])  # 高峰月份的数字
    peak_month_count = int(peak_month['game_count'])   # 高峰月份的游戏数量
    
    # 更新图表样式，使其更美观
    fig8.update_layout(
        xaxis=dict(tickmode='linear', dtick=1),  # 设置X轴刻度为整数，每个月份都显示
        showlegend=False  # 隐藏图例，因为颜色已经表达了数量信息
    )
    
    # 在图表上标注高峰月份
    fig8.add_annotation(
        x=peak_month_num,  # 标注位置：高峰月份
        y=peak_month_count,  # 标注位置：高峰数量
        text=f"高峰: {peak_month_count}款",  # 标注文本
        showarrow=True,  # 显示箭头指向数据点
        arrowhead=2,  # 箭头样式
        bgcolor="yellow"  # 标注背景色
    )
    
    visuals['monthly_analysis'] = fig8  # 存储月度分析图表
    visuals['peak_month_info'] = (peak_month_num, peak_month_count)  # 存储高峰月份信息供分析使用
    
    return visuals  # 返回包含所有图表的字典

def create_small_multiples(df):
    """
    创建小倍数图替代地图（因为没有地理字段）
    返回小倍数图表对象
    """
    # 选择热门游戏类型进行对比分析
    top_genres = df['main_genre'].value_counts().head(6).index.tolist()  # 获取前6个热门类型
    genre_subset = df[df['main_genre'].isin(top_genres)]  # 筛选这些类型的数据
    
    # 创建小倍数散点图 - 每个类型一个子图
    fig = px.scatter(genre_subset, 
                    x='price',  # X轴：价格
                    y='positive_ratio',  # Y轴：好评率
                    color='main_genre',  # 按类型着色
                    facet_col='main_genre',  # 按类型分面（创建多个子图）
                    facet_col_wrap=3,  # 每行显示3个子图
                    hover_data=['name', 'release_year'],  # 悬停显示的信息
                    title="📊 热门游戏类型：价格 vs 好评率多维度对比",
                    labels={'price': '价格 (美元)', 'positive_ratio': '好评率'})
    
    fig.update_layout(height=600)  # 设置图表高度
    return fig  # 返回图表对象

def create_data_quality_section(df):
    """
    创建数据质量检查部分
    显示数据完整性、缺失值、重复值等信息
    """
    # 数据质量部分的主标题
    st.header("📊 数据质量报告")
    
    # 创建三列布局显示关键质量指标
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 缺失值分析 - 计算数据集中缺失值的总体比例
        missing_data = df.isnull().sum()  # 计算每列的缺失值数量
        total_cells = np.prod(df.shape)  # 修复：使用 np.prod 替代 np.product
        missing_percentage = (missing_data.sum() / total_cells) * 100  # 计算缺失值百分比
        st.metric("总缺失值比例", f"{missing_percentage:.2f}%")  # 显示缺失值比例指标
    
    with col2:
        # 重复值分析 - 计算完全重复的记录数量
        duplicates = df.duplicated().sum()  # 计算重复记录数
        st.metric("重复记录数", duplicates)  # 显示重复记录数指标
    
    with col3:
        # 数据完整性分析 - 计算没有任何缺失值的完整记录比例
        complete_rows = df.notnull().all(axis=1).sum()  # 计算完整记录数
        completeness = (complete_rows / len(df)) * 100  # 计算完整记录百分比
        st.metric("完整记录比例", f"{completeness:.2f}%")  # 显示完整性指标
    
    # 详细的数据质量分析部分
    st.subheader("详细数据质量指标")
    
    # 各列缺失值统计 - 创建详细的缺失值分析表格
    missing_stats = pd.DataFrame({
        '列名': df.columns,  # 所有列名
        '缺失值数量': df.isnull().sum().values,  # 每列的缺失值数量
        '缺失值比例': (df.isnull().sum() / len(df) * 100).values  # 每列的缺失值百分比
    })
    missing_stats = missing_stats[missing_stats['缺失值数量'] > 0]  # 只显示有缺失值的列
    
    if len(missing_stats) > 0:
        st.write("**各列缺失值统计:**")  # 表格标题
        st.dataframe(missing_stats, use_container_width=True)  # 显示缺失值统计表格
    else:
        st.success("✅ 没有发现缺失值")  # 如果没有缺失值，显示成功消息
    
    # 数据验证检查部分 - 检查数据的逻辑一致性
    st.subheader("数据验证检查")
    
    # 定义数据验证检查项
    validation_checks = [
        ("价格非负", (df['price'] >= 0).all()),  # 检查所有价格是否都非负
        ("好评率在0-1之间", ((df['positive_ratio'] >= 0) & (df['positive_ratio'] <= 1)).all()),  # 检查好评率范围
        ("游戏时长非负", (df['average_playtime'] >= 0).all()),  # 检查游戏时长非负
        ("发布日期合理", (df['release_year'] >= 1990).all())  # 检查发布日期合理性
    ]
    
    # 显示每个验证检查的结果
    for check_name, check_result in validation_checks:
        if check_result:
            st.success(f"✅ {check_name}")  # 检查通过，显示成功图标
        else:
            st.error(f"❌ {check_name}")  # 检查失败，显示错误图标

def calculate_key_metrics(df):
    """
    计算关键指标和统计数据
    返回包含各种指标的字典
    """
    metrics = {}  # 存储指标的字典
    
    # 基础统计指标
    metrics['total_games'] = len(df)  # 游戏总数
    metrics['free_game_percentage'] = df['is_free'].mean() * 100  # 免费游戏比例
    metrics['avg_rating'] = df['positive_ratio'].mean() * 100  # 平均好评率
    metrics['year_range'] = f"{df['release_year'].min()}-{df['release_year'].max()}"  # 时间范围
    
    # 时间趋势相关指标
    yearly_releases = df.groupby('release_year').size().reset_index(name='count')
    peak_year = yearly_releases.loc[yearly_releases['count'].idxmax()]  # 找到发布高峰年份
    metrics['peak_year'] = int(peak_year['release_year'])  # 高峰年份
    metrics['peak_year_count'] = int(peak_year['count'])  # 高峰年份发布数量
    
    # 价格相关指标
    price_stats = df[df['price'] > 0]  # 只考虑付费游戏
    metrics['avg_price'] = price_stats['price'].mean()  # 平均价格
    metrics['median_price'] = price_stats['price'].median()  # 价格中位数
    
    # 平台相关指标
    metrics['windows_games'] = df['windows_support'].sum()  # Windows游戏数量
    metrics['mac_games'] = df['mac_support'].sum()  # Mac游戏数量
    metrics['linux_games'] = df['linux_support'].sum()  # Linux游戏数量
    metrics['multi_platform_games'] = df['multi_platform'].sum()  # 多平台游戏数量
    
    # 类型相关指标
    genre_counts = df['main_genre'].value_counts()  # 类型计数
    metrics['top_genres'] = genre_counts.head(5).index.tolist()  # 前5个类型
    metrics['unique_genres'] = df['main_genre'].nunique()  # 唯一类型数量

     # 月度分析相关指标 - 新增的月度统计数据
    monthly_counts = df.groupby('release_month').size()  # 按月份统计游戏数量
    metrics['peak_month'] = int(monthly_counts.idxmax())  # 发布高峰月份（1-12）
    metrics['peak_month_count'] = int(monthly_counts.max())  # 高峰月份的游戏数量
    metrics['slow_month'] = int(monthly_counts.idxmin())  # 发布低谷月份
    metrics['slow_month_count'] = int(monthly_counts.min())  # 低谷月份的游戏数量
    
    return metrics  # 返回包含所有指标的字典

def main():
    """
    Streamlit应用主函数
    构建完整的网页应用界面
    """
    # 设置网页配置 - 这些设置会影响整个网页应用的显示
    st.set_page_config(
        page_title="Steam游戏数据分析平台",  # 浏览器标签页标题
        page_icon="🎮",  # 网页图标（显示在浏览器标签页）
        layout="wide",  # 宽屏布局（充分利用屏幕宽度）
        initial_sidebar_state="expanded"  # 侧边栏初始状态为展开
    )
    
    # 显示加载状态 - 在数据加载和处理期间显示旋转图标
    with st.spinner('🚀 正在加载数据和生成可视化图表...'):
        # 加载并预处理数据
        df = load_and_preprocess_data()
        
        # 创建侧边栏过滤器 - 在左侧边栏显示过滤控件
        filters = create_sidebar_filters(df)
        
        # 应用过滤器 - 根据用户选择筛选数据
        filtered_df = apply_filters(df, filters)
        
        # 创建所有可视化图表 - 基于过滤后的数据生成图表
        visuals = create_all_visualizations(filtered_df)
        
        # 计算关键指标 - 基于过滤后的数据计算KPI
        metrics = calculate_key_metrics(filtered_df)
    
    # 应用主标题 - 显示在网页顶部的标题
    st.title("🎮 Steam游戏数据分析平台")
    
    # 创建顶部标签页导航 - 在现有标签页中添加月度分析
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📋 数据集概览",      # 标签1：数据概览和基本信息
        "📈 时间趋势分析",    # 标签2：时间序列分析  
        "📅 月度发布分析",    # 标签3：新增的月度分析板块 🆕
        "💰 价格销量分析",    # 标签4：价格与销售关系分析
        "⏱️ 评价参与度分析",  # 标签5：评价与用户参与度分析
        "🎮 游戏类型分析",    # 标签6：游戏类型分布分析
        "🏢 开发商分析",      # 标签7：开发商和发行商分析
        "💻 平台支持分析",    # 标签8：跨平台支持分析
        "🆓 免费付费分析",    # 标签9：商业模式对比分析
        "📊 小倍数分析",      # 标签10：多维度对比分析
        "✅ 数据质量报告"     # 标签11：数据质量检查
    ])
    
    # 数据集概览模块 - 标签页1的内容
    with tab1:
        st.header("📋 数据集概览")  # 模块标题
        
        # 创建指标卡片布局 - 使用4列布局显示关键指标
        col1, col2, col3, col4 = st.columns(4)  # 创建4个等宽列
        
        with col1:
            # 显示游戏总数指标卡
            st.metric("游戏总数", f"{metrics['total_games']:,}")  # 使用千位分隔符格式化数字
            
        with col2:
            # 显示免费游戏比例指标卡
            st.metric("免费游戏比例", f"{metrics['free_game_percentage']:.1f}%")  # 保留1位小数
            
        with col3:
            # 显示平均好评率指标卡
            st.metric("平均好评率", f"{metrics['avg_rating']:.1f}%")  # 保留1位小数
            
        with col4:
            # 显示数据时间范围指标卡
            st.metric("数据时间范围", metrics['year_range'])  # 显示年份范围
        
        # 数据样本展示部分
        st.subheader("📄 数据样本预览")  # 子标题
        # 选择要显示的列并展示前10行数据
        sample_data = df[['name', 'release_year', 'main_genre', 'price', 'positive_ratio', 'owners_median']].head(10)
        st.dataframe(sample_data, use_container_width=True)  # 显示数据表格，自适应容器宽度
        
        # 数据集基本信息部分
        st.subheader("ℹ️ 数据集基本信息")  # 子标题
        col1, col2 = st.columns(2)  # 创建2列布局
        
        with col1:
            # 左侧列显示基础统计信息
            st.write(f"- **总记录数**: {metrics['total_games']:,}")  # 总记录数
            st.write(f"- **数据列数**: {len(df.columns)}")  # 数据列数
            st.write(f"- **游戏类型数量**: {metrics['unique_genres']}")  # 唯一游戏类型数量
            
        with col2:
            # 右侧列显示平台支持信息
            st.write(f"- **Windows游戏**: {metrics['windows_games']:,}")  # Windows平台游戏数
            st.write(f"- **Mac游戏**: {metrics['mac_games']:,}")  # Mac平台游戏数
            st.write(f"- **Linux游戏**: {metrics['linux_games']:,}")  # Linux平台游戏数
    
    # 时间趋势分析模块 - 标签页2的内容
    with tab2:
        st.header("📈 游戏发布趋势分析")  # 模块标题
        
        # 显示年度趋势图表
        st.plotly_chart(visuals['time_trend'], use_container_width=True)  # 显示图表，自适应宽度
        
        # 添加分析结论部分
        st.subheader("📝 分析结论")  # 子标题
        
        # 使用信息框显示关键发现 - 突出显示重要信息
        st.info(f"🎯 **发布高峰年份**: {metrics['peak_year']}年，发布了 {metrics['peak_year_count']} 款游戏")
        st.success(f"🚀 **热门游戏类型**: {', '.join(metrics['top_genres'])}")  # 显示热门类型
    
    # 月度发布分析模块 - 标签页3的内容
    with tab3:
        st.header("📅 游戏发布月度趋势分析")  # 模块标题
        
        # 显示月度分析柱状图
        st.plotly_chart(visuals['monthly_analysis'], use_container_width=True)  # 显示月度发布趋势图
        
        # 月度分析结论部分
        st.subheader("📊 月度发布统计分析")  # 子标题
        
        # 创建三列布局显示月度统计数据
        col1, col2, col3 = st.columns(3)  # 创建3列布局
        
        with col1:
            # 显示发布高峰月份和数量
            peak_month_num, peak_month_count = visuals['peak_month_info']  # 获取高峰月份信息
            st.metric("发布高峰月份", f"{peak_month_num}月")  # 显示高峰月份
            st.metric("高峰月发布数量", f"{peak_month_count}款")  # 显示高峰月游戏数量
            
        with col2:
            # 显示发布低谷月份和数量
            st.metric("发布低谷月份", f"{metrics['slow_month']}月")  # 显示低谷月份
            st.metric("低谷月发布数量", f"{metrics['slow_month_count']}款")  # 显示低谷月游戏数量
            
        with col3:
            # 显示月度发布差异
            monthly_variation = metrics['peak_month_count'] - metrics['slow_month_count']  # 计算高低峰差异
            st.metric("月间最大差异", f"{monthly_variation}款")  # 显示月度发布差异
            avg_monthly = len(df) // 12  # 计算月平均发布数量
            st.metric("月平均发布量", f"{avg_monthly}款")  # 显示月平均发布量
        
        # 分析结论
        st.subheader("🔍 月度发布规律分析")  # 子标题
        
        # 使用信息框突出显示关键发现
        st.info(f"🎯 **年度发布高峰**: {metrics['peak_month']}月是游戏发布最集中的月份，共发布了 {metrics['peak_month_count']} 款游戏")
        st.warning(f"📉 **年度发布低谷**: {metrics['slow_month']}月是游戏发布最少的月份，仅发布了 {metrics['slow_month_count']} 款游戏")
        

        # 价格销量分析模块 - 标签页4的内容
    with tab4:
        st.header(" 价格与销量关系分析")  # 模块标题
    
        # 价格区间分析部分
        st.subheader(" 价格区间销量分析")  # 子标题
    
        # 创建价格区间分析
        price_bins = [0, 5, 10, 20, 30, 50, 100, float('inf')]  # 定义价格区间
        price_labels = ['免费', '0-5$', '5-10$', '10-20$', '20-30$', '30-50$', '50$+']  # 区间标签
    
        # 为数据分配价格区间
        df_price_analysis = df.copy()
        df_price_analysis['price_range'] = pd.cut(df_price_analysis['price'], bins=price_bins, labels=price_labels, right=False)
    
        # 计算每个价格区间的平均销量和游戏数量
        price_range_stats = df_price_analysis.groupby('price_range').agg({
            'owners_median': 'mean',  # 平均销量
            'name': 'count',  # 游戏数量
            'positive_ratio': 'mean'  # 平均好评率
        }).reset_index()
    
        # 创建价格区间分析图表
        col1, col2 = st.columns(2)  # 创建2列布局
    
        with col1:
            # 价格区间 vs 平均销量柱状图
            fig_price_sales = px.bar(price_range_stats, 
                               x='price_range', 
                               y='owners_median',
                               title=' 各价格区间平均销量',
                               labels={'price_range': '价格区间', 'owners_median': '平均销量'},
                               color='owners_median',
                               color_continuous_scale='viridis')
            st.plotly_chart(fig_price_sales, use_container_width=True)
    
        with col2:
            # 价格区间 vs 游戏数量柱状图
            fig_price_count = px.bar(price_range_stats, 
                               x='price_range', 
                               y='name',
                               title=' 各价格区间游戏数量', 
                               labels={'price_range': '价格区间', 'name': '游戏数量'},
                               color='name',
                               color_continuous_scale='plasma')
            st.plotly_chart(fig_price_count, use_container_width=True)
    
        # 关键指标统计
        st.subheader("💡 关键价格指标")  # 子标题
        col1, col2, col3, col4 = st.columns(4)  # 创建4列布局
    
        with col1:
           # 显示平均价格指标
           st.metric("平均价格", f"${metrics['avg_price']:.2f}")  # 格式化价格显示
        
        with col2:
           # 显示价格中位数指标
           st.metric("价格中位数", f"${metrics['median_price']:.2f}")  # 格式化价格显示
        
        with col3:
           # 显示免费游戏数量指标
           free_count = df['is_free'].sum()  # 计算免费游戏总数
           st.metric("免费游戏数量", f"{free_count:,}")  # 显示免费游戏数
        
        with col4:
           # 显示最畅销价格区间
           best_price_range = price_range_stats.loc[price_range_stats['owners_median'].idxmax()]
           st.metric("最畅销价格区间", best_price_range['price_range'])  # 显示最畅销价格区间
    
    


    # 评价参与度分析模块 - 标签页5的内容
    with tab5:
        st.header("⏱️ 游戏评价与玩家参与度分析")  # 模块标题
        
        # 显示评价时长关系图
        st.plotly_chart(visuals['rating_vs_playtime'], use_container_width=True)  # 显示评价与时长关系图
        
        # 参与度分析部分
        st.subheader("🎯 玩家参与度分析")  # 子标题
        
        # 计算不同时长区间的评价表现
        short_play = df[df['average_playtime'] < 100]  # 短时长游戏（小于100分钟）
        medium_play = df[(df['average_playtime'] >= 100) & (df['average_playtime'] <= 1000)]  # 中等时长（100-1000分钟）
        long_play = df[df['average_playtime'] > 1000]  # 长时长游戏（大于1000分钟）
        
        col1, col2, col3 = st.columns(3)  # 创建3列布局显示不同时长区间的评价
        
        with col1:
            short_rating = short_play['positive_ratio'].mean() * 100  # 短时长平均好评率
            st.metric("短时长游戏好评率", f"{short_rating:.1f}%")  # 显示短时长好评率
            
        with col2:
            medium_rating = medium_play['positive_ratio'].mean() * 100  # 中等时长平均好评率
            st.metric("中等时长游戏好评率", f"{medium_rating:.1f}%")  # 显示中等时长好评率
            
        with col3:
            long_rating = long_play['positive_ratio'].mean() * 100  # 长时长平均好评率
            st.metric("长时长游戏好评率", f"{long_rating:.1f}%")  # 显示长时长好评率
        
        # 分析结论
        st.write("""
        **分析结论:**
        - 游戏时长与好评率呈现正相关关系
        - 玩家投入时间越多，对游戏的评价往往越正面
        - 游戏深度和内容质量是维持玩家长期参与的关键因素
        """)  # 参与度分析结论
    
    # 游戏类型分析模块 - 标签页6的内容
    with tab6:
        st.header("🎮 游戏类型市场分析")  # 模块标题
        
        # 显示类型分布图
        st.plotly_chart(visuals['genre_distribution'], use_container_width=True)  # 显示类型分布图
        
        # 市场洞察
        st.write("""
        **市场洞察:**
        - Action和Adventure类型在数量上占据市场主导
        - 不同类型在定价策略和玩家接受度上存在显著差异
        - 小众类型可能在某些细分市场表现突出
        """)  # 类型分析结论
    

    # 开发商分析模块 - 标签页7的内容
    with tab7:
        st.header("🏢 游戏开发商与发行商分析")  # 模块标题
        
        # 显示发行商数量图
        st.plotly_chart(visuals['publisher_analysis'], use_container_width=True)  # 显示发行商分析图
        
        # Valve专门分析部分（Steam平台所有者）
        st.subheader("⭐ Valve专门分析")  # 子标题
        
        # 筛选Valve发行的游戏
        valve_games = df[df['publisher'] == 'Valve']  # Valve发行的游戏
        non_valve_games = df[df['publisher'] != 'Valve']  # 非Valve发行的游戏
        
        # 如果存在Valve游戏，显示详细分析
        if len(valve_games) > 0:
            col1, col2, col3 = st.columns(3)  # 创建3列布局
            
            with col1:
                st.metric("Valve游戏数量", len(valve_games))  # Valve游戏数量
                
            with col2:
                valve_rating = valve_games['positive_ratio'].mean() * 100  # Valve平均好评率
                st.metric("Valve平均好评率", f"{valve_rating:.1f}%")  # 显示Valve好评率
                
            with col3:
                valve_sales = valve_games['owners_median'].mean()  # Valve平均销量
                st.metric("Valve平均销量", f"{valve_sales:,.0f}")  # 显示Valve销量
            
            # Valve表现分析结论
            st.write("""
            **Valve表现分析:**
            - 作为平台方，Valve在游戏质量和数量上都表现优异
            - Valve游戏通常具有较高的制作标准和玩家认可度
            - 平台生态与第一方游戏形成良性循环
            """)  # Valve专门分析
    
    # 平台支持分析模块 - 标签页8的内容
    with tab8:
        st.header("💻 跨平台支持分析")  # 模块标题
        
        # 显示平台分布饼图
        st.plotly_chart(visuals['platform_support'], use_container_width=True)  # 显示平台支持饼图
        
        # 多平台vs单平台对比分析
        st.subheader("🔧 多平台支持价值分析")  # 子标题
        
        # 计算多平台和单平台游戏的对比指标
        platform_comparison = df.groupby('multi_platform').agg({
            'positive_ratio': 'mean',  # 平均好评率
            'owners_median': 'mean',  # 平均销量
            'average_playtime': 'mean',  # 平均游戏时长
            'name': 'count'  # 游戏数量
        }).reset_index()
        platform_comparison['平台类型'] = platform_comparison['multi_platform'].map({True: '多平台游戏', False: '单平台游戏'})
        
        # 显示平台对比数据 - 遍历每行数据并格式化显示
        for _, row in platform_comparison.iterrows():
            st.write(f"**{row['平台类型']}**")  # 平台类型标题
            st.write(f"- 游戏数量: {row['name']:,}款 ({row['name']/len(df)*100:.1f}%)")  # 游戏数量及占比
            st.write(f"- 平均好评率: {row['positive_ratio']:.2%}")  # 平均好评率（百分比格式）
            st.write(f"- 平均销量: {row['owners_median']:,.0f}")  # 平均销量（千位分隔）
            st.write(f"- 平均游戏时长: {row['average_playtime']:.0f}分钟")  # 平均游戏时长
            st.write("")  # 空行分隔，提高可读性
        
        # 平台策略建议
        st.write("""
        **平台策略建议:**
        - 多平台游戏在销量和评价上普遍表现更好
        - Windows是必须支持的基础平台
        - 支持Mac和Linux可以触及更广泛的玩家群体
        - 跨平台开发需要考虑技术成本和目标用户
        """)  # 平台策略分析结论
    
    # 免费付费分析模块 - 标签页9的内容
    with tab9:
        st.header("🆓 免费 vs 付费游戏商业模式分析")  # 模块标题
        
        # 显示免费付费对比图
        st.plotly_chart(visuals['free_vs_paid'], use_container_width=True)  # 显示免费付费对比图
        
        # 详细商业模式分析部分
        st.subheader("💼 商业模式深度分析")  # 子标题
        
        # 获取免费付费对比数据
        free_paid_stats = df.groupby('is_free').agg({
            'name': 'count',  # 游戏数量
            'positive_ratio': 'mean',  # 平均好评率
            'average_playtime': 'mean',  # 平均游戏时长
            'owners_median': 'mean',  # 平均销量
            'achievements': 'mean'  # 平均成就数量
        }).reset_index()
        free_paid_stats['类型'] = free_paid_stats['is_free'].map({True: '免费游戏', False: '付费游戏'})
        
        # 显示详细对比 - 遍历免费和付费游戏类型
        for _, row in free_paid_stats.iterrows():
            st.write(f"### {row['类型']}")  # 使用三级标题显示游戏类型
            col1, col2, col3, col4 = st.columns(4)  # 创建4列布局显示指标
            
            with col1:
                st.metric("游戏数量", f"{row['name']:,}")  # 游戏数量
                
            with col2:
                st.metric("平均好评率", f"{row['positive_ratio']:.2%}")  # 平均好评率（百分比格式）
                
            with col3:
                st.metric("平均游戏时长", f"{row['average_playtime']:.0f}")  # 平均游戏时长
                
            with col4:
                st.metric("平均销量", f"{row['owners_median']:,.0f}")  # 平均销量
        

    
    # 小倍数分析模块 - 标签页10的内容（新增）
    with tab10:
        st.header("📊 多维度对比分析")  # 模块标题
        
        # 创建并显示小倍数图
        small_multiples_fig = create_small_multiples(df)  # 生成小倍数图
        st.plotly_chart(small_multiples_fig, use_container_width=True)  # 显示小倍数图
        
        # 小倍数图分析说明
        st.subheader("🔍 分析说明")  # 子标题
        st.write("""
        **小倍数图解读指南:**
        - 每个子图代表一个游戏类型的价格与好评率关系
        - 点的位置显示该类型游戏的定价策略和市场接受度
        - 点的颜色区分不同游戏类型，便于对比分析
        - 右上角的类型表示高价格高评价的优质游戏
        - 左下角的类型可能表示低价格低评价的入门级游戏
        """)  # 小倍数图解读说明
    
    # 数据质量报告模块 - 标签页11的内容（新增）
    with tab11:
        # 调用数据质量检查函数，显示完整的数据质量报告
        create_data_quality_section(df)  # 注意：这里使用原始数据df而不是filtered_df

    

    
    # 页脚信息 - 显示在网页底部
    st.markdown("---")  # 分隔线
    st.markdown("🎮 *Steam游戏数据分析平台:基于真实Steam数据集的分析工具*")  # 平台描述
    st.markdown("📧 *数据来源: Steam游戏数据库*")  # 数据来源和技术栈
    st.markdown("🔧*分析工具: Python + Streamlit*")

# 程序入口点 - 确保代码只在直接运行时执行，不在导入时执行
if __name__ == "__main__":
    # 运行Streamlit应用
    main()