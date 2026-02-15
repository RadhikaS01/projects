// This is the entry point of the application. It initializes the application and sets up any necessary configurations or middleware.

const express = require('express');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const userController = require('./controllers/userController');
const app = express();

app.use(bodyParser.json());
mongoose.connect('mongodb://localhost:27017/users', { useNewUrlParser: true, useUnifiedTopology: true });

app.post('/users', userController.createUser);
app.get('/users', userController.getUsers);

app.listen(3000, () => {
console.log('User service running on port 3000');
});