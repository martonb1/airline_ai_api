USE Airline;
SELECT 
    airline,
    SUM(passenger_load) AS total_passengers
FROM dbo.airline_dataset
GROUP BY airline
ORDER BY total_passengers DESC;
