import streamlit as st  # 导入streamlit用于创建网页应用界面
import pandas as pd  # 导入pandas用于数据处理
import plotly.express as px  # 导入plotly.express用于创建交互式图表
from utils.viz import create_small_multiples  # 从utils.viz模块导入小倍数图函数

def show_tab6(df, metrics, visuals):
    """
    显示标签页6：游戏类型分析
    对应原标签页6的内容
    """
    st.header("🎮 Game Genre Market Analysis")  # 模块标题
    st.plotly_chart(visuals['genre_distribution'], use_container_width=True)  # 显示类型分布图，自适应宽度
    st.write("""  # 市场洞察分析
    **Market Insights:**
    - Action and Adventure genres dominate the market in terms of quantity
    - Different genres show significant differences in pricing strategies and player acceptance
    - Niche genres may perform exceptionally well in specific market segments
    """)

def show_tab7(df, metrics, visuals):
    """
    显示标签页7：开发商分析
    对应原标签页7的内容
    """
    st.header("🏢 Game Developer & Publisher Analysis")  # 模块标题
    st.plotly_chart(visuals['publisher_analysis'], use_container_width=True)  # 显示发行商分析图，自适应宽度
    
    st.subheader("⭐ Valve Special Analysis")  # Valve专门分析子标题
    
    valve_games = df[df['publisher'] == 'Valve']  # 筛选Valve发行的游戏
    non_valve_games = df[df['publisher'] != 'Valve']  # 筛选非Valve发行的游戏
    
    if len(valve_games) > 0:  # 如果存在Valve游戏
        col1, col2, col3 = st.columns(3)  # 创建3列布局显示Valve分析指标
        
        with col1:
            st.metric("Valve Games Count", len(valve_games))  # 显示Valve游戏数量指标
        
        with col2:
            valve_rating = valve_games['positive_ratio'].mean() * 100  # 计算Valve游戏平均好评率
            st.metric("Valve Average Positive Rating", f"{valve_rating:.1f}%")  # 显示Valve平均好评率指标，保留1位小数
        
        with col3:
            valve_sales = valve_games['owners_median'].mean()  # 计算Valve游戏平均销量
            st.metric("Valve Average Sales", f"{valve_sales:,.0f}")  # 显示Valve平均销量指标，使用千位分隔符
        
        st.write("""  # Valve表现分析结论
        **Valve Performance Analysis:**
        - As the platform owner, Valve excels in both game quality and quantity
        - Valve games typically have high production standards and player recognition
        - Platform ecosystem and first-party games form a virtuous cycle
        """)

def show_tab8(df, metrics, visuals):
    """
    显示标签页8：平台支持分析
    对应原标签页8的内容
    """
    st.header("💻 Cross-platform Support Analysis")  # 模块标题
    st.plotly_chart(visuals['platform_support'], use_container_width=True)  # 显示平台支持饼图，自适应宽度
    
    st.subheader("🔧 Multi-platform Support Value Analysis")  # 多平台支持价值分析子标题
    
    platform_comparison = df.groupby('multi_platform').agg({  # 按多平台支持分组统计
        'positive_ratio': 'mean',  # 平均好评率
        'owners_median': 'mean',  # 平均销量
        'average_playtime': 'mean',  # 平均游戏时长
        'name': 'count'  # 游戏数量
    }).reset_index()  # 重置索引
    platform_comparison['Platform Type'] = platform_comparison['multi_platform'].map({True: 'Multi-platform Games', False: 'Single-platform Games'})  # 映射平台类型名称
    
    for _, row in platform_comparison.iterrows():  # 遍历平台对比数据
        st.write(f"**{row['Platform Type']}**")  # 显示平台类型标题
        st.write(f"- Game Count: {row['name']:,} games ({row['name']/len(df)*100:.1f}%)")  # 显示游戏数量及占比，使用千位分隔符
        st.write(f"- Average Positive Rating: {row['positive_ratio']:.2%}")  # 显示平均好评率，百分比格式
        st.write(f"- Average Sales: {row['owners_median']:,.0f}")  # 显示平均销量，使用千位分隔符
        st.write(f"- Average Playtime: {row['average_playtime']:.0f} minutes")  # 显示平均游戏时长
        st.write("")  # 空行分隔，提高可读性
    
    st.write("""  # 平台策略建议
    **Platform Strategy Recommendations:**
    - Multi-platform games generally perform better in both sales and ratings
    - Windows is the essential base platform that must be supported
    - Supporting Mac and Linux can reach a wider player base
    - Cross-platform development requires consideration of technical costs and target users
    """)

def show_tab9(df, metrics, visuals):
    """
    显示标签页9：免费付费分析
    对应原标签页9的内容
    """
    st.header("🆓 Free vs Paid Games Business Model Analysis")  # 模块标题
    st.plotly_chart(visuals['free_vs_paid'], use_container_width=True)  # 显示免费付费对比图，自适应宽度
    
    st.subheader("💼 Business Model Deep Analysis")  # 商业模式深度分析子标题
    
    free_paid_stats = df.groupby('is_free').agg({  # 按是否免费分组统计
        'name': 'count',  # 游戏数量
        'positive_ratio': 'mean',  # 平均好评率
        'average_playtime': 'mean',  # 平均游戏时长
        'owners_median': 'mean',  # 平均销量
        'achievements': 'mean'  # 平均成就数量
    }).reset_index()  # 重置索引
    free_paid_stats['Type'] = free_paid_stats['is_free'].map({True: 'Free Games', False: 'Paid Games'})  # 映射类型名称
    
    for _, row in free_paid_stats.iterrows():  # 遍历免费和付费游戏统计数据
        st.write(f"### {row['Type']}")  # 使用三级标题显示游戏类型
        col1, col2, col3, col4 = st.columns(4)  # 创建4列布局显示详细指标
        
        with col1:
            st.metric("Game Count", f"{row['name']:,}")  # 显示游戏数量，使用千位分隔符
        
        with col2:
            st.metric("Average Positive Rating", f"{row['positive_ratio']:.2%}")  # 显示平均好评率，百分比格式
        
        with col3:
            st.metric("Average Playtime", f"{row['average_playtime']:.0f}")  # 显示平均游戏时长
        
        with col4:
            st.metric("Average Sales", f"{row['owners_median']:,.0f}")  # 显示平均销量，使用千位分隔符
    
    st.write("""  # 商业模式选择建议
    **Business Model Selection Recommendations:**
    - **Free Games**: Suitable for products pursuing user scale and network effects
    - **Paid Games**: Suitable for products focusing on core experience and single sales
    - **Hybrid Model**: Free base version + paid content hybrid model is increasingly popular
    - **Subscription Model**: Suitable for service-type games providing continuous content updates
    """)

def show_tab10(df, metrics, visuals):
    """
    显示标签页10：小倍数分析
    对应原标签页10的内容
    """
    st.header("📊 Multi-dimensional Comparative Analysis")  # 模块标题
    small_multiples_fig = create_small_multiples(df)  # 生成小倍数图
    st.plotly_chart(small_multiples_fig, use_container_width=True)  # 显示小倍数图，自适应宽度
    
    st.subheader("🔍 Analysis Guide")  # 分析说明子标题
    st.write("""  # 小倍数图解读指南
    **Small Multiples Interpretation Guide:**
    - Each subplot represents the relationship between price and positive rating for a game genre
    - Point positions show the pricing strategy and market acceptance of that genre
    - Colors distinguish different game genres for easy comparison
    - Top-right genres indicate high-price, high-rating premium games
    - Bottom-left genres may represent low-price, low-rating entry-level games
    """)