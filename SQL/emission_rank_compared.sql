USE Airline;
WITH airline_stats AS (
    SELECT 
        airline,
        SUM(passenger_load) AS total_passengers,
        SUM(co2_emissions_tonnes) AS total_co2,
        CAST(SUM(co2_emissions_tonnes) * 1.0 / NULLIF(SUM(passenger_load),0) AS DECIMAL(10,4)) AS co2_per_passenger
    FROM dbo.airline_dataset
    GROUP BY airline
)
SELECT
    airline,
    total_passengers,
    total_co2,
    co2_per_passenger,
    RANK() OVER (ORDER BY co2_per_passenger ASC) AS efficiency_rank,
    AVG(co2_per_passenger) OVER () AS global_avg_co2_per_passenger,
    co2_per_passenger - AVG(co2_per_passenger) OVER () AS diff_from_avg
FROM airline_stats
ORDER BY efficiency_rank;
