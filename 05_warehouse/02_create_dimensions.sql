CREATE TABLE gold.DimDate
(
    date_key        INT          NOT NULL,
    calendar_date   DATE         NOT NULL,
    year_number     INT          NOT NULL,
    quarter_number  INT          NOT NULL,
    month_number    INT          NOT NULL,
    month_name      VARCHAR(12)  NOT NULL,
    day_of_month    INT          NOT NULL,
    day_of_week     INT          NOT NULL,
    day_name        VARCHAR(12)  NOT NULL,
    is_weekend      BIT          NOT NULL
);

CREATE TABLE gold.DimBorough
(
    borough_key  INT          NOT NULL,
    borough      VARCHAR(50)  NOT NULL
);

CREATE TABLE gold.DimZone
(
    zone_key      INT           NOT NULL,
    zone_name     VARCHAR(100)  NOT NULL,
    service_zone  VARCHAR(50)   NOT NULL,
    borough_key   INT           NOT NULL,
    borough       VARCHAR(50)   NOT NULL
);

CREATE TABLE gold.DimFX
(
    date_key     INT    NOT NULL,
    usd_per_eur  FLOAT  NULL,
    eur_per_usd  FLOAT  NULL
);

CREATE TABLE gold.DimGDP
(
    country_code    VARCHAR(3)    NOT NULL,
    country_name    VARCHAR(100)  NOT NULL,
    year_number     INT           NOT NULL,
    gdp_usd         FLOAT         NOT NULL,
    gdp_growth_pct  FLOAT         NULL
);

ALTER TABLE gold.DimDate    ADD CONSTRAINT PK_DimDate    PRIMARY KEY NONCLUSTERED (date_key) NOT ENFORCED;
ALTER TABLE gold.DimBorough ADD CONSTRAINT PK_DimBorough PRIMARY KEY NONCLUSTERED (borough_key) NOT ENFORCED;
ALTER TABLE gold.DimZone    ADD CONSTRAINT PK_DimZone    PRIMARY KEY NONCLUSTERED (zone_key) NOT ENFORCED;
ALTER TABLE gold.DimFX      ADD CONSTRAINT PK_DimFX      PRIMARY KEY NONCLUSTERED (date_key) NOT ENFORCED;
ALTER TABLE gold.DimGDP     ADD CONSTRAINT PK_DimGDP     PRIMARY KEY NONCLUSTERED (country_code, year_number) NOT ENFORCED;
