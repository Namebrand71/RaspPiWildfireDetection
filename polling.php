<?php

// Set database connection parameters
$hostname = 'localhost';  // Replace with your MySQL server hostname
$username = 'root';  // Replace with your MySQL username
$password = 'password';  // Replace with your MySQL password
$database = 'piSenseDB';  // Replace with your MySQL database name


// Create a database connection
$mysqli = new mysqli($hostname, $username, $password, $database);

// Check the connection
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}

// Function to insert sensor data into the specified table
// Function to insert sensor data into the specified table
function insertSensorData($table, $temperature, $humidity, $windSpeed, $soilMoisture) {
    global $mysqli;
	
	$time = time();

    $query = "INSERT INTO $table (temperature, humidity, wind_speed, soil_moisture, timestamp_column) VALUES (?, ?, ?, ?, ?)";
    $statement = $mysqli->prepare($query);

    // Bind parameters
    $statement->bind_param('ddddd', $temperature, $humidity, $windSpeed, $soilMoisture, $time);

    // Execute the query
    $result = $statement->execute();

    // Check if the query was successful
    if ($result) {
        echo "Data inserted successfully into $table table.\n";
    } else {
        echo "Error inserting data into $table table: " . $statement->error . "\n";
    }

    // Close the statement
    $statement->close();
}



// Check if the request method is POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get the JSON data from the request body
    $json_data = file_get_contents('php://input');

    // Parse JSON data
    $data = json_decode($json_data, true);

    // Check if JSON decoding was successful
    if ($data !== null && is_array($data)) {
        // Iterate through the array of data objects
        foreach ($data as $item) {
            // Extract data from each object
            $table = $item['table'];
            $temperature = $item['temperature'];
            $humidity = $item['humidity'];
            $windSpeed = $item['windSpeed'];
            $soilMoisture = $item['soilMoisture'];
            echo "Table: $table\n";
            echo "Temperature: $temperature\n";
            echo "Humidity: $humidity\n";
            echo "Wind Speed: $windSpeed\n";
            echo "Soil Moisture: $soilMoisture\n";

            // Check if the table name is valid
            if (in_array($table, ['sensor_readings1', 'sensor_readings2', 'sensor_readings3'])) {
                // Insert data into the specified table
                insertSensorData($table, $temperature, $humidity, $windSpeed, $soilMoisture);
            } else {
                echo "Invalid table name: $table\n";
            }
        }
    } else {
        echo "Error decoding JSON data or invalid data format.\n";
    }
}

function getMostRecentReadings($mysqli, $tableName) {
    $sql = "SELECT temperature, humidity, wind_speed, soil_moisture 
            FROM $tableName 
            ORDER BY timestamp_column DESC 
            LIMIT 1";

    $result = $mysqli->query($sql);

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        return $row;
    } else {
        return null;
    }
}

// Function to handle GET requests
function handleGetRequest() {
    global $mysqli;

    // Check if the table parameter is set in the GET request
    if (isset($_GET['table'])) {
        $tableName = $_GET['table'];

        // Check if the requested table exists
        if (in_array($tableName, ['sensor_readings1', 'sensor_readings2', 'sensor_readings3'])) {
            // Get the most recent readings from the specified table
            $readings = getMostRecentReadings($mysqli, $tableName);

            // Output the JSON response
            header('Content-Type: application/json');
            echo json_encode($readings);
        } else {
            // Invalid table name
            echo "Invalid table name";
        }
    } else {
        // Table parameter is not set
        echo "Table parameter is missing";
    }
}

// Handle GET requests
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    handleGetRequest();
}
// Close the database connection
$mysqli->close();

?>
