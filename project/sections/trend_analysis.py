import streamlit as st  # 导入streamlit用于创建网页应用界面
import pandas as pd  # 导入pandas用于数据处理
import plotly.express as px  # 导入plotly.express用于创建交互式图表

def show_tab2(df, metrics, visuals):
    """
    显示标签页2：时间趋势分析
    对应原标签页2的内容
    """
    st.header("📈 Game Release Trend Analysis")  # 模块标题
    st.plotly_chart(visuals['time_trend'], use_container_width=True)  # 显示年度趋势图表，自适应宽度
    st.subheader("📝 Analysis Conclusions")  # 分析结论子标题
    st.info(f"🎯 **Peak Release Year**: {metrics['peak_year']}, released {metrics['peak_year_count']} games")  # 使用信息框显示发布高峰年份
    st.success(f"🚀 **Popular Game Genres**: {', '.join(metrics['top_genres'])}")  # 使用成功框显示热门游戏类型

def show_tab3(df, metrics, visuals):
    """
    显示标签页3：月度发布分析
    对应原标签页3的内容
    """
    st.header("📅 Monthly Game Release Trend Analysis")  # 模块标题
    st.plotly_chart(visuals['monthly_analysis'], use_container_width=True)  # 显示月度分析柱状图，自适应宽度
    st.subheader("📊 Monthly Release Statistics")  # 月度发布统计子标题
    
    col1, col2, col3 = st.columns(3)  # 创建3列布局显示月度统计数据
    
    with col1:
        peak_month_num, peak_month_count = visuals['peak_month_info']  # 获取高峰月份信息
        st.metric("Peak Release Month", f"Month {peak_month_num}")  # 显示发布高峰月份
        st.metric("Peak Month Release Count", f"{peak_month_count} games")  # 显示高峰月游戏数量
    
    with col2:
        st.metric("Lowest Release Month", f"Month {metrics['slow_month']}")  # 显示发布低谷月份
        st.metric("Lowest Month Release Count", f"{metrics['slow_month_count']} games")  # 显示低谷月游戏数量
    
    with col3:
        monthly_variation = metrics['peak_month_count'] - metrics['slow_month_count']  # 计算高低峰差异
        st.metric("Maximum Monthly Difference", f"{monthly_variation} games")  # 显示月度发布差异
        avg_monthly = len(df) // 12  # 计算月平均发布数量
        st.metric("Average Monthly Release", f"{avg_monthly} games")  # 显示月平均发布量
    
    st.subheader("🔍 Monthly Release Pattern Analysis")  # 月度发布规律分析子标题
    st.info(f"🎯 **Annual Release Peak**: Month {metrics['peak_month']} is the most concentrated month for game releases, with {metrics['peak_month_count']} games released")  # 使用信息框突出显示年度发布高峰
    st.warning(f"📉 **Annual Release Low**: Month {metrics['slow_month']} is the month with the fewest game releases, with only {metrics['slow_month_count']} games released")  # 使用警告框突出显示年度发布低谷

def show_tab4(df, metrics, visuals):
    """
    显示标签页4：价格销量分析
    对应原标签页4的内容
    """
    st.header("💰 Price vs Sales Analysis")  # 模块标题
    st.plotly_chart(visuals['price_vs_sales'], use_container_width=True)  # 显示价格与销量关系散点图，自适应宽度
    
    # 价格区间分析部分
    st.subheader("💰 Price Range Sales Analysis")  # 价格区间分析子标题
    
    price_bins = [0, 5, 10, 20, 30, 50, 100, float('inf')]  # 定义价格区间边界
    price_labels = ['Free', '0-5$', '5-10$', '10-20$', '20-30$', '30-50$', '50$+']  # 价格区间标签
    
    df_price_analysis = df.copy()  # 创建数据副本用于价格分析
    df_price_analysis['price_range'] = pd.cut(df_price_analysis['price'], bins=price_bins, labels=price_labels, right=False)  # 为数据分配价格区间
    
    price_range_stats = df_price_analysis.groupby('price_range').agg({  # 按价格区间分组统计
        'owners_median': 'mean',  # 平均销量
        'name': 'count',  # 游戏数量
        'positive_ratio': 'mean'  # 平均好评率
    }).reset_index()  # 重置索引
    
    col1, col2 = st.columns(2)  # 创建2列布局显示价格区间分析图表
    
    with col1:
        fig_price_sales = px.bar(price_range_stats,  # 创建价格区间vs平均销量柱状图
                               x='price_range',  # X轴：价格区间
                               y='owners_median',  # Y轴：平均销量
                               title='💰 Average Sales by Price Range',  # 图表标题
                               labels={'price_range': 'Price Range', 'owners_median': 'Average Sales'},  # 轴标签重命名
                               color='owners_median',  # 根据平均销量值着色
                               color_continuous_scale='viridis')  # 使用viridis颜色方案
        st.plotly_chart(fig_price_sales, use_container_width=True)  # 显示图表，自适应宽度
    
    with col2:
        fig_price_count = px.bar(price_range_stats,  # 创建价格区间vs游戏数量柱状图
                               x='price_range',  # X轴：价格区间
                               y='name',  # Y轴：游戏数量
                               title='📊 Game Count by Price Range',  # 图表标题
                               labels={'price_range': 'Price Range', 'name': 'Number of Games'},  # 轴标签重命名
                               color='name',  # 根据游戏数量值着色
                               color_continuous_scale='plasma')  # 使用plasma颜色方案
        st.plotly_chart(fig_price_count, use_container_width=True)  # 显示图表，自适应宽度
    
    st.subheader("💡 Key Price Metrics")  # 关键价格指标子标题
    col1, col2, col3, col4 = st.columns(4)  # 创建4列布局显示价格相关指标
    
    with col1:
        st.metric("Average Price", f"${metrics['avg_price']:.2f}")  # 显示平均价格指标，格式化显示2位小数
    
    with col2:
        st.metric("Median Price", f"${metrics['median_price']:.2f}")  # 显示价格中位数指标，格式化显示2位小数
    
    with col3:
        free_count = df['is_free'].sum()  # 计算免费游戏总数
        st.metric("Free Games Count", f"{free_count:,}")  # 显示免费游戏数量指标，使用千位分隔符
    
    with col4:
        best_price_range = price_range_stats.loc[price_range_stats['owners_median'].idxmax()]  # 找到最畅销价格区间
        st.metric("Best-selling Price Range", best_price_range['price_range'])  # 显示最畅销价格区间指标

def show_tab5(df, metrics, visuals):
    """
    显示标签页5：评价参与度分析
    对应原标签页5的内容
    """
    st.header("⏱️ Game Rating & Player Engagement Analysis")  # 模块标题
    st.plotly_chart(visuals['rating_vs_playtime'], use_container_width=True)  # 显示评价与时长关系图，自适应宽度
    
    st.subheader("🎯 Player Engagement Analysis")  # 玩家参与度分析子标题
    
    short_play = df[df['average_playtime'] < 100]  # 筛选短时长游戏（小于100分钟）
    medium_play = df[(df['average_playtime'] >= 100) & (df['average_playtime'] <= 1000)]  # 筛选中等时长游戏（100-1000分钟）
    long_play = df[df['average_playtime'] > 1000]  # 筛选长时长游戏（大于1000分钟）
    
    col1, col2, col3 = st.columns(3)  # 创建3列布局显示不同时长区间的评价
    
    with col1:
        short_rating = short_play['positive_ratio'].mean() * 100  # 计算短时长游戏平均好评率
        st.metric("Short Playtime Positive Rating", f"{short_rating:.1f}%")  # 显示短时长游戏好评率指标，保留1位小数
    
    with col2:
        medium_rating = medium_play['positive_ratio'].mean() * 100  # 计算中等时长游戏平均好评率
        st.metric("Medium Playtime Positive Rating", f"{medium_rating:.1f}%")  # 显示中等时长游戏好评率指标，保留1位小数
    
    with col3:
        long_rating = long_play['positive_ratio'].mean() * 100  # 计算长时长游戏平均好评率
        st.metric("Long Playtime Positive Rating", f"{long_rating:.1f}%")  # 显示长时长游戏好评率指标，保留1位小数
    
    st.write("""  # 参与度分析结论
    **Analysis Conclusions:**
    - Game playtime shows positive correlation with positive ratings
    - The more time players invest, the more positive their evaluations tend to be
    - Game depth and content quality are key factors in maintaining long-term player engagement
    """)