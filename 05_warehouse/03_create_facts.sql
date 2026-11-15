CREATE TABLE gold.FactTaxiDaily
(
    date_key          INT     NOT NULL,
    zone_key          INT     NOT NULL,
    trip_count        BIGINT  NOT NULL,
    passenger_count   BIGINT  NULL,
    distance_miles    FLOAT   NOT NULL,
    fare_usd          FLOAT   NOT NULL,
    tip_usd           FLOAT   NOT NULL,
    revenue_usd       FLOAT   NOT NULL,
    revenue_eur       FLOAT   NULL,
    avg_duration_min  FLOAT   NOT NULL
);

CREATE TABLE gold.FactAirQualityDaily
(
    date_key       INT          NOT NULL,
    borough_key    INT          NOT NULL,
    parameter      VARCHAR(10)  NOT NULL,
    units          VARCHAR(10)  NOT NULL,
    avg_value      FLOAT        NOT NULL,
    min_value      FLOAT        NOT NULL,
    max_value      FLOAT        NOT NULL,
    reading_count  BIGINT       NOT NULL,
    sensor_count   BIGINT       NOT NULL
);

CREATE TABLE gold.FactMobilityAirHourly
(
    date_key     INT          NOT NULL,
    hour_of_day  INT          NOT NULL,
    time_of_day  VARCHAR(20)  NOT NULL,
    borough_key  INT          NOT NULL,
    trip_count   BIGINT       NULL,
    revenue_usd  FLOAT        NULL,
    pm25_avg     FLOAT        NULL,
    no2_avg      FLOAT        NULL,
    o3_avg       FLOAT        NULL
);

ALTER TABLE gold.FactTaxiDaily         ADD CONSTRAINT FK_FactTaxiDaily_DimDate         FOREIGN KEY (date_key)    REFERENCES gold.DimDate (date_key)       NOT ENFORCED;
ALTER TABLE gold.FactTaxiDaily         ADD CONSTRAINT FK_FactTaxiDaily_DimZone         FOREIGN KEY (zone_key)    REFERENCES gold.DimZone (zone_key)       NOT ENFORCED;
ALTER TABLE gold.FactAirQualityDaily   ADD CONSTRAINT FK_FactAirQualityDaily_DimDate   FOREIGN KEY (date_key)    REFERENCES gold.DimDate (date_key)       NOT ENFORCED;
ALTER TABLE gold.FactAirQualityDaily   ADD CONSTRAINT FK_FactAirQualityDaily_DimBorough FOREIGN KEY (borough_key) REFERENCES gold.DimBorough (borough_key) NOT ENFORCED;
ALTER TABLE gold.FactMobilityAirHourly ADD CONSTRAINT FK_FactMobilityAirHourly_DimDate FOREIGN KEY (date_key)    REFERENCES gold.DimDate (date_key)       NOT ENFORCED;
ALTER TABLE gold.FactMobilityAirHourly ADD CONSTRAINT FK_FactMobilityAirHourly_DimBorough FOREIGN KEY (borough_key) REFERENCES gold.DimBorough (borough_key) NOT ENFORCED;
