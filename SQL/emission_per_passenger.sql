USE Airline;
SELECT 
    airline,
    SUM(co2_emissions_tonnes) AS total_co2,
    SUM(passenger_load) AS total_passengers,
    CAST(SUM(co2_emissions_tonnes) * 1.0 / NULLIF(SUM(passenger_load),0) AS DECIMAL(10,4)) 
        AS co2_per_passenger
FROM dbo.airline_dataset
GROUP BY airline
ORDER BY co2_per_passenger ASC;
