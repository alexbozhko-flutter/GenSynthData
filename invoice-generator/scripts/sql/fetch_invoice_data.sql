-- Запрос для получения данных инвойса
-- Параметры:
--   %s: ID инвойса (integer)
-- Возвращает:
--   - Номер инвойса (invoice_in_number)
--   - Дату создания (invoice_date)
--   - Позицию товара (item_position)
--   - ID продукта (product_id)
--   - Наименование продукта с коллекцией (product_design)
--   - Артикул продукта (product_sku)
--   - Параметры продукта (parameters) в формате <Key><Value>;<Key><Value>
--   - Количество (quantity)
--   - Цену закупки (purchase_price)
--   - Сумму по позиции (item_amount)

SELECT
    ii.id AS invoice_in_number,
    ii.created_date AS invoice_date,
    iic.id AS item_position,
    iic.product_id,
    col.name AS collection_name,
    p.name AS product_name,
    pt.name AS product_type_name,
    p.sku AS product_sku,
    get_product_attributes_string_v2(p.id) AS parameters,
    iic.quantity,
    iic.purchase_price,
    (iic.quantity * iic.purchase_price) AS item_amount
FROM
    invoicesin ii
        JOIN
    invoiceincontents iic ON ii.id = iic.invoice_in_id
        JOIN
    products p ON iic.product_id = p.id
        LEFT JOIN
    collections col ON p.collection_id = col.id
        LEFT JOIN
    producttypes pt ON p.product_type_id = pt.id
WHERE
    ii.id = %s
ORDER BY
    iic.id; 