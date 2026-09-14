-- ============================================================
-- RFM 用户分层 SQL（适用于 MySQL 8+ / PostgreSQL 思路一致）
-- 演示：从订单表计算 R/F/M，并用分位打分完成用户分层
-- ============================================================

WITH user_rfm AS (
    SELECT
        user_id,
        MAX(order_date)                                   AS last_order_date,
        COUNT(DISTINCT order_id)                          AS frequency,
        SUM(amount)                                       AS monetary,
        DATEDIFF(CURRENT_DATE, MAX(order_date))           AS recency
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL 365 DAY
    GROUP BY user_id
),
scored AS (
    SELECT
        user_id,
        recency,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY recency DESC)  AS r_score,  -- 越近分越高
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,  -- 越多分越高
        NTILE(4) OVER (ORDER BY monetary ASC)  AS m_score   -- 越高分越高
    FROM user_rfm
)
SELECT
    user_id,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN '重要价值客户'
        WHEN r_score >= 4 AND f_score <= 2 AND m_score >= 3 THEN '重要发展客户'
        WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN '重要唤回客户'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN '流失风险客户'
        WHEN r_score >= 3 AND f_score <= 2 AND m_score <= 3 THEN '新客/潜力客户'
        ELSE '一般价值客户'
    END AS segment
FROM scored
ORDER BY user_id;
