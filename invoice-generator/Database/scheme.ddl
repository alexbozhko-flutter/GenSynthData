create table currencyrates
(
    id   serial,
    date date           not null,
    rate numeric(10, 5) not null,
    primary key ()
)
    using ???;

alter table currencyrates
    owner to latest;

create table customers
(
    id                  serial,
    full_name           varchar(255),
    discount_percentage integer default 0,
    phone               varchar(255),
    email               varchar(255),
    primary key ()
)
    using ???;

alter table customers
    owner to latest;

create table entrepreneurs
(
    id             integer default nextval('entrepreneurs_id_seq'::regclass) not null,
    name           varchar(255)                                              not null,
    account_number varchar(50),
    mfo            varchar(10),
    okpo_code      varchar(15),
    bank_name      varchar(255),
    phone          varchar(20),
    primary key ()
)
    using ???;

alter table entrepreneurs
    owner to latest;

create table manufacturers
(
    id      serial,
    name    varchar(255) not null,
    country varchar(255),
    primary key ()
)
    using ???;

alter table manufacturers
    owner to latest;

create table collections
(
    id              serial,
    name            varchar(255),
    manufacturer_id integer
        references manufacturers (),
    primary key ()
)
    using ???;

alter table collections
    owner to latest;

create table producttypes
(
    id           serial,
    name         varchar(255) not null,
    base_name    varchar(255),
    base_name_fr varchar(255),
    base_name_de varchar(255),
    base_name_it varchar(255),
    base_name_uk varchar(255),
    id_new       integer,
    primary key (),
    constraint name_unique
        unique ()
)
    using ???;

comment on column producttypes.base_name_fr is 'Название типа продукта на французском языке';

comment on column producttypes.base_name_de is 'Название типа продукта на немецком языке';

comment on column producttypes.base_name_it is 'Название типа продукта на итальянском языке';

comment on column producttypes.base_name_uk is 'Название типа продукта на украинском языке';

alter table producttypes
    owner to latest;

create table products
(
    id                   serial,
    name                 varchar(255)      not null,
    sku                  varchar(128)      not null,
    manufacturer_barcode varchar(16),
    retail_price         integer default 0 not null,
    cashless_price       integer default 0 not null,
    manufacturer_id      integer           not null
        references manufacturers (),
    collection_id        integer
        references collections (),
    product_type_id      integer           not null
        references producttypes (),
    product_type_id_new  integer,
    primary key (),
    constraint manufacturer_barcode_unique
        unique (),
    constraint sku_unique
        unique ()
)
    using ???;

alter table products
    owner to latest;

create table shops
(
    id      serial,
    name    varchar(255) not null,
    address varchar(255),
    primary key ()
)
    using ???;

alter table shops
    owner to latest;

create table invoicesin
(
    id           serial,
    created_date date,
    shop_id      integer
        references shops (),
    isclosed     boolean        default false not null,
    coefficient  numeric(10, 2) default 1.0   not null,
    primary key ()
)
    using ???;

alter table invoicesin
    owner to latest;

create table invoiceincontents
(
    id             serial,
    product_id     integer                  not null
        references products (),
    purchase_price numeric(10, 2) default 0 not null,
    quantity       integer        default 1 not null,
    invoice_in_id  integer                  not null
        references invoicesin (),
    taken_quantity integer        default 0 not null,
    primary key ()
)
    using ???;

alter table invoiceincontents
    owner to latest;

create table invoicesout
(
    id           serial,
    created_date date                  not null,
    shop_id      integer               not null
        references shops (),
    saletime     timestamp             not null,
    isclosed     boolean default false not null,
    customer_id  integer
                                       references customers ()
                                           on delete set null,
    checkid      varchar(36),
    primary key ()
)
    using ???;

alter table invoicesout
    owner to latest;

create table invoiceoutcontents
(
    id             serial,
    product_id     integer
        references products (),
    sale_price     integer,
    quantity       integer,
    invoice_out_id integer
        references invoicesout (),
    primary key ()
)
    using ???;

alter table invoiceoutcontents
    owner to latest;

create table invoicesout_checks
(
    id            serial,
    check_code    uuid    not null,
    invoiceout_id integer not null
        references invoicesout ()
            on delete cascade,
    created_date  date    not null,
    primary key ()
)
    using ???;

alter table invoicesout_checks
    owner to latest;

create table suppliers
(
    id          serial,
    name        varchar(255),
    description text,
    phone       varchar(16),
    primary key ()
)
    using ???;

alter table suppliers
    owner to latest;

create table users
(
    id       serial,
    username varchar(255) not null,
    password varchar(255) not null,
    shop_id  integer default 0
        references shops (),
    primary key ()
)
    using ???;

alter table users
    owner to latest;

create table warehousestate
(
    id           serial,
    product_id   integer                             not null
        references products (),
    shop_id      integer                             not null
        references shops (),
    quantity     integer   default 0                 not null,
    last_updated timestamp default CURRENT_TIMESTAMP not null,
    primary key ()
)
    using ???;

alter table warehousestate
    owner to latest;

create table product_attributes
(
    id             serial
        primary key,
    attribute_name varchar(100) not null
)
    using ???;

alter table product_attributes
    owner to latest;

create table product_attribute_values
(
    id           serial
        primary key,
    product_id   integer
        references products (),
    attribute_id integer
        references product_attributes,
    value        varchar(255) not null
)
    using ???;

alter table product_attribute_values
    owner to latest;

create view "vwStore"
            (id, product_name, sku, manufacturer_barcode, retail_price, cashless_price, product_type, manufacturer,
             collection, stock_balance)
as
SELECT p.id,
       p.name                                                   AS product_name,
       p.sku,
       p.manufacturer_barcode,
       p.retail_price,
       p.cashless_price,
       pt.name                                                  AS product_type,
       m.name                                                   AS manufacturer,
       COALESCE(c.name, 'отдельный продукт'::character varying) AS collection,
       ((SELECT COALESCE(sum(invoiceincontents.quantity), 0::bigint) AS "coalesce"
         FROM invoiceincontents
         WHERE invoiceincontents.product_id = p.id)) -
       ((SELECT COALESCE(sum(invoiceoutcontents.quantity), 0::bigint) AS "coalesce"
         FROM invoiceoutcontents
         WHERE invoiceoutcontents.product_id = p.id))           AS stock_balance
FROM products p
         JOIN producttypes pt ON p.product_type_id = pt.id
         JOIN manufacturers m ON p.manufacturer_id = m.id
         LEFT JOIN collections c ON p.collection_id = c.id;

alter table "vwStore"
    owner to latest;

create view "vwStore2"
            (id, product_name, sku, manufacturer_barcode, retail_price, cashless_price, product_type, manufacturer,
             collection, stock_balance)
as
SELECT ws.product_id                                            AS id,
       p.name                                                   AS product_name,
       p.sku,
       p.manufacturer_barcode,
       p.retail_price,
       p.cashless_price,
       pt.name                                                  AS product_type,
       m.name                                                   AS manufacturer,
       COALESCE(c.name, 'отдельный продукт'::character varying) AS collection,
       ws.quantity                                              AS stock_balance
FROM warehousestate ws
         JOIN products p ON ws.product_id = p.id
         JOIN producttypes pt ON p.product_type_id = pt.id
         JOIN manufacturers m ON p.manufacturer_id = m.id
         LEFT JOIN collections c ON p.collection_id = c.id;

alter table "vwStore2"
    owner to latest;

create view "vwStoreReport"
            (id, product_name, sku, manufacturer_barcode, retail_price, cashless_price, product_type, manufacturer,
             collection, stock_balance)
as
SELECT ws.product_id                                            AS id,
       p.name                                                   AS product_name,
       p.sku,
       p.manufacturer_barcode,
       p.retail_price,
       p.cashless_price,
       pt.name                                                  AS product_type,
       m.name                                                   AS manufacturer,
       COALESCE(c.name, 'отдельный продукт'::character varying) AS collection,
       ws.quantity                                              AS stock_balance
FROM warehousestate ws
         JOIN products p ON ws.product_id = p.id
         JOIN producttypes pt ON p.product_type_id = pt.id
         JOIN manufacturers m ON p.manufacturer_id = m.id
         LEFT JOIN collections c ON p.collection_id = c.id
WHERE ws.quantity > 0;

alter table "vwStoreReport"
    owner to latest;

create procedure add_invoice_into_warehouse_state(IN in_id integer)
    language plpgsql
as
$$
DECLARE
    product_id_var INTEGER;
    shop_id_var INTEGER;
    quantity_var INTEGER;
BEGIN
    FOR product_id_var, shop_id_var, quantity_var IN (
        SELECT 
            invoiceincontents.product_id, 
            invoicesin.shop_id, 
            invoiceincontents.quantity
        FROM 
            invoiceincontents
        JOIN 
            invoicesin ON invoiceincontents.invoice_in_id = invoicesin.id
        WHERE 
            invoiceincontents.invoice_in_id = in_id
    )
    LOOP
	IF is_product_in_stock(product_id_var, shop_id_var) THEN
	
	UPDATE latest.warehousestate
	SET quantity = quantity + quantity_var
	WHERE product_id = product_id_var AND shop_id = shop_id_var;

	ELSE 
	
	INSERT INTO warehousestate (product_id, shop_id, quantity)
		VALUES (product_id_var, shop_id_var, quantity_var);

	END IF;	
        -- VALUES (product_id, shop_id, quantity_)
        -- ON CONFLICT (product_id, shop_id)
        -- DO UPDATE SET quantity = warehousestate.quantity + excluded.quantity;
    END LOOP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Something went wrong: %', SQLERRM;
        ROLLBACK;
END;
$$;

alter procedure add_invoice_into_warehouse_state(integer) owner to latest;

create function check_isclosed_change() returns trigger
    language plpgsql
as
$$
BEGIN
   IF NEW.isclosed IS DISTINCT FROM OLD.isclosed AND NEW.isclosed = TRUE THEN
      CALL latest.add_invoice_into_warehouse_state(NEW.id);
   END IF;
   RETURN NEW;
END;
$$;

alter function check_isclosed_change() owner to latest;

create function get_product_count_in_stock(p_product_id integer, p_shop_id integer) returns integer
    language plpgsql
as
$$
DECLARE
    v_stock INTEGER;
BEGIN
    SELECT COALESCE(SUM(quantity), 0)
    INTO v_stock
    FROM warehousestate
    WHERE (product_id = p_product_id) AND (shop_id = p_shop_id);

    RETURN v_stock;
END;
$$;

alter function get_product_count_in_stock(integer, integer) owner to latest;

create function is_invoice_fully_received(in_id integer) returns boolean
    language plpgsql
as
$$DECLARE
    fully_received BOOLEAN;
    taken_quantity_var INTEGER;
    quantity_var INTEGER;
    positions_count INTEGER;
BEGIN
    -- Проверяем количество позиций в накладной
    SELECT COUNT(*) INTO positions_count
    FROM invoiceincontents
    WHERE invoiceincontents.invoice_in_id = in_id;

    -- Если позиций нет, возвращаем false
    IF positions_count = 0 THEN
        RETURN false;
    END IF;

    fully_received := true;
    FOR taken_quantity_var, quantity_var IN (
        SELECT 
            invoiceincontents.taken_quantity, 
            invoiceincontents.quantity
        FROM 
            invoiceincontents        
        WHERE 
            invoiceincontents.invoice_in_id = in_id
    )
    LOOP
        IF taken_quantity_var <> quantity_var THEN
            fully_received := false;
            EXIT;
        END IF;    
    END LOOP;
    RETURN fully_received;
END;
$$;

alter function is_invoice_fully_received(integer) owner to latest;

create function is_product_in_stock(p_product_id integer, p_shop_id integer) returns boolean
    language plpgsql
as
$$
DECLARE
    v_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 
        FROM latest.warehousestate 
        WHERE product_id = p_product_id AND shop_id = p_shop_id
    ) INTO v_exists;
    
    RETURN v_exists;
END;
$$;

alter function is_product_in_stock(integer, integer) owner to latest;

create function prevent_modification_on_closed_invoice() returns trigger
    language plpgsql
as
$$
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF (SELECT isclosed FROM latest.invoicesin WHERE id = OLD.invoice_in_id) THEN
      RAISE EXCEPTION '#1001. Cannot modify contents of a closed invoice.';
    END IF;
    RETURN OLD;
  ELSE
    IF (SELECT isclosed FROM latest.invoicesin WHERE id = NEW.invoice_in_id) THEN
      RAISE EXCEPTION '#1001. Cannot modify contents of a closed invoice.';
    END IF;
    RETURN NEW;
  END IF;
END;
$$;

alter function prevent_modification_on_closed_invoice() owner to latest;

create function prevent_modification_on_closed_invoiceout() returns trigger
    language plpgsql
as
$$
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF (SELECT isclosed FROM latest.invoicesout WHERE id = OLD.invoice_out_id) THEN
      RAISE EXCEPTION '#1001. Cannot modify contents of a closed invoice.';
    END IF;
    RETURN OLD;
  ELSE
    IF (SELECT isclosed FROM latest.invoicesout WHERE id = NEW.invoice_out_id) THEN
      RAISE EXCEPTION '#1001. Cannot modify contents of a closed invoice.';
    END IF;
    RETURN NEW;
  END IF;
END;
$$;

alter function prevent_modification_on_closed_invoiceout() owner to latest;

create procedure subtract_invoice_out_from_warehouse_state(IN out_id integer)
    language plpgsql
as
$$
DECLARE
    product_id_var INTEGER;
    shop_id_var INTEGER;
    quantity_var INTEGER;
	current_quantity INTEGER; -- текущее количество на складе
BEGIN
    FOR product_id_var, shop_id_var, quantity_var IN (
        SELECT 
            invoiceoutcontents.product_id, 
            invoicesout.shop_id, 
            invoiceoutcontents.quantity
        FROM 
            invoiceoutcontents
        JOIN 
            invoicesout ON invoiceoutcontents.invoice_out_id = invoicesout.id
        WHERE 
            invoiceoutcontents.invoice_out_id= out_id
    )
    LOOP
	
	-- Получите текущее количество товара на складе
    SELECT quantity INTO current_quantity
    FROM latest.warehousestate
    WHERE product_id = product_id_var AND shop_id = shop_id_var;
	
	IF is_product_in_stock(product_id_var, shop_id_var) THEN
	
	IF current_quantity < quantity_var THEN
		RAISE EXCEPTION '#0012. The product is not in stock.';
	END IF;
	
	UPDATE latest.warehousestate
			SET quantity = quantity - quantity_var
			WHERE product_id = product_id_var AND shop_id = shop_id_var;	

	ELSE 
	
		RAISE EXCEPTION '#0011. The product is not in stock.';

	END IF;	
        -- VALUES (product_id, shop_id, quantity_)
        -- ON CONFLICT (product_id, shop_id)
        -- DO UPDATE SET quantity = warehousestate.quantity + excluded.quantity;
    END LOOP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Something went wrong: %', SQLERRM;
        ROLLBACK;
END;
$$;

alter procedure subtract_invoice_out_from_warehouse_state(integer) owner to latest;

create function subtract_invoice_out_from_warehouse_state_trigger() returns trigger
    language plpgsql
as
$$
BEGIN
  -- Попытка вызова процедуры
  BEGIN
    CALL latest.subtract_invoice_out_from_warehouse_state(NEW.id);
  EXCEPTION
    WHEN OTHERS THEN
      -- В случае исключения откатываем транзакцию
     -- RAISE NOTICE 'Exception: %', SQLERRM;
	  RAISE EXCEPTION '#1003. There is not enough stock available in the warehouse.';
      NEW.isclosed := FALSE;
      RETURN NEW;
  END;
  RETURN NEW;
END;
$$;

alter function subtract_invoice_out_from_warehouse_state_trigger() owner to latest;

create function get_product_attributes_string(p_product_id integer) returns text
    language plpgsql
as
$$
DECLARE
    result_string TEXT := '';
    attribute_record RECORD;
BEGIN
    FOR attribute_record IN
        SELECT pa.attribute_name, pav.value
        FROM product_attribute_values pav
                 JOIN product_attributes pa ON pav.attribute_id = pa.id
        WHERE pav.product_id = p_product_id
        LOOP
            result_string := result_string || attribute_record.attribute_name || attribute_record.value || ';';
        END LOOP;

    -- Удаляем последний лишний символ ';' если строка не пустая
    IF LENGTH(result_string) > 0 THEN
        result_string := SUBSTRING(result_string FROM 1 FOR LENGTH(result_string) - 1);
    END IF;

    RETURN result_string;
END;
$$;

alter function get_product_attributes_string(integer) owner to latest;

create function get_product_attributes_string_v2(p_product_id integer) returns text
    language plpgsql
as
$$
DECLARE
    result_string TEXT := '';
    attribute_record RECORD;
BEGIN
    FOR attribute_record IN
        SELECT pa.attribute_name, pav.value
        FROM product_attribute_values pav
                 JOIN product_attributes pa ON pav.attribute_id = pa.id
        WHERE pav.product_id = p_product_id
        LOOP
            result_string := result_string || '<' || attribute_record.attribute_name || '>' || '<' || attribute_record.value || '>' || ';';
        END LOOP;

    -- Удаляем последний лишний символ ';' если строка не пустая
    IF LENGTH(result_string) > 0 THEN
        result_string := SUBSTRING(result_string FROM 1 FOR LENGTH(result_string) - 1);
    END IF;

    RETURN result_string;
END;
$$;

alter function get_product_attributes_string_v2(integer) owner to latest;

create function get_product_attribute_values_only_string(p_product_id integer) returns text
    language plpgsql
as
$$
DECLARE
    result_string TEXT := '';
    val_record RECORD; -- Переменная для хранения строки из результата запроса
BEGIN
    FOR val_record IN
        SELECT pav.value
        FROM product_attribute_values pav
        WHERE pav.product_id = p_product_id
        ORDER BY pav.attribute_id -- Сортируем по ID атрибута для консистентного порядка значений
    -- Если порядок не важен, эту строку можно удалить.
    -- Альтернативно, можно сортировать по pa.id или pa.attribute_name,
    -- если присоединить таблицу product_attributes.
        LOOP
            result_string := result_string || val_record.value || ';';
        END LOOP;

    -- Удаляем последний лишний символ ';' если строка не пустая
    IF LENGTH(result_string) > 0 THEN
        result_string := SUBSTRING(result_string FROM 1 FOR LENGTH(result_string) - 1);
    END IF;

    RETURN result_string;
END;
$$;

alter function get_product_attribute_values_only_string(integer) owner to latest;