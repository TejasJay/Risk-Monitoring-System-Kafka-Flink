SET sql-client.execution.result-mode = 'TABLEAU';


------------------------------------------- MAIN TRANSACTION TABLE -------------------------------------------------

CREATE TABLE Transactions (
  `Name` STRING,
  `Address` STRING,
  `Email` STRING,
  `City` STRING,
  `State` STRING,
  `Country` STRING,
  `Phone Number` STRING,
  `Account Number` STRING,
  `IP Address` STRING,
  `Login Devices` ARRAY<STRING>,
  `Card Types` ARRAY<STRING>,
  `Transaction Types` ARRAY<STRING>,
  `Card Number` STRING,
  `Usual Transaction Amount` DOUBLE,
  `Transaction ID` STRING,
  `Transaction Time` STRING,
  `Current Login Device` STRING,
  `Current Card Type` STRING,
  `Current Transaction Type` STRING,
  `Current Transaction Amount` DOUBLE,
  `Fraud Flags` STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'bank_transactions',
  'properties.bootstrap.servers' = 'localhost:9092',
  'format' = 'json',
  'properties.group.id' = 'fraud_alerts_reader',
  'scan.startup.mode' = 'earliest-offset'
);



CREATE TABLE TransactionsWithEventTime (
  `Name` STRING,
  `Address` STRING,
  `Email` STRING,
  `City` STRING,
  `State` STRING,
  `Country` STRING,
  `Phone Number` STRING,
  `Account Number` STRING,
  `IP Address` STRING,
  `Login Devices` ARRAY<STRING>,
  `Card Types` ARRAY<STRING>,
  `Transaction Types` ARRAY<STRING>,
  `Card Number` STRING,
  `Usual Transaction Amount` DOUBLE,
  `Transaction ID` STRING,
  `Transaction Time` STRING,
  `Current Login Device` STRING,
  `Current Card Type` STRING,
  `Current Transaction Type` STRING,
  `Current Transaction Amount` DOUBLE,
  `Fraud Flags` STRING,
  event_ts AS TO_TIMESTAMP(`Transaction Time`, 'yyyy-MM-dd HH:mm:ss.SSS'),
  WATERMARK FOR event_ts AS event_ts - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'bank_transactions',
  'properties.bootstrap.servers' = 'localhost:9092',
  'format' = 'json',
  'properties.group.id' = 'fraud_alerts_reader',
  'scan.startup.mode' = 'earliest-offset'
);




------------------------------------------- FRAUD DASHBOARD -------------------------------------------------

-- Recreate FraudDashboard as APPEND-ONLY Kafka
CREATE TABLE FraudDashboard (
  win_start TIMESTAMP(3),
  metric_type STRING,
  metric_key STRING,
  metric_value DOUBLE
) WITH (
  'connector' = 'kafka',
  'topic' = 'fraud_dashboard',
  'properties.bootstrap.servers' = 'localhost:9092',
  'format' = 'json',
  'scan.startup.mode' = 'earliest-offset',
 'properties.group.id' = 'fraud_alerts_reader'
);

------------------------------------------- RISK MATRIX -------------------------------------------------

CREATE TABLE CustomerRisk (
  `Name` STRING,
  `Account Number` STRING,
  Total_Txns BIGINT,
  Fraud_Txns BIGINT,
  Avg_Amount DOUBLE,
  Risk_Level STRING,
  PRIMARY KEY (`Account Number`) NOT ENFORCED
) WITH (
  'connector' = 'upsert-kafka',
  'topic' = 'customer_risk',
  'properties.bootstrap.servers' = 'localhost:9092',
  'key.format' = 'json',
  'properties.group.id' = 'fraud_alerts_reader',
  'value.format' = 'json'
);



------------------------------------------- BLOCKED CUSTOMERS -------------------------------------------------

CREATE TABLE BlockedCustomers (
  `Name` STRING,
  `Account Number` STRING,
  `Current Transaction Amount` DOUBLE,
  `Transaction ID` STRING,
  `Transaction Time` STRING,
  Reason STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'blocked_customers',
  'properties.bootstrap.servers' = 'localhost:9092',
  'format' = 'json',
  'properties.group.id' = 'fraud_alerts_reader',
  'scan.startup.mode' = 'earliest-offset'
);

------------------------------------------- EXECUTE STATEMENT SET -------------------------------------------------

EXECUTE STATEMENT SET
BEGIN

  -- Insert into FraudDashboard

	-- Insert analytics into FraudDashboard using CTEs
	INSERT INTO FraudDashboard
	WITH
	  fraud_by_device AS (
	    SELECT
	      TUMBLE_START(event_ts, INTERVAL '1' MINUTE) AS win_start,
	      `Current Login Device` AS device,
	      COUNT(*) AS fraud_count
	    FROM TransactionsWithEventTime
	    WHERE `Fraud Flags` <> 'No Fraud'
	    GROUP BY TUMBLE(event_ts, INTERVAL '1' MINUTE), `Current Login Device`
	  ),

	  high_risk_txns AS (
	    SELECT
	      TUMBLE_START(event_ts, INTERVAL '1' MINUTE) AS win_start,
	      COUNT(*) AS high_risk_count
	    FROM TransactionsWithEventTime
	    WHERE `Current Transaction Amount` > 10000
	    GROUP BY TUMBLE(event_ts, INTERVAL '1' MINUTE)
	  ),

	  fraud_by_card AS (
	    SELECT
	      TUMBLE_START(event_ts, INTERVAL '1' MINUTE) AS win_start,
	      `Current Card Type` AS card_type,
	      COUNT(*) AS total_txns,
	      SUM(CASE WHEN `Fraud Flags` <> 'No Fraud' THEN 1 ELSE 0 END) AS fraud_txns
	    FROM TransactionsWithEventTime
	    GROUP BY TUMBLE(event_ts, INTERVAL '1' MINUTE), `Current Card Type`
	  )

	-- UNION of 3 metric types
	SELECT
	  win_start,
	  'fraud_count_by_device' AS metric_type,
	  device AS metric_key,
	  CAST(fraud_count AS DOUBLE) AS metric_value
	FROM fraud_by_device

	UNION ALL

	SELECT
	  win_start,
	  'high_risk_txn_count' AS metric_type,
	  'all' AS metric_key,
	  CAST(high_risk_count AS DOUBLE)
	FROM high_risk_txns

	UNION ALL

	SELECT
	  win_start,
	  'fraud_percentage_by_card' AS metric_type,
	  card_type AS metric_key,
	  ROUND(fraud_txns * 100.0 / total_txns, 2) AS metric_value
	FROM fraud_by_card;



  -- Insert into CustomerRisk
  INSERT INTO CustomerRisk
  SELECT
    `Name`,
    `Account Number`,
    COUNT(*) AS Total_Txns,
    SUM(CASE WHEN `Fraud Flags` <> 'No Fraud' THEN 1 ELSE 0 END) AS Fraud_Txns,
    AVG(`Current Transaction Amount`) AS Avg_Amount,
    CASE
      WHEN SUM(CASE WHEN `Fraud Flags` <> 'No Fraud' THEN 1 ELSE 0 END) >= 3
           OR MAX(`Current Transaction Amount`) > 10000 THEN 'High Risk'
      WHEN SUM(CASE WHEN `Fraud Flags` <> 'No Fraud' THEN 1 ELSE 0 END) BETWEEN 1 AND 2
           OR AVG(`Current Transaction Amount`) > 5000 THEN 'Moderate Risk'
      ELSE 'Low Risk'
    END AS Risk_Level
  FROM Transactions
  GROUP BY `Name`, `Account Number`;

  -- Insert into BlockedCustomers
  INSERT INTO BlockedCustomers
  SELECT
    `Name`,
    `Account Number`,
    `Current Transaction Amount`,
    `Transaction ID`,
    `Transaction Time`,
    'Amount exceeds $50,000' AS Reason
  FROM Transactions
  WHERE `Current Transaction Amount` > 50000;

END;

-- Prevent session to close


SHOW TABLES;


