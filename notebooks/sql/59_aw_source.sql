-- Read-only Parquet sources are registered by the notebook. Derived facts live
-- only in this in-memory connection. Keep order and line grains separate.
CREATE MACRO aw_known_sum(x) AS CASE WHEN count(*) > count(x) THEN NULL ELSE sum(x) END;

CREATE TEMP TABLE aw_lines AS
WITH priced AS (
    SELECT d.SalesOrderID AS order_id, h.OrderDate::DATE AS order_date,
           d.ProductID AS product_id, p.Name AS product,
           coalesce(cat.Name, 'Unclassified') AS category,
           coalesce(sub.Name, 'Unclassified') AS subcategory,
           d.OrderQty::BIGINT AS units, d.LineTotal::DOUBLE AS net_sales,
           (d.OrderQty * d.UnitPrice * d.UnitPriceDiscount)::DOUBLE AS discount_value,
           coalesce(cost.StandardCost, p.StandardCost)::DOUBLE AS unit_cost,
           cost.StandardCost IS NULL AND p.StandardCost IS NOT NULL AS cost_fallback
    FROM SalesOrderDetail d
    JOIN SalesOrderHeader h USING (SalesOrderID)
    LEFT JOIN Product p USING (ProductID)
    LEFT JOIN ProductSubcategory sub USING (ProductSubcategoryID)
    LEFT JOIN ProductCategory cat USING (ProductCategoryID)
    LEFT JOIN LATERAL (
        SELECT StandardCost FROM ProductCostHistory ch
        WHERE ch.ProductID = d.ProductID AND ch.StartDate::DATE <= h.OrderDate::DATE
          AND (ch.EndDate IS NULL OR ch.EndDate::DATE >= h.OrderDate::DATE)
        ORDER BY ch.StartDate DESC LIMIT 1
    ) cost ON TRUE
    WHERE h.Status = 5
)
SELECT *, net_sales - units * unit_cost AS gross_contribution FROM priced;

CREATE TEMP TABLE aw_orders AS
WITH amounts AS (
    SELECT order_id, sum(net_sales) AS net_sales,
           aw_known_sum(gross_contribution) AS gross_contribution,
           sum(units) AS units,
           sum(net_sales) FILTER (WHERE cost_fallback) AS fallback_sales,
           sum(net_sales) FILTER (WHERE unit_cost IS NULL) AS missing_cost_sales
    FROM aw_lines GROUP BY order_id
)
SELECT h.SalesOrderID AS order_id, h.OrderDate::DATE AS order_date,
       h.ShipDate::DATE AS ship_date, h.DueDate::DATE AS due_date,
       h.CustomerID AS customer_id, c.StoreID AS store_id,
       coalesce(s.Name, 'Customer ' || h.CustomerID) AS customer,
       CASE WHEN h.OnlineOrderFlag THEN 'Online' ELSE 'Sales-assisted' END AS channel,
       h.TerritoryID AS territory_id, coalesce(t.Name, 'Unassigned') AS territory,
       coalesce(t."Group", 'Unassigned') AS region,
       coalesce(cr.Name, t.CountryRegionCode, 'Unassigned') AS country,
       t.CountryRegionCode AS country_code,
       coalesce(sm.Name, 'Unspecified') AS ship_method,
       a.net_sales, a.gross_contribution, a.units, a.fallback_sales, a.missing_cost_sales,
       h.SubTotal::DOUBLE AS header_subtotal, h.Freight::DOUBLE AS freight,
       date_diff('day', h.OrderDate::DATE, h.ShipDate::DATE) AS dispatch_days
FROM SalesOrderHeader h
JOIN amounts a ON a.order_id = h.SalesOrderID
LEFT JOIN Customer c USING (CustomerID)
LEFT JOIN Store s ON s.BusinessEntityID = c.StoreID
LEFT JOIN SalesTerritory t ON t.TerritoryID = h.TerritoryID
LEFT JOIN CountryRegion cr ON cr.CountryRegionCode = t.CountryRegionCode
LEFT JOIN ShipMethod sm USING (ShipMethodID)
WHERE h.Status = 5;

CREATE TEMP VIEW aw_first_seen AS
SELECT customer_id, min(order_date) AS first_seen FROM aw_orders GROUP BY customer_id;
