CREATE PROCEDURE gold.usp_reload_table
    @target_table SYSNAME,
    @source_table SYSNAME
AS
BEGIN
    DECLARE @columns NVARCHAR(MAX) = (
        SELECT STRING_AGG(CAST(QUOTENAME(COLUMN_NAME) AS NVARCHAR(MAX)), ', ') WITHIN GROUP (ORDER BY ORDINAL_POSITION)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'gold' AND TABLE_NAME = @target_table
    );

    DECLARE @statement NVARCHAR(MAX) = CONCAT(
        N'DELETE FROM gold.', QUOTENAME(@target_table), N'; ',
        N'INSERT INTO gold.', QUOTENAME(@target_table), N' (', @columns, N') ',
        N'SELECT ', @columns, N' FROM lh_gold.dbo.', QUOTENAME(@source_table), N';'
    );

    EXEC sp_executesql @statement;
END;
GO

CREATE PROCEDURE gold.usp_load_star_schema
AS
BEGIN
    EXEC gold.usp_reload_table 'DimDate', 'dim_date';
    EXEC gold.usp_reload_table 'DimBorough', 'dim_borough';
    EXEC gold.usp_reload_table 'DimZone', 'dim_zone';
    EXEC gold.usp_reload_table 'DimFX', 'dim_fx';
    EXEC gold.usp_reload_table 'DimGDP', 'dim_gdp';
    EXEC gold.usp_reload_table 'FactTaxiDaily', 'fact_taxi_daily';
    EXEC gold.usp_reload_table 'FactAirQualityDaily', 'fact_air_quality_daily';
    EXEC gold.usp_reload_table 'FactMobilityAirHourly', 'fact_mobility_air_hourly';
END;
GO
