<?php
if(isset($_GET['name']) && isset($_GET['age'])) {
    $name = $_GET['name'];
    $age = $_GET['age'];
    $message = "Hello $name, you are $age years old!";
    echo $message;
} else {
    echo "Please provide a name and age parameter.";
}
?>
