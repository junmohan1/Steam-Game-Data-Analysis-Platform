import streamlit as st  # 导入streamlit库，用于构建网页应用
import pandas as pd  # 导入pandas库，用于数据处理和分析
from PIL import Image  # 导入PIL库用于处理图片
from utils.io import load_and_preprocess_data  # 从utils.io模块导入数据加载和预处理函数
from utils.prep import create_sidebar_filters, apply_filters, calculate_key_metrics  # 从utils.prep模块导入过滤器创建、应用和指标计算函数
from utils.viz import create_all_visualizations  # 从utils.viz模块导入可视化图表创建函数
from sections.data_overview import show_tab1, show_tab11  # 从sections.data_overview模块导入标签页1和11显示函数
from sections.trend_analysis import show_tab2, show_tab3, show_tab4, show_tab5  # 从sections.trend_analysis模块导入标签页2-5显示函数
from sections.market_analysis import show_tab6, show_tab7, show_tab8, show_tab9, show_tab10  # 从sections.market_analysis模块导入标签页6-10显示函数
from sections.conclusions import show_tab12  # 从sections.conclusions模块导入标签页12显示函数

def main():
    """
    Streamlit应用主函数
    构建完整的网页应用界面
    """
    # 设置网页配置 - 这些设置会影响整个网页应用的显示
    st.set_page_config(
        page_title="Steam Game Data Analysis Platform",  # 浏览器标签页标题
        page_icon="🎮",  # 网页图标（显示在浏览器标签页）
        layout="wide",  # 宽屏布局（充分利用屏幕宽度）
        initial_sidebar_state="expanded"  # 侧边栏初始状态为展开
    )
    
    # ========== 在侧边栏顶部添加本地图标 ==========
    with st.sidebar:
        # 使用Streamlit的columns来居中显示图片
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            try:
                # 加载并显示WUT图标
                wut_image = Image.open('C:/Users/ASUS/unit/project/WUT.png')
                st.image(wut_image, width=160)  # 设置宽度为160像素
                
                # 添加一些间距
                st.write("")  # 空行
                
                # 加载并显示EFREI图标
                efrei_image = Image.open('C:/Users/ASUS/unit/project/efrei.png')
                st.image(efrei_image, width=160)  # 设置宽度为160像素
                
            except FileNotFoundError:
                st.error("❌ Icon files not found, please check file paths")
            except Exception as e:
                st.error(f"❌ Error loading images: {e}")
        
        # 添加分隔线
        st.markdown("---")
    
    # 显示加载状态 - 在数据加载和处理期间显示旋转图标和提示文本
    with st.spinner('🚀 Loading data and generating visualizations...'):
        df = load_and_preprocess_data()  # 加载并预处理数据，返回处理后的DataFrame
        filters = create_sidebar_filters(df)  # 创建侧边栏过滤器，返回用户选择的过滤条件字典
        filtered_df = apply_filters(df, filters)  # 应用过滤器，返回过滤后的DataFrame
        metrics = calculate_key_metrics(filtered_df)  # 计算关键指标，返回包含各种指标的字典
        visuals = create_all_visualizations(filtered_df)  # 创建所有可视化图表，返回包含所有图表的字典
    
    # 应用主标题 - 显示在网页顶部的标题
    st.title("🎮 Steam Game Data Analysis Platform")
    
    # 创建顶部标签页导航 - 定义12个标签页
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12_tab = st.tabs([
        "📋 Dataset Overview",      # 标签1：数据概览和基本信息
        "📈 Time Trend Analysis",    # 标签2：时间序列分析  
        "📅 Monthly Release Analysis",    # 标签3：月度分析板块
        "💰 Price vs Sales Analysis",    # 标签4：价格与销售关系分析
        "⏱️ Rating & Engagement Analysis",  # 标签5：评价与用户参与度分析
        "🎮 Game Genre Analysis",    # 标签6：游戏类型分布分析
        "🏢 Publisher Analysis",      # 标签7：开发商和发行商分析
        "💻 Platform Support Analysis",    # 标签8：跨平台支持分析
        "🆓 Free vs Paid Analysis",    # 标签9：商业模式对比分析
        "📊 Multi-dimensional Analysis",      # 标签10：多维度对比分析
        "✅ Data Quality Report",     # 标签11：数据质量检查
        "💡 Business Insights"   # 标签12：业务结论和建议
    ])
    
    # 标签页1：数据集概览
    with tab1:
        show_tab1(filtered_df, metrics, visuals)  # 调用标签页1显示函数
    
    # 标签页2：时间趋势分析
    with tab2:
        show_tab2(filtered_df, metrics, visuals)  # 调用标签页2显示函数
    
    # 标签页3：月度发布分析
    with tab3:
        show_tab3(filtered_df, metrics, visuals)  # 调用标签页3显示函数
    
    # 标签页4：价格销量分析
    with tab4:
        show_tab4(filtered_df, metrics, visuals)  # 调用标签页4显示函数
    
    # 标签页5：评价参与度分析
    with tab5:
        show_tab5(filtered_df, metrics, visuals)  # 调用标签页5显示函数
    
    # 标签页6：游戏类型分析
    with tab6:
        show_tab6(filtered_df, metrics, visuals)  # 调用标签页6显示函数
    
    # 标签页7：开发商分析
    with tab7:
        show_tab7(filtered_df, metrics, visuals)  # 调用标签页7显示函数
    
    # 标签页8：平台支持分析
    with tab8:
        show_tab8(filtered_df, metrics, visuals)  # 调用标签页8显示函数
    
    # 标签页9：免费付费分析
    with tab9:
        show_tab9(filtered_df, metrics, visuals)  # 调用标签页9显示函数
    
    # 标签页10：小倍数分析
    with tab10:
        show_tab10(filtered_df, metrics, visuals)  # 调用标签页10显示函数
    
    # 标签页11：数据质量报告
    with tab11:
        show_tab11(filtered_df, metrics, visuals)  # 调用标签页11显示函数
    
    # 标签页12：业务结论和建议
    with tab12_tab:
        show_tab12(filtered_df, metrics, visuals)  # 调用标签页12显示函数
    
    # 页脚信息 - 显示在网页底部
    st.markdown("---")  # 分隔线
    st.markdown("*Steam Game Data Analysis Platform: Interactive analysis tool based on real Steam data*")  # 平台描述
    st.markdown("*Data Source: Steam Game Database*")  # 数据来源
    st.markdown("*Analysis Tools: Python + Streamlit*")  # 技术栈信息
    st.markdown("*Professor:Mano Mathew*")
    st.markdown("*Student name:Yueteng Zhang*")
    st.markdown("*github Url:https://github.com/junmohan1/Steam-Game-Data-Analysis-Platform.git*")


# 程序入口点 - 确保代码只在直接运行时执行，不在导入时执行
if __name__ == "__main__":
    main()  # 运行Streamlit应用主函数