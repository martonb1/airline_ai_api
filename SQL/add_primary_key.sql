USE Airline;
GO
ALTER TABLE dbo.airline_dataset
ADD flight_id INT IDENTITY(1,1) PRIMARY KEY;
