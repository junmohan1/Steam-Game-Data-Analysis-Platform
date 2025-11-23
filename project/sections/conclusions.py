import streamlit as st  # 导入streamlit用于创建网页应用界面
import pandas as pd  # 导入pandas用于数据处理

def show_tab12(df, metrics, visuals):
    """
    显示标签页12：业务结论和建议
    这是新增的标签页12内容
    """
    st.header("💡 Business Insights & Strategic Recommendations")  # 模块主标题
    
    # 关键发现总结
    st.subheader("🎯 Key Findings Summary")  # 关键发现子标题
    
    col1, col2 = st.columns(2)  # 创建2列布局显示关键指标
    
    with col1:
        st.metric("Total Market Size", f"{metrics['total_games']:,} games")  # 显示市场总规模指标
        st.metric("Paid Games Dominance", f"{(100 - metrics['free_game_percentage']):.1f}%")  # 显示付费游戏占比指标
        st.metric("Player Satisfaction", f"{metrics['avg_rating']:.1f}% positive rating")  # 显示玩家满意度指标
    
    with col2:
        st.metric("Release Peak", f"{metrics['peak_year']}")  # 显示发布高峰年份指标
        st.metric("Multi-platform Trend", f"{metrics['multi_platform_games']:,} games")  # 显示多平台游戏数量指标
        st.metric("Genre Diversity", f"{metrics['unique_genres']} genres")  # 显示类型多样性指标
    
    # 市场趋势分析
    st.subheader("📈 Market Trend Analysis")  # 市场趋势分析子标题
    
    st.info(f"""
    **Annual Release Trend**: Steam platform game releases show continuous growth, especially peaking in {metrics['peak_year']}, indicating the prosperity of the digital distribution market.
    **Monthly Release Pattern**: Month {metrics['peak_month']} is the peak period for game releases, possibly related to holiday seasons and business strategies, with developers tending to release games before important sales seasons.
    """)  # 使用信息框显示市场趋势分析，动态插入指标数据
    
    # 定价策略洞察
    st.subheader("💰 Pricing Strategy Insights")  # 定价策略洞察子标题
    
    st.success(f"""
    **Price Sensitivity**: Games in the $20-30 price range perform best in both sales and positive ratings, indicating this is the most accepted price range by consumers.
    **Free Game Effect**: Although free games account for {metrics['free_game_percentage']:.1f}% of the total, they have unique advantages in user acquisition and player engagement.
    **Value Perception**: High-priced games need to provide corresponding high-quality content to justify their value, otherwise they may face sales challenges.
    """)  # 使用成功框显示定价策略洞察，动态插入免费游戏比例
    
    # 平台战略建议
    st.subheader("🔧 Platform Strategy Recommendations")  # 平台战略建议子标题
    
    st.warning("""
    **Windows Dominance**: Windows platform supports nearly 100% of games and is the essential base platform for ensuring compatibility.
    **Cross-platform Opportunities**: Multi-platform games have obvious advantages in user coverage and business performance, supporting Mac and Linux can additionally cover about 30% of potential users.
    **Technical Investment**: Cross-platform development requires upfront technical investment but can significantly expand market coverage in the long term.
    """)  # 使用警告框显示平台战略建议
    
    # 类型市场机会
    st.subheader("🎮 Genre Market Opportunities")  # 类型市场机会子标题
    
    st.write(f"""
    **Mainstream Genres**: {', '.join(metrics['top_genres'][:3])} and other genres dominate in quantity, with intense competition but large user bases.
    **Niche Opportunities**: Small niche genres may have blue ocean market opportunities, especially those with high ratings but low quantity.
    **Innovation Space**: Genre fusion and innovation may bring new market growth points.
    """)  # 显示类型市场机会分析，动态插入前3个热门类型
    
    # 开发者策略
    st.subheader("🏢 Developer Strategy Recommendations")  # 开发者策略建议子标题
    
    col1, col2 = st.columns(2)  # 创建2列布局显示开发者策略
    
    with col1:
        st.write("**Independent Developers**:")  # 独立开发者策略标题
        st.write("""
        - Focus on niche genres and unique gameplay
        - Use free or low-price strategies to acquire initial users
        - Emphasize community building and player feedback
        - Consider multi-platform releases to expand influence
        """)  # 独立开发者具体建议
    
    with col2:
        st.write("**Large Developers**:")  # 大型开发商策略标题
        st.write("""
        - Invest in high-quality, high-price point flagship products
        - Establish genre brands and serialized products
        - Deploy multi-platform and cross-platform experiences
        - Explore free + in-app purchase hybrid business models
        """)  # 大型开发商具体建议
    
    # 未来展望
    st.subheader("🔮 Future Development Trends")  # 未来发展趋势子标题
    
    st.info("""
    **Technology Driven**: Cloud gaming, AI-generated content and other new technologies will reshape game development and distribution models.
    **Business Model Evolution**: Subscription models, games as a service and other new models will continue to develop and grow.
    **Globalization Opportunities**: Growth in emerging markets provides new growth momentum for game globalization.
    **Community Operations**: Player communities will become key factors in long-term game success.
    """)  # 使用信息框显示未来发展趋势
    
    # 行动建议
    st.subheader("🚀 Immediate Action Recommendations")  # 立即行动建议子标题
    
    st.success(f"""
    1. **Market Entry**: New developers are advised to enter with ${int(metrics['median_price'])}-$20 price range {metrics['top_genres'][0] if metrics['top_genres'] else "mainstream"} genres
    2. **Platform Strategy**: Ensure Windows compatibility, actively consider Mac/Linux support
    3. **Quality First**: Invest in game quality and player experience, positive ratings are key to long-term success
    4. **Data Driven**: Continuously monitor market data and player feedback, adjust strategies promptly
    """)  # 使用成功框显示立即行动建议，动态插入价格和类型数据
    
    # 数据局限性说明
    st.markdown("---")  # 添加分隔线
    st.subheader("📝 Analysis Limitations")  # 分析局限性说明子标题
    
    st.write("""
    - **Data Timeliness**: This analysis is based on historical data, market conditions may have changed
    - **Data Coverage**: The dataset may not include all Steam games, especially recently released works
    - **Estimated Data**: Sales data are range estimates and may have certain errors
    - **Causality**: Correlation analysis cannot directly prove causality, requires further verification
    - **Cultural Factors**: Analysis is mainly based on quantitative data, qualitative factors like culture and region are not considered
    """)  # 显示分析局限性说明