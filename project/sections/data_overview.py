import streamlit as st  # 导入streamlit用于创建网页应用界面
import pandas as pd  # 导入pandas用于数据处理
from utils.viz import create_data_quality_section  # 从utils.viz模块导入数据质量报告函数

def show_tab1(df, metrics, visuals):
    """
    显示标签页1：数据集概览
    对应原标签页1的内容
    """
    st.header("📋 Dataset Overview")  # 模块标题
    
    col1, col2, col3, col4 = st.columns(4)  # 创建4个等宽列布局用于显示关键指标
    
    with col1:
        st.metric("Total Games", f"{metrics['total_games']:,}")  # 显示游戏总数指标卡，使用千位分隔符格式化数字
    
    with col2:
        st.metric("Free Games Percentage", f"{metrics['free_game_percentage']:.1f}%")  # 显示免费游戏比例指标卡，保留1位小数
    
    with col3:
        st.metric("Average Positive Rating", f"{metrics['avg_rating']:.1f}%")  # 显示平均好评率指标卡，保留1位小数
    
    with col4:
        st.metric("Data Time Range", metrics['year_range'])  # 显示数据时间范围指标卡
    
    st.subheader("📄 Data Sample Preview")  # 数据样本展示子标题
    sample_data = df[['name', 'release_year', 'main_genre', 'price', 'positive_ratio', 'owners_median']].head(10)  # 选择要显示的列并取前10行数据
    st.dataframe(sample_data, use_container_width=True)  # 显示数据表格，自适应容器宽度
    
    st.subheader("ℹ️ Dataset Basic Information")  # 数据集基本信息子标题
    col1, col2 = st.columns(2)  # 创建2列布局
    
    with col1:
        st.write(f"- **Total Records**: {metrics['total_games']:,}")  # 显示总记录数，使用千位分隔符
        st.write(f"- **Number of Columns**: {len(df.columns)}")  # 显示数据列数
        st.write(f"- **Number of Game Genres**: {metrics['unique_genres']}")  # 显示唯一游戏类型数量
    
    with col2:
        st.write(f"- **Windows Games**: {metrics['windows_games']:,}")  # 显示Windows平台游戏数
        st.write(f"- **Mac Games**: {metrics['mac_games']:,}")  # 显示Mac平台游戏数
        st.write(f"- **Linux Games**: {metrics['linux_games']:,}")  # 显示Linux平台游戏数

def show_tab11(df, metrics, visuals):
    """
    显示标签页11：数据质量报告
    对应原标签页11的内容
    """

    create_data_quality_section(df)  # 调用数据质量报告函数显示完整的数据质量分析