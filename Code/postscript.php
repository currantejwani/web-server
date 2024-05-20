<?php
if(isset($_POST['name']) && isset($_POST['age'])) {
    $name = $_POST['name'];
    $age = $_POST['age'];
    $message = "Hello $name, you are $age years old!";
    echo $message;
} else {
    echo "Please provide a name and age parameter.";
}
?>