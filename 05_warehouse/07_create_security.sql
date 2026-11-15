CREATE TABLE gold.SecurityUserBorough
(
    user_email   VARCHAR(256)  NOT NULL,
    borough_key  INT           NOT NULL
);

INSERT INTO gold.SecurityUserBorough (user_email, borough_key)
SELECT 'manhattan.analyst@yourtenant.onmicrosoft.com', borough_key
FROM gold.DimBorough
WHERE borough = 'Manhattan';
